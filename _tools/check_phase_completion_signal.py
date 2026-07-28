#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二フェイズ作業の終端シグナル契約、動的許可状態、出力形を検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "PHASE_COMPLETION_SIGNAL.json"
STATE_PATH = P4 / "REGULATED_PHASE_STATE.json"
AUDIT_STATUS_PATH = P4 / "audit_status.json"
MARKER = "規定フェイズ完了"
STATUS_PREFIX = "規定フェイズ結果: "
ALLOWED_RESULTS = {"success", "error"}
EXPECTED_PHASE_ORDER = ["quality_reaudit", "narrative_readthrough"]
EXPECTED_STATE_PATH = "_phase4_proofread/REGULATED_PHASE_STATE.json"
EXPECTED_SCOPE = "regulated_phase_terminal"
AUDIT_STATUS_NORMALIZATION = {
    "quality_reaudit": {
        "in_progress": "in_progress",
        "complete": "complete",
        "terminal_error": "terminal_error",
    },
    "narrative_readthrough": {
        "queued_after_pair_reaudit": "queued",
        "queued": "queued",
        "in_progress": "in_progress",
        "complete": "complete",
        "terminal_error": "terminal_error",
    },
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT)}")
    return value


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if contract.get("contract_id") != "regulated-phase-completion-signal-v2-authorized":
        errors.append("contract_id mismatch")
    if contract.get("marker") != MARKER:
        errors.append(f"marker must be {MARKER!r}")
    if contract.get("status_prefix") != STATUS_PREFIX:
        errors.append(f"status_prefix must be {STATUS_PREFIX!r}")
    if set(contract.get("allowed_results", [])) != ALLOWED_RESULTS:
        errors.append("allowed_results must be success and error")
    if contract.get("state_file") != EXPECTED_STATE_PATH:
        errors.append("state_file mismatch")

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
        "release_phase2_completion_does_not_emit",
        "train_merge_does_not_emit",
        "dynamic_authorization_required",
    }
    if not isinstance(emission, dict):
        errors.append("emission must be an object")
    else:
        for key in sorted(required_true):
            if emission.get(key) is not True:
                errors.append(f"emission.{key} must be true")

    eligibility = contract.get("eligibility")
    if not isinstance(eligibility, dict):
        errors.append("eligibility must be an object")
    else:
        expected = {
            "authorization_scope": EXPECTED_SCOPE,
            "success_phase_status": "complete",
            "error_phase_status": "terminal_error",
            "routine_pause_is_error": False,
            "ci_phase2_is_regulated_phase": False,
            "transport_merge_is_regulated_phase": False,
        }
        for key, value in expected.items():
            if eligibility.get(key) != value:
                errors.append(f"eligibility.{key} mismatch")

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


def normalized_audit_status(audit_status: dict[str, Any], phase_id: str) -> str | None:
    project = audit_status.get("project")
    phase = project.get(phase_id) if isinstance(project, dict) else None
    raw = phase.get("status") if isinstance(phase, dict) else None
    return AUDIT_STATUS_NORMALIZATION.get(phase_id, {}).get(raw)


def validate_runtime_state(state: dict[str, Any], audit_status: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != 1:
        errors.append("REGULATED_PHASE_STATE.schema_version must be 1")
    if state.get("contract") != "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json":
        errors.append("REGULATED_PHASE_STATE.contract mismatch")
    if state.get("phase_order") != EXPECTED_PHASE_ORDER:
        errors.append("REGULATED_PHASE_STATE.phase_order mismatch")
    active_phase = state.get("active_phase")
    if active_phase not in EXPECTED_PHASE_ORDER:
        errors.append("REGULATED_PHASE_STATE.active_phase invalid")

    phases = state.get("phases")
    if not isinstance(phases, dict):
        errors.append("REGULATED_PHASE_STATE.phases must be an object")
    else:
        for phase_id in EXPECTED_PHASE_ORDER:
            phase = phases.get(phase_id)
            if not isinstance(phase, dict):
                errors.append(f"REGULATED_PHASE_STATE.phases.{phase_id} must be an object")
                continue
            status = phase.get("status")
            if status not in {"queued", "in_progress", "complete", "terminal_error"}:
                errors.append(f"REGULATED_PHASE_STATE.phases.{phase_id}.status invalid")
            audit_value = normalized_audit_status(audit_status, phase_id)
            if audit_value is None:
                errors.append(f"audit_status.project.{phase_id}.status is unsupported")
            elif status != audit_value:
                errors.append(
                    f"regulated phase state mismatch for {phase_id}: state={status!r} audit={audit_value!r}"
                )

    if state.get("routine_pause_is_terminal_error") is not False:
        errors.append("routine_pause_is_terminal_error must be false")
    forbidden = set(state.get("forbidden_terminal_aliases", []))
    required_aliases = {
        "ci_train.finalization_phase=phase2",
        "release phase2 success",
        "transport=merged",
        "train merged",
        "wave complete",
        "single pair complete",
        "single chapter complete",
    }
    if not required_aliases.issubset(forbidden):
        errors.append("REGULATED_PHASE_STATE.forbidden_terminal_aliases incomplete")

    authorization = state.get("signal_authorization")
    if authorization is not None:
        if not isinstance(authorization, dict):
            errors.append("signal_authorization must be null or object")
        else:
            phase_id = authorization.get("phase_id")
            result = authorization.get("result")
            if authorization.get("authorized") is not True:
                errors.append("signal_authorization.authorized must be true")
            if authorization.get("scope") != EXPECTED_SCOPE:
                errors.append("signal_authorization.scope mismatch")
            if phase_id != active_phase:
                errors.append("signal_authorization.phase_id must match active_phase")
            if result not in ALLOWED_RESULTS:
                errors.append("signal_authorization.result invalid")
            event_id = authorization.get("event_id")
            if not isinstance(event_id, str) or not event_id.strip():
                errors.append("signal_authorization.event_id must be non-empty")
            evidence = authorization.get("evidence")
            if not isinstance(evidence, list) or not evidence or any(
                not isinstance(item, str) or not item.strip() for item in evidence
            ):
                errors.append("signal_authorization.evidence must be a non-empty string list")
            if isinstance(phases, dict) and phase_id in EXPECTED_PHASE_ORDER and result in ALLOWED_RESULTS:
                phase = phases.get(phase_id)
                status = phase.get("status") if isinstance(phase, dict) else None
                expected_status = "complete" if result == "success" else "terminal_error"
                if status != expected_status:
                    errors.append(
                        f"authorized {result} requires active phase status {expected_status!r}"
                    )
    return errors


def validate_signal_authorization(state: dict[str, Any], result: str) -> list[str]:
    if result not in ALLOWED_RESULTS:
        return [f"unsupported result: {result}"]
    authorization = state.get("signal_authorization")
    if not isinstance(authorization, dict):
        return ["regulated phase terminal signal is not authorized"]
    errors: list[str] = []
    if authorization.get("authorized") is not True:
        errors.append("regulated phase terminal signal is not authorized")
    if authorization.get("scope") != EXPECTED_SCOPE:
        errors.append("regulated phase terminal authorization scope mismatch")
    if authorization.get("phase_id") != state.get("active_phase"):
        errors.append("regulated phase terminal authorization phase mismatch")
    if authorization.get("result") != result:
        errors.append("regulated phase terminal authorization result mismatch")
    phases = state.get("phases")
    phase = phases.get(state.get("active_phase")) if isinstance(phases, dict) else None
    status = phase.get("status") if isinstance(phase, dict) else None
    expected_status = "complete" if result == "success" else "terminal_error"
    if status != expected_status:
        errors.append(f"regulated phase terminal status must be {expected_status}")
    return errors


def validate_terminal_response(text: str, result: str, state: dict[str, Any]) -> list[str]:
    errors = validate_signal_authorization(state, result)
    lines = [line.rstrip() for line in text.splitlines()]
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        return [*errors, "terminal response is empty"]
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
        contract = load_object(CONTRACT_PATH)
        state = load_object(STATE_PATH)
        audit_status = load_object(AUDIT_STATUS_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = [
        *validate_contract(contract),
        *validate_runtime_state(state, audit_status),
    ]
    if args.response_file is not None:
        if args.result is None:
            errors.append("--result is required with --response-file")
        else:
            try:
                text = args.response_file.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"cannot read response file: {exc}")
            else:
                errors.extend(validate_terminal_response(text, args.result, state))
    print("=== Regulated phase completion signal ===")
    print(f"active phase: {state.get('active_phase')}")
    print(f"signal authorized: {isinstance(state.get('signal_authorization'), dict)}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: regulated phase marker requires an authorized terminal phase state")
    return 0


if __name__ == "__main__":
    sys.exit(main())
