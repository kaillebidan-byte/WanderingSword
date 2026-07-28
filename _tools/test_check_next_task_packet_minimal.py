#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_next_task_packet_v3 as checker


def sample() -> tuple[dict, dict, dict]:
    work = {
        "current_pair": "宇文逸↔莫問",
        "last_completed_batch": 88,
        "pair_applied_keys": 1165,
        "project_applied_keys": 1541,
        "checkpoint": {"status": "verified", "produced_by_pr": 122, "batch": 88, "pair_applied_keys": 1165, "project_applied_keys": 1541},
        "operation_mode": {"declared_state": "translation_frozen"},
        "ci_train": {
            "phase": "phase1_wave",
            "train_id": "yuwen-mowen-train-08",
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "branch": "agent/yuwen-mowen-train-08",
            "status": "verified",
            "transport_status": "verified",
            "base_checkpoint_batch": 84,
            "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
            "caps": {"bundle_count": 6, "reviewed_rows": 80},
        },
    }
    manifest = {
        "schema_version": 2,
        "phase": "phase1_wave",
        "train_id": "yuwen-mowen-train-08",
        "branch": "agent/yuwen-mowen-train-08",
        "status": "verified",
        "transport": {"status": "verified"},
        "base_checkpoint": {"batch": 84},
        "thresholds": work["ci_train"]["thresholds"],
        "caps": work["ci_train"]["caps"],
        "allowed_early_release_reasons": ["workflow_change", "schema_change", "security_or_visibility", "urgent_build_verification"],
        "release_trigger": None,
        "totals": {"bundle_count": 4, "reviewed_rows": 45, "fix_keys": 18, "new_pair_keys": 0},
        "bundles": [],
    }
    packet = {
        "schema_version": 6,
        "status": "ready",
        "task_id": "reservation",
        "based_on_checkpoint": {"batch": 88, "pair_applied_keys": 1165, "project_applied_keys": 1541, "produced_by_pr": 122, "release_id": "r1", "release_evidence": "_phase4_proofread/RELEASE_EVIDENCE_X.json"},
        "current_pair": "宇文逸↔莫問",
        "scene_groups": ["5649_1"],
        "reservation": {"status": "reserved_only", "wave_id": None, "packet_id": None, "preparation_started": False, "quality_audit_started": False, "encoding_started": False, "formal_batch": None},
        "source": {"artifact_workflow": "Relation audit extraction", "artifact_name": "relation-audit-evidence", "artifact_file": "x.json", "artifact_digest": "sha256:x", "artifact_head": "a" * 40, "freshness_rule": "refresh after merge"},
        "release_candidate": {"train_id": "yuwen-mowen-train-08", "release_id": "r1", "pr": 122, "status": "merged"},
        "do_not_do": ["do not prepare"],
        "ci_train": {"phase": "phase1_wave", "train_id": "yuwen-mowen-train-08", "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json", "planned_batch": 85},
    }
    return work, manifest, packet


def main() -> None:
    work, manifest, packet = sample()
    original = checker.legacy.validate_manifest
    checker.legacy.validate_manifest = lambda manifest, work: []
    try:
        assert checker.validate_minimal_reservation(work, manifest, packet) == []
        detailed = copy.deepcopy(packet)
        detailed["scene_flow"] = []
        assert any("private preparation detail" in error for error in checker.validate_minimal_reservation(work, manifest, detailed))
        stale = copy.deepcopy(packet)
        stale["based_on_checkpoint"]["project_applied_keys"] = 1539
        assert any("project_applied_keys mismatch" in error for error in checker.validate_minimal_reservation(work, manifest, stale))

        active_work = copy.deepcopy(work)
        active_manifest = copy.deepcopy(manifest)
        active_packet = copy.deepcopy(packet)
        active_work["ci_train"].update({"train_id": "yuwen-mowen-train-09", "status": "accumulating", "transport_status": "not_ready", "base_checkpoint_batch": 88, "private_stage": {"stage": "private_quality_audit"}})
        active_work["operation_mode"]["declared_state"] = "private_translation_work"
        active_manifest.update({"train_id": "yuwen-mowen-train-09", "branch": "agent/yuwen-mowen-train-09", "status": "accumulating", "transport": {"status": "not_ready"}, "base_checkpoint": {"batch": 88}, "totals": {"bundle_count": 0, "reviewed_rows": 0, "fix_keys": 0, "new_pair_keys": 0}, "bundles": []})
        active_packet["scene_groups"] = ["5649_1", "5650_1"]
        active_packet["reservation"] = {"status": "quality_audit_active", "wave_id": "wave-09", "packet_id": "packet-01", "preparation_started": True, "quality_audit_started": True, "encoding_started": False, "formal_batch": None}
        active_packet["ci_train"].update({"train_id": "yuwen-mowen-train-09", "planned_batch": 89})
        assert checker.validate_minimal_reservation(active_work, active_manifest, active_packet) == []
        broken = copy.deepcopy(active_packet)
        broken["reservation"]["formal_batch"] = 89
        assert any("formal_batch" in error for error in checker.validate_minimal_reservation(active_work, active_manifest, broken))
    finally:
        checker.legacy.validate_manifest = original
    print("OK: minimal and active reservations are stage-aligned")


if __name__ == "__main__":
    main()
