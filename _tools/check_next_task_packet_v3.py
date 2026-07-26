#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXT_TASK_PACKET schema v6のminimal reservationと旧schemaを検査する。"""
from __future__ import annotations

import argparse
import sys
from typing import Any

import check_next_task_packet_v2 as legacy
from check_next_task_packet_v2 import *  # noqa: F401,F403


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_minimal_reservation(
    work: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    *,
    allow_pending: bool = False,
) -> list[str]:
    errors: list[str] = []
    if packet.get("schema_version") != 6:
        errors.append("minimal reservation schema_version must be 6")
    if packet.get("status") != "ready":
        errors.append("NEXT_TASK_PACKET.status must be ready")
    if packet.get("current_pair") != work.get("current_pair"):
        errors.append("current_pair mismatch")

    checkpoint = work.get("checkpoint", {})
    checkpoint_status = checkpoint.get("status") if isinstance(checkpoint, dict) else None
    transitional = checkpoint_status == "pending_audit_sync" and allow_pending
    if checkpoint_status != "verified" and not transitional:
        errors.append("minimal reservation requires a verified base checkpoint")

    based = packet.get("based_on_checkpoint")
    if not isinstance(based, dict):
        errors.append("based_on_checkpoint must be an object")
        based = {}
    expected = {
        "batch": work.get("last_completed_batch"),
        "pair_applied_keys": work.get("pair_applied_keys"),
        "project_applied_keys": work.get("project_applied_keys"),
        "produced_by_pr": checkpoint.get("produced_by_pr") if isinstance(checkpoint, dict) else None,
    }
    if not transitional:
        for key, value in expected.items():
            if based.get(key) != value:
                errors.append(f"checkpoint {key} mismatch: packet={based.get(key)!r} work={value!r}")
    for key in ("release_id", "release_evidence"):
        if not _nonempty(based.get(key)):
            errors.append(f"based_on_checkpoint.{key} is required")

    scenes = packet.get("scene_groups")
    if not isinstance(scenes, list) or not scenes or any(not _nonempty(item) for item in scenes):
        errors.append("scene_groups must be a non-empty string list")

    reservation = packet.get("reservation")
    if not isinstance(reservation, dict):
        errors.append("reservation must be an object")
    else:
        if reservation.get("status") != "reserved_only":
            errors.append("reservation.status must be reserved_only")
        for key in ("wave_id", "packet_id", "formal_batch"):
            if reservation.get(key) is not None:
                errors.append(f"reservation.{key} must be null before preparation")
        for key in ("preparation_started", "quality_audit_started", "encoding_started"):
            if reservation.get(key) is not False:
                errors.append(f"reservation.{key} must be false")

    source = packet.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
        source = {}
    for key in (
        "artifact_workflow",
        "artifact_name",
        "artifact_file",
        "artifact_digest",
        "artifact_head",
        "freshness_rule",
    ):
        if not _nonempty(source.get(key)):
            errors.append(f"source.{key} is required")

    forbidden_detail = (
        "scene_flow",
        "batch_planning",
        "allusion_and_fact_gates",
        "ownership_boundary",
        "skill_review",
        "expected_outputs",
        "cold_start_first_report",
    )
    for key in forbidden_detail:
        if key in packet:
            errors.append(f"minimal reservation must not contain private preparation detail: {key}")

    release = packet.get("release_candidate")
    if not isinstance(release, dict):
        errors.append("release_candidate must be an object")
    else:
        for key in ("train_id", "release_id"):
            if not _nonempty(release.get(key)):
                errors.append(f"release_candidate.{key} is required")
        if release.get("status") not in {"ready_for_public_ci", "in_public_ci", "verified", "merged"}:
            errors.append("release_candidate.status is invalid")
        if not isinstance(release.get("pr"), int) or release.get("pr") <= 0:
            errors.append("release_candidate.pr must be a positive integer")

    do_not_do = packet.get("do_not_do")
    if not isinstance(do_not_do, list) or not do_not_do or any(not _nonempty(item) for item in do_not_do):
        errors.append("do_not_do must be a non-empty string list")

    train = packet.get("ci_train")
    if not isinstance(train, dict):
        errors.append("ci_train must be an object")
        train = {}
    current_train = work.get("ci_train", {})
    for key in ("phase", "train_id"):
        if train.get(key) != current_train.get(key):
            errors.append(f"ci_train.{key} mismatch")
    if train.get("manifest") != "_phase4_proofread/CI_TRAIN_MANIFEST.json":
        errors.append("ci_train.manifest path is invalid")
    base_batch = manifest.get("base_checkpoint", {}).get("batch")
    bundles = manifest.get("bundles")
    expected_batch = base_batch + len(bundles) + 1 if isinstance(base_batch, int) and isinstance(bundles, list) else None
    if train.get("planned_batch") != expected_batch:
        errors.append(f"ci_train.planned_batch mismatch: packet={train.get('planned_batch')!r}, expected={expected_batch!r}")

    errors.extend(f"CI_TRAIN_MANIFEST: {error}" for error in legacy.validate_manifest(manifest, work))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-pending", action="store_true")
    return parser.parse_args()


def main() -> int:
    packet = legacy.load(legacy.PACKET_PATH)
    if int(packet.get("schema_version", 0)) < 6:
        return legacy.main()

    args = parse_args()
    work = legacy.load(legacy.WORK_PATH)
    manifest = legacy.load(legacy.MANIFEST_PATH)
    errors = validate_minimal_reservation(work, manifest, packet, allow_pending=args.allow_pending)
    print("=== Minimal next-wave reservation ===")
    print(f"pair: {packet.get('current_pair')}")
    print(f"checkpoint batch: {packet.get('based_on_checkpoint', {}).get('batch')}")
    print(f"reserved scenes: {', '.join(map(str, packet.get('scene_groups', [])))}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: minimal reservation is transport-safe; preparation detail remains private")
    return 0


if __name__ == "__main__":
    sys.exit(main())
