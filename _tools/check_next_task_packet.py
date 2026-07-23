#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXT_TASK_PACKET.jsonがverified checkpointと次作業を十分に復元できるか検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
WORK_PATH = P4 / "CURRENT_WORK.json"
PACKET_PATH = P4 / "NEXT_TASK_PACKET.json"


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help=(
            "pending_audit_sync中は旧verified checkpoint由来のパケット保持を許容する。"
            "checkpointがverifiedなら通常どおり完全一致を要求する"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    work = load(WORK_PATH)
    packet = load(PACKET_PATH)
    errors: list[str] = []

    checkpoint = work.get("checkpoint", {})
    checkpoint_status = checkpoint.get("status")
    transitional = checkpoint_status == "pending_audit_sync"
    allow_transitional = args.allow_pending and transitional

    based = packet.get("based_on_checkpoint", {})
    expected = {
        "batch": work.get("last_completed_batch"),
        "pair_applied_keys": work.get("pair_applied_keys"),
        "project_applied_keys": work.get("project_applied_keys"),
        "produced_by_pr": checkpoint.get("produced_by_pr"),
    }
    if not allow_transitional:
        for key, value in expected.items():
            if based.get(key) != value:
                errors.append(f"checkpoint {key} mismatch: packet={based.get(key)!r} work={value!r}")

    if checkpoint_status != "verified" and not allow_transitional:
        errors.append("NEXT_TASK_PACKET may be published only from a verified checkpoint")
    if packet.get("status") != "ready":
        errors.append("NEXT_TASK_PACKET.status must be ready")
    if packet.get("current_pair") != work.get("current_pair"):
        errors.append("current_pair mismatch")

    work_scenes = work.get("immediate_next", {}).get("scene_groups", [])
    packet_scenes = packet.get("scene_groups", [])
    if not allow_transitional and packet_scenes != work_scenes:
        errors.append(f"scene_groups mismatch: packet={packet_scenes!r} work={work_scenes!r}")
    if not packet_scenes:
        errors.append("scene_groups must not be empty")

    source = packet.get("source", {})
    for key in (
        "target",
        "namespace",
        "families",
        "artifact_workflow",
        "artifact_name",
        "artifact_file",
        "freshness_rule",
    ):
        if not source.get(key):
            errors.append(f"source.{key} is required")

    flow = packet.get("scene_flow", [])
    if not isinstance(flow, list) or len(flow) != len(packet_scenes):
        errors.append("scene_flow must contain exactly one entry per scene_group")
    else:
        mapped = [item.get("scene") for item in flow if isinstance(item, dict)]
        if mapped != packet_scenes:
            errors.append(f"scene_flow order mismatch: {mapped!r} != {packet_scenes!r}")
        for item in flow:
            if not isinstance(item, dict):
                continue
            for key in ("function", "speaker_order", "focus_keys", "voice_questions"):
                if not item.get(key):
                    errors.append(f"scene_flow[{item.get('scene')}].{key} is required")

    gates = packet.get("allusion_and_fact_gates", {})
    if "allusion_review_candidates" not in gates or "fact_doubts" not in gates:
        errors.append("allusion_and_fact_gates must keep allusion and fact doubts separate")

    ownership = packet.get("ownership_boundary", {})
    if not ownership.get("pair_batch") or not ownership.get("cross_register"):
        errors.append("ownership_boundary must define pair_batch and cross_register")

    skill = packet.get("skill_review", {})
    if skill.get("default") != "no_change":
        errors.append("skill_review.default must be no_change; modify only on a generalizable finding")
    if not skill.get("rule") or not skill.get("separate_layers"):
        errors.append("skill_review must define promotion rule and layer separation")

    outputs = packet.get("expected_outputs", [])
    required_tokens = ("locres", "pak", "CURRENT_WORK", "checkpoint verified")
    joined = "\n".join(map(str, outputs))
    for token in required_tokens:
        if token not in joined:
            errors.append(f"expected_outputs missing token: {token}")

    report = packet.get("cold_start_first_report", {})
    for key in ("current", "open_pr", "start", "drift"):
        if not report.get(key):
            errors.append(f"cold_start_first_report.{key} is required")

    print("=== Next task cold-start packet ===")
    print(f"pair: {packet.get('current_pair')}")
    print(f"checkpoint status: {checkpoint_status}")
    print(f"packet checkpoint batch: {based.get('batch')}")
    print(f"packet scenes: {', '.join(map(str, packet_scenes))}")
    print(f"task id: {packet.get('task_id')}")
    if allow_transitional:
        print(
            "TRANSITIONAL: CURRENT_WORKは次束へ進んでいるが、"
            "NEXT_TASK_PACKETは監査索引同期とverified確定まで旧checkpoint版を保持する"
        )
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    if allow_transitional:
        print("OK TRANSITIONAL: packet structure valid; checkpoint/scene一致はverified時に再検査")
    else:
        print("OK: cold-start packet is complete and matches CURRENT_WORK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
