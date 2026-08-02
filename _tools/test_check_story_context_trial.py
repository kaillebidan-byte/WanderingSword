#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MODULE_PATH = HERE / "_tools" / "check_story_context_trial.py"
K1 = "CG表\x1fQuestDlgs\x1f13511_1_Dlgs_Index4_Text"
K2 = "CG表\x1fQuestDlgs\x1f13512_1_Dlgs_Index0_Text"
K3 = "CG表\x1fQuestDlgs\x1f12118_13_Dlgs_Index7_Text"


def module():
    spec = importlib.util.spec_from_file_location("check_story_context_trial", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load trial checker")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fixture(root: Path) -> None:
    for relative in (
        "_story_context/events/e.json",
        "_story_context/scene_context/e.json",
        "_story_context/spoiler_context/e.json",
        "_story_context/crosschecks/e.json",
    ):
        write(root / relative, {"fixture": relative})
    write(root / "_phase4_proofread/source_zh.json", {K1: "a", K2: "b", K3: "c"})
    trial = {
        "schema_version": 1,
        "trial_id": "phase1_doubt_resolution_quest_13511",
        "event_id": "quest_13511_fengming_staff",
        "mode": "read_only_phase1_simulation",
        "purpose": "fixture",
        "inputs": {
            "event_manifest": "_story_context/events/e.json",
            "scene_context": "_story_context/scene_context/e.json",
            "spoiler_context": "_story_context/spoiler_context/e.json",
            "crosscheck": "_story_context/crosschecks/e.json",
        },
        "cases": [
            {
                "case_id": "resolved",
                "doubt": "d",
                "scene_time_limit": "s",
                "crosschecked_resolution": "r",
                "outcome": "resolved",
                "phase1_use": "u",
                "source_keys": [K1, K2],
            },
            {
                "case_id": "preserved",
                "doubt": "d",
                "scene_time_limit": "s",
                "crosschecked_resolution": "r",
                "outcome": "preserve_ambiguity",
                "phase1_use": "u",
                "source_keys": [K3],
            },
        ],
        "result": {
            "resolved_cases": 1,
            "preserved_ambiguity_cases": 1,
            "source_citations_sufficient": True,
            "scene_spoiler_separation_sufficient": True,
            "downstream_crosscheck_sufficient": True,
            "phase1_doubt_resolution_trial_passed": True,
            "approved_reference_scope": "quest_13511_fengming_staff",
        },
        "non_interference": {
            "phase1_phase2_progress_mutation": "none",
            "translation_mutation": "none",
            "owner_write": "none",
            "locres_mutation": "none",
            "pak_mutation": "none",
            "game_verification_mutation": "none",
        },
        "completed_utc": "2026-08-02T02:28:00Z",
    }
    write(root / "_story_context/trials/trial.json", trial)
    state = {
        "current_stage": "reference_ready",
        "formal_reference": True,
        "active_event": "quest_13511_fengming_staff",
        "artifacts": {
            "event_manifest": "_story_context/events/e.json",
            "scene_context": "_story_context/scene_context/e.json",
            "spoiler_context": "_story_context/spoiler_context/e.json",
            "crosscheck": "_story_context/crosschecks/e.json",
            "doubt_resolution_trial": "_story_context/trials/trial.json",
        },
    }
    write(root / "_story_context/STATE.json", state)
    gate = {
        "status": "open",
        "formal_reference_allowed": True,
        "approved_event": "quest_13511_fengming_staff",
        "evidence": ["_story_context/trials/trial.json"],
        "approved_scope": {
            "event_id": "quest_13511_fengming_staff",
            "cross_event_inference_allowed": False,
            "speaker_asset_aliasing_allowed": False,
        },
    }
    write(root / "_story_context/REFERENCE_GATE.json", gate)


def main() -> None:
    checker = module()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        fixture(root)
        result = checker.validate(root)
        assert result["status"] == "ok"
        assert result["resolved_cases"] == 1
        assert result["preserved_ambiguity_cases"] == 1

        trial_path = root / "_story_context/trials/trial.json"
        trial = json.loads(trial_path.read_text(encoding="utf-8"))
        trial["cases"][1]["outcome"] = "resolved"
        trial["result"]["resolved_cases"] = 2
        trial["result"]["preserved_ambiguity_cases"] = 0
        write(trial_path, trial)
        try:
            checker.validate(root)
        except checker.TrialError as exc:
            assert "preserved ambiguity" in str(exc)
        else:
            raise AssertionError("missing preserved ambiguity was accepted")

        fixture(root)
        trial = json.loads(trial_path.read_text(encoding="utf-8"))
        trial["cases"][0]["source_keys"] = ["missing"]
        write(trial_path, trial)
        try:
            checker.validate(root)
        except checker.TrialError as exc:
            assert "unknown source key" in str(exc)
        else:
            raise AssertionError("unknown source key was accepted")

        fixture(root)
        trial = json.loads(trial_path.read_text(encoding="utf-8"))
        trial["non_interference"]["translation_mutation"] = "changed"
        write(trial_path, trial)
        try:
            checker.validate(root)
        except checker.TrialError as exc:
            assert "forbidden mutation" in str(exc)
        else:
            raise AssertionError("forbidden mutation was accepted")

    print("test_check_story_context_trial: OK")


if __name__ == "__main__":
    main()
