#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXT_TASK_PACKETを列車蓄積中・release待ち・適用遷移の各状態で検査する。"""
from __future__ import annotations

import argparse
import sys
from typing import Any

import check_next_task_packet as legacy
from check_ci_train_manifest_v2 import validate_manifest

WORK_PATH = legacy.WORK_PATH
PACKET_PATH = legacy.PACKET_PATH
MANIFEST_PATH = legacy.MANIFEST_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="pending_audit_sync中の旧verified packetと所有遷移を許容する",
    )
    return parser.parse_args()


def validate_scene_alignment(
    work: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    *,
    allow_transitional: bool,
    errors: list[str],
) -> None:
    packet_scenes = packet.get("scene_groups", [])
    work_scenes = work.get("immediate_next", {}).get("scene_groups", [])
    status = manifest.get("status")

    # accumulating中だけCURRENT_WORK.immediate_nextは今すぐ監査する場面を指す。
    # ready/in_public_ci/verifiedではCURRENT_WORKはrelease作業を指し、
    # NEXT_TASK_PACKETはrelease後の次列車を先取りするため一致を要求しない。
    if status == "accumulating" and not allow_transitional and packet_scenes != work_scenes:
        errors.append(
            f"scene_groups mismatch during accumulation: "
            f"packet={packet_scenes!r} work={work_scenes!r}"
        )


def validate_train_packet(
    current: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    errors: list[str],
) -> None:
    train = packet.get("ci_train")
    if not isinstance(train, dict):
        errors.append("NEXT_TASK_PACKET.ci_train must be an object")
        return

    current_train = current.get("ci_train", {})
    for key in ("phase", "train_id"):
        if train.get(key) != current_train.get(key):
            errors.append(
                f"ci_train.{key} mismatch: packet={train.get(key)!r}, "
                f"current={current_train.get(key)!r}"
            )
    if train.get("manifest") != "_phase4_proofread/CI_TRAIN_MANIFEST.json":
        errors.append("ci_train.manifest path is invalid")
    if train.get("bundle_status_on_completion") != "reviewed_pending_ci":
        errors.append("ci_train.bundle_status_on_completion must be reviewed_pending_ci")
    if train.get("do_not_apply_until_release") is not True:
        errors.append("ci_train.do_not_apply_until_release must be true")

    base_batch = manifest.get("base_checkpoint", {}).get("batch")
    bundles = manifest.get("bundles", [])
    expected_batch = (
        base_batch + len(bundles) + 1
        if isinstance(base_batch, int) and isinstance(bundles, list)
        else None
    )
    if train.get("planned_batch") != expected_batch:
        errors.append(
            f"ci_train.planned_batch mismatch: packet={train.get('planned_batch')!r}, "
            f"expected={expected_batch!r}"
        )

    manifest_errors = validate_manifest(manifest, current)
    errors.extend(f"CI_TRAIN_MANIFEST: {error}" for error in manifest_errors)


def main() -> int:
    args = parse_args()
    work = legacy.load(WORK_PATH)
    packet = legacy.load(PACKET_PATH)
    manifest = legacy.load(MANIFEST_PATH)
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
                errors.append(
                    f"checkpoint {key} mismatch: packet={based.get(key)!r} work={value!r}"
                )

    if checkpoint_status != "verified" and not allow_transitional:
        errors.append("NEXT_TASK_PACKET requires a verified base checkpoint")
    if packet.get("status") != "ready":
        errors.append("NEXT_TASK_PACKET.status must be ready")
    if packet.get("current_pair") != work.get("current_pair"):
        errors.append("current_pair mismatch")

    packet_scenes = packet.get("scene_groups", [])
    validate_scene_alignment(
        work,
        manifest,
        packet,
        allow_transitional=allow_transitional,
        errors=errors,
    )
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
        errors.append("allusion_and_fact_gates must separate allusion and fact doubts")

    ownership = packet.get("ownership_boundary", {})
    if not ownership.get("pair_batch") or not ownership.get("cross_register"):
        errors.append("ownership_boundary must define pair_batch and cross_register")
    owners = legacy.collect_fix_owners(errors)
    legacy.validate_machine_ownership(
        packet,
        owners,
        allow_consumed=args.allow_pending,
        errors=errors,
        transitions=transitions,
    )

    skill = packet.get("skill_review", {})
    if skill.get("default") != "no_change":
        errors.append("skill_review.default must be no_change")
    if not skill.get("rule") or not skill.get("separate_layers"):
        errors.append("skill_review must define promotion rule and layer separation")

    outputs = packet.get("expected_outputs")
    if (
        not isinstance(outputs, list)
        or not outputs
        or any(not isinstance(item, str) or not item.strip() for item in outputs)
    ):
        errors.append("expected_outputs must be a non-empty string list")

    report = packet.get("cold_start_first_report", {})
    for key in ("current", "open_pr", "start", "drift"):
        if not report.get(key):
            errors.append(f"cold_start_first_report.{key} is required")

    validate_train_packet(work, manifest, packet, errors)

    print("=== Next task cold-start packet v2 ===")
    print(f"pair: {packet.get('current_pair')}")
    print(f"checkpoint status: {checkpoint_status}")
    print(f"packet checkpoint batch: {based.get('batch')}")
    print(f"packet scenes: {', '.join(map(str, packet_scenes))}")
    print(f"task id: {packet.get('task_id')}")
    print(
        f"CI train: {manifest.get('train_id')} / {manifest.get('status')} / "
        f"{manifest.get('totals', {}).get('bundle_count')} bundle(s)"
    )
    if allow_transitional:
        print("TRANSITIONAL: old verified packet is allowed during pending_audit_sync")
    for message in transitions:
        print(f"TRANSITIONAL: {message}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: packet, ownership, and CI train state are complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
