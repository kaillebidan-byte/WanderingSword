#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_autonomous_cycle as checker


def contract() -> dict:
    return {
        "execution_policy": {
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
            "allowed_pause_reasons": sorted(checker.PAUSE_REASONS),
            "paused_state_requires_exact_next_action": True,
            "normal_cycle_requires_no_extra_user_continue_message": True,
        }
    }


def state(stage: str, transport: str, status: str, checkpoint: str) -> dict:
    running = status in {"running", "paused"}
    return {
        "stage": stage,
        "transport": {"status": transport},
        "cycle_control": {
            "status": status,
            "private_completion_target": "ready_for_public_ci",
            "public_completion_target": "awaiting_private_merge",
            "post_public_completion_target": "merged",
            "continuation_required": running,
            "stop_reason": "turn_capacity_checkpoint" if status == "paused" else None,
            "exact_next_action": "continue from the recorded checkpoint" if running else None,
            "last_safe_checkpoint": checkpoint,
        },
    }


def main() -> None:
    c = contract()

    # Intermediate boundaries are checkpoints, not normal conversation stops.
    for stage in ("private_preparation", "private_quality_audit", "private_encoding"):
        value = state(stage, "not_ready", "running", stage)
        assert checker.validate(c, value) == []
        stopped = copy.deepcopy(value)
        stopped["cycle_control"].update({
            "status": "target_reached",
            "continuation_required": False,
            "exact_next_action": None,
        })
        assert any("intermediate private stage" in error for error in checker.validate(c, stopped))

    # Explicit emergency checkpoint is allowed only with a reason and exact next action.
    paused = state("private_encoding", "not_ready", "paused", "private_encoding")
    assert checker.validate(c, paused) == []
    missing_reason = copy.deepcopy(paused)
    missing_reason["cycle_control"]["stop_reason"] = None
    assert any("allowed stop_reason" in error for error in checker.validate(c, missing_reason))

    # Normal private, public and post-public completion points.
    for transport in ("ready_for_public_ci", "awaiting_private_merge", "merged"):
        reached = state("translation_frozen", transport, "target_reached", transport)
        assert checker.validate(c, reached) == [], transport

    # Public work cannot stop at in_public_ci or verified.
    for transport in ("in_public_ci", "verified"):
        value = state("translation_frozen", transport, "target_reached", transport)
        assert any("awaiting_private_merge" in error for error in checker.validate(c, value))

    # Translation freeze alone is not enough; private preflight must reach ready_for_public_ci.
    value = state("translation_frozen", "not_ready", "target_reached", "translation_frozen")
    assert any("private preflight" in error for error in checker.validate(c, value))

    # Future scheduled mode is always public and never changes repository visibility.
    future = copy.deepcopy(c)
    future["execution_policy"]["future_scheduler_changes_visibility"] = True
    assert any(
        "future_scheduler_changes_visibility" in error
        for error in checker.validate(future, state("translation_frozen", "merged", "target_reached", "merged"))
    )

    print("test_check_autonomous_cycle: OK")


if __name__ == "__main__":
    main()
