#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import tempfile
from pathlib import Path

from fixed_cycle_initializer import InitializerError, initialize_with_semantic_boundary

SHA = "a" * 40


def execution_modes() -> dict:
    return {
        "selection": {"private": "manual_visibility_cycle", "public": "always_public_full_pipeline"},
        "modes": {
            "manual_visibility_cycle": {
                "visibility_change_actor": "user",
                "visibility_changes_required": True,
                "public_translation_forbidden": True,
                "deep_failure_returns_private": True,
            },
            "always_public_full_pipeline": {
                "visibility_change_actor": "none",
                "visibility_changes_required": False,
                "visibility_change_requests_forbidden": True,
                "deep_failure_returns_private": False,
            },
        },
    }


def fixtures():
    current = {
        "current_pair": "宇文逸↔莫問",
        "checkpoint": {
            "status": "verified",
            "batch": 157,
            "pair_applied_keys": 1351,
            "project_applied_keys": 1727,
            "produced_by_pr": 162,
            "release_identity": {
                "kind": "pr_release_v2",
                "release_id": "yuwen-mowen-train-26-r1",
                "evidence": "_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_26.json",
                "pr": 162,
                "validated_head": SHA,
            },
        },
        "operation_mode": {"declared_state": "translation_frozen"},
        "ci_train": {
            "phase": "phase1_wave",
            "policy": "_phase4_proofread/CI_TRAIN_PHASE2.md",
            "quality_policy": "_phase4_proofread/TRANSLATION_QUALITY_GATE.md",
            "private_stage_policy": "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md",
            "train_id": "yuwen-mowen-train-26",
            "transport_status": "merged",
            "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
            "caps": {"bundle_count": 6, "reviewed_rows": 80},
        },
    }
    state = {
        "schema_version": 2,
        "contract": "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json",
        "train_id": "yuwen-mowen-train-26",
        "stage": "translation_frozen",
        "mode": "wave_v2",
        "cycle_control": {
            "status": "target_reached",
            "continuation_required": False,
            "stop_reason": None,
            "exact_next_action": None,
            "last_safe_checkpoint": "merged",
            "execution_mode": "always_public_full_pipeline",
            "cycle_start_visibility": "public",
            "mode_locked_for_cycle": True,
            "private_completion_target": "ready_for_public_ci",
            "public_completion_target": "awaiting_private_merge",
            "post_public_completion_target": "merged",
            "normal_completion_target": "merged",
        },
        "transport": {"status": "merged"},
        "ownership_policy": {},
    }
    manifest = {
        "schema_version": 2,
        "phase": "phase1_wave",
        "train_id": "yuwen-mowen-train-26",
        "transport": {"status": "merged", "merge_sha": SHA},
        "thresholds": {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20},
        "caps": {"bundle_count": 6, "reviewed_rows": 80},
        "allowed_early_release_reasons": ["workflow_change", "schema_change", "security_or_visibility", "urgent_build_verification"],
    }
    packet = {
        "schema_version": 6,
        "status": "ready",
        "current_pair": "宇文逸↔莫問",
        "reservation": {
            "status": "reserved_only",
            "wave_id": None,
            "packet_id": None,
            "preparation_started": False,
            "quality_audit_started": False,
            "encoding_started": False,
            "formal_batch": None,
        },
        "source": {
            "artifact_workflow": "Release train orchestrator",
            "artifact_run": 30360391808,
            "artifact_id": 8688546867,
            "artifact_name": "relation-audit-evidence",
            "artifact_file": "yuwen_mowen.json",
            "artifact_digest": "sha256:test",
            "artifact_head": SHA,
        },
        "release_candidate": {
            "train_id": "yuwen-mowen-train-26",
            "release_id": "yuwen-mowen-train-26-r1",
            "pr": 162,
            "status": "merged",
            "merge_sha": SHA,
        },
    }
    scenes = ["5296_7", "5297_2", "5300_1", "5302_2", "5302_3", "5302_4"]
    counts = [11, 16, 8, 16, 4, 7]
    artifact = {
        "groups": [
            {
                "family": f"{scene}_Dlgs",
                "rows": [
                    {"key": f"{scene}_Dlgs_Index{index}_Text", "speaker": "莫问", "zh": f"zh-{scene}-{index}", "ja": f"ja-{scene}-{index}"}
                    for index in range(count)
                ],
            }
            for scene, count in zip(scenes, counts)
        ]
    }
    request = {
        "schema_version": 1,
        "contract_id": "translation-factory-request-v1",
        "operation": "initialize_with_semantic_boundary",
        "executor": "fixed_cycle_initializer",
        "expected_controller_action": "initialize_next_cycle_from_reservation",
        "branch": "agent/yuwen-mowen-train-27",
        "source": {
            "artifact_workflow": "Release train orchestrator",
            "artifact_run": 30360391808,
            "artifact_id": 8688546867,
            "artifact_name": "relation-audit-evidence",
            "artifact_file": "yuwen_mowen.json",
            "artifact_digest": "sha256:test",
            "artifact_head": SHA,
        },
        "semantic_boundary": {
            "scene_groups": scenes,
            "unique_reviewed_rows": 62,
            "semantic_extension": {"used": True, "reason": "complete_semantic_unit"},
            "timeline": "武当へ戻った一行が休息し、莫問の演武と出生談を経て稽古へ戻る。",
            "branch_note": "5302_2の実演予告を5302_3の演武と5302_4の家族談まで含めて閉じる。",
            "seal_attestation": "六場面・62行で意味単位が完結するため、60行を2行だけ延長した。",
            "candidate_questions": ["宇文逸と莫問の師兄弟registerを保てているか"],
            "allusion_candidates": ["無極は太極を生み、太極は両儀を生む"],
            "fact_doubts": ["出生談はこの時点の莫問本人の認識として扱う"],
        },
        "output": {
            "candidate_path": "_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5296_7_5302_4_2026-07-29.json",
            "preparation_path": "_phase4_proofread/PREPARATION_YUWEN_MOWEN_TRAIN27_WAVE01_2026-07-29.md",
        },
    }
    return current, state, manifest, packet, request, artifact


def main() -> None:
    p4 = Path(tempfile.mkdtemp()) / "_phase4_proofread"
    p4.mkdir()
    result = initialize_with_semantic_boundary(*fixtures(), "public", execution_modes(), base_commit="b" * 40, p4=p4)
    assert result["train_id"] == "yuwen-mowen-train-27"
    assert result["branch"] == "agent/yuwen-mowen-train-27"
    assert result["state"]["stage"] == "private_quality_audit"
    assert result["state"]["permissions"]["translation_judgment_allowed"] is True
    assert result["manifest"]["status"] == "accumulating"
    assert result["manifest"]["totals"]["reviewed_rows"] == 0
    assert result["packet"]["reservation"]["status"] == "quality_audit_active"
    assert result["row_count"] == 62
    assert len(result["candidate"]["rows"]) == 62
    assert result["candidate"]["ownership_snapshot"]["row_count"] == 62
    assert result["current"]["operation_mode"]["execution_mode"] == "always_public_full_pipeline"

    current, state, manifest, packet, request, artifact = fixtures()
    request = copy.deepcopy(request)
    request["semantic_boundary"]["unique_reviewed_rows"] = 61
    try:
        initialize_with_semantic_boundary(current, state, manifest, packet, request, artifact, "public", execution_modes(), p4=p4)
    except InitializerError as exc:
        assert "row count mismatch" in str(exc)
    else:
        raise AssertionError("row mismatch must block")
    print("test_fixed_cycle_initializer: OK")


if __name__ == "__main__":
    main()
