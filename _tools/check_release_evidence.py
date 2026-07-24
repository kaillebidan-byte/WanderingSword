#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PR内で確定したrelease証跡を検査し、squash後の状態PR依存をなくす。"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CURRENT_PATH = ROOT / "_phase4_proofread" / "CURRENT_WORK.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_WORKFLOWS = {
    "relation": "Relation audit extraction",
    "cross": "Cross register QA",
    "apply": "Apply curated localization fixes",
}
VALID_LINEAGE_MODES = {"branch_ancestor", "squash_merged"}


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def evidence_path_from_current(current: dict[str, Any]) -> Path:
    checkpoint = current.get("checkpoint", {})
    identity = checkpoint.get("release_identity", {}) if isinstance(checkpoint, dict) else {}
    path = identity.get("evidence") if isinstance(identity, dict) else None
    if not isinstance(path, str) or not path.startswith("_phase4_proofread/RELEASE_EVIDENCE_") or not path.endswith(".json"):
        raise SystemExit("ERROR: checkpoint.release_identity.evidence is invalid")
    return ROOT / path


def validate_evidence(evidence: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    checkpoint = current.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return ["CURRENT_WORK.checkpoint must be an object"]
    identity = checkpoint.get("release_identity")
    if not isinstance(identity, dict):
        return ["checkpoint.release_identity must be an object"]

    if evidence.get("schema_version") != 1:
        errors.append("release evidence schema_version must be 1")
    if evidence.get("status") != "verified":
        errors.append("release evidence status must be verified")
    if identity.get("kind") != "pr_release_v1":
        errors.append("checkpoint.release_identity.kind must be pr_release_v1")

    release_id = evidence.get("release_id")
    if not _nonempty(release_id):
        errors.append("release_id must be a non-empty string")
    if identity.get("release_id") != release_id:
        errors.append("checkpoint release_id does not match evidence")

    train_id = evidence.get("train_id")
    if not _nonempty(train_id):
        errors.append("train_id must be a non-empty string")

    pr = evidence.get("pr")
    if not _positive_int(pr):
        errors.append("release evidence pr must be a positive integer")
    if identity.get("pr") != pr or checkpoint.get("produced_by_pr") != pr:
        errors.append("release PR does not match checkpoint")

    ci_head = evidence.get("ci_head")
    asset_head = evidence.get("asset_head")
    if not _sha(ci_head):
        errors.append("ci_head must be a 40-character lowercase SHA")
    if not _sha(asset_head):
        errors.append("asset_head must be a 40-character lowercase SHA")
    if identity.get("validated_head") != asset_head:
        errors.append("checkpoint validated_head does not match evidence asset_head")

    counts = evidence.get("counts")
    if not isinstance(counts, dict):
        errors.append("counts must be an object")
        counts = {}
    for key, expected in (
        ("batch", current.get("last_completed_batch")),
        ("pair_applied_keys", current.get("pair_applied_keys")),
        ("project_applied_keys", current.get("project_applied_keys")),
    ):
        if counts.get(key) != expected or checkpoint.get(key) != expected:
            errors.append(
                f"{key} mismatch: evidence={counts.get(key)!r}, "
                f"checkpoint={checkpoint.get(key)!r}, current={expected!r}"
            )
    if counts.get("pending_fixes") != 0:
        errors.append("counts.pending_fixes must be 0")

    runs = evidence.get("runs")
    if not isinstance(runs, dict):
        errors.append("runs must be an object")
        runs = {}
    for key, workflow in EXPECTED_WORKFLOWS.items():
        item = runs.get(key)
        if not isinstance(item, dict):
            errors.append(f"runs.{key} must be an object")
            continue
        if not _positive_int(item.get("id")):
            errors.append(f"runs.{key}.id must be a positive integer")
        if item.get("workflow") != workflow:
            errors.append(f"runs.{key}.workflow must be {workflow!r}")
        if item.get("head_sha") != ci_head:
            errors.append(f"runs.{key}.head_sha must equal ci_head")
        if item.get("conclusion") != "success":
            errors.append(f"runs.{key}.conclusion must be success")

    lineage = evidence.get("lineage")
    if not isinstance(lineage, dict):
        errors.append("lineage must be an object")
    else:
        mode = lineage.get("mode")
        if mode not in VALID_LINEAGE_MODES:
            errors.append(f"lineage.mode must be one of {sorted(VALID_LINEAGE_MODES)!r}")
        if mode == "squash_merged":
            if not _sha(lineage.get("merge_sha")):
                errors.append("squash_merged lineage needs merge_sha")
        elif mode == "branch_ancestor" and lineage.get("merge_sha") is not None:
            errors.append("branch_ancestor lineage must not define merge_sha")

    applied_record = checkpoint.get("applied_record")
    if evidence.get("applied_record") != applied_record:
        errors.append("evidence applied_record does not match checkpoint")
    if not isinstance(applied_record, str) or not (ROOT / applied_record).is_file():
        errors.append(f"checkpoint applied_record does not exist: {applied_record!r}")

    return errors


def _git_is_ancestor(older: str, newer: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", older, newer],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return True, ""
    if result.returncode == 1:
        return False, "not an ancestor"
    return False, result.stderr.strip() or f"git returned {result.returncode}"


def verify_git_lineage(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lineage = evidence.get("lineage", {})
    mode = lineage.get("mode") if isinstance(lineage, dict) else None
    if mode == "branch_ancestor":
        for older, newer, label in (
            (str(evidence.get("ci_head", "")), str(evidence.get("asset_head", "")), "ci_head -> asset_head"),
            (str(evidence.get("asset_head", "")), "HEAD", "asset_head -> HEAD"),
        ):
            ok, detail = _git_is_ancestor(older, newer)
            if not ok:
                errors.append(f"release lineage failed for {label}: {detail}")
    elif mode == "squash_merged":
        merge_sha = str(lineage.get("merge_sha", ""))
        ok, detail = _git_is_ancestor(merge_sha, "HEAD")
        if not ok:
            errors.append(f"merged release SHA is not an ancestor of HEAD: {detail}")
    return errors


def _api_json(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "wandering-sword-release-evidence-check",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GitHub API request failed for {url}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"GitHub API returned non-object for {url}")
    return value


def verify_github(evidence: dict[str, Any], repository: str, token: str) -> list[str]:
    errors: list[str] = []
    pr = evidence.get("pr")
    ci_head = evidence.get("ci_head")
    runs = evidence.get("runs", {})
    for key, expected_name in EXPECTED_WORKFLOWS.items():
        item = runs.get(key, {}) if isinstance(runs, dict) else {}
        run_id = item.get("id") if isinstance(item, dict) else None
        if not _positive_int(run_id):
            continue
        try:
            run = _api_json(
                f"https://api.github.com/repos/{repository}/actions/runs/{run_id}", token
            )
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        if run.get("name") != expected_name:
            errors.append(f"GitHub run {run_id} name mismatch: {run.get('name')!r}")
        if run.get("conclusion") != "success":
            errors.append(f"GitHub run {run_id} is not successful")
        if run.get("head_sha") != ci_head:
            errors.append(f"GitHub run {run_id} head_sha mismatch")
        if run.get("event") != "pull_request":
            errors.append(f"GitHub run {run_id} event must be pull_request")
        prs = run.get("pull_requests", [])
        numbers = {
            item.get("number") for item in prs if isinstance(item, dict) and _positive_int(item.get("number"))
        } if isinstance(prs, list) else set()
        if pr not in numbers:
            errors.append(f"GitHub run {run_id} is not attached to PR #{pr}")

    lineage = evidence.get("lineage", {})
    if isinstance(lineage, dict) and lineage.get("mode") == "squash_merged" and _positive_int(pr):
        try:
            pull = _api_json(f"https://api.github.com/repos/{repository}/pulls/{pr}", token)
        except RuntimeError as exc:
            errors.append(str(exc))
        else:
            if pull.get("merged") is not True:
                errors.append(f"PR #{pr} is not merged")
            if pull.get("merge_commit_sha") != lineage.get("merge_sha"):
                errors.append(f"PR #{pr} merge SHA does not match release evidence")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-github", action="store_true")
    parser.add_argument("--verify-git-lineage", action="store_true")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_object(CURRENT_PATH)
    evidence_path = evidence_path_from_current(current)
    evidence = load_object(evidence_path)
    errors = validate_evidence(evidence, current)

    if args.verify_git_lineage and not errors:
        errors.extend(verify_git_lineage(evidence))
    if args.verify_github and not errors:
        token = os.environ.get("GITHUB_TOKEN", "")
        if not args.repository:
            errors.append("--verify-github requires --repository or GITHUB_REPOSITORY")
        elif not token:
            errors.append("--verify-github requires GITHUB_TOKEN")
        else:
            errors.extend(verify_github(evidence, args.repository, token))

    print("=== Release evidence ===")
    print(f"release: {evidence.get('release_id')}")
    print(f"train: {evidence.get('train_id')}")
    print(f"PR: {evidence.get('pr')}")
    print(f"lineage: {evidence.get('lineage', {}).get('mode')}")
    print(f"evidence: {evidence_path.relative_to(ROOT)}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: release evidence is complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
