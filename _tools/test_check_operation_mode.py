#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_operation_mode の状態遷移を回帰検証する。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_operation_mode.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_operation_mode", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_operation_mode.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_module()

    assert module.resolve_effective_mode("private_translation_work", "private") == "private_translation_work"
    assert module.resolve_effective_mode("private_translation_work", "public") == "return_private_required"
    assert module.resolve_effective_mode("ready_for_public_ci", "private") == "ready_for_public_ci"
    assert module.resolve_effective_mode("ready_for_public_ci", "public") == "public_ci_window"
    assert module.resolve_effective_mode("public_ci_blocked", "private") == "public_ci_blocked"
    assert module.resolve_effective_mode("public_ci_blocked", "public") == "return_private_required"
    assert module.resolve_effective_mode("private_translation_work", None) == "private_translation_work"

    assert module.VALID_DECLARED_STATES == {
        "private_translation_work",
        "ready_for_public_ci",
        "public_ci_blocked",
    }
    assert module.VALID_DERIVED_STATES == {"public_ci_window", "return_private_required"}

    current = {
        "operation_mode": {
            "declared_state": "private_translation_work",
            "protocol": "_phase4_proofread/PUBLIC_CI_WINDOW.md",
            "actual_visibility_source": "github_repository_metadata",
            "visibility_change_actor": "user",
            "phrases": {
                "request_public": "公開CI窓を開いてください。",
                "confirm_public": "公開した",
                "request_private": "privateへ戻してください。",
                "confirm_private": "privateに戻した",
            },
            "public_ci_exit_checks": sorted(module.REQUIRED_COMPLETION_CHECKS),
            "open_pr_only_after_ready": True,
            "public_translation_forbidden": True,
            "deep_failure_returns_private": True,
        }
    }
    assert module.validate_operation_mode(current) == []

    broken = {"operation_mode": {"declared_state": "public_ci_window"}}
    errors = module.validate_operation_mode(broken)
    assert any("declared_state" in error for error in errors)
    assert any("protocol" in error for error in errors)

    print("test_check_operation_mode: OK")


if __name__ == "__main__":
    main()
