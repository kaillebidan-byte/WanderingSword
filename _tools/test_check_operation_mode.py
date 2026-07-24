#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_operation_mode のphase1状態遷移を回帰検証する。"""
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


def sample_current(train_status="accumulating", declared="private_translation_work"):
    return {
        "operation_mode": {
            "declared_state": declared,
            "protocol": "_phase4_proofread/PUBLIC_CI_WINDOW.md",
            "actual_visibility_source": "github_repository_metadata",
            "visibility_change_actor": "user",
            "phrases": {
                "request_public": "公開CI窓を開いてください。",
                "confirm_public": "公開した",
                "request_private": "privateへ戻してください。",
                "confirm_private": "privateに戻した",
            },
            "public_ci_exit_checks": [
                "relation_audit_success",
                "cross_register_success",
                "apply_curated_fixes_success",
                "zero_pending_fixes",
                "verified_checkpoint",
                "zero_unresolved_review_threads",
                "translation_pr_squash_merged",
                "post_merge_state_pr_squash_merged",
            ],
            "open_pr_only_after_ready": True,
            "draft_train_pr_allowed_while_private": True,
            "train_release_requires_manifest_ready": True,
            "public_translation_forbidden": True,
            "deep_failure_returns_private": True,
        },
        "ci_train": {
            "phase": "phase1_pilot",
            "policy": "_phase4_proofread/CI_TRAIN_PHASE1.md",
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "train_id": "test-train",
            "branch": "agent/test-train",
            "status": train_status,
        },
    }


def main() -> None:
    module = load_module()

    assert module.resolve_effective_mode("private_translation_work", "private") == "private_translation_work"
    assert module.resolve_effective_mode("private_translation_work", "public") == "return_private_required"
    assert module.resolve_effective_mode("ready_for_public_ci", "private") == "ready_for_public_ci"
    assert module.resolve_effective_mode("ready_for_public_ci", "public") == "public_ci_window"
    assert module.resolve_effective_mode("public_ci_blocked", "private") == "public_ci_blocked"
    assert module.resolve_effective_mode("public_ci_blocked", "public") == "return_private_required"

    assert module.validate_operation_mode(sample_current()) == []
    assert module.validate_operation_mode(
        sample_current("ready_for_public_ci", "ready_for_public_ci")
    ) == []
    assert module.validate_operation_mode(
        sample_current("in_public_ci", "ready_for_public_ci")
    ) == []
    assert module.validate_operation_mode(
        sample_current("verified", "ready_for_public_ci")
    ) == []

    bad = sample_current("accumulating", "ready_for_public_ci")
    errors = module.validate_operation_mode(bad)
    assert any("accumulating train" in error for error in errors)

    bad = sample_current("ready_for_public_ci", "private_translation_work")
    errors = module.validate_operation_mode(bad)
    assert any("ready/in_public_ci train" in error for error in errors)

    broken = {"operation_mode": {"declared_state": "public_ci_window"}}
    errors = module.validate_operation_mode(broken)
    assert any("declared_state" in error for error in errors)
    assert any("ci_train" in error for error in errors)

    print("test_check_operation_mode: OK")


if __name__ == "__main__":
    main()
