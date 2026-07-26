#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase2相当のローカル検査を一命令で実行し、finalization修復pushを防ぐ。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "_tools"

CHECKS = (
    ("check_state_json_integrity.py",),
    ("check_release_evidence.py", "--verify-git-lineage"),
    ("check_handoff_consistency_v2.py", "--require-verified"),
    ("check_ci_train_manifest_v2.py",),
    ("check_private_translation_stage.py",),
    ("check_autonomous_cycle.py",),
    ("check_candidate_ownership.py", "--release-live"),
    ("check_fix_owner_delta.py",),
    ("check_translation_quality_gate.py",),
    ("check_next_task_packet.py",),
    ("check_batch_planning.py",),
)
TESTS = (
    ("test_check_state_json_integrity.py",),
    ("test_check_candidate_ownership.py",),
    ("test_check_next_task_packet_minimal.py",),
    ("test_check_release_transport_state.py",),
    ("test_check_autonomous_cycle.py",),
    ("test_write_applied_record.py",),
    ("test_release_ci_triggers.py",),
    ("test_check_visibility_preflight_contract.py",),
    ("test_check_operation_mode.py",),
    ("test_check_private_translation_stage.py",),
    ("test_check_release_evidence.py",),
    ("test_check_release_evidence_github.py",),
    ("test_check_handoff_consistency_v2.py",),
    ("test_check_ci_train_manifest.py",),
    ("test_check_next_task_packet_ownership.py",),
    ("test_check_batch_planning.py",),
    ("test_check_ci_train_state_v2.py",),
    ("test_check_translation_quality_gate.py",),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-tests", action="store_true")
    return parser.parse_args()


def run(command: tuple[str, ...]) -> int:
    print("\n=== " + " ".join(command) + " ===")
    return subprocess.run(
        [sys.executable, str(TOOLS / command[0]), *command[1:]],
        cwd=ROOT,
        check=False,
    ).returncode


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    for command in CHECKS + (TESTS if args.with_tests else ()):
        if run(command) != 0:
            failures.append(" ".join(command))
    if failures:
        print("\nFAILED release finalization: " + ", ".join(failures))
        return 1
    if subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=False).returncode != 0:
        print("FAILED: git diff --check")
        return 1
    print("\nOK: local phase2-equivalent finalization checks passed")
    print("Live owner measurement is authoritative during release; stored preparation snapshot drift is diagnostic only.")
    print("The GitHub phase2 run still verifies repository visibility, workflow evidence, and PR attachment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
