#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wave v2のkeep-only正式束と次wave予約分離を回帰検証する。"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str):
    path = ROOT / "_tools" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_current(status: str, declared: str) -> dict:
    transport = status if status in {"ready_for_public_ci", "in_public_ci"} else "not_ready"
    return {
        "checkpoint": {
            "status": "verified",
            "batch": 65,
            "pair_applied_keys": 1167,
            "project_applied_keys": 1521,
            "produced_by_pr": 111,
            "translation_head": "a" * 40,
            "verified_head": "a" * 40,
        },
        "operation_mode": {"declared_state": declared},
        "immediate_next": {"scene_groups": ["release-scene"]},
        "ci_train": {
            "phase": "phase1_wave",
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "train_id": "test-train",
            "branch": "agent/test-train",
            "status": status,
            "transport_status": transport,
            "base_checkpoint_batch": 65,
            "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
            "caps": {"bundle_count": 6, "reviewed_rows": 80},
        },
    }


def sample_manifest(status: str) -> dict:
    bundles = []
    for offset in range(4):
        fixes = 1 if offset == 0 else 0
        bundles.append(
            {
                "batch": 66 + offset,
                "review_status": "complete",
                "apply_status": "pending",
                "scene_groups": [f"scene-{offset}"],
                "reviewed_rows": 10,
                "fix_keys": fixes,
                "new_pair_keys": fixes,
                "fix_files": (["_phase4_proofread/fixes_relation_test.json"] if fixes else []),
                "review_record": f"_phase4_proofread/REVIEW_TEST_{offset}.md",
                "ownership_summary": {
                    "existing_keys": 0,
                    "new_keys": fixes,
                    "cross_register_keys": 0,
                },
            }
        )
    return {
        "schema_version": 2,
        "phase": "phase1_wave",
        "train_id": "test-train",
        "branch": "agent/test-train",
        "status": status,
        "transport": {"status": status},
        "base_checkpoint": {
            "batch": 65,
            "pair_applied_keys": 1167,
            "project_applied_keys": 1521,
            "produced_by_pr": 111,
            "translation_head": "a" * 40,
            "verified_head": "a" * 40,
        },
        "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
        "caps": {"bundle_count": 6, "reviewed_rows": 80},
        "allowed_early_release_reasons": [
            "workflow_change",
            "schema_change",
            "security_or_visibility",
            "urgent_build_verification",
        ],
        "release_trigger": None,
        "totals": {
            "bundle_count": 4,
            "reviewed_rows": 40,
            "fix_keys": 1,
            "new_pair_keys": 1,
        },
        "bundles": bundles,
    }


def main() -> None:
    manifest_v2 = load("check_ci_train_manifest_v2.py")
    packet_v2 = load("check_next_task_packet_v2.py")

    current_ready = sample_current("ready_for_public_ci", "translation_frozen")
    manifest_ready = sample_manifest("ready_for_public_ci")
    errors = manifest_v2.validate_manifest(manifest_ready, current_ready, require_ready=True)
    assert errors == [], errors

    bad = sample_manifest("ready_for_public_ci")
    bad["bundles"][1]["fix_files"] = ["_phase4_proofread/fixes_noop.json"]
    errors = manifest_v2.validate_manifest(bad, current_ready)
    assert any("keep-only bundle" in error for error in errors)

    packet = {"scene_groups": ["next-wave-scene"]}
    errors = []
    packet_v2.validate_scene_alignment(
        current_ready,
        manifest_ready,
        packet,
        allow_transitional=False,
        errors=errors,
    )
    assert errors == [], errors

    current_accumulating = sample_current("accumulating", "private_translation_work")
    manifest_accumulating = sample_manifest("accumulating")
    errors = []
    packet_v2.validate_scene_alignment(
        current_accumulating,
        manifest_accumulating,
        packet,
        allow_transitional=False,
        errors=errors,
    )
    assert any("during accumulation" in error for error in errors)

    print("test_check_ci_train_state_v2: OK")


if __name__ == "__main__":
    main()
