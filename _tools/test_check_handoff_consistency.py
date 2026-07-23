#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_handoff_consistency のcheckpoint判定を回帰検証する。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_handoff_consistency.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_handoff_consistency", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_handoff_consistency.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_module()

    errors: list[str] = []
    warnings: list[str] = []
    module.report_sync_mismatch(
        "record index mismatch",
        checkpoint_verified=True,
        errors=errors,
        warnings=warnings,
    )
    assert errors == ["record index mismatch"]
    assert warnings == []

    errors = []
    warnings = []
    module.report_sync_mismatch(
        "record index mismatch",
        checkpoint_verified=False,
        errors=errors,
        warnings=warnings,
    )
    assert errors == []
    assert warnings == ["TRANSITIONAL: record index mismatch"]

    assert module.VALID_CHECKPOINT_STATES == {"verified", "pending_audit_sync"}
    assert module.VALID_PR_TRIAGE_STATES == {"active", "superseded", "abandoned", "unrelated"}

    print("test_check_handoff_consistency: OK")


if __name__ == "__main__":
    main()
