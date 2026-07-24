#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXT_TASK_PACKETの監査行数と小束例外を検査する。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PACKET_PATH = ROOT / "_phase4_proofread" / "NEXT_TASK_PACKET.json"
TARGET_MIN = 15
TARGET_MAX = 30
ALLOWED_EXCEPTION_REASONS = {
    "isolated_branch_boundary",
    "high_risk_scene",
    "no_adjacent_in_scope_scene",
    "atomic_duplicate_set",
    "oversized_atomic_scene",
}


def load_packet(path: Path = PACKET_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("ERROR: NEXT_TASK_PACKET top level must be an object")
    return value


def focus_keys(packet: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    flow = packet.get("scene_flow", [])
    if not isinstance(flow, list):
        return keys
    for item in flow:
        if not isinstance(item, dict):
            continue
        item_keys = item.get("focus_keys", [])
        if isinstance(item_keys, list):
            keys.extend(key for key in item_keys if isinstance(key, str))
    return keys


def validate(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    planning = packet.get("batch_planning")
    if not isinstance(planning, dict):
        return ["batch_planning must be an object"]

    reviewed_rows = planning.get("reviewed_rows")
    target = planning.get("target_rows")
    adjacent = planning.get("adjacent_candidates_checked")
    grouping = planning.get("grouping_decision")
    exception = planning.get("exception")

    keys = focus_keys(packet)
    if not isinstance(reviewed_rows, int) or reviewed_rows <= 0:
        errors.append("batch_planning.reviewed_rows must be a positive integer")
    elif reviewed_rows != len(keys):
        errors.append(
            f"reviewed_rows mismatch: packet={reviewed_rows}, focus_keys={len(keys)}"
        )

    if not isinstance(target, dict):
        errors.append("batch_planning.target_rows must be an object")
    else:
        if target.get("min") != TARGET_MIN or target.get("max") != TARGET_MAX:
            errors.append(
                f"target_rows must be fixed at min={TARGET_MIN}, max={TARGET_MAX}"
            )

    if not isinstance(adjacent, list) or any(not isinstance(v, str) for v in adjacent):
        errors.append("batch_planning.adjacent_candidates_checked must be a string list")
        adjacent = []
    if not isinstance(grouping, str) or not grouping.strip():
        errors.append("batch_planning.grouping_decision is required")

    if isinstance(reviewed_rows, int) and reviewed_rows > 0:
        outside = reviewed_rows < TARGET_MIN or reviewed_rows > TARGET_MAX
        if not outside:
            if exception is not None:
                errors.append("batch_planning.exception must be null inside the target range")
        else:
            if not isinstance(exception, dict):
                errors.append("out-of-range batch requires batch_planning.exception")
            else:
                reason = exception.get("reason_code")
                detail = exception.get("detail")
                if reason not in ALLOWED_EXCEPTION_REASONS:
                    errors.append(
                        "batch_planning.exception.reason_code must be one of "
                        + ", ".join(sorted(ALLOWED_EXCEPTION_REASONS))
                    )
                if not isinstance(detail, str) or not detail.strip():
                    errors.append("batch_planning.exception.detail is required")
                if reviewed_rows < TARGET_MIN and not adjacent:
                    errors.append(
                        "small batch exception requires adjacent_candidates_checked"
                    )

    return errors


def main() -> int:
    packet = load_packet()
    errors = validate(packet)
    planning = packet.get("batch_planning", {})
    print("=== Batch planning ===")
    print(f"reviewed rows: {planning.get('reviewed_rows')}")
    print(f"target rows: {TARGET_MIN}-{TARGET_MAX}")
    print(f"scene groups: {', '.join(map(str, packet.get('scene_groups', [])))}")
    print(f"grouping: {planning.get('grouping_decision')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: review-row target and batching rationale are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
