#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_operation_modeの手動往復・常時public・legacy移行を検証する。"""
from __future__ import annotations

import copy
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


def contract() -> dict:
    return {
        "supported_modes": ["manual_visibility_cycle", "always_public_full_pipeline"],
        "mode_selection_source": "repository_visibility_at_cycle_start",
        "selection": {
            "private": "manual_visibility_cycle",
            "public": "always_public_full_pipeline",
        },
        "lock": {
            "scope": "cycle",
            "may_change_only_when_previous_transport_is": "merged",
        },
        "shared_pipeline": {
            "stage_permissions_remain_authoritative": True,
        },
    }


def sample_current(
    train_status="verified",
    declared="translation_frozen",
    phase="phase2",
    execution_mode="manual_visibility_cycle",
    explicit=True,
):
    phase2 = phase == "phase2"
    manual = execution_mode == "manual_visibility_cycle"
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
    mode = {
        "declared_state": declared,
        "protocol": (
            "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md"
            if declared == "translation_frozen"
            else "_phase4_proofread/PUBLIC_CI_WINDOW.md"
        ),
        "actual_visibility_source": "github_repository_metadata",
        "visibility_change_actor": "user" if manual else "none",
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
        "public_translation_forbidden": manual,
        "deep_failure_returns_private": manual,
        "single_pr_finalization": phase2,
        "post_merge_state_pr_required": not phase2,
    }
    if explicit:
        mode.update({
            "execution_mode": execution_mode,
            "cycle_start_visibility": "private" if manual else "public",
            "mode_locked_for_cycle": True,
            "visibility_change_required": manual,
            "visibility_change_requests_forbidden": not manual,
            "stage_permissions_are_authoritative": True,
            "normal_cycle_completion_target": "visibility_boundary_or_merged" if manual else "merged",
        })
    return {
        "operation_mode": mode,
        "ci_train": {
            "phase": "phase1_wave",
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
            "transport_status": "merged" if train_status == "verified" else "not_ready",
        },
    }


def main() -> None:
    module = load_module()
    c = contract()

    assert module.resolve_effective_mode("private_translation_work", "private") == "private_translation_work"
    assert module.resolve_effective_mode("private_translation_work", "public") == "return_private_required"
    assert module.resolve_effective_mode("translation_frozen", "private") == "translation_frozen"
    assert module.resolve_effective_mode("translation_frozen", "public") == "public_ci_window"
    assert module.resolve_effective_mode(
        "private_translation_work", "public", "always_public_full_pipeline"
    ) == "always_public_translation_work"
    assert module.resolve_effective_mode(
        "translation_frozen", "public", "always_public_full_pipeline"
    ) == "public_ci_window"
    assert module.resolve_effective_mode(
        "private_translation_work", "private", "always_public_full_pipeline"
    ) == "return_public_required"

    assert module.validate_operation_mode(sample_current(), c) == []
    assert module.validate_operation_mode(sample_current(explicit=False), c) == []
    assert module.validate_operation_mode(sample_current(phase="phase1"), c) == []
    assert module.validate_operation_mode(
        sample_current(execution_mode="always_public_full_pipeline"), c
    ) == []
    assert module.validate_operation_mode(
        sample_current("ready_for_public_ci", "translation_frozen"), c
    ) == []
    assert module.validate_operation_mode(
        sample_current("in_public_ci", "translation_frozen"), c
    ) == []

    bad = sample_current(execution_mode="always_public_full_pipeline")
    bad["operation_mode"]["public_translation_forbidden"] = True
    errors = module.validate_operation_mode(bad, c)
    assert any("public_translation_forbidden" in error for error in errors)

    bad = sample_current(execution_mode="always_public_full_pipeline")
    bad["operation_mode"]["cycle_start_visibility"] = "private"
    errors = module.validate_operation_mode(bad, c)
    assert any("cycle_start_visibility" in error for error in errors)

    bad = sample_current()
    bad["operation_mode"]["public_ci_exit_checks"].append("post_merge_state_pr_squash_merged")
    errors = module.validate_operation_mode(bad, c)
    assert any("must not require" in error for error in errors)

    bad = sample_current()
    bad["operation_mode"]["post_merge_state_pr_required"] = True
    errors = module.validate_operation_mode(bad, c)
    assert any("post_merge_state_pr_required=false" in error for error in errors)

    bad = sample_current("accumulating", "translation_frozen")
    bad["operation_mode"]["protocol"] = "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md"
    errors = module.validate_operation_mode(bad, c)
    assert any("accumulating train" in error for error in errors)

    bad = sample_current("ready_for_public_ci", "ready_for_public_ci")
    errors = module.validate_operation_mode(bad, c)
    assert any("requires translation_frozen" in error for error in errors)

    bad = copy.deepcopy(sample_current())
    bad["ci_train"]["phase"] = "phase1_pilot"
    errors = module.validate_operation_mode(bad, c)
    assert any("phase1_wave" in error for error in errors)

    broken_contract = copy.deepcopy(c)
    broken_contract["selection"]["public"] = "manual_visibility_cycle"
    errors = module.validate_operation_mode(sample_current(), broken_contract)
    assert any("selection mismatch" in error for error in errors)

    print("test_check_operation_mode: OK")


if __name__ == "__main__":
    main()
