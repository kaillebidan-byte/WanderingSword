#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_phase_completion_signal as checker


def contract() -> dict:
    return {
        "schema_version": 2,
        "contract_id": "regulated-phase-completion-signal-v2-authorized",
        "marker": checker.MARKER,
        "status_prefix": checker.STATUS_PREFIX,
        "allowed_results": ["success", "error"],
        "state_file": checker.EXPECTED_STATE_PATH,
        "pipeline": {
            "phase_order": ["quality_reaudit", "narrative_readthrough"],
            "phases": {
                "quality_reaudit": {"position": 1, "description": "pair reaudit"},
                "narrative_readthrough": {"position": 2, "description": "chapter readthrough"},
            },
        },
        "emission": {
            "required_on_phase_success": True,
            "required_on_phase_error": True,
            "exactly_once": True,
            "marker_must_be_last_nonempty_line": True,
            "trailing_content_forbidden": True,
            "status_line_immediately_precedes_marker": True,
            "marker_is_not_success_signal": True,
            "routine_wave_completion_does_not_emit": True,
            "visibility_checkpoint_does_not_emit": True,
            "single_pair_or_single_chapter_completion_does_not_emit": True,
            "release_phase2_completion_does_not_emit": True,
            "train_merge_does_not_emit": True,
            "dynamic_authorization_required": True,
        },
        "eligibility": {
            "authorization_scope": checker.EXPECTED_SCOPE,
            "success_phase_status": "complete",
            "error_phase_status": "terminal_error",
            "routine_pause_is_error": False,
            "ci_phase2_is_regulated_phase": False,
            "transport_merge_is_regulated_phase": False,
        },
        "automation": {
            "terminal_detection": "last_nonempty_line_exact_match",
            "result_detection": "immediately_preceding_status_line",
            "success_line": "規定フェイズ結果: success",
            "error_line": "規定フェイズ結果: error",
            "user_input_required": False,
        },
    }


def audit(quality="in_progress", narrative="queued_after_pair_reaudit") -> dict:
    return {
        "project": {
            "quality_reaudit": {"status": quality},
            "narrative_readthrough": {"status": narrative},
        }
    }


def state(quality="in_progress", narrative="queued", authorization=None) -> dict:
    return {
        "schema_version": 1,
        "contract": "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
        "phase_order": ["quality_reaudit", "narrative_readthrough"],
        "active_phase": "quality_reaudit",
        "phases": {
            "quality_reaudit": {"status": quality},
            "narrative_readthrough": {"status": narrative},
        },
        "signal_authorization": authorization,
        "last_terminal_event": None,
        "routine_pause_is_terminal_error": False,
        "forbidden_terminal_aliases": [
            "ci_train.finalization_phase=phase2",
            "release phase2 success",
            "transport=merged",
            "train merged",
            "wave complete",
            "single pair complete",
            "single chapter complete",
        ],
    }


def authorization(result: str) -> dict:
    return {
        "authorized": True,
        "scope": checker.EXPECTED_SCOPE,
        "phase_id": "quality_reaudit",
        "result": result,
        "event_id": f"quality-reaudit-{result}-01",
        "evidence": ["_phase4_proofread/audit_status.json"],
    }


def main() -> None:
    assert checker.validate_contract(contract()) == []
    assert checker.validate_runtime_state(state(), audit()) == []

    # A train/PR/cycle completion may look syntactically valid but is forbidden while the project phase is in progress.
    train_completion = "PR #146をsquash統合した。\n規定フェイズ結果: success\n規定フェイズ完了\n"
    errors = checker.validate_terminal_response(train_completion, "success", state())
    assert any("not authorized" in error for error in errors)

    success_state = state("complete", authorization=authorization("success"))
    assert checker.validate_runtime_state(success_state, audit("complete")) == []
    assert checker.validate_terminal_response(train_completion, "success", success_state) == []

    error_state = state("terminal_error", authorization=authorization("error"))
    assert checker.validate_runtime_state(error_state, audit("terminal_error")) == []
    error_text = "規定フェイズが継続不能。\n規定フェイズ結果: error\n規定フェイズ完了\n"
    assert checker.validate_terminal_response(error_text, "error", error_state) == []

    wrong_result = checker.validate_terminal_response(error_text, "success", error_state)
    assert any("result mismatch" in error for error in wrong_result)

    missing_phase2_rule = copy.deepcopy(contract())
    missing_phase2_rule["emission"]["release_phase2_completion_does_not_emit"] = False
    assert any("release_phase2" in error for error in checker.validate_contract(missing_phase2_rule))

    mismatched_state = state()
    mismatched_state["phases"]["quality_reaudit"]["status"] = "complete"
    assert any("state mismatch" in error for error in checker.validate_runtime_state(mismatched_state, audit()))

    assert checker.validate_terminal_response("規定フェイズ結果: success\n", "success", success_state)
    assert checker.validate_terminal_response("規定フェイズ完了\n説明が後ろ\n", "error", error_state)
    assert checker.validate_terminal_response(
        "規定フェイズ結果: success\n規定フェイズ完了\n規定フェイズ完了\n",
        "success",
        success_state,
    )

    print("test_check_phase_completion_signal: OK")


if __name__ == "__main__":
    main()
