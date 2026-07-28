#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXT_TASK_PACKETの詳細束とsemantic wave extensionを検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PACKET_PATH = ROOT / "_phase4_proofread" / "NEXT_TASK_PACKET.json"
DETAIL_MIN = 15
DETAIL_MAX = 30
SEMANTIC_MIN = 40
SEMANTIC_STANDARD_MAX = 60
SEMANTIC_HARD_MAX = 80
DETAIL_EXCEPTION_REASONS = {
    "isolated_branch_boundary",
    "high_risk_scene",
    "no_adjacent_in_scope_scene",
    "atomic_duplicate_set",
    "oversized_atomic_scene",
}
SEMANTIC_EXCEPTION_REASON = "complete_semantic_unit"


def load_packet(path: Path = PACKET_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("ERROR: NEXT_TASK_PACKET top level must be object")
    return value


def is_minimal_reservation(packet: dict[str, Any]) -> bool:
    return packet.get("schema_version") == 6 and packet.get("reservation", {}).get("status") == "reserved_only"


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


def _validate_common(planning: dict[str, Any], errors: list[str]) -> tuple[int | None, list[str], Any]:
    reviewed_rows = planning.get("reviewed_rows")
    adjacent = planning.get("adjacent_candidates_checked")
    grouping = planning.get("grouping_decision")
    if not isinstance(reviewed_rows, int) or reviewed_rows <= 0:
        errors.append("batch_planning.reviewed_rows must be a positive integer")
        reviewed_rows = None
    if not isinstance(adjacent, list) or any(not isinstance(v, str) for v in adjacent):
        errors.append("batch_planning.adjacent_candidates_checked must be a string list")
        adjacent = []
    if not isinstance(grouping, str) or not grouping.strip():
        errors.append("batch_planning.grouping_decision is required")
    return reviewed_rows, adjacent, planning.get("exception")


def _validate_detail(packet: dict[str, Any], planning: dict[str, Any], errors: list[str]) -> None:
    reviewed_rows, adjacent, exception = _validate_common(planning, errors)
    keys = focus_keys(packet)
    if reviewed_rows is not None and reviewed_rows != len(keys):
        errors.append(f"reviewed_rows mismatch: packet={reviewed_rows}, focus_keys={len(keys)}")
    target = planning.get("target_rows")
    if target != {"min": DETAIL_MIN, "max": DETAIL_MAX}:
        errors.append(f"target_rows must be fixed at min={DETAIL_MIN}, max={DETAIL_MAX}")
    if reviewed_rows is None:
        return
    outside = reviewed_rows < DETAIL_MIN or reviewed_rows > DETAIL_MAX
    if reviewed_rows < DETAIL_MIN and not adjacent:
        errors.append("small batch exception requires adjacent_candidates_checked")
    if not outside:
        if exception is not None:
            errors.append("batch_planning.exception must be null inside the target range")
        return
    if not isinstance(exception, dict):
        errors.append("out-of-range batch requires batch_planning.exception")
        return
    reason = exception.get("reason_code")
    detail = exception.get("detail")
    if reason not in DETAIL_EXCEPTION_REASONS:
        errors.append("batch_planning.exception.reason_code must be one of " + ", ".join(sorted(DETAIL_EXCEPTION_REASONS)))
    if not isinstance(detail, str) or not detail.strip():
        errors.append("batch_planning.exception.detail is required")


def _validate_semantic(packet: dict[str, Any], planning: dict[str, Any], errors: list[str]) -> None:
    reviewed_rows, adjacent, exception = _validate_common(planning, errors)
    if planning.get("target_rows") != {"min": SEMANTIC_MIN, "max": SEMANTIC_STANDARD_MAX}:
        errors.append(f"semantic target_rows must be min={SEMANTIC_MIN}, max={SEMANTIC_STANDARD_MAX}")
    if planning.get("hard_max") != SEMANTIC_HARD_MAX:
        errors.append(f"semantic hard_max must be {SEMANTIC_HARD_MAX}")
    scenes = packet.get("scene_groups")
    if not isinstance(scenes, list) or not scenes or any(not isinstance(v, str) or not v for v in scenes):
        errors.append("semantic wave requires non-empty scene_groups")
    if reviewed_rows is None:
        return
    if reviewed_rows < SEMANTIC_MIN or reviewed_rows > SEMANTIC_HARD_MAX:
        errors.append(f"semantic wave reviewed_rows must be {SEMANTIC_MIN}..{SEMANTIC_HARD_MAX}")
    if reviewed_rows <= SEMANTIC_STANDARD_MAX:
        if exception is not None:
            errors.append("semantic exception must be null at 60 rows or below")
        return
    if not isinstance(exception, dict):
        errors.append("semantic extension above 60 rows requires batch_planning.exception")
        return
    if exception.get("reason_code") != SEMANTIC_EXCEPTION_REASON:
        errors.append("semantic extension reason_code must be complete_semantic_unit")
    detail = exception.get("detail")
    if not isinstance(detail, str) or not detail.strip():
        errors.append("semantic extension detail is required")
    if not adjacent:
        errors.append("semantic extension requires adjacent_candidates_checked")


def validate(packet: dict[str, Any]) -> list[str]:
    if is_minimal_reservation(packet):
        return []
    errors: list[str] = []
    planning = packet.get("batch_planning")
    if not isinstance(planning, dict):
        return ["batch_planning must be an object"]
    mode = planning.get("mode", "detail_packet")
    if mode == "detail_packet":
        _validate_detail(packet, planning, errors)
    elif mode == "semantic_wave":
        _validate_semantic(packet, planning, errors)
    else:
        errors.append("batch_planning.mode must be detail_packet or semantic_wave")
    return errors


def main() -> int:
    packet = load_packet()
    errors = validate(packet)
    print("=== Batch planning ===")
    if is_minimal_reservation(packet):
        print("minimal reservation: detailed batching is deferred to private preparation")
    else:
        planning = packet.get("batch_planning", {})
        print(f"mode: {planning.get('mode', 'detail_packet')}")
        print(f"reviewed rows: {planning.get('reviewed_rows')}")
        print(f"scene groups: {', '.join(map(str, packet.get('scene_groups', [])))}")
        print(f"grouping: {planning.get('grouping_decision')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: reservation, detailed batch, or semantic wave planning is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
