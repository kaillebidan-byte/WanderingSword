#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail closed when the declared story-context artifact layout drifts from the live tree."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = Path("_story_context/STORY_CONTEXT_PREPARATION_CONTRACT.json")
STATE = Path("_story_context/STATE.json")

EXPECTED_PATH_FIELDS = {
    "checker": "_tools/check_story_context_layer.py",
    "regression_test": "_tools/test_check_story_context_layer.py",
    "contract_path_checker": "_tools/check_story_context_contract_paths.py",
    "contract_path_regression_test": "_tools/test_check_story_context_contract_paths.py",
    "candidate_extractor": "_tools/build_story_context_candidates.py",
    "candidate_regression_test": "_tools/test_build_story_context_candidates.py",
    "trial_checker": "_tools/check_story_context_trial.py",
    "trial_regression_test": "_tools/test_check_story_context_trial.py",
    "contract_workflow": ".github/workflows/story-context-bootstrap.yml",
}

EXPECTED_STAGE_ARTIFACTS = {
    "investigated": ["_story_context/INVESTIGATION_2026-08-02.md"],
    "contract_ready": [
        "_story_context/STORY_CONTEXT_PREPARATION_CONTRACT.json",
        "_story_context/PHASE_BASELINE.json",
        "_story_context/STATE.json",
        "_story_context/REFERENCE_GATE.json",
        "_story_context/schemas/candidate_inventory.schema.json",
        "_story_context/schemas/event_manifest.schema.json",
        "_story_context/schemas/scene_context.schema.json",
        "_story_context/schemas/spoiler_context.schema.json",
        "_tools/build_story_context_candidates.py",
        "_tools/test_build_story_context_candidates.py",
        "_tools/check_story_context_layer.py",
        "_tools/test_check_story_context_layer.py",
        "_tools/check_story_context_contract_paths.py",
        "_tools/test_check_story_context_contract_paths.py",
        "_tools/check_story_context_trial.py",
        "_tools/test_check_story_context_trial.py",
        ".github/workflows/story-context-bootstrap.yml",
    ],
    "candidate_inventory_ready": ["_story_context/candidates/*.json"],
    "event_manifest_ready": ["_story_context/events/*/event_manifest.json"],
    "scene_context_ready": ["_story_context/scene_context/*.json"],
    "spoiler_context_ready": ["_story_context/spoiler_context/*.json"],
    "crosschecked": ["_story_context/crosschecks/*.json"],
    "reference_ready": [
        "_story_context/trials/*.json",
        "_story_context/REFERENCE_GATE.json",
    ],
}

ARTIFACT_STAGE = {
    "candidate_inventory": "candidate_inventory_ready",
    "event_manifest": "event_manifest_ready",
    "scene_context": "scene_context_ready",
    "spoiler_context": "spoiler_context_ready",
    "crosscheck": "crosschecked",
    "doubt_resolution_trial": "reference_ready",
}


class ContractPathError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractPathError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractPathError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractPathError(f"JSON root must be an object: {path}")
    return value


def validate_contract_shape(contract: dict[str, Any]) -> None:
    for field, expected in EXPECTED_PATH_FIELDS.items():
        if contract.get(field) != expected:
            raise ContractPathError(f"contract path mismatch: {field}")
    if contract.get("stage_artifacts") != EXPECTED_STAGE_ARTIFACTS:
        raise ContractPathError("stage_artifacts mismatch")


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    contract = load(root / CONTRACT)
    state = load(root / STATE)
    validate_contract_shape(contract)

    for stage, patterns in EXPECTED_STAGE_ARTIFACTS.items():
        for pattern in patterns:
            if not list(root.glob(pattern)):
                raise ContractPathError(f"declared stage artifact missing: {stage}: {pattern}")

    stage_order = contract.get("stage_order")
    if not isinstance(stage_order, list) or state.get("current_stage") not in stage_order:
        raise ContractPathError("state stage is not declared")
    current_index = stage_order.index(state["current_stage"])
    artifacts = state.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ContractPathError("state.artifacts must be an object")

    for artifact_name, stage in ARTIFACT_STAGE.items():
        stage_index = stage_order.index(stage)
        artifact_path = artifacts.get(artifact_name)
        if current_index >= stage_index:
            if not isinstance(artifact_path, str) or not matches(
                artifact_path, EXPECTED_STAGE_ARTIFACTS[stage]
            ):
                raise ContractPathError(
                    f"state artifact path is outside declared stage layout: {artifact_name}"
                )
            if not (root / artifact_path).is_file():
                raise ContractPathError(f"state artifact missing: {artifact_path}")
        elif artifact_path is not None:
            raise ContractPathError(f"state artifact declared before stage: {artifact_name}")

    return {
        "status": "ok",
        "current_stage": state["current_stage"],
        "validated_stage_count": len(EXPECTED_STAGE_ARTIFACTS),
        "validated_path_fields": len(EXPECTED_PATH_FIELDS),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except (OSError, ContractPathError) as exc:
        print(json.dumps({"status": "blocked", "detail": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
