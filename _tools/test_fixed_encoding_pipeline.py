#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "fixed_encoding_pipeline.py"


def load_module():
    spec = importlib.util.spec_from_file_location("fixed_encoding_pipeline", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load fixed_encoding_pipeline")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
    assert module.audit_identity(Path("AUDIT_DECISIONS_YUWEN_MOWEN_TRAIN27_WAVE01_2026-07-29.json")) == (27, 1, "2026-07-29")
    broken = dict(decision)
    broken["keeps"] = []
    try:
        module.validate_decision(broken, candidate)
    except module.EncodingError as exc:
        assert "partition mismatch" in str(exc)
    else:
        raise AssertionError("missing keep must fail")
    print("test_fixed_encoding_pipeline: OK")


if __name__ == "__main__":
    main()
