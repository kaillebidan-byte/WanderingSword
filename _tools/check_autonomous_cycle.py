#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手動visibility反復と常時public pipelineの完走目標・例外停止理由を検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "EXECUTION_MODES.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"

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
EXECUTION_MODES = {
    "manual_visibility_cycle",
    "always_public_full_pipeline",
}
MODE_START_VISIBILITY = {
    "manual_visibility_cycle": "private",
    "always_public_full_pipeline": "public",
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


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(contract.get("supported_modes", [])) != EXECUTION_MODES:
        errors.append("execution contract supported_modes mismatch")
    if contract.get("mode_selection_source") != "repository_visibility_at_cycle_start":
        errors.append("execution contract mode_selection_source mismatch")
    if contract.get("selection") != {
        "private": "manual_visibility_cycle",
        "public": "always_public_full_pipeline",
    }:
        errors.append("execution contract selection mismatch")
    lock = contract.get("lock")
    if not isinstance(lock, dict):
        errors.append("execution contract lock must be an object")
    else:
        if lock.get("scope") != "cycle":
            errors.append("execution contract lock.scope must be cycle")
        if lock.get("may_change_only_when_previous_transport_is") != "merged":
            errors.append("execution mode changes must require previous transport=merged")
    input_policy = contract.get("input_policy")
    if not isinstance(input_policy, dict) or input_policy.get("mode_specific_phrase_required") is not False:
        errors.append("execution modes must use the same continue phrase")
    shared = contract.get("shared_pipeline")
    if not isinstance(shared, dict):
        errors.append("execution contract shared_pipeline must be an object")
    else:
        if shared.get("private_stage_names_are_cognitive_not_visibility") is not True:
            errors.append("private stage names must be cognitive, not visibility constraints")
        if shared.get("manifest_ready_required_before_ci") is not True:
            errors.append("manifest ready must remain required before CI")
        if shared.get("stage_permissions_remain_authoritative") is not True:
            errors.append("stage permissions must remain authoritative")
    return errors


def resolve_control_mode(control: dict[str, Any]) -> tuple[str, bool]:
    explicit = control.get("execution_mode")
    if explicit is None:
        return "manual_visibility_cycle", False
    return str(explicit), True


def validate(
    contract: dict[str, Any],
    state: dict[str, Any],
    current: dict[str, Any] | None = None,
) -> list[str]:
    errors = validate_contract(contract)
    control = state.get("cycle_control")
    if not isinstance(control, dict):
        return errors + ["state.cycle_control must be an object"]

    execution_mode, explicit_mode = resolve_control_mode(control)
    if execution_mode not in EXECUTION_MODES:
        errors.append("cycle_control.execution_mode invalid")
        execution_mode = "manual_visibility_cycle"

    stage = state.get("stage")
    transport = state.get("transport", {}).get("status")
    if not explicit_mode and (
        stage in {"private_preparation", "private_quality_audit", "private_encoding"}
        or transport == "not_ready"
    ):
        errors.append("new translation cycle requires explicit execution_mode selection")

    if explicit_mode:
        expected_visibility = MODE_START_VISIBILITY[execution_mode]
        if control.get("cycle_start_visibility") != expected_visibility:
            errors.append(f"cycle_control.cycle_start_visibility must be {expected_visibility!r}")
        if control.get("mode_locked_for_cycle") is not True:
            errors.append("cycle_control.mode_locked_for_cycle must be true")
        expected_normal_target = (
            "visibility_boundary_or_merged"
            if execution_mode == "manual_visibility_cycle"
            else "merged"
        )
        if control.get("normal_completion_target") != expected_normal_target:
            errors.append(f"cycle_control.normal_completion_target must be {expected_normal_target!r}")

    if isinstance(current, dict):
        current_mode = current.get("operation_mode")
        if not isinstance(current_mode, dict):
            errors.append("CURRENT_WORK.operation_mode must be an object")
        else:
            current_execution = current_mode.get("execution_mode")
            current_explicit = current_execution is not None
            if explicit_mode != current_explicit:
                errors.append("CURRENT_WORK and PRIVATE_STAGE_STATE explicit mode lock mismatch")
            elif explicit_mode:
                if current_execution != execution_mode:
                    errors.append("CURRENT_WORK and PRIVATE_STAGE_STATE execution_mode mismatch")
                if current_mode.get("cycle_start_visibility") != control.get("cycle_start_visibility"):
                    errors.append("CURRENT_WORK and PRIVATE_STAGE_STATE cycle_start_visibility mismatch")
                if current_mode.get("mode_locked_for_cycle") is not True:
                    errors.append("CURRENT_WORK.operation_mode.mode_locked_for_cycle must be true")

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
        if explicit_mode and execution_mode == "always_public_full_pipeline" and checkpoint != "merged":
            errors.append("always_public_full_pipeline can reach a normal target only at merged")

    if stage in {"private_preparation", "private_quality_audit", "private_encoding"} and status == "target_reached":
        errors.append("intermediate private stage cannot be a conversational completion target")
    if stage == "translation_frozen" and transport == "not_ready" and status == "target_reached":
        errors.append("translation_frozen/not_ready must continue through release preflight")
    if transport in {"in_public_ci", "verified"} and status == "target_reached":
        errors.append("public execution must continue through awaiting_private_merge")
    if transport in TARGETS and status == "target_reached" and checkpoint != transport:
        errors.append("target_reached checkpoint must match transport.status")
    if (
        explicit_mode
        and execution_mode == "always_public_full_pipeline"
        and transport in {"ready_for_public_ci", "awaiting_private_merge"}
        and status == "target_reached"
    ):
        errors.append("always-public execution must continue without a visibility boundary")

    return errors


def main() -> int:
    contract = load(CONTRACT_PATH)
    state = load(STATE_PATH)
    current = load(CURRENT_PATH)
    errors = validate(contract, state, current)
    control = state.get("cycle_control", {})
    execution_mode, explicit_mode = resolve_control_mode(control)
    print("=== Autonomous visibility cycle ===")
    print(f"execution mode: {execution_mode}{'' if explicit_mode else ' (legacy inferred)'}")
    print(f"status: {control.get('status')}")
    print(f"checkpoint: {control.get('last_safe_checkpoint')}")
    print(f"continuation required: {control.get('continuation_required')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: cycle mode, completion and pause semantics are deterministic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
