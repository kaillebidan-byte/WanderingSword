#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_autonomous_cycle as checker


def contract() -> dict:
    return {
        "supported_modes": sorted(checker.EXECUTION_MODES),
        "mode_selection_source": "repository_visibility_at_cycle_start",
        "selection": {
            "private": "manual_visibility_cycle",
            "public": "always_public_full_pipeline",
        },
        "lock": {
            "scope": "cycle",
            "may_change_only_when_previous_transport_is": "merged",
        },
        "input_policy": {
            "continue_phrase": "作業の続きを",
            "mode_specific_phrase_required": False,
        },
        "shared_pipeline": {
            "private_stage_names_are_cognitive_not_visibility": True,
            "manifest_ready_required_before_ci": True,
            "stage_permissions_remain_authoritative": True,
        },
    }


def state(
    stage: str,
    transport: str,
    status: str,
    checkpoint: str,
    execution_mode: str = "manual_visibility_cycle",
    explicit: bool = True,
) -> dict:
    running = status in {"running", "paused"}
    manual = execution_mode == "manual_visibility_cycle"
    control = {
        "status": status,
        "private_completion_target": "ready_for_public_ci",
        "public_completion_target": "awaiting_private_merge",
        "post_public_completion_target": "merged",
        "continuation_required": running,
        "stop_reason": "turn_capacity_checkpoint" if status == "paused" else None,
        "exact_next_action": "continue from the recorded checkpoint" if running else None,
        "last_safe_checkpoint": checkpoint,
    }
    if explicit:
        control.update({
            "execution_mode": execution_mode,
            "cycle_start_visibility": "private" if manual else "public",
            "mode_locked_for_cycle": True,
            "normal_completion_target": "visibility_boundary_or_merged" if manual else "merged",
        })
    return {
        "stage": stage,
        "transport": {"status": transport},
        "cycle_control": control,
    }


def current(execution_mode: str = "manual_visibility_cycle", explicit: bool = True) -> dict:
    manual = execution_mode == "manual_visibility_cycle"
    mode = {}
    if explicit:
        mode.update({
            "execution_mode": execution_mode,
            "cycle_start_visibility": "private" if manual else "public",
            "mode_locked_for_cycle": True,
        })
    return {"operation_mode": mode}


def main() -> None:
    c = contract()

    legacy = state(
        "translation_frozen",
        "awaiting_private_merge",
        "target_reached",
        "awaiting_private_merge",
        explicit=False,
    )
    assert checker.validate(c, legacy, current(explicit=False)) == []

    for stage in ("private_preparation", "private_quality_audit", "private_encoding"):
        value = state(stage, "not_ready", "running", stage)
        assert checker.validate(c, value, current()) == []
        stopped = copy.deepcopy(value)
        stopped["cycle_control"].update({
            "status": "target_reached",
            "continuation_required": False,
            "exact_next_action": None,
        })
        assert any("intermediate private stage" in error for error in checker.validate(c, stopped))

    paused = state("private_encoding", "not_ready", "paused", "private_encoding")
    assert checker.validate(c, paused, current()) == []
    missing_reason = copy.deepcopy(paused)
    missing_reason["cycle_control"]["stop_reason"] = None
    assert any("allowed stop_reason" in error for error in checker.validate(c, missing_reason))

    for transport in ("ready_for_public_ci", "awaiting_private_merge", "merged"):
        reached = state("translation_frozen", transport, "target_reached", transport)
        assert checker.validate(c, reached, current()) == [], transport

    for transport in ("ready_for_public_ci", "awaiting_private_merge"):
        reached = state(
            "translation_frozen",
            transport,
            "target_reached",
            transport,
            "always_public_full_pipeline",
        )
        errors = checker.validate(c, reached, current("always_public_full_pipeline"))
        assert any("only at merged" in error or "without a visibility boundary" in error for error in errors)

    merged = state(
        "translation_frozen",
        "merged",
        "target_reached",
        "merged",
        "always_public_full_pipeline",
    )
    assert checker.validate(c, merged, current("always_public_full_pipeline")) == []

    for transport in ("in_public_ci", "verified"):
        value = state("translation_frozen", transport, "target_reached", transport)
        assert any("awaiting_private_merge" in error for error in checker.validate(c, value))

    value = state("translation_frozen", "not_ready", "target_reached", "translation_frozen")
    assert any("release preflight" in error for error in checker.validate(c, value))

    mismatched = state(
        "private_preparation",
        "not_ready",
        "running",
        "private_preparation",
        "always_public_full_pipeline",
    )
    errors = checker.validate(c, mismatched, current("manual_visibility_cycle"))
    assert any("execution_mode mismatch" in error for error in errors)

    print("test_check_autonomous_cycle: OK")


if __name__ == "__main__":
    main()
