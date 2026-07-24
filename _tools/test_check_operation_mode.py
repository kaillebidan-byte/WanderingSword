#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_operation_mode のphase1互換とphase2単一PR最終化を検証する。"""
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


def sample_current(train_status="accumulating", declared="private_translation_work", phase="phase2"):
    phase2 = phase == "phase2"
    checks = [
        "relation_audit_success",
        "cross_register_success",
        "apply_curated_fixes_success",
        "zero_pending_fixes",
        "verified_checkpoint",
        "zero_unresolved_review_threads",
        "translation_pr_squash_merged",
    ]
    if phase2:
        checks += ["release_evidence_verified", "single_pr_state_finalized"]
    else:
        checks += ["post_merge_state_pr_squash_merged"]
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
            "public_ci_exit_checks": checks,
            "open_pr_only_after_ready": True,
            "draft_train_pr_allowed_while_private": True,
            "train_release_requires_manifest_ready": True,
            "public_translation_forbidden": True,
            "deep_failure_returns_private": True,
            "single_pr_finalization": phase2,
            "post_merge_state_pr_required": not phase2,
        },
        "ci_train": {
            "phase": "phase1_pilot",
            "finalization_phase": phase,
            "policy": (
                "_phase4_proofread/CI_TRAIN_PHASE2.md"
                if phase2
                else "_phase4_proofread/CI_TRAIN_PHASE1.md"
            ),
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
    assert module.resolve_effective_mode("ready_for_public_ci", "public") == "public_ci_window"

    assert module.validate_operation_mode(sample_current()) == []
    assert module.validate_operation_mode(sample_current(phase="phase1")) == []
    assert module.validate_operation_mode(
        sample_current("ready_for_public_ci", "ready_for_public_ci")
    ) == []

    bad = sample_current()
    bad["operation_mode"]["public_ci_exit_checks"].append("post_merge_state_pr_squash_merged")
    errors = module.validate_operation_mode(bad)
    assert any("must not require" in error for error in errors)

    bad = sample_current()
    bad["operation_mode"]["post_merge_state_pr_required"] = True
    errors = module.validate_operation_mode(bad)
    assert any("post_merge_state_pr_required=false" in error for error in errors)

    bad = sample_current("accumulating", "ready_for_public_ci")
    errors = module.validate_operation_mode(bad)
    assert any("accumulating train" in error for error in errors)

    print("test_check_operation_mode: OK")


if __name__ == "__main__":
    main()
