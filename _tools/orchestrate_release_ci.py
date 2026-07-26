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

WORKFLOWS = {
    "Relation audit extraction": "relation-audit.yml",
    "Cross register QA": "cross-register-qa.yml",
    "Apply curated localization fixes": "apply-curated-fixes.yml",
}
QA_WORKFLOWS = ("Relation audit extraction", "Cross register QA")
APPLY_WORKFLOW = "Apply curated localization fixes"


def api_json(method: str, url: str, token: str, payload: Any | None = None) -> Any:
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
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {detail}") from exc


def select_new_run(runs: list[dict[str, Any]], name: str, baseline: int, target_sha: str) -> dict[str, Any] | None:
    matches = [
        run for run in runs
        if run.get("name") == name
        and run.get("event") == "workflow_dispatch"
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

    def pull(self) -> dict[str, Any]:
        value = api_json("GET", f"{self.base}/pulls/{self.pr}", self.token)
        if not isinstance(value, dict):
            raise RuntimeError("GitHub pull response must be an object")
        return value

    def current_head(self) -> str:
        return str(self.pull().get("head", {}).get("sha", ""))

    def head_ref(self) -> str:
        return str(self.pull().get("head", {}).get("ref", ""))

    def runs(self) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode({"event": "workflow_dispatch", "head_sha": self.target_sha, "per_page": 100})
        value = api_json("GET", f"{self.base}/actions/runs?{query}", self.token)
        runs = value.get("workflow_runs", []) if isinstance(value, dict) else []
        return [run for run in runs if isinstance(run, dict)]

    def baselines(self, names: tuple[str, ...]) -> dict[str, int]:
        runs = self.runs()
        return {
            name: max((int(run["id"]) for run in runs if run.get("name") == name and isinstance(run.get("id"), int)), default=0)
            for name in names
        }

    def dispatch(self, name: str, head_ref: str) -> None:
        filename = WORKFLOWS[name]
        endpoint = urllib.parse.quote(filename, safe="")
        payload = {
            "ref": head_ref,
            "inputs": {
                "pr_number": str(self.pr),
                "target_sha": self.target_sha,
                "head_ref": head_ref,
            },
        }
        api_json("POST", f"{self.base}/actions/workflows/{endpoint}/dispatches", self.token, payload)
        print(f"dispatched {name} on {head_ref}@{self.target_sha}")

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
    report: dict[str, Any] = {
        "schema_version": 2,
        "repository": args.repository,
        "pr": args.pr,
        "target_sha": args.target_sha,
        "event": "workflow_dispatch",
        "stages": {},
    }
    try:
        if client.current_head() != args.target_sha:
            raise RuntimeError("PR head changed before release QA")
        head_ref = client.head_ref()
        if not head_ref:
            raise RuntimeError("PR head ref is empty")

        qa_baselines = client.baselines(QA_WORKFLOWS)
        for name in QA_WORKFLOWS:
            client.dispatch(name, head_ref)
        qa_runs = client.wait_workflows(QA_WORKFLOWS, qa_baselines, args.timeout, args.poll)
        report["stages"]["qa"] = {
            name: {"id": run.get("id"), "event": run.get("event"), "conclusion": run.get("conclusion")}
            for name, run in qa_runs.items()
        }

        if client.current_head() != args.target_sha:
            raise RuntimeError("PR head changed between QA and Apply")
        apply_baselines = client.baselines((APPLY_WORKFLOW,))
        client.dispatch(APPLY_WORKFLOW, head_ref)
        apply_run = client.wait_workflows((APPLY_WORKFLOW,), apply_baselines, args.timeout, args.poll)[APPLY_WORKFLOW]
        report["stages"]["apply"] = {
            "id": apply_run.get("id"),
            "event": apply_run.get("event"),
            "conclusion": apply_run.get("conclusion"),
        }
        report["status"] = "success"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        raise
    finally:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: release CI completed in order; report={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
