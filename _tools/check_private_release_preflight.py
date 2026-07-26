#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公開前後に翻訳内容へ触れず、Apply前の輸送準備を一括検査する。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "_tools"

BASE_CHECKS_BEFORE_OWNERSHIP = [
    ["check_state_json_integrity.py"],
    ["check_private_translation_stage.py"],
    ["check_autonomous_cycle.py"],
]
BASE_CHECKS_AFTER_OWNERSHIP = [
    ["check_fix_owner_delta.py"],
    ["check_ci_train_manifest_v2.py"],
    ["check_next_task_packet.py", "--allow-pending"],
    ["check_batch_planning.py"],
    ["check_translation_quality_gate.py"],
    ["check_release_transport_state.py"],
]
TESTS = [
    ["test_check_state_json_integrity.py"],
    ["test_check_candidate_ownership.py"],
    ["test_check_fix_owner_delta.py"],
    ["test_check_next_task_packet_minimal.py"],
    ["test_check_release_transport_state.py"],
    ["test_check_autonomous_cycle.py"],
    ["test_write_applied_record.py"],
    ["test_release_ci_triggers.py"],
    ["test_check_operation_mode.py"],
    ["test_check_private_translation_stage.py"],
    ["test_check_ci_train_manifest.py"],
    ["test_check_next_task_packet_ownership.py"],
    ["test_check_batch_planning.py"],
    ["test_check_translation_quality_gate.py"],
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-tests", action="store_true")
    parser.add_argument("--repository-visibility", choices=("private", "public"), default="private")
    parser.add_argument(
        "--no-refresh-derived",
        action="store_true",
        help="private時のcandidate ownership snapshot自動更新を無効化する",
    )
    return parser.parse_args()


def run(command: list[str]) -> int:
    path = TOOLS / command[0]
    print(f"\n=== {' '.join(command)} ===")
    return subprocess.run(
        [sys.executable, str(path), *command[1:]],
        cwd=ROOT,
        check=False,
    ).returncode


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    if args.repository_visibility == "private" and not args.no_refresh_derived:
        if run(["check_candidate_ownership.py", "--write"]) != 0:
            failures.append("check_candidate_ownership.py --write")

    ownership_check = [
        "check_candidate_ownership.py",
        "--require-current-wave" if args.repository_visibility == "private" else "--release-live",
    ]
    checks = [
        ["check_operation_mode.py", "--repository-visibility", args.repository_visibility],
        *BASE_CHECKS_BEFORE_OWNERSHIP,
        ownership_check,
        *BASE_CHECKS_AFTER_OWNERSHIP,
    ]
    for command in checks + (TESTS if args.with_tests else []):
        if run(command) != 0:
            failures.append(" ".join(command))

    if subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=False).returncode != 0:
        failures.append("git diff --check")

    if failures:
        print("\nFAILED release preflight: " + ", ".join(failures))
        return 1

    if args.repository_visibility == "private":
        changed = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        print("\n=== Frozen release files to commit together ===")
        print(changed.stdout.rstrip() or "(clean)")
        print("Do not edit release files after this check and before the public CI window.")
    else:
        print("\nRelease preflight used live owner measurement; stored snapshot drift alone is non-blocking.")

    print(f"\nOK: pre-Apply release preflight passed for {args.repository_visibility}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
