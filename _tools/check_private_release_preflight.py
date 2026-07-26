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

BASE_CHECKS = [
    ["check_private_translation_stage.py"],
    ["check_candidate_ownership.py", "--require-current-wave"],
    ["check_ci_train_manifest_v2.py"],
    ["check_next_task_packet.py", "--allow-pending"],
    ["check_batch_planning.py"],
    ["check_translation_quality_gate.py"],
    ["check_release_transport_state.py"],
]
TESTS = [
    ["test_check_candidate_ownership.py"],
    ["test_check_next_task_packet_minimal.py"],
    ["test_check_release_transport_state.py"],
    ["test_orchestrate_release_ci.py"],
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


def main() -> int:
    args = parse_args()
    checks = [["check_operation_mode.py", "--repository-visibility", args.repository_visibility], *BASE_CHECKS]
    failures: list[str] = []
    for command in checks + (TESTS if args.with_tests else []):
        path = TOOLS / command[0]
        print(f"\n=== {command[0]} ===")
        result = subprocess.run([sys.executable, str(path), *command[1:]], cwd=ROOT, check=False)
        if result.returncode != 0:
            failures.append(command[0])
    if failures:
        print("\nFAILED release preflight: " + ", ".join(failures))
        return 1
    print(f"\nOK: pre-Apply release preflight passed for {args.repository_visibility}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
