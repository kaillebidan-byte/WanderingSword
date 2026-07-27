#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_phase_completion_signal as checker


def contract() -> dict:
    return {
        "schema_version": 1,
        "contract_id": "regulated-phase-completion-signal-v1",
        "marker": checker.MARKER,
        "status_prefix": checker.STATUS_PREFIX,
        "allowed_results": ["success", "error"],
        "pipeline": {
            "phase_order": ["quality_reaudit", "narrative_readthrough"],
            "phases": {
                "quality_reaudit": {
                    "position": 1,
                    "description": "pair reaudit",
                },
                "narrative_readthrough": {
                    "position": 2,
                    "description": "chapter readthrough correction",
                },
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
        },
        "automation": {
            "terminal_detection": "last_nonempty_line_exact_match",
            "result_detection": "immediately_preceding_status_line",
            "success_line": "規定フェイズ結果: success",
            "error_line": "規定フェイズ結果: error",
            "user_input_required": False,
        },
    }


def main() -> None:
    value = contract()
    assert checker.validate_contract(value) == []

    for result in ("success", "error"):
        text = f"処理結果の説明\n規定フェイズ結果: {result}\n規定フェイズ完了\n"
        assert checker.validate_terminal_response(text, result) == []

    missing_error_signal = copy.deepcopy(value)
    missing_error_signal["emission"]["required_on_phase_error"] = False
    assert any("required_on_phase_error" in error for error in checker.validate_contract(missing_error_signal))

    bad_order = copy.deepcopy(value)
    bad_order["pipeline"]["phase_order"].reverse()
    assert any("phase_order" in error for error in checker.validate_contract(bad_order))

    assert checker.validate_terminal_response("規定フェイズ結果: success\n", "success")
    assert checker.validate_terminal_response("規定フェイズ完了\n説明が後ろ\n", "error")
    assert checker.validate_terminal_response(
        "規定フェイズ結果: success\n規定フェイズ完了\n規定フェイズ完了\n",
        "success",
    )
    assert checker.validate_terminal_response(
        "規定フェイズ結果: success\n規定フェイズ完了\n",
        "error",
    )

    print("test_check_phase_completion_signal: OK")


if __name__ == "__main__":
    main()
