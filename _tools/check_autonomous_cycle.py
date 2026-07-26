#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""private/public/private反復の完走目標と例外停止理由を検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "PRIVATE_TRANSLATION_STAGES.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"

STAGES = {
    "private_preparation",
    "private_quality_audit",
    "private_encoding",
    "translation_frozen",
}
TRANSPORT = {
    "not_ready",
    "ready_for_public_ci",
    "in_public_ci",
    "verified",
    "awaiting_private_merge",
    "merged",
}
TARGETS = {
    "ready_for_public_ci",
    "awaiting_private_merge",
    "merged",
}
PAUSE_REASONS = {
    "user_decision_required",
    "checker_failure",
    "external_dependency_unavailable",
    "turn_capacity_checkpoint",
}
STATUSES = {"running", "paused", "target_reached"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(contract: dict[str, Any], state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = contract.get("execution_policy")
    if not isinstance(policy, dict):
        return ["contract.execution_policy must be an object"]

    expected_policy = {
        "stage_boundaries_are_conversational_stops": False,
        "private_completion_target": "ready_for_public_ci",
        "public_completion_target": "awaiting_private_merge",
        "post_public_completion_target": "merged",
        "current_manual_mode": "private_public_private",
        "visibility_change_is_external": True,
        "scheduler_consumes_cycle_control": True,
        "future_scheduled_mode": "always_public_full_pipeline",
        "future_scheduler_changes_visibility": False,
        "future_scheduler_runs_all_stages": True,
        "normal_cycle_requires_no_extra_user_continue_message": True,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            errors.append(f"contract.execution_policy.{key} mismatch")
    if set(policy.get("allowed_pause_reasons", [])) != PAUSE_REASONS:
        errors.append("contract.execution_policy.allowed_pause_reasons mismatch")
    if policy.get("paused_state_requires_exact_next_action") is not True:
        errors.append("contract.execution_policy.paused_state_requires_exact_next_action must be true")

    control = state.get("cycle_control")
    if not isinstance(control, dict):
        return errors + ["state.cycle_control must be an object"]

    for key, expected in (
        ("private_completion_target", "ready_for_public_ci"),
        ("public_completion_target", "awaiting_private_merge"),
        ("post_public_completion_target", "merged"),
    ):
        if control.get(key) != expected:
            errors.append(f"cycle_control.{key} mismatch")

    status = control.get("status")
    if status not in STATUSES:
        errors.append("cycle_control.status invalid")
    continuation = control.get("continuation_required")
    if not isinstance(continuation, bool):
        errors.append("cycle_control.continuation_required must be boolean")

    stop_reason = control.get("stop_reason")
    next_action = control.get("exact_next_action")
    checkpoint = control.get("last_safe_checkpoint")
    if checkpoint not in STAGES | TRANSPORT:
        errors.append("cycle_control.last_safe_checkpoint invalid")

    if status == "running":
        if continuation is not True:
            errors.append("running cycle requires continuation_required=true")
        if stop_reason is not None:
            errors.append("running cycle must not define stop_reason")
        if not _nonempty(next_action):
            errors.append("running cycle requires exact_next_action")
    elif status == "paused":
        if continuation is not True:
            errors.append("paused cycle requires continuation_required=true")
        if stop_reason not in PAUSE_REASONS:
            errors.append("paused cycle requires an allowed stop_reason")
        if not _nonempty(next_action):
            errors.append("paused cycle requires exact_next_action")
    elif status == "target_reached":
        if continuation is not False:
            errors.append("target_reached requires continuation_required=false")
        if stop_reason is not None:
            errors.append("target_reached must not define stop_reason")
        if next_action is not None:
            errors.append("target_reached must not define exact_next_action")
        if checkpoint not in TARGETS:
            errors.append("target_reached checkpoint must be a cycle completion target")

    stage = state.get("stage")
    transport = state.get("transport", {}).get("status")
    if stage in {"private_preparation", "private_quality_audit", "private_encoding"} and status == "target_reached":
        errors.append("intermediate private stage cannot be a conversational completion target")
    if stage == "translation_frozen" and transport == "not_ready" and status == "target_reached":
        errors.append("translation_frozen/not_ready must continue through private preflight")
    if transport in {"in_public_ci", "verified"} and status == "target_reached":
        errors.append("public execution must continue through awaiting_private_merge")
    if transport in TARGETS and status == "target_reached" and checkpoint != transport:
        errors.append("target_reached checkpoint must match transport.status")

    return errors


def main() -> int:
    contract = load(CONTRACT_PATH)
    state = load(STATE_PATH)
    errors = validate(contract, state)
    control = state.get("cycle_control", {})
    print("=== Autonomous visibility cycle ===")
    print(f"status: {control.get('status')}")
    print(f"checkpoint: {control.get('last_safe_checkpoint')}")
    print(f"continuation required: {control.get('continuation_required')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: cycle completion and pause semantics are deterministic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
