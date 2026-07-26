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
        "checkpoint": {"status": "verified", "produced_by_pr": 122},
        "ci_train": {"phase": "phase1_wave", "train_id": "yuwen-mowen-train-08"},
    }
    manifest = {
        "schema_version": 2,
        "phase": "phase1_wave",
        "train_id": "yuwen-mowen-train-08",
        "branch": "agent/yuwen-mowen-train-08",
        "status": "verified",
        "transport": {"status": "verified"},
        "base_checkpoint": {"batch": 84},
        "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
        "caps": {"bundle_count": 6, "reviewed_rows": 60},
        "allowed_early_release_reasons": ["workflow_change", "schema_change", "security_or_visibility", "urgent_build_verification"],
        "release_trigger": None,
        "totals": {"bundle_count": 4, "reviewed_rows": 45, "fix_keys": 18, "new_pair_keys": 0},
        "bundles": [
            {"batch": batch, "review_status": "complete", "apply_status": "verified", "scene_groups": [str(batch)], "reviewed_rows": rows, "fix_keys": fixes, "new_pair_keys": 0, "fix_files": (["_phase4_proofread/fixes_x.json"] if fixes else []), "review_record": f"_phase4_proofread/REVIEW_{batch}.md", "ownership_summary": {"existing_keys": rows, "new_keys": 0, "cross_register_keys": 0}}
            for batch, rows, fixes in ((85, 15, 11), (86, 5, 0), (87, 7, 2), (88, 18, 5))
        ],
    }
    work["checkpoint"].update({"batch": 88, "pair_applied_keys": 1165, "project_applied_keys": 1541})
    work["ci_train"].update({
        "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
        "branch": "agent/yuwen-mowen-train-08",
        "status": "verified",
        "transport_status": "verified",
        "base_checkpoint_batch": 84,
        "thresholds": manifest["thresholds"],
        "caps": manifest["caps"],
    })
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
        "ci_train": {"phase": "phase1_wave", "train_id": "yuwen-mowen-train-08", "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json", "planned_batch": 89},
    }
    return work, manifest, packet


def main() -> None:
    work, manifest, packet = sample()
    # isolate this test from legacy manifest file-existence checks
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
    finally:
        checker.legacy.validate_manifest = original
    print("OK: minimal reservation excludes preparation detail and detects stale checkpoints")


if __name__ == "__main__":
    main()
