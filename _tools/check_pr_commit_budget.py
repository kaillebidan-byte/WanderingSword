#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub APIの一ファイル一commit化を検出し、PRのcommit数を制限する。"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "_phase4_proofread" / "GITHUB_API_WRITE_POLICY.json"


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("GitHub API write policy must be an object")
    return value


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if policy.get("contract_id") != "github-api-write-policy-v1":
        errors.append("contract_id mismatch")
    if policy.get("canonical_repository") != "kaillebidan-byte/WanderingSword":
        errors.append("canonical_repository mismatch")

    transport = policy.get("write_transport")
    if not isinstance(transport, dict):
        errors.append("write_transport must be an object")
    else:
        if transport.get("multiple_paths") != "atomic_git_commit_required":
            errors.append("multiple path writes must require an atomic git commit")
        if transport.get("file_by_file_contents_commit_loop_forbidden") is not True:
            errors.append("file-by-file contents commit loop must be forbidden")
        if transport.get("collect_complete_write_set_before_first_write") is not True:
            errors.append("complete write set must be collected before writing")
        if transport.get("max_conflict_retry_count") != 1:
            errors.append("max_conflict_retry_count must be 1")

    budget = policy.get("pull_request_commit_budget")
    if not isinstance(budget, dict):
        errors.append("pull_request_commit_budget must be an object")
    else:
        normal = budget.get("normal_target")
        hard = budget.get("hard_max")
        if not isinstance(normal, int) or normal <= 0:
            errors.append("normal_target must be a positive integer")
        if not isinstance(hard, int) or hard <= 0:
            errors.append("hard_max must be a positive integer")
        if isinstance(normal, int) and isinstance(hard, int) and normal > hard:
            errors.append("normal_target must not exceed hard_max")
        if budget.get("count_range") != "base_exclusive_to_head_inclusive":
            errors.append("commit count range mismatch")

    compaction = policy.get("history_compaction")
    if not isinstance(compaction, dict):
        errors.append("history_compaction must be an object")
    else:
        expected = {
            "trigger": "commit_count_above_normal_target",
            "target": "same_repository_draft_pr_only",
            "method": "reuse_head_tree_with_base_as_single_parent",
            "force_update": "force_with_lease_exact_expected_head",
            "base_branch": "main",
            "workflow": ".github/workflows/compact-pr-branch.yml",
            "helper": "_tools/compact_pr_branch.py",
        }
        for key, expected_value in expected.items():
            if compaction.get(key) != expected_value:
                errors.append(f"history_compaction.{key} mismatch")
        for key in (
            "expected_head_required",
            "tree_identity_required",
            "open_pr_required",
            "draft_required",
        ):
            if compaction.get(key) is not True:
                errors.append(f"history_compaction.{key} must be true")

    discovery = policy.get("discovery")
    if not isinstance(discovery, dict):
        errors.append("discovery must be an object")
    else:
        if discovery.get("web_search_for_github_api_usage_forbidden") is not True:
            errors.append("web search for GitHub API usage must be forbidden")
        if discovery.get("same_failed_arguments_must_not_be_retried_repeatedly") is not True:
            errors.append("repeated retries with unchanged arguments must be forbidden")
    return errors


def count_commits(base: str, head: str, *, root: Path = ROOT) -> int:
    result = subprocess.run(
        ["git", "rev-list", "--count", f"{base}..{head}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git rev-list failed"
        raise ValueError(message)
    return int(result.stdout.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument("--validate-policy-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        policy = load_policy(args.policy)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate_policy(policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.validate_policy_only:
        print("OK: GitHub API write policy is structurally valid")
        return 0
    if not args.base or not args.head:
        print("ERROR: --base and --head are required unless --validate-policy-only is used")
        return 1

    try:
        commits = count_commits(args.base, args.head)
    except ValueError as exc:
        print(f"ERROR: cannot count PR commits: {exc}")
        return 1

    budget = policy["pull_request_commit_budget"]
    normal_target = budget["normal_target"]
    hard_max = budget["hard_max"]
    print(f"PR commit count: {commits}")
    print(f"normal target: <= {normal_target}")
    print(f"hard maximum: <= {hard_max}")
    if commits > hard_max:
        print(
            "FAILED: PR commit budget exceeded. Do not commit one path at a time through the "
            "Contents API. Rebuild or compact the draft branch through the same-tree "
            "history-compaction workflow."
        )
        return 1
    if commits > normal_target:
        print(
            "WARNING: commit count is above the normal target. Use the same-tree "
            "history-compaction workflow before additional writes."
        )
    print("OK: PR commit budget passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
