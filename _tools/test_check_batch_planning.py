#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_batch_planningの回帰テスト。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_batch_planning.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_batch_planning", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_batch_planning.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def packet(rows: int, *, exception=None, adjacent=None) -> dict:
    return {
        "scene_groups": ["demo"],
        "scene_flow": [
            {
                "scene": "demo",
                "focus_keys": [f"Demo_Index{i}_Text" for i in range(rows)],
            }
        ],
        "batch_planning": {
            "reviewed_rows": rows,
            "target_rows": {"min": 15, "max": 30},
            "adjacent_candidates_checked": adjacent or [],
            "grouping_decision": "test grouping",
            "exception": exception,
        },
    }


def main() -> None:
    module = load_module()

    assert module.validate(packet(16)) == []

    errors = module.validate(packet(7))
    assert any("requires batch_planning.exception" in error for error in errors)
    assert any("requires adjacent_candidates_checked" in error for error in errors)

    valid_small = packet(
        7,
        adjacent=["next_scene"],
        exception={
            "reason_code": "high_risk_scene",
            "detail": "分岐境界と重大な事実疑義があり単独監査する",
        },
    )
    assert module.validate(valid_small) == []

    mismatch = packet(16)
    mismatch["batch_planning"]["reviewed_rows"] = 15
    assert any("reviewed_rows mismatch" in error for error in module.validate(mismatch))

    weakened = packet(16)
    weakened["batch_planning"]["target_rows"] = {"min": 5, "max": 30}
    assert any("target_rows must be fixed" in error for error in module.validate(weakened))

    minimal = {
        "schema_version": 6,
        "reservation": {"status": "reserved_only"},
        "scene_groups": ["demo"],
    }
    assert module.validate(minimal) == []
    assert module.is_minimal_reservation(minimal)

    print("test_check_batch_planning: OK")


if __name__ == "__main__":
    main()
