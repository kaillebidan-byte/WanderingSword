#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release evidenceのGitHub Actions実体とPR対応を検査する。"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Callable

import check_release_evidence as core

JsonFetcher = Callable[[str, str], dict[str, Any]]


def verify_github(
    evidence: dict[str, Any],
    repository: str,
    token: str,
    *,
    fetch_json: JsonFetcher = core._api_json,
) -> list[str]:
    errors: list[str] = []
    pr = evidence.get("pr")
    ci_head = evidence.get("ci_head")
    runs = evidence.get("runs", {})
    lineage = evidence.get("lineage", {})
    lineage_mode = lineage.get("mode") if isinstance(lineage, dict) else None

    for key, expected_name in core.EXPECTED_WORKFLOWS.items():
        item = runs.get(key, {}) if isinstance(runs, dict) else {}
        run_id = item.get("id") if isinstance(item, dict) else None
        if not core._positive_int(run_id):
            continue
        try:
            run = fetch_json(
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
            candidate.get("number")
            for candidate in prs
            if isinstance(candidate, dict)
            and core._positive_int(candidate.get("number"))
        } if isinstance(prs, list) else set()
        if lineage_mode != "squash_merged" and pr not in numbers:
            errors.append(f"GitHub run {run_id} is not attached to PR #{pr}")

    if lineage_mode == "squash_merged" and core._positive_int(pr):
        try:
            pull = fetch_json(
                f"https://api.github.com/repos/{repository}/pulls/{pr}", token
            )
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
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = core.load_object(core.CURRENT_PATH)
    evidence_path = core.evidence_path_from_current(current)
    evidence = core.load_object(evidence_path)
    errors = core.validate_evidence(evidence, current)

    token = os.environ.get("GITHUB_TOKEN", "")
    if not args.repository:
        errors.append("GitHub verification requires --repository or GITHUB_REPOSITORY")
    elif not token:
        errors.append("GitHub verification requires GITHUB_TOKEN")
    elif not errors:
        errors.extend(verify_github(evidence, args.repository, token))

    print("=== Release evidence GitHub verification ===")
    print(f"release: {evidence.get('release_id')}")
    print(f"PR: {evidence.get('pr')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: GitHub workflow and PR evidence are complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
