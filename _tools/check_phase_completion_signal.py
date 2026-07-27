#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二フェイズ作業の終端シグナル契約と出力形を検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "_phase4_proofread" / "PHASE_COMPLETION_SIGNAL.json"
MARKER = "規定フェイズ完了"
STATUS_PREFIX = "規定フェイズ結果: "
ALLOWED_RESULTS = {"success", "error"}
EXPECTED_PHASE_ORDER = ["quality_reaudit", "narrative_readthrough"]


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("phase completion contract top level must be object")
    return value


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if contract.get("contract_id") != "regulated-phase-completion-signal-v1":
        errors.append("contract_id mismatch")
    if contract.get("marker") != MARKER:
        errors.append(f"marker must be {MARKER!r}")
    if contract.get("status_prefix") != STATUS_PREFIX:
        errors.append(f"status_prefix must be {STATUS_PREFIX!r}")
    if set(contract.get("allowed_results", [])) != ALLOWED_RESULTS:
        errors.append("allowed_results must be success and error")

    pipeline = contract.get("pipeline")
    if not isinstance(pipeline, dict):
        errors.append("pipeline must be an object")
    else:
        if pipeline.get("phase_order") != EXPECTED_PHASE_ORDER:
            errors.append("pipeline.phase_order mismatch")
        phases = pipeline.get("phases")
        if not isinstance(phases, dict):
            errors.append("pipeline.phases must be an object")
        else:
            for position, phase_id in enumerate(EXPECTED_PHASE_ORDER, start=1):
                phase = phases.get(phase_id)
                if not isinstance(phase, dict):
                    errors.append(f"pipeline.phases.{phase_id} must be an object")
                    continue
                if phase.get("position") != position:
                    errors.append(f"pipeline.phases.{phase_id}.position mismatch")
                description = phase.get("description")
                if not isinstance(description, str) or not description.strip():
                    errors.append(f"pipeline.phases.{phase_id}.description must be non-empty")

    emission = contract.get("emission")
    required_true = {
        "required_on_phase_success",
        "required_on_phase_error",
        "exactly_once",
        "marker_must_be_last_nonempty_line",
        "trailing_content_forbidden",
        "status_line_immediately_precedes_marker",
        "marker_is_not_success_signal",
        "routine_wave_completion_does_not_emit",
        "visibility_checkpoint_does_not_emit",
        "single_pair_or_single_chapter_completion_does_not_emit",
    }
    if not isinstance(emission, dict):
        errors.append("emission must be an object")
    else:
        for key in sorted(required_true):
            if emission.get(key) is not True:
                errors.append(f"emission.{key} must be true")

    automation = contract.get("automation")
    if not isinstance(automation, dict):
        errors.append("automation must be an object")
    else:
        expected = {
            "terminal_detection": "last_nonempty_line_exact_match",
            "result_detection": "immediately_preceding_status_line",
            "success_line": f"{STATUS_PREFIX}success",
            "error_line": f"{STATUS_PREFIX}error",
            "user_input_required": False,
        }
        for key, value in expected.items():
            if automation.get(key) != value:
                errors.append(f"automation.{key} mismatch")
    return errors


def validate_terminal_response(text: str, result: str) -> list[str]:
    errors: list[str] = []
    if result not in ALLOWED_RESULTS:
        return [f"unsupported result: {result}"]
    lines = [line.rstrip() for line in text.splitlines()]
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        return ["terminal response is empty"]
    if nonempty.count(MARKER) != 1:
        errors.append("terminal response must contain marker exactly once")
    if nonempty[-1] != MARKER:
        errors.append("marker must be the last non-empty line")
    expected_status = f"{STATUS_PREFIX}{result}"
    if len(nonempty) < 2 or nonempty[-2] != expected_status:
        errors.append(f"marker must be immediately preceded by {expected_status!r}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-file", type=Path)
    parser.add_argument("--result", choices=sorted(ALLOWED_RESULTS))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_contract()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate_contract(contract)
    if args.response_file is not None:
        if args.result is None:
            errors.append("--result is required with --response-file")
        else:
            try:
                text = args.response_file.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"cannot read response file: {exc}")
            else:
                errors.extend(validate_terminal_response(text, args.result))
    print("=== Regulated phase completion signal ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: success and error terminal responses use the exact final marker")
    return 0


if __name__ == "__main__":
    sys.exit(main())
