#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通常応答と規定終端応答をlive stateから分離し、予約tokenをroutine経路へ露出しない。"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import check_phase_completion_signal as phase_checker

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
POLICY_PATH = P4 / "FINAL_RESPONSE_POLICY.json"
STATE_PATH = P4 / "REGULATED_PHASE_STATE.json"
SAFE_POLICY_ENTRY = "_phase4_proofread/FINAL_RESPONSE_POLICY.json"
RAW_ROUTINE_ENTRIES = {
    "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
    "_phase4_proofread/REGULATED_PHASE_STATE.json",
}


class FinalResponsePolicyError(ValueError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalResponsePolicyError(f"top level must be object: {path}")
    return value


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if policy.get("contract_id") != "final-response-policy-v1-opaque-terminal":
        errors.append("contract_id mismatch")
    expected_paths = {
        "live_state": "_phase4_proofread/REGULATED_PHASE_STATE.json",
        "validator": "_tools/check_phase_completion_signal.py",
        "terminal_renderer": "_tools/render_phase_completion_suffix.py",
        "resume_entrypoint": "_tools/resume_work_entrypoint.py",
    }
    for key, value in expected_paths.items():
        if policy.get(key) != value:
            errors.append(f"{key} mismatch")

    normal = policy.get("normal_response")
    if not isinstance(normal, dict):
        errors.append("normal_response must be an object")
    else:
        if normal.get("reserved_terminal_token_allowed") is not False:
            errors.append("normal response must forbid reserved terminal token")
        if normal.get("safe_completion_label") != "通常作業cycle完了":
            errors.append("normal response safe completion label mismatch")
        if normal.get("draft_validation_required") is not True:
            errors.append("normal response draft validation must be required")
        if normal.get("renderer_execution_forbidden") is not True:
            errors.append("normal response renderer execution must be forbidden")
        aliases = normal.get("terminal_inference_forbidden_from")
        required = {
            "wave complete",
            "train merged",
            "transport merged",
            "release phase2 success",
            "cycle target reached",
            "single pair complete",
            "single chapter complete",
        }
        if not isinstance(aliases, list) or not required.issubset(set(aliases)):
            errors.append("normal response terminal inference aliases incomplete")

    terminal = policy.get("authorized_terminal")
    if not isinstance(terminal, dict):
        errors.append("authorized_terminal must be an object")
    else:
        for key in (
            "reserved_terminal_token_allowed",
            "live_authorization_required",
            "manual_suffix_construction_forbidden",
            "renderer_output_only",
            "validator_must_accept_renderer_output",
        ):
            if terminal.get(key) is not True:
                errors.append(f"authorized_terminal.{key} must be true")

    routine = policy.get("routine_read_policy")
    if not isinstance(routine, dict):
        errors.append("routine_read_policy must be an object")
    else:
        if routine.get("opaque_terminal_token") is not True:
            errors.append("routine read must keep terminal token opaque")
        if routine.get("raw_signal_contract_is_validator_only") is not True:
            errors.append("raw signal contract must be validator-only")
        if routine.get("raw_live_authorization_is_controller_only") is not True:
            errors.append("raw live authorization must be controller-only")
        if routine.get("mandatory_read_order_entry") != SAFE_POLICY_ENTRY:
            errors.append("mandatory read order entry mismatch")

    # routineに読むpolicy自体へ予約tokenの字面を露出させない。
    serialized = json.dumps(policy, ensure_ascii=False)
    if phase_checker.MARKER in serialized:
        errors.append("opaque policy must not expose reserved terminal token")
    return errors


def build_gate(policy: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    errors = validate_policy(policy)
    if errors:
        raise FinalResponsePolicyError("; ".join(errors))

    authorization = state.get("signal_authorization")
    if authorization is None:
        normal = policy["normal_response"]
        return {
            "policy": SAFE_POLICY_ENTRY,
            "mode": "normal_response",
            "reserved_terminal_token_allowed": False,
            "safe_completion_label": normal["safe_completion_label"],
            "draft_validation_required": True,
            "renderer_execution_forbidden": True,
            "validator": policy["validator"],
            "terminal_inference_forbidden_from": list(normal["terminal_inference_forbidden_from"]),
        }
    if not isinstance(authorization, dict):
        raise FinalResponsePolicyError("signal_authorization must be null or object")
    result = authorization.get("result")
    if result not in phase_checker.ALLOWED_RESULTS:
        raise FinalResponsePolicyError("live authorization result is invalid")
    auth_errors = phase_checker.validate_signal_authorization(state, result)
    if auth_errors:
        raise FinalResponsePolicyError("; ".join(auth_errors))
    return {
        "policy": SAFE_POLICY_ENTRY,
        "mode": "authorized_terminal",
        "reserved_terminal_token_allowed": True,
        "manual_suffix_construction_forbidden": True,
        "renderer_required": True,
        "renderer": policy["terminal_renderer"],
        "validator": policy["validator"],
    }


def sanitize_mandatory_read_order(current: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    updated = copy.deepcopy(current)
    order = updated.get("mandatory_read_order")
    if not isinstance(order, list):
        raise FinalResponsePolicyError("CURRENT_WORK.mandatory_read_order must be a list")
    filtered = [item for item in order if item not in RAW_ROUTINE_ENTRIES and item != SAFE_POLICY_ENTRY]
    try:
        index = filtered.index("_phase4_proofread/EXECUTION_MODES.json") + 1
    except ValueError:
        try:
            index = filtered.index("AGENTS.md") + 1
        except ValueError:
            index = 0
    filtered.insert(index, SAFE_POLICY_ENTRY)
    updated["mandatory_read_order"] = filtered
    return updated, updated != current


def assert_work_order_is_opaque(work_order: dict[str, Any]) -> None:
    serialized = json.dumps(work_order, ensure_ascii=False)
    if phase_checker.MARKER in serialized:
        raise FinalResponsePolicyError("work order exposed reserved terminal token")
