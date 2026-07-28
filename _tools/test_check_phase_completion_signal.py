#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_phase_completion_signal as checker


def contract() -> dict:
    return {
        "schema_version": 3,
        "contract_id": "regulated-phase-completion-signal-v3-consumer-gated",
        "marker": checker.MARKER,
        "authorization_prefix": checker.AUTH_PREFIX,
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
            "authorization_line_immediately_precedes_status": True,
            "marker_is_not_success_signal": True,
            "marker_only_must_be_rejected_by_consumers": True,
            "unauthorized_marker_must_not_stop_automation": True,
            "reserved_marker_forbidden_without_authorization": True,
            "routine_wave_completion_does_not_emit": True,
            "visibility_checkpoint_does_not_emit": True,
            "single_pair_or_single_chapter_completion_does_not_emit": True,
            "release_phase2_completion_does_not_emit": True,
            "train_merge_does_not_emit": True,
            "dynamic_authorization_required": True,
            "live_state_match_required": True,
        },
        "eligibility": {
            "authorization_scope": checker.EXPECTED_SCOPE,
            "success_phase_status": "complete",
            "error_phase_status": "terminal_error",
            "authorization_event_id_required": True,
            "routine_pause_is_error": False,
            "ci_phase2_is_regulated_phase": False,
            "transport_merge_is_regulated_phase": False,
        },
        "automation": {
            "terminal_detection": "validated_three_line_suffix_against_live_state",
            "authorization_detection": "third_nonempty_line_from_end_matches_live_event_id",
            "result_detection": "second_nonempty_line_from_end_matches_live_result",
            "marker_detection": "last_nonempty_line_exact_match",
            "marker_only_is_terminal": False,
            "live_state_validation_required": True,
            "live_state_unavailable_behavior": "reject_terminal",
            "consumer_reference": checker.EXPECTED_CONSUMER,
            "python_validator": "_tools/check_phase_completion_signal.py",
            "agent_gate": checker.EXPECTED_AGENT_GATE,
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
        "schema_version": 2,
        "contract": "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
        "phase_order": ["quality_reaudit", "narrative_readthrough"],
        "active_phase": "quality_reaudit",
        "phases": {
            "quality_reaudit": {"status": quality},
            "narrative_readthrough": {"status": narrative},
        },
        "signal_authorization": authorization,
        "consumer_gate": {
            "marker_only_accepted": False,
            "live_state_match_required": True,
            "live_state_unavailable_behavior": "reject_terminal",
            "authorization_line_prefix": checker.AUTH_PREFIX,
            "authorization_value_source": "signal_authorization.event_id",
            "result_value_source": "signal_authorization.result",
            "response_suffix_lines": 3,
            "python_validator": "_tools/check_phase_completion_signal.py",
            "javascript_validator": checker.EXPECTED_CONSUMER,
            "agent_gate": checker.EXPECTED_AGENT_GATE,
        },
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
        "event_id": f"quality-reaudit-{result}-terminal-001",
        "evidence": ["_phase4_proofread/audit_status.json"],
    }


def terminal_text(result: str, event_id: str) -> str:
    return (
        "フェイズ全体の終端根拠を確定した。\n"
        f"{checker.AUTH_PREFIX}{event_id}\n"
        f"{checker.STATUS_PREFIX}{result}\n"
        f"{checker.MARKER}\n"
    )


def main() -> None:
    assert checker.validate_contract(contract()) == []
    assert checker.validate_runtime_state(state(), audit()) == []

    normal_response = "train-23をsquash統合した。\n次候補を予約した。\n"
    assert checker.validate_response(normal_response, state()) == []

    # 実際の再発文。固定markerだけでは、見た目に関係なく送信前ゲートで拒否する。
    train23_bad = "train-23はmerged / target_reachedまで完走した。\n規定フェイズ完了\n"
    errors = checker.validate_response(train23_bad, state())
    assert any("not authorized" in error or "result line" in error for error in errors)

    # 旧二行形式も、live event IDが無いため拒否する。
    two_line = "規定フェイズ結果: success\n規定フェイズ完了\n"
    success_state = state("complete", authorization=authorization("success"))
    errors = checker.validate_response(two_line, success_state)
    assert any("event ID" in error for error in errors)

    # モデルがevent IDを捏造してもlive state不一致で拒否する。
    invented = (
        "規定フェイズ認可: invented-event-999\n"
        "規定フェイズ結果: success\n"
        "規定フェイズ完了\n"
    )
    errors = checker.validate_response(invented, success_state)
    assert any("live authorization event ID" in error for error in errors)

    assert checker.validate_runtime_state(success_state, audit("complete")) == []
    success_id = success_state["signal_authorization"]["event_id"]
    assert checker.validate_response(terminal_text("success", success_id), success_state) == []

    error_state = state("terminal_error", authorization=authorization("error"))
    assert checker.validate_runtime_state(error_state, audit("terminal_error")) == []
    error_id = error_state["signal_authorization"]["event_id"]
    assert checker.validate_response(terminal_text("error", error_id), error_state) == []

    wrong_result = checker.validate_response(terminal_text("success", error_id), error_state)
    assert any("result mismatch" in error for error in wrong_result)

    missing_consumer_rule = copy.deepcopy(contract())
    missing_consumer_rule["emission"]["marker_only_must_be_rejected_by_consumers"] = False
    assert any("marker_only" in error for error in checker.validate_contract(missing_consumer_rule))

    missing_unavailable_rule = copy.deepcopy(contract())
    missing_unavailable_rule["automation"]["live_state_unavailable_behavior"] = "accept_marker"
    assert any("live_state_unavailable_behavior" in error for error in checker.validate_contract(missing_unavailable_rule))

    mismatched_state = state()
    mismatched_state["phases"]["quality_reaudit"]["status"] = "complete"
    assert any("state mismatch" in error for error in checker.validate_runtime_state(mismatched_state, audit()))

    permissive_gate = state()
    permissive_gate["consumer_gate"]["marker_only_accepted"] = True
    assert any("marker_only_accepted" in error for error in checker.validate_runtime_state(permissive_gate, audit()))

    unavailable_accept = state()
    unavailable_accept["consumer_gate"]["live_state_unavailable_behavior"] = "accept_marker"
    assert any("live_state_unavailable_behavior" in error for error in checker.validate_runtime_state(unavailable_accept, audit()))

    print("test_check_phase_completion_signal: OK")


if __name__ == "__main__":
    main()
