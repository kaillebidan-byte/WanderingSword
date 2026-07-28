#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳内容へ触れず、Apply前の輸送準備、scope、cycle実行モードを一括検査する。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "_tools"

BASE_CHECKS = [
    ["check_state_json_integrity.py"],
    ["check_project_scope_lock.py"],
    ["check_phase_completion_signal.py"],
    ["check_private_translation_stage.py"],
    ["check_autonomous_cycle.py"],
    ["check_candidate_ownership.py", "--release-live"],
    ["check_owner_assignment_result.py"],
    ["check_fix_owner_delta.py"],
    ["check_ci_train_manifest_v2.py"],
    ["check_next_task_packet.py", "--allow-pending"],
    ["check_batch_planning.py"],
    ["check_translation_quality_gate.py"],
    ["check_release_transport_state.py"],
]
TESTS = [
    ["test_check_state_json_integrity.py"],
    ["test_check_project_scope_lock.py"],
    ["test_check_phase_completion_signal.py"],
    ["test_reconcile_merged_cycle.py"],
    ["test_check_candidate_ownership.py"],
    ["test_apply_owner_assignment.py"],
    ["test_check_fix_owner_delta.py"],
    ["test_check_next_task_packet_minimal.py"],
    ["test_check_release_transport_state.py"],
    ["test_check_autonomous_cycle.py"],
    ["test_select_cycle_execution_mode.py"],
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
    checks = [
        ["check_project_scope_lock.py", "--repository", "kaillebidan-byte/WanderingSword"],
        ["check_operation_mode.py", "--repository-visibility", args.repository_visibility],
        *BASE_CHECKS,
    ]
    for command in checks + (TESTS if args.with_tests else []):
        if run(command) != 0:
            failures.append(" ".join(command))

    if subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=False).returncode != 0:
        failures.append("git diff --check")

    if failures:
        print("\nFAILED release preflight: " + ", ".join(failures))
        return 1

    print("\nRelease preflight used live owner measurement and sealed owner-assignment evidence.")
    print("Stored candidate ownership snapshots remain immutable pre-quality-audit records.")
    print("External repository scope is locked to kaillebidan-byte/WanderingSword.")
    print("Regulated phase marker requires an authorized terminal phase state.")
    print(f"Cycle execution mode is valid for repository visibility {args.repository_visibility}.")
    print(f"\nOK: pre-Apply release preflight passed for {args.repository_visibility}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
