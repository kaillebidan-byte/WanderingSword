#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新チャット用申し送りと監査状態の整合を検査する。"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
AUDIT_PATH = P4 / "audit_status.json"
TODO_PATH = P4 / "_TODO.md"


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as fp:
            value = json.load(fp)
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: required file not found: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top-level JSON must be an object: {path.relative_to(ROOT)}")
    return value


def batch_number(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"batch(\d+)", value)
    return int(match.group(1)) if match else None


def check_git_ancestor(commit: str, errors: list[str], warnings: list[str]) -> None:
    if not commit:
        errors.append("CURRENT_WORK.translation_base_commit is empty")
        return
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except OSError as exc:
        warnings.append(f"git ancestor check skipped: {exc}")
        return
    if result.returncode == 1:
        errors.append(f"translation_base_commit is not an ancestor of HEAD: {commit}")
    elif result.returncode not in (0, 1):
        warnings.append(f"git ancestor check failed: {result.stderr.strip()}")


def main() -> int:
    current = load_json(CURRENT_PATH)
    audit = load_json(AUDIT_PATH)
    errors: list[str] = []
    warnings: list[str] = []

    for path in (ROOT / "README.md", P4 / "CURRENT_HANDOFF.md", ROOT / "AGENTS.md"):
        if not path.is_file():
            errors.append(f"required onboarding file missing: {path.relative_to(ROOT)}")

    current_pair = current.get("current_pair")
    audit_current = audit.get("current", {})
    if current_pair != audit_current.get("pair"):
        errors.append(
            f"current pair mismatch: CURRENT_WORK={current_pair!r}, "
            f"audit_status={audit_current.get('pair')!r}"
        )

    current_cluster = current.get("current_cluster")
    if current_cluster != audit_current.get("cluster"):
        errors.append(
            f"current cluster mismatch: CURRENT_WORK={current_cluster!r}, "
            f"audit_status={audit_current.get('cluster')!r}"
        )

    latest_build = audit.get("project", {}).get("latest_build", {})
    project_keys = current.get("project_applied_keys")
    if project_keys != latest_build.get("applied_keys"):
        errors.append(
            f"project applied key mismatch: CURRENT_WORK={project_keys!r}, "
            f"audit_status={latest_build.get('applied_keys')!r}"
        )

    pair_status = audit.get("pair_status", {}).get(current_pair, {})
    pair_keys = current.get("pair_applied_keys")
    if pair_keys != pair_status.get("applied_keys"):
        errors.append(
            f"pair applied key mismatch: CURRENT_WORK={pair_keys!r}, "
            f"audit_status={pair_status.get('applied_keys')!r}"
        )

    last_batch = current.get("last_completed_batch")
    translation_batch = batch_number(pair_status.get("translation_reaudited"))
    build_batch = batch_number(pair_status.get("build_verified"))
    for label, observed in (
        ("translation_reaudited", translation_batch),
        ("build_verified", build_batch),
    ):
        if observed is None:
            errors.append(f"audit_status pair field has no batch number: {label}")
        elif observed != last_batch:
            errors.append(
                f"completed batch mismatch for {label}: CURRENT_WORK={last_batch!r}, "
                f"audit_status={observed!r}"
            )

    record_index = latest_build.get("record_index", [])
    expected_record = f"APPLIED_FIXES_YUWEN_MOWEN_BATCH{last_batch}_"
    if not any(expected_record in str(path) for path in record_index):
        errors.append(f"latest applied record is absent from audit_status.record_index: {expected_record}")

    immediate = current.get("immediate_next", {})
    if not immediate.get("scene_groups") or not immediate.get("task"):
        errors.append("CURRENT_WORK.immediate_next must include scene_groups and task")

    if current.get("build_status") != latest_build.get("status"):
        errors.append(
            f"build status mismatch: CURRENT_WORK={current.get('build_status')!r}, "
            f"audit_status={latest_build.get('status')!r}"
        )
    if current.get("game_verified") != latest_build.get("game_verified"):
        errors.append(
            f"game verification mismatch: CURRENT_WORK={current.get('game_verified')!r}, "
            f"audit_status={latest_build.get('game_verified')!r}"
        )

    check_git_ancestor(str(current.get("translation_base_commit", "")), errors, warnings)

    audit_next = audit_current.get("next_action")
    current_next = immediate.get("task")
    if audit_next and current_next and audit_next != current_next:
        warnings.append(
            "audit_status.current.next_action differs from CURRENT_WORK.immediate_next.task; "
            "README defines CURRENT_WORK as the immediate-work source"
        )

    try:
        todo_text = TODO_PATH.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        warnings.append("_TODO.md not found")
    else:
        mowen_line = next(
            (line for line in todo_text.splitlines() if line.startswith("- [ ] **宇文逸↔莫問**")),
            "",
        )
        match = re.search(r"計(\d+)キー", mowen_line)
        if match and int(match.group(1)) != pair_keys:
            warnings.append(
                f"_TODO.md has stale 宇文逸↔莫問 count: {match.group(1)} != {pair_keys}; "
                "use CURRENT_WORK/audit_status for current counts"
            )

    print("=== Handoff consistency ===")
    print(f"pair: {current_pair}")
    print(f"completed batch: {last_batch}")
    print(f"pair keys: {pair_keys}")
    print(f"project keys: {project_keys}")
    print(f"next scenes: {', '.join(map(str, immediate.get('scene_groups', [])))}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
