#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "fixed_encoding_pipeline.py"
CONTROL_BEFORE = 'speaker_01$@$<Y>原文 {0}</>#nl次の行\r\n終端'


def load_module():
    spec = importlib.util.spec_from_file_location("fixed_encoding_pipeline", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load fixed_encoding_pipeline")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def control_payload(after: str) -> tuple[dict, dict]:
    candidate = {
        "scene_groups": ["control_fixture"],
        "rows": [{"key": "Control_Index0_Text", "ja": CONTROL_BEFORE}],
    }
    decision = {
        "status": "audited",
        "scene_groups": ["control_fixture"],
        "fixes": [
            {
                "key": "Control_Index0_Text",
                "before": CONTROL_BEFORE,
                "after": after,
                "reason": "control regression",
            }
        ],
        "keeps": [],
    }
    return decision, candidate


def assert_control_rejected(module, after: str, expected: str) -> None:
    decision, candidate = control_payload(after)
    try:
        module.validate_decision(decision, candidate)
    except module.EncodingError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"expected rejection: {expected}")


def main() -> None:
    module = load_module()
    candidate = {
        "scene_groups": ["demo"],
        "rows": [
            {"key": "Demo_Index0_Text", "ja": "before"},
            {"key": "Demo_Index1_Text", "ja": "keep"},
        ],
    }
    decision = {
        "status": "audited",
        "scene_groups": ["demo"],
        "fixes": [{"key": "Demo_Index0_Text", "before": "before", "after": "after", "reason": "meaning"}],
        "keeps": ["Demo_Index1_Text"],
        "allusion_review_candidates": [],
        "allusion_review_resolved": [],
        "fact_doubts": [],
    }
    result = module.validate_decision(decision, candidate)
    assert result["fix_map"] == {"Demo_Index0_Text": "after"}
    assert result["keeps"] == ["Demo_Index1_Text"]
    assert module.identity(Path("AUDIT_DECISIONS_YUWEN_MOWEN_TRAIN27_WAVE01_2026-07-29.json")) == (27, 1, "2026-07-29")
    broken = dict(decision)
    broken["keeps"] = []
    try:
        module.validate_decision(broken, candidate)
    except module.EncodingError as exc:
        assert "partition mismatch" in str(exc)
    else:
        raise AssertionError("missing keep must fail")

    valid = 'speaker_01$@$<Y>修正文 {0}</>#nl続き\r\n終端'
    control_decision, control_candidate = control_payload(valid)
    control_result = module.validate_decision(control_decision, control_candidate)
    assert control_result["fix_map"] == {"Control_Index0_Text": valid}

    assert_control_rejected(module, 'speaker_02$@$<Y>修正文 {0}</>#nl続き\r\n終端', "speaker/control prefix changed")
    assert_control_rejected(module, '<Y>修正文 {0}</>#nl続き\r\n終端', "speaker delimiter changed")
    assert_control_rejected(module, 'speaker_01$@$修正文 {0}</>#nl続き\r\n終端', "control token sequence changed")
    assert_control_rejected(module, 'speaker_01$@$<Y><B>修正文 {0}</>#nl続き\r\n終端', "control token sequence changed")
    assert_control_rejected(module, 'speaker_01$@$<Y>修正文</> {0}#nl続き\r\n終端', "control token sequence changed")
    assert_control_rejected(module, 'speaker_01$@$<Y>修正文 {1}</>#nl続き\r\n終端', "control token sequence changed")
    assert_control_rejected(module, 'speaker_01$@$<Y>修正文 {0}</>#nl続き\n終端', "control token sequence changed")

    print("test_fixed_encoding_pipeline: OK")


if __name__ == "__main__":
    main()
