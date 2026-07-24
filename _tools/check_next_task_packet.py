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
FIX_GLOB = "fixes_*.json"
FIELD_SEPARATOR = "\x1f"


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
            "また、未所有候補がpacketで宣言したplanned_ownerへ同一PR内で収録された状態を許容する。"
            "checkpointがverifiedならcheckpoint・場面一致は通常どおり要求する"
        ),
    )
    return parser.parse_args()


def full_key(source: dict[str, Any], short_key: str) -> str:
    return FIELD_SEPARATOR.join(
        (str(source.get("target", "")), str(source.get("namespace", "")), short_key)
    )


def collect_fix_owners(errors: list[str]) -> dict[str, list[str]]:
    owners: dict[str, list[str]] = {}
    for path in sorted(P4.glob(FIX_GLOB)):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read ownership source {path.relative_to(ROOT)}: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"ownership source must be object: {path.relative_to(ROOT)}")
            continue
        rel = path.relative_to(ROOT).as_posix()
        for key in value:
            if isinstance(key, str) and key.count(FIELD_SEPARATOR) == 2:
                owners.setdefault(key, []).append(rel)
    return owners


def validate_machine_ownership(
    packet: dict[str, Any],
    owners: dict[str, list[str]],
    *,
    allow_consumed: bool,
    errors: list[str],
    transitions: list[str],
) -> None:
    ownership = packet.get("ownership_boundary", {})
    machine = ownership.get("machine_ownership") if isinstance(ownership, dict) else None
    if not isinstance(machine, dict):
        errors.append("ownership_boundary.machine_ownership must be an object")
        return

    existing = machine.get("existing")
    unowned = machine.get("unowned")
    if not isinstance(existing, list):
        errors.append("machine_ownership.existing must be a list")
        existing = []
    if not isinstance(unowned, list):
        errors.append("machine_ownership.unowned must be a list")
        unowned = []

    source = packet.get("source", {})
    flow = packet.get("scene_flow", [])
    focus_keys: list[str] = []
    if isinstance(flow, list):
        for item in flow:
            if isinstance(item, dict) and isinstance(item.get("focus_keys"), list):
                focus_keys.extend(key for key in item["focus_keys"] if isinstance(key, str))

    if len(focus_keys) != len(set(focus_keys)):
        errors.append("scene_flow focus_keys must not contain duplicates")
    focus_set = set(focus_keys)
    claimed: dict[str, str] = {}

    def claim(short_key: str, label: str) -> None:
        if short_key in claimed:
            errors.append(
                f"machine ownership duplicate claim: {short_key!r} in {claimed[short_key]} and {label}"
            )
        claimed[short_key] = label
        if short_key not in focus_set:
            errors.append(f"machine ownership claims non-focus key: {short_key!r}")

    for index, entry in enumerate(existing):
        if not isinstance(entry, dict):
            errors.append(f"machine_ownership.existing[{index}] must be an object")
            continue
        path = entry.get("path")
        keys = entry.get("keys")
        if not isinstance(path, str) or not path.startswith("_phase4_proofread/fixes_") or not path.endswith(".json"):
            errors.append(f"machine_ownership.existing[{index}].path is invalid: {path!r}")
            continue
        if not isinstance(keys, list) or not keys:
            errors.append(f"machine_ownership.existing[{index}].keys must be a non-empty list")
            continue
        if not (ROOT / path).is_file():
            errors.append(f"declared ownership source does not exist: {path}")
        for short_key in keys:
            if not isinstance(short_key, str):
                errors.append(f"machine_ownership.existing[{index}] contains non-string key")
                continue
            claim(short_key, path)
            observed = owners.get(full_key(source, short_key), [])
            if path not in observed:
                errors.append(
                    f"ownership mismatch for {short_key}: declared={path!r}, observed={observed!r}"
                )
            if len(observed) > 1:
                errors.append(f"multiple fix owners for {short_key}: {observed!r}")

    for index, entry in enumerate(unowned):
        if not isinstance(entry, dict):
            errors.append(f"machine_ownership.unowned[{index}] must be an object")
            continue
        short_key = entry.get("key")
        planned_owner = entry.get("planned_owner")
        if not isinstance(short_key, str):
            errors.append(f"machine_ownership.unowned[{index}].key must be a string")
            continue
        if (
            not isinstance(planned_owner, str)
            or not planned_owner.startswith("_phase4_proofread/fixes_")
            or not planned_owner.endswith(".json")
        ):
            errors.append(
                f"machine_ownership.unowned[{index}].planned_owner is invalid: {planned_owner!r}"
            )
            continue
        claim(short_key, f"unowned->{planned_owner}")
        observed = owners.get(full_key(source, short_key), [])
        if not observed:
            continue
        if allow_consumed and observed == [planned_owner]:
            transitions.append(f"planned owner consumed {short_key}: {planned_owner}")
            continue
        errors.append(
            f"key declared unowned is already owned: {short_key}, observed={observed!r}, "
            f"planned_owner={planned_owner!r}"
        )

    missing = sorted(focus_set - set(claimed))
    extra = sorted(set(claimed) - focus_set)
    if missing:
        errors.append(f"machine ownership does not cover focus keys: {missing!r}")
    if extra:
        errors.append(f"machine ownership contains extra keys: {extra!r}")


def main() -> int:
    args = parse_args()
    work = load(WORK_PATH)
    packet = load(PACKET_PATH)
    errors: list[str] = []
    transitions: list[str] = []

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
    owners = collect_fix_owners(errors)
    validate_machine_ownership(
        packet,
        owners,
        allow_consumed=args.allow_pending,
        errors=errors,
        transitions=transitions,
    )

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
    for message in transitions:
        print(f"TRANSITIONAL: {message}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    if allow_transitional or transitions:
        print("OK TRANSITIONAL: packet structure and machine ownership are valid")
    else:
        print("OK: cold-start packet is complete and matches CURRENT_WORK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
