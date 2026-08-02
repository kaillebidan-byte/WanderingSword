#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the read-only Phase 1 doubt-resolution trial and reference approval scope."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE = Path("_story_context/STATE.json")
GATE = Path("_story_context/REFERENCE_GATE.json")
SOURCE = Path("_phase4_proofread/source_zh.json")
TRIAL_ARTIFACT = "doubt_resolution_trial"


class TrialError(ValueError):
    pass


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TrialError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise TrialError(f"invalid JSON: {path}: {exc}") from exc


def obj(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TrialError(f"{label} must be an object")
    return value


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrialError(f"{label} must be a non-empty string")
    return value


def strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise TrialError(f"{label} must be a non-empty string array")
    if len(value) != len(set(value)):
        raise TrialError(f"{label} contains duplicates")
    return list(value)


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    state = obj(load(root / STATE), "state")
    gate = obj(load(root / GATE), "gate")
    stage = state.get("current_stage")

    if stage != "reference_ready":
        if state.get("formal_reference") is not False:
            raise TrialError("formal_reference must remain false before reference_ready")
        if gate.get("status") != "closed" or gate.get("formal_reference_allowed") is not False:
            raise TrialError("reference gate must remain closed before reference_ready")
        return {"status": "not_ready", "current_stage": stage}

    if state.get("formal_reference") is not True:
        raise TrialError("reference_ready requires formal_reference true")
    event_id = text(state.get("active_event"), "active_event")
    artifacts = obj(state.get("artifacts"), "state.artifacts")
    trial_relative = text(artifacts.get(TRIAL_ARTIFACT), TRIAL_ARTIFACT)
    trial = obj(load(root / trial_relative), "trial")
    source = obj(load(root / SOURCE), "source index")

    if trial.get("schema_version") != 1:
        raise TrialError("trial schema_version mismatch")
    if trial.get("trial_id") != "phase1_doubt_resolution_quest_13511":
        raise TrialError("trial identity mismatch")
    if trial.get("event_id") != event_id:
        raise TrialError("trial event does not match active_event")
    if trial.get("mode") != "read_only_phase1_simulation":
        raise TrialError("trial mode must be read-only simulation")

    inputs = obj(trial.get("inputs"), "trial.inputs")
    expected_inputs = {
        "event_manifest": artifacts.get("event_manifest"),
        "scene_context": artifacts.get("scene_context"),
        "spoiler_context": artifacts.get("spoiler_context"),
        "crosscheck": artifacts.get("crosscheck"),
    }
    if inputs != expected_inputs:
        raise TrialError("trial inputs do not match state artifacts")
    for relative in inputs.values():
        if not isinstance(relative, str) or not (root / relative).is_file():
            raise TrialError(f"trial input missing: {relative}")

    cases = trial.get("cases")
    if not isinstance(cases, list) or len(cases) < 2:
        raise TrialError("trial must contain multiple doubt cases")
    outcomes: list[str] = []
    case_ids: set[str] = set()
    for index, raw in enumerate(cases):
        case = obj(raw, f"cases[{index}]")
        case_id = text(case.get("case_id"), "case_id")
        if case_id in case_ids:
            raise TrialError(f"duplicate case_id: {case_id}")
        case_ids.add(case_id)
        for key in ("doubt", "scene_time_limit", "crosschecked_resolution", "phase1_use"):
            text(case.get(key), f"{case_id}.{key}")
        outcome = case.get("outcome")
        if outcome not in {"resolved", "preserve_ambiguity"}:
            raise TrialError(f"invalid outcome: {case_id}")
        outcomes.append(outcome)
        for source_key in strings(case.get("source_keys"), f"{case_id}.source_keys"):
            if source_key not in source:
                raise TrialError(f"unknown source key in trial: {source_key}")

    if "resolved" not in outcomes or "preserve_ambiguity" not in outcomes:
        raise TrialError("trial must demonstrate both resolution and preserved ambiguity")

    result = obj(trial.get("result"), "trial.result")
    if result.get("resolved_cases") != outcomes.count("resolved"):
        raise TrialError("resolved case count mismatch")
    if result.get("preserved_ambiguity_cases") != outcomes.count("preserve_ambiguity"):
        raise TrialError("preserved ambiguity count mismatch")
    for key in (
        "source_citations_sufficient",
        "scene_spoiler_separation_sufficient",
        "downstream_crosscheck_sufficient",
        "phase1_doubt_resolution_trial_passed",
    ):
        if result.get(key) is not True:
            raise TrialError(f"trial sufficiency failed: {key}")
    if result.get("approved_reference_scope") != event_id:
        raise TrialError("approved trial scope mismatch")

    non_interference = obj(trial.get("non_interference"), "trial.non_interference")
    required_mutations = {
        "phase1_phase2_progress_mutation",
        "translation_mutation",
        "owner_write",
        "locres_mutation",
        "pak_mutation",
        "game_verification_mutation",
    }
    if set(non_interference) != required_mutations:
        raise TrialError("trial non-interference fields mismatch")
    if any(value != "none" for value in non_interference.values()):
        raise TrialError("trial recorded a forbidden mutation")

    if gate.get("status") != "open" or gate.get("formal_reference_allowed") is not True:
        raise TrialError("reference gate is not open at reference_ready")
    if gate.get("approved_event") != event_id:
        raise TrialError("gate approved_event mismatch")
    evidence = strings(gate.get("evidence"), "gate.evidence")
    if trial_relative not in evidence:
        raise TrialError("gate evidence omits doubt-resolution trial")
    scope = obj(gate.get("approved_scope"), "gate.approved_scope")
    if scope.get("event_id") != event_id or scope.get("cross_event_inference_allowed") is not False:
        raise TrialError("gate scope is not event-bounded")
    if scope.get("speaker_asset_aliasing_allowed") is not False:
        raise TrialError("gate must forbid unsupported speaker asset aliasing")

    return {
        "status": "ok",
        "current_stage": stage,
        "event_id": event_id,
        "trial": trial_relative,
        "resolved_cases": outcomes.count("resolved"),
        "preserved_ambiguity_cases": outcomes.count("preserve_ambiguity"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except (OSError, TrialError) as exc:
        print(json.dumps({"status": "blocked", "detail": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
