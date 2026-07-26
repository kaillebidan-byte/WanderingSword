#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release-ciをpreflight後のQA二本→Applyへ直列化する。"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

QA_WORKFLOWS = ("Relation audit extraction", "Cross register QA")
APPLY_WORKFLOW = "Apply curated localization fixes"


def api_json(method: str, url: str, token: str, payload: Any | None = None, *, allow_404: bool = False) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "wandering-sword-release-orchestrator",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return None
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {detail}") from exc


def select_new_run(runs: list[dict[str, Any]], name: str, baseline: int, target_sha: str) -> dict[str, Any] | None:
    matches = [
        run for run in runs
        if run.get("name") == name
        and run.get("head_sha") == target_sha
        and isinstance(run.get("id"), int)
        and run["id"] > baseline
    ]
    return max(matches, key=lambda item: item["id"]) if matches else None


class GitHubRelease:
    def __init__(self, repository: str, pr: int, target_sha: str, token: str) -> None:
        self.repository = repository
        self.pr = pr
        self.target_sha = target_sha
        self.token = token
        self.base = f"https://api.github.com/repos/{repository}"

    def current_head(self) -> str:
        value = api_json("GET", f"{self.base}/pulls/{self.pr}", self.token)
        return str(value.get("head", {}).get("sha", ""))

    def ensure_label(self, name: str, color: str) -> None:
        url = f"{self.base}/labels/{urllib.parse.quote(name, safe='')}"
        if api_json("GET", url, self.token, allow_404=True) is None:
            api_json("POST", f"{self.base}/labels", self.token, {"name": name, "color": color})

    def add_label(self, name: str) -> None:
        api_json("POST", f"{self.base}/issues/{self.pr}/labels", self.token, {"labels": [name]})

    def remove_label(self, name: str) -> None:
        api_json("DELETE", f"{self.base}/issues/{self.pr}/labels/{urllib.parse.quote(name, safe='')}", self.token, allow_404=True)

    def runs(self) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode({"event": "pull_request", "head_sha": self.target_sha, "per_page": 100})
        value = api_json("GET", f"{self.base}/actions/runs?{query}", self.token)
        runs = value.get("workflow_runs", []) if isinstance(value, dict) else []
        return [run for run in runs if isinstance(run, dict)]

    def baselines(self, names: tuple[str, ...]) -> dict[str, int]:
        runs = self.runs()
        return {
            name: max((int(run["id"]) for run in runs if run.get("name") == name and isinstance(run.get("id"), int)), default=0)
            for name in names
        }

    def wait_workflows(self, names: tuple[str, ...], baselines: dict[str, int], timeout: int, poll: int) -> dict[str, dict[str, Any]]:
        deadline = time.monotonic() + timeout
        completed: dict[str, dict[str, Any]] = {}
        while time.monotonic() < deadline:
            runs = self.runs()
            for name in names:
                run = select_new_run(runs, name, baselines.get(name, 0), self.target_sha)
                if run is None:
                    continue
                print(f"{name}: run={run.get('id')} status={run.get('status')} conclusion={run.get('conclusion')}")
                if run.get("status") == "completed":
                    if run.get("conclusion") != "success":
                        raise RuntimeError(f"{name} failed: run={run.get('id')} conclusion={run.get('conclusion')}")
                    completed[name] = run
            if all(name in completed for name in names):
                return completed
            time.sleep(poll)
        missing = [name for name in names if name not in completed]
        raise RuntimeError(f"timed out waiting for workflows: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--target-sha", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--poll", type=int, default=15)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("ERROR: GITHUB_TOKEN is required")

    client = GitHubRelease(args.repository, args.pr, args.target_sha, token)
    qa_label = "release-qa"
    apply_label = "release-apply"
    report: dict[str, Any] = {
        "schema_version": 1,
        "repository": args.repository,
        "pr": args.pr,
        "target_sha": args.target_sha,
        "stages": {},
    }
    client.ensure_label(qa_label, "1d76db")
    client.ensure_label(apply_label, "5319e7")
    client.remove_label(qa_label)
    client.remove_label(apply_label)
    try:
        if client.current_head() != args.target_sha:
            raise RuntimeError("PR head changed before release QA")
        qa_baselines = client.baselines(QA_WORKFLOWS)
        client.add_label(qa_label)
        qa_runs = client.wait_workflows(QA_WORKFLOWS, qa_baselines, args.timeout, args.poll)
        report["stages"]["qa"] = {name: {"id": run.get("id"), "conclusion": run.get("conclusion")} for name, run in qa_runs.items()}
        client.remove_label(qa_label)

        if client.current_head() != args.target_sha:
            raise RuntimeError("PR head changed between QA and Apply")
        apply_baselines = client.baselines((APPLY_WORKFLOW,))
        client.add_label(apply_label)
        apply_runs = client.wait_workflows((APPLY_WORKFLOW,), apply_baselines, args.timeout, args.poll)
        apply_run = apply_runs[APPLY_WORKFLOW]
        report["stages"]["apply"] = {"id": apply_run.get("id"), "conclusion": apply_run.get("conclusion")}
        report["status"] = "success"
    finally:
        client.remove_label(qa_label)
        client.remove_label(apply_label)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: release CI completed in order; report={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
