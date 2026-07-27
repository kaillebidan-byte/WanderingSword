#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cycle開始時のrepository visibilityから実行モードを選び、二つの状態正本へ固定する。"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
CONTRACT_PATH = P4 / "EXECUTION_MODES.json"
VALID_VISIBILITIES = {"private", "public"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def selected_values(contract: dict[str, Any], visibility: str) -> dict[str, Any]:
    if visibility not in VALID_VISIBILITIES:
        raise ValueError(f"unsupported repository visibility: {visibility}")
    selection = contract.get("selection")
    modes = contract.get("modes")
    if not isinstance(selection, dict) or not isinstance(modes, dict):
        raise ValueError("EXECUTION_MODES selection and modes must be objects")
    execution_mode = selection.get(visibility)
    definition = modes.get(execution_mode)
    if not isinstance(execution_mode, str) or not isinstance(definition, dict):
        raise ValueError(f"EXECUTION_MODES does not define visibility {visibility!r}")
    manual = execution_mode == "manual_visibility_cycle"
    return {
        "execution_mode": execution_mode,
        "cycle_start_visibility": visibility,
        "mode_locked_for_cycle": True,
        "visibility_change_actor": definition.get("visibility_change_actor"),
        "visibility_change_required": bool(definition.get("visibility_changes_required")),
        "visibility_change_requests_forbidden": bool(definition.get("visibility_change_requests_forbidden", False)),
        "public_translation_forbidden": bool(definition.get("public_translation_forbidden", False)),
        "deep_failure_returns_private": bool(definition.get("deep_failure_returns_private")),
        "stage_permissions_are_authoritative": True,
        "normal_cycle_completion_target": "visibility_boundary_or_merged" if manual else "merged",
    }


def apply_selection(
    current: dict[str, Any],
    state: dict[str, Any],
    contract: dict[str, Any],
    visibility: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    values = selected_values(contract, visibility)
    operation_mode = current.get("operation_mode")
    control = state.get("cycle_control")
    if not isinstance(operation_mode, dict):
        raise ValueError("CURRENT_WORK.operation_mode must be an object")
    if not isinstance(control, dict):
        raise ValueError("PRIVATE_STAGE_STATE.cycle_control must be an object")

    transport = state.get("transport", {}).get("status")
    existing_mode = control.get("execution_mode")
    existing_visibility = control.get("cycle_start_visibility")
    locked = control.get("mode_locked_for_cycle") is True

    if locked and transport != "merged":
        if existing_mode == values["execution_mode"] and existing_visibility == visibility:
            return current, state
        raise ValueError(
            "active cycle mode is locked; complete or reconcile the current cycle before selecting a new mode"
        )
    if not locked and existing_mode is None and transport != "merged":
        raise ValueError(
            "legacy active cycle must complete or be reconciled to merged before explicit mode selection"
        )

    operation_mode.update(values)
    control.update({
        "execution_mode": values["execution_mode"],
        "cycle_start_visibility": values["cycle_start_visibility"],
        "mode_locked_for_cycle": True,
        "normal_completion_target": values["normal_cycle_completion_target"],
    })
    return current, state


def write_json(path: Path, value: dict[str, Any]) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-visibility", required=True, choices=sorted(VALID_VISIBILITIES))
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load(CONTRACT_PATH)
        current = load(CURRENT_PATH)
        state = load(STATE_PATH)
        current, state = apply_selection(current, state, contract, args.repository_visibility)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    values = selected_values(contract, args.repository_visibility)
    print(f"selected execution mode: {values['execution_mode']}")
    print(f"cycle start visibility: {values['cycle_start_visibility']}")
    if not args.write:
        print("DRY RUN: pass --write to update CURRENT_WORK and PRIVATE_STAGE_STATE")
        return 0

    try:
        write_json(CURRENT_PATH, current)
        write_json(STATE_PATH, state)
    except OSError as exc:
        print(f"ERROR: failed to write execution mode: {exc}")
        return 1
    print("OK: cycle execution mode is locked in both state authorities")
    return 0


if __name__ == "__main__":
    sys.exit(main())
