#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "select_cycle_execution_mode.py"


def load_module():
    spec = importlib.util.spec_from_file_location("select_cycle_execution_mode", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load select_cycle_execution_mode.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract() -> dict:
    return {
        "selection": {
            "private": "manual_visibility_cycle",
            "public": "always_public_full_pipeline",
        },
        "modes": {
            "manual_visibility_cycle": {
                "visibility_change_actor": "user",
                "visibility_changes_required": True,
                "public_translation_forbidden": True,
                "deep_failure_returns_private": True,
            },
            "always_public_full_pipeline": {
                "visibility_change_actor": "none",
                "visibility_changes_required": False,
                "visibility_change_requests_forbidden": True,
                "deep_failure_returns_private": False,
            },
        },
    }


def sample(transport: str = "merged", explicit: bool = True) -> tuple[dict, dict]:
    current_mode = {}
    control = {}
    if explicit:
        current_mode.update({
            "execution_mode": "manual_visibility_cycle",
            "cycle_start_visibility": "private",
            "mode_locked_for_cycle": True,
        })
        control.update({
            "execution_mode": "manual_visibility_cycle",
            "cycle_start_visibility": "private",
            "mode_locked_for_cycle": True,
        })
    return (
        {"operation_mode": current_mode},
        {
            "transport": {"status": transport},
            "cycle_control": control,
        },
    )


def main() -> None:
    module = load_module()
    c = contract()

    current, state = sample()
    current, state = module.apply_selection(current, state, c, "public")
    assert current["operation_mode"]["execution_mode"] == "always_public_full_pipeline"
    assert current["operation_mode"]["visibility_change_required"] is False
    assert current["operation_mode"]["public_translation_forbidden"] is False
    assert state["cycle_control"]["execution_mode"] == "always_public_full_pipeline"
    assert state["cycle_control"]["normal_completion_target"] == "merged"

    current, state = sample()
    current, state = module.apply_selection(current, state, c, "private")
    assert current["operation_mode"]["execution_mode"] == "manual_visibility_cycle"
    assert current["operation_mode"]["visibility_change_required"] is True
    assert state["cycle_control"]["normal_completion_target"] == "visibility_boundary_or_merged"

    current, state = sample("not_ready")
    same_current, same_state = module.apply_selection(
        copy.deepcopy(current), copy.deepcopy(state), c, "private"
    )
    assert same_current["operation_mode"]["execution_mode"] == "manual_visibility_cycle"
    assert same_state["cycle_control"]["execution_mode"] == "manual_visibility_cycle"

    current, state = sample("not_ready")
    try:
        module.apply_selection(current, state, c, "public")
    except ValueError as exc:
        assert "mode is locked" in str(exc)
    else:
        raise AssertionError("active cycle mode change must fail")

    current, state = sample("not_ready", explicit=False)
    try:
        module.apply_selection(current, state, c, "public")
    except ValueError as exc:
        assert "legacy active cycle" in str(exc)
    else:
        raise AssertionError("legacy active cycle must not be relabeled")

    print("test_select_cycle_execution_mode: OK")


if __name__ == "__main__":
    main()
