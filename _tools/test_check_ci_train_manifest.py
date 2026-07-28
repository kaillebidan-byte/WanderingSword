#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_ci_train_manifest のwave v2集計・release条件を回帰検証する。"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_ci_train_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_ci_train_manifest", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_ci_train_manifest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def current(status="accumulating", declared="private_translation_work", transport="not_ready"):
    return {
        "checkpoint": {
            "status": "verified",
            "batch": 60,
            "pair_applied_keys": 1166,
            "project_applied_keys": 1517,
            "produced_by_pr": 103,
            "translation_head": "a" * 40,
            "verified_head": "a" * 40,
        },
        "operation_mode": {"declared_state": declared},
        "ci_train": {
            "phase": "phase1_wave",
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "train_id": "test-train",
            "branch": "agent/test-train",
            "status": status,
            "transport_status": transport,
            "base_checkpoint_batch": 60,
            "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
            "caps": {"bundle_count": 6, "reviewed_rows": 80},
        },
    }


def base_manifest(status="accumulating", transport="not_ready"):
    return {
        "schema_version": 2,
        "phase": "phase1_wave",
        "train_id": "test-train",
        "branch": "agent/test-train",
        "draft_pr": None,
        "status": status,
        "transport": {"status": transport, "translation_stage": "translation_frozen" if transport != "not_ready" else "private_preparation"},
        "base_checkpoint": {
            "batch": 60,
            "pair_applied_keys": 1166,
            "project_applied_keys": 1517,
            "produced_by_pr": 103,
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
        "totals": {"bundle_count": 0, "reviewed_rows": 0, "fix_keys": 0, "new_pair_keys": 0},
        "bundles": [],
    }


def bundle(batch, scene, rows=10, fixes=5, apply="pending"):
    return {
        "batch": batch,
        "review_status": "complete",
        "apply_status": apply,
        "scene_groups": [scene],
        "reviewed_rows": rows,
        "fix_keys": fixes,
        "new_pair_keys": 1,
        "fix_files": [f"_phase4_proofread/fixes_relation_test_batch{batch}.json"],
        "review_record": f"_phase4_proofread/REVIEW_TEST_BATCH{batch}.md",
        "ownership_summary": {"existing_keys": max(fixes - 1, 0), "new_keys": 1, "cross_register_keys": 0},
    }


def recalc(manifest):
    manifest["totals"] = {
        "bundle_count": len(manifest["bundles"]),
        "reviewed_rows": sum(x["reviewed_rows"] for x in manifest["bundles"]),
        "fix_keys": sum(x["fix_keys"] for x in manifest["bundles"]),
        "new_pair_keys": sum(x["new_pair_keys"] for x in manifest["bundles"]),
    }


def advanced_current(checkpoint_status="pending_audit_sync"):
    value = current("in_public_ci", "translation_frozen", "in_public_ci")
    value["checkpoint"] = {
        "status": checkpoint_status,
        "batch": 61,
        "pair_applied_keys": 1166,
        "project_applied_keys": 1518,
        "produced_by_pr": 106,
        "translation_head": "b" * 40,
        "verified_head": "a" * 40,
    }
    value["ci_train"]["applied_result"] = {
        "asset_head": "b" * 40,
        "pair_applied_keys": 1166,
        "project_applied_keys": 1518,
        "pending_fixes": 0,
    }
    return value


def main() -> None:
    module = load_module()
    manifest = base_manifest()
    assert module.validate_manifest(manifest, current()) == []
    assert module.release_state(manifest) == (False, [])

    ready = base_manifest("ready_for_public_ci", "ready_for_public_ci")
    ready["bundles"] = [bundle(61 + i, f"scene-{i}") for i in range(4)]
    recalc(ready)
    errors = module.validate_manifest(ready, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci"), require_ready=True)
    assert errors == [], errors

    bad_status = copy.deepcopy(ready)
    bad_status["bundles"][0]["status"] = "reviewed_pending_ci"
    assert any("deprecated" in error for error in module.validate_manifest(bad_status, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci")))

    bad_totals = copy.deepcopy(ready)
    bad_totals["totals"]["fix_keys"] += 1
    assert any("totals.fix_keys mismatch" in error for error in module.validate_manifest(bad_totals, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci")))

    premature = base_manifest("ready_for_public_ci", "ready_for_public_ci")
    assert any("needs a threshold" in error for error in module.validate_manifest(premature, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci")))

    early = base_manifest("ready_for_public_ci", "ready_for_public_ci")
    early["release_trigger"] = {"reason": "schema_change", "detail": "verify wave schema"}
    assert module.validate_manifest(early, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci"), require_ready=True) == []

    at_cap = base_manifest("ready_for_public_ci", "ready_for_public_ci")
    at_cap["bundles"] = [bundle(61 + i, f"scene-cap-{i}", rows=16, fixes=1) for i in range(5)]
    recalc(at_cap)
    assert module.validate_manifest(
        at_cap,
        current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci"),
        require_ready=True,
    ) == []

    over = base_manifest("ready_for_public_ci", "ready_for_public_ci")
    over["bundles"] = [bundle(61 + i, f"scene-{i}", rows=14, fixes=1) for i in range(6)]
    recalc(over)
    assert any("reviewed_rows exceeds" in error for error in module.validate_manifest(over, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci")))

    pending = base_manifest("in_public_ci", "in_public_ci")
    pending["release_trigger"] = {"reason": "schema_change", "detail": "verify with one bundle"}
    pending["bundles"] = [bundle(61, "scene-61", rows=5, fixes=3)]
    recalc(pending)
    assert module.validate_manifest(pending, advanced_current(), require_ready=True) == []

    verified_manifest = copy.deepcopy(pending)
    verified_manifest["status"] = "verified"
    verified_manifest["transport"]["status"] = "verified"
    verified_manifest["bundles"][0]["apply_status"] = "verified"
    verified_current = advanced_current("verified")
    verified_current["ci_train"]["status"] = "verified"
    verified_current["ci_train"]["transport_status"] = "verified"
    assert module.validate_manifest(verified_manifest, verified_current) == []

    with_candidate = copy.deepcopy(ready)
    with_candidate["candidate_packets"] = []
    assert any("PRIVATE_STAGE_STATE" in error for error in module.validate_manifest(with_candidate, current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci")))

    print("test_check_ci_train_manifest: OK")


if __name__ == "__main__":
    main()
