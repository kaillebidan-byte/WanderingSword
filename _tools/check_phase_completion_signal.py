#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二フェイズ終端シグナルをlive stateと照合し、通常応答も送信前検査する。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "PHASE_COMPLETION_SIGNAL.json"
STATE_PATH = P4 / "REGULATED_PHASE_STATE.json"
AUDIT_STATUS_PATH = P4 / "audit_status.json"
MARKER = "規定フェイズ完了"
AUTH_PREFIX = "規定フェイズ認可: "
STATUS_PREFIX = "規定フェイズ結果: "
ALLOWED_RESULTS = {"success", "error"}
EXPECTED_PHASE_ORDER = ["quality_reaudit", "narrative_readthrough"]
EXPECTED_STATE_PATH = "_phase4_proofread/REGULATED_PHASE_STATE.json"
EXPECTED_SCOPE = "regulated_phase_terminal"
EXPECTED_CONSUMER = "_tools/regulated_phase_terminal_consumer.js"
EXPECTED_AGENT_GATE = "_phase4_proofread/FINAL_RESPONSE_GATE.md"
EVENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
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
    if contract.get("schema_version") != 3:
        errors.append("schema_version must be 3")
    if contract.get("contract_id") != "regulated-phase-completion-signal-v3-consumer-gated":
        errors.append("contract_id mismatch")
    if contract.get("marker") != MARKER:
        errors.append(f"marker must be {MARKER!r}")
    if contract.get("authorization_prefix") != AUTH_PREFIX:
        errors.append(f"authorization_prefix must be {AUTH_PREFIX!r}")
    if contract.get("status_prefix") != STATUS_PREFIX:
        errors.append(f"status_prefix must be {STATUS_PREFIX!r}")
    if set(contract.get("allowed_results", [])) != ALLOWED_RESULTS:
        errors.append("allowed_results must be success and error")
    if contract.get("state_file") != EXPECTED_STATE_PATH:
        errors.append("state_file mismatch")

    pipeline = contract.get("pipeline")
    if not isinstance(pipeline, dict) or pipeline.get("phase_order") != EXPECTED_PHASE_ORDER:
        errors.append("pipeline.phase_order mismatch")
    else:
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
                if not isinstance(phase.get("description"), str) or not phase["description"].strip():
                    errors.append(f"pipeline.phases.{phase_id}.description must be non-empty")

    emission = contract.get("emission")
    required_true = {
        "required_on_phase_success",
        "required_on_phase_error",
        "exactly_once",
        "marker_must_be_last_nonempty_line",
        "trailing_content_forbidden",
        "status_line_immediately_precedes_marker",
        "authorization_line_immediately_precedes_status",
        "marker_is_not_success_signal",
        "marker_only_must_be_rejected_by_consumers",
        "unauthorized_marker_must_not_stop_automation",
        "reserved_marker_forbidden_without_authorization",
        "routine_wave_completion_does_not_emit",
        "visibility_checkpoint_does_not_emit",
        "single_pair_or_single_chapter_completion_does_not_emit",
        "release_phase2_completion_does_not_emit",
        "train_merge_does_not_emit",
        "dynamic_authorization_required",
        "live_state_match_required",
    }
    if not isinstance(emission, dict):
        errors.append("emission must be an object")
    else:
        for key in sorted(required_true):
            if emission.get(key) is not True:
                errors.append(f"emission.{key} must be true")

    eligibility = contract.get("eligibility")
    expected_eligibility = {
        "authorization_scope": EXPECTED_SCOPE,
        "success_phase_status": "complete",
        "error_phase_status": "terminal_error",
        "authorization_event_id_required": True,
        "routine_pause_is_error": False,
        "ci_phase2_is_regulated_phase": False,
        "transport_merge_is_regulated_phase": False,
    }
    if not isinstance(eligibility, dict):
        errors.append("eligibility must be an object")
    else:
        for key, value in expected_eligibility.items():
            if eligibility.get(key) != value:
                errors.append(f"eligibility.{key} mismatch")

    automation = contract.get("automation")
    expected_automation = {
        "terminal_detection": "validated_three_line_suffix_against_live_state",
        "authorization_detection": "third_nonempty_line_from_end_matches_live_event_id",
        "result_detection": "second_nonempty_line_from_end_matches_live_result",
        "marker_detection": "last_nonempty_line_exact_match",
        "marker_only_is_terminal": False,
        "live_state_validation_required": True,
        "live_state_unavailable_behavior": "reject_terminal",
        "consumer_reference": EXPECTED_CONSUMER,
        "python_validator": "_tools/check_phase_completion_signal.py",
        "agent_gate": EXPECTED_AGENT_GATE,
        "success_line": f"{STATUS_PREFIX}success",
        "error_line": f"{STATUS_PREFIX}error",
        "user_input_required": False,
    }
    if not isinstance(automation, dict):
        errors.append("automation must be an object")
    else:
        for key, value in expected_automation.items():
            if automation.get(key) != value:
                errors.append(f"automation.{key} mismatch")
    if not (ROOT / EXPECTED_AGENT_GATE).is_file():
        errors.append("agent final response gate document is missing")
    if not (ROOT / EXPECTED_CONSUMER).is_file():
        errors.append("browser terminal consumer is missing")
    return errors


def normalized_audit_status(audit_status: dict[str, Any], phase_id: str) -> str | None:
    project = audit_status.get("project")
    phase = project.get(phase_id) if isinstance(project, dict) else None
    raw = phase.get("status") if isinstance(phase, dict) else None
    return AUDIT_STATUS_NORMALIZATION.get(phase_id, {}).get(raw)


def validate_runtime_state(state: dict[str, Any], audit_status: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != 2:
        errors.append("REGULATED_PHASE_STATE.schema_version must be 2")
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

    gate = state.get("consumer_gate")
    expected_gate = {
        "marker_only_accepted": False,
        "live_state_match_required": True,
        "live_state_unavailable_behavior": "reject_terminal",
        "authorization_line_prefix": AUTH_PREFIX,
        "authorization_value_source": "signal_authorization.event_id",
        "result_value_source": "signal_authorization.result",
        "response_suffix_lines": 3,
        "python_validator": "_tools/check_phase_completion_signal.py",
        "javascript_validator": EXPECTED_CONSUMER,
        "agent_gate": EXPECTED_AGENT_GATE,
    }
    if not isinstance(gate, dict):
        errors.append("REGULATED_PHASE_STATE.consumer_gate must be an object")
    else:
        for key, value in expected_gate.items():
            if gate.get(key) != value:
                errors.append(f"consumer_gate.{key} mismatch")

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
            if not isinstance(event_id, str) or EVENT_ID_RE.fullmatch(event_id) is None:
                errors.append("signal_authorization.event_id format invalid")
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
                    errors.append(f"authorized {result} requires active phase status {expected_status!r}")
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
    event_id = authorization.get("event_id")
    if not isinstance(event_id, str) or EVENT_ID_RE.fullmatch(event_id) is None:
        errors.append("regulated phase terminal event ID is invalid")
    phases = state.get("phases")
    phase = phases.get(state.get("active_phase")) if isinstance(phases, dict) else None
    status = phase.get("status") if isinstance(phase, dict) else None
    expected_status = "complete" if result == "success" else "terminal_error"
    if status != expected_status:
        errors.append(f"regulated phase terminal status must be {expected_status}")
    return errors


def nonempty_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def validate_terminal_response(text: str, result: str, state: dict[str, Any]) -> list[str]:
    errors = validate_signal_authorization(state, result)
    lines = nonempty_lines(text)
    if not lines:
        return [*errors, "terminal response is empty"]
    if lines.count(MARKER) != 1:
        errors.append("terminal response must contain marker exactly once")
    if lines[-1] != MARKER:
        errors.append("marker must be the last non-empty line")
    expected_status = f"{STATUS_PREFIX}{result}"
    if len(lines) < 2 or lines[-2] != expected_status:
        errors.append(f"marker must be immediately preceded by {expected_status!r}")
    authorization = state.get("signal_authorization")
    event_id = authorization.get("event_id") if isinstance(authorization, dict) else None
    expected_authorization = f"{AUTH_PREFIX}{event_id}" if isinstance(event_id, str) else None
    if expected_authorization is None or len(lines) < 3 or lines[-3] != expected_authorization:
        errors.append("status line must be immediately preceded by the live authorization event ID")
    return errors


def infer_result(lines: list[str]) -> str | None:
    if len(lines) < 2 or not lines[-2].startswith(STATUS_PREFIX):
        return None
    value = lines[-2][len(STATUS_PREFIX):]
    return value if value in ALLOWED_RESULTS else None


def validate_response(text: str, state: dict[str, Any], asserted_result: str | None = None) -> list[str]:
    """送信前ゲート。予約markerが無い通常応答は通し、含む場合だけlive認可を必須化する。"""
    lines = nonempty_lines(text)
    if MARKER not in lines:
        if asserted_result is not None:
            return ["asserted terminal result but reserved marker is absent"]
        return []
    inferred = infer_result(lines)
    if inferred is None:
        return [
            "reserved marker is present but a valid result line is not immediately before it",
            *validate_signal_authorization(state, asserted_result or "invalid"),
        ]
    errors = validate_terminal_response(text, inferred, state)
    if asserted_result is not None and inferred != asserted_result:
        errors.append("asserted terminal result does not match response result line")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-file", type=Path)
    parser.add_argument("--result", choices=sorted(ALLOWED_RESULTS))
    parser.add_argument("--json", action="store_true")
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
    errors = [*validate_contract(contract), *validate_runtime_state(state, audit_status)]
    terminal_candidate = False
    if args.response_file is not None:
        try:
            text = args.response_file.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read response file: {exc}")
        else:
            terminal_candidate = MARKER in nonempty_lines(text)
            errors.extend(validate_response(text, state, args.result))
    accepted = not errors
    if args.json:
        print(json.dumps({
            "accepted": accepted,
            "terminal_candidate": terminal_candidate,
            "active_phase": state.get("active_phase"),
            "signal_authorized": isinstance(state.get("signal_authorization"), dict),
            "errors": errors,
        }, ensure_ascii=False))
    else:
        print("=== Regulated phase completion signal ===")
        print(f"active phase: {state.get('active_phase')}")
        print(f"signal authorized: {isinstance(state.get('signal_authorization'), dict)}")
        print(f"terminal candidate: {terminal_candidate}")
        for error in errors:
            print(f"ERROR: {error}")
        if accepted:
            print("OK: response is safe to send; terminal marker requires live three-line authorization")
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())
