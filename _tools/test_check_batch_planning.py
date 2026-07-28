#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_batch_planning.py"
def load_module():
    spec = importlib.util.spec_from_file_location("check_batch_planning", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def detail(rows: int, *, exception=None, adjacent=None):
    return {
        "scene_groups": ["demo"],
        "scene_flow": [{"scene": "demo", "focus_keys": [f"Demo_Index{i}_Text" for i in range(rows)]}],
        "batch_planning": {
            "mode": "detail_packet",
            "reviewed_rows": rows,
            "target_rows": {"min": 15, "max": 30},
            "adjacent_candidates_checked": adjacent or [],
            "grouping_decision": "detail grouping",
            "exception": exception,
        },
    }

def semantic(rows: int, *, exception=None):
    return {
        "schema_version": 6,
        "scene_groups": ["a", "b"],
        "reservation": {"status": "encoded"},
        "batch_planning": {
            "mode": "semantic_wave",
            "reviewed_rows": rows,
            "target_rows": {"min": 40, "max": 60},
            "hard_max": 80,
            "adjacent_candidates_checked": ["a", "b"],
            "grouping_decision": "二場面で意味単位が閉じる",
            "exception": exception,
        },
    }

def main():
    module = load_module()
    assert module.validate(detail(16)) == []
    assert module.validate(detail(7, adjacent=["next"], exception={"reason_code":"high_risk_scene","detail":"境界"})) == []
    assert module.validate(semantic(40)) == []
    assert module.validate(semantic(60)) == []
    assert module.validate(semantic(62, exception={"reason_code":"complete_semantic_unit","detail":"60行で実演直前に切れる"})) == []
    assert any("requires batch_planning.exception" in e for e in module.validate(semantic(62)))
    assert any("40..80" in e for e in module.validate(semantic(81, exception={"reason_code":"complete_semantic_unit","detail":"too large"})))
    minimal = {"schema_version":6,"reservation":{"status":"reserved_only"},"scene_groups":["demo"]}
    assert module.validate(minimal) == []
    print("test_check_batch_planning: OK")
if __name__ == "__main__":
    main()
