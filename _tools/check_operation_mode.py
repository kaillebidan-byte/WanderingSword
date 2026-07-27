#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳段階、CI輸送、phase2最終化とcycle実行モードを検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
EXECUTION_CONTRACT_PATH = P4 / "EXECUTION_MODES.json"
VALID_DECLARED_STATES = {"private_translation_work", "translation_frozen", "ready_for_public_ci", "public_ci_blocked"}
VALID_VISIBILITIES = {"private", "public"}
VALID_EXECUTION_MODES = {"manual_visibility_cycle", "always_public_full_pipeline"}
MODE_START_VISIBILITY = {
    "manual_visibility_cycle": "private",
    "always_public_full_pipeline": "public",
}
VALID_TRAIN_STATUSES = {"accumulating", "ready_for_public_ci", "in_public_ci", "verified", "aborted"}
PUBLIC_PROTOCOL = "_phase4_proofread/PUBLIC_CI_WINDOW.md"
FROZEN_PROTOCOL = "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md"
EXPECTED_TRAIN_MANIFEST = "_phase4_proofread/CI_TRAIN_MANIFEST.json"
EXPECTED_VISIBILITY_SOURCE = "github_repository_metadata"
PHASE1_POLICY = "_phase4_proofread/CI_TRAIN_PHASE1.md"
PHASE2_POLICY = "_phase4_proofread/CI_TRAIN_PHASE2.md"
PHASE1_COMPLETION_CHECKS = {
    "relation_audit_success", "cross_register_success", "apply_curated_fixes_success",
    "zero_pending_fixes", "verified_checkpoint", "zero_unresolved_review_threads",
    "translation_pr_squash_merged", "post_merge_state_pr_squash_merged",
}
PHASE2_COMPLETION_CHECKS = {
    "relation_audit_success", "cross_register_success", "apply_curated_fixes_success",
    "zero_pending_fixes", "release_evidence_verified", "single_pr_state_finalized",
    "verified_checkpoint", "zero_unresolved_review_threads", "translation_pr_squash_merged",
}


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def validate_execution_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(contract.get("supported_modes", [])) != VALID_EXECUTION_MODES:
        errors.append("EXECUTION_MODES.supported_modes mismatch")
    if contract.get("mode_selection_source") != "repository_visibility_at_cycle_start":
        errors.append("EXECUTION_MODES.mode_selection_source mismatch")
    if contract.get("selection") != {
        "private": "manual_visibility_cycle",
        "public": "always_public_full_pipeline",
    }:
        errors.append("EXECUTION_MODES.selection mismatch")
    lock = contract.get("lock")
    if not isinstance(lock, dict):
        errors.append("EXECUTION_MODES.lock must be an object")
    else:
        if lock.get("scope") != "cycle":
            errors.append("EXECUTION_MODES.lock.scope must be cycle")
        if lock.get("may_change_only_when_previous_transport_is") != "merged":
            errors.append("EXECUTION_MODES mode changes must require previous transport=merged")
    shared = contract.get("shared_pipeline")
    if not isinstance(shared, dict) or shared.get("stage_permissions_remain_authoritative") is not True:
        errors.append("EXECUTION_MODES shared stage permissions must remain authoritative")
    return errors


def resolve_execution_mode(mode: dict[str, Any]) -> tuple[str, bool]:
    """Return execution mode and whether it was explicitly locked in state."""
    explicit = mode.get("execution_mode")
    if explicit is None:
        return "manual_visibility_cycle", False
    return str(explicit), True


def resolve_effective_mode(
    declared_state: str,
    visibility: str | None,
    execution_mode: str = "manual_visibility_cycle",
) -> str:
    if visibility is None:
        return declared_state
    if visibility not in VALID_VISIBILITIES:
        raise ValueError(f"unsupported repository visibility: {visibility}")
    if execution_mode not in VALID_EXECUTION_MODES:
        raise ValueError(f"unsupported execution mode: {execution_mode}")

    if execution_mode == "always_public_full_pipeline":
        if visibility != "public":
            return "return_public_required"
        if declared_state in {"translation_frozen", "ready_for_public_ci"}:
            return "public_ci_window"
        if declared_state == "private_translation_work":
            return "always_public_translation_work"
        return declared_state

    if declared_state in {"translation_frozen", "ready_for_public_ci"} and visibility == "public":
        return "public_ci_window"
    if declared_state in {"private_translation_work", "public_ci_blocked"} and visibility == "public":
        return "return_private_required"
    return declared_state


def validate_effective_visibility(effective: str) -> list[str]:
    if effective == "return_private_required":
        return ["repository visibility is incompatible with manual_visibility_cycle"]
    if effective == "return_public_required":
        return ["repository visibility is incompatible with always_public_full_pipeline"]
    return []


def validate_operation_mode(
    current: dict[str, Any],
    execution_contract: dict[str, Any] | None = None,
) -> list[str]:
    errors = validate_execution_contract(execution_contract) if execution_contract is not None else []
    mode = current.get("operation_mode")
    if not isinstance(mode, dict):
        return errors + ["CURRENT_WORK.operation_mode must be an object"]

    execution_mode, explicit_mode = resolve_execution_mode(mode)
    if execution_mode not in VALID_EXECUTION_MODES:
        errors.append("operation_mode.execution_mode must be one of " + ", ".join(sorted(VALID_EXECUTION_MODES)))
        execution_mode = "manual_visibility_cycle"

    if explicit_mode:
        expected_start_visibility = MODE_START_VISIBILITY[execution_mode]
        if mode.get("cycle_start_visibility") != expected_start_visibility:
            errors.append(f"operation_mode.cycle_start_visibility must be {expected_start_visibility!r}")
        if mode.get("mode_locked_for_cycle") is not True:
            errors.append("operation_mode.mode_locked_for_cycle must be true")

    declared = mode.get("declared_state")
    if declared not in VALID_DECLARED_STATES:
        errors.append("operation_mode.declared_state must be one of " + ", ".join(sorted(VALID_DECLARED_STATES)))
    expected_protocol = FROZEN_PROTOCOL if declared == "translation_frozen" else PUBLIC_PROTOCOL
    protocol = mode.get("protocol")
    if protocol != expected_protocol:
        errors.append(f"operation_mode.protocol must be {expected_protocol!r}")
    elif not (ROOT / protocol).is_file():
        errors.append(f"operation mode protocol does not exist: {protocol}")

    if mode.get("actual_visibility_source") != EXPECTED_VISIBILITY_SOURCE:
        errors.append("operation_mode.actual_visibility_source is invalid")

    manual = execution_mode == "manual_visibility_cycle"
    if explicit_mode:
        expected_actor = "user" if manual else "none"
        expected_completion = "visibility_boundary_or_merged" if manual else "merged"
        expected_values = {
            "visibility_change_actor": expected_actor,
            "visibility_change_required": manual,
            "visibility_change_requests_forbidden": not manual,
            "public_translation_forbidden": manual,
            "deep_failure_returns_private": manual,
            "stage_permissions_are_authoritative": True,
            "normal_cycle_completion_target": expected_completion,
        }
        for key, expected in expected_values.items():
            if mode.get(key) != expected:
                errors.append(f"operation_mode.{key} must be {expected!r}")
    else:
        if mode.get("visibility_change_actor") != "user":
            errors.append("legacy manual mode requires visibility_change_actor='user'")
        if mode.get("public_translation_forbidden") is not True:
            errors.append("legacy manual mode requires public_translation_forbidden=true")
        if mode.get("deep_failure_returns_private") is not True:
            errors.append("legacy manual mode requires deep_failure_returns_private=true")

    phrases = mode.get("phrases")
    if not isinstance(phrases, dict):
        errors.append("operation_mode.phrases must be an object")
    else:
        for key in ("request_public", "confirm_public", "request_private", "confirm_private"):
            if not isinstance(phrases.get(key), str) or not phrases.get(key, "").strip():
                errors.append(f"operation_mode.phrases.{key} must be non-empty")

    train = current.get("ci_train")
    if not isinstance(train, dict):
        return errors + ["CURRENT_WORK.ci_train must be an object"]
    finalization_phase = train.get("finalization_phase", "phase1")
    if finalization_phase not in {"phase1", "phase2"}:
        errors.append("ci_train.finalization_phase must be phase1 or phase2")
        finalization_phase = "phase1"
    required_checks = PHASE2_COMPLETION_CHECKS if finalization_phase == "phase2" else PHASE1_COMPLETION_CHECKS
    checks = mode.get("public_ci_exit_checks")
    if not isinstance(checks, list) or any(not isinstance(item, str) for item in checks):
        errors.append("operation_mode.public_ci_exit_checks must be a string list")
    else:
        missing = sorted(required_checks - set(checks))
        if missing:
            errors.append(f"operation_mode.public_ci_exit_checks missing: {missing!r}")
        if finalization_phase == "phase2" and "post_merge_state_pr_squash_merged" in checks:
            errors.append("phase2 must not require post_merge_state_pr_squash_merged")

    for key in ("open_pr_only_after_ready", "draft_train_pr_allowed_while_private", "train_release_requires_manifest_ready"):
        if mode.get(key) is not True:
            errors.append(f"operation_mode.{key} must be true")
    if finalization_phase == "phase2":
        if mode.get("single_pr_finalization") is not True:
            errors.append("phase2 requires operation_mode.single_pr_finalization=true")
        if mode.get("post_merge_state_pr_required") is not False:
            errors.append("phase2 requires operation_mode.post_merge_state_pr_required=false")
    elif mode.get("post_merge_state_pr_required") is False:
        errors.append("phase1 cannot disable post_merge_state_pr_required")

    if train.get("phase") != "phase1_wave":
        errors.append("ci_train.phase must be phase1_wave")
    expected_policy = PHASE2_POLICY if finalization_phase == "phase2" else PHASE1_POLICY
    if train.get("policy") != expected_policy:
        errors.append(f"ci_train.policy must be {expected_policy!r}")
    elif not (ROOT / expected_policy).is_file():
        errors.append(f"CI train policy does not exist: {expected_policy}")
    if train.get("manifest") != EXPECTED_TRAIN_MANIFEST:
        errors.append(f"ci_train.manifest must be {EXPECTED_TRAIN_MANIFEST!r}")
    elif not (ROOT / EXPECTED_TRAIN_MANIFEST).is_file():
        errors.append(f"CI train manifest does not exist: {EXPECTED_TRAIN_MANIFEST}")
    if not isinstance(train.get("train_id"), str) or not train.get("train_id"):
        errors.append("ci_train.train_id must be non-empty")
    if not isinstance(train.get("branch"), str) or not train.get("branch", "").startswith("agent/"):
        errors.append("ci_train.branch must be an agent/* branch")
    train_status = train.get("status")
    if train_status not in VALID_TRAIN_STATUSES:
        errors.append(f"ci_train.status must be one of {sorted(VALID_TRAIN_STATUSES)!r}")
    if not explicit_mode and (declared == "private_translation_work" or train_status == "accumulating"):
        errors.append("new translation cycle requires explicit execution_mode selection")
    if train_status == "accumulating" and declared != "private_translation_work":
        errors.append("accumulating train requires private_translation_work")
    if train_status in {"ready_for_public_ci", "in_public_ci"} and declared != "translation_frozen":
        errors.append("ready/in_public_ci train requires translation_frozen")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-visibility", choices=sorted(VALID_VISIBILITIES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_object(CURRENT_PATH)
    contract = load_object(EXECUTION_CONTRACT_PATH)
    errors = validate_operation_mode(current, contract)
    mode = current.get("operation_mode", {})
    train = current.get("ci_train", {})
    declared = str(mode.get("declared_state", ""))
    execution_mode, explicit_mode = resolve_execution_mode(mode)
    effective = (
        resolve_effective_mode(declared, args.repository_visibility, execution_mode)
        if declared in VALID_DECLARED_STATES and execution_mode in VALID_EXECUTION_MODES
        else "invalid"
    )
    errors.extend(validate_effective_visibility(effective))
    print("=== Operation mode ===")
    print(f"execution mode: {execution_mode}{'' if explicit_mode else ' (legacy inferred)'}")
    print(f"declared state: {declared}")
    print(f"repository visibility: {args.repository_visibility or 'not supplied'}")
    print(f"effective state: {effective}")
    print(f"CI train: {train.get('train_id')} / {train.get('status')} / transport={train.get('transport_status')}")
    print(f"finalization: {train.get('finalization_phase', 'phase1')}")
    if effective == "return_private_required":
        print("ACTION REQUIRED: manual public CI is not active; return the repository to private")
    elif effective == "return_public_required":
        print("ACTION REQUIRED: always-public mode is locked; restore public visibility")
    elif effective == "public_ci_window":
        print("OK WINDOW: translation remains frozen; run CI and integration only")
    elif effective == "public_ci_blocked":
        print("BLOCKED: preserve the locked execution mode and repair from the recorded checkpoint")
    elif effective == "private_translation_work":
        print("OK PRIVATE: continue the active private stage")
    elif effective == "always_public_translation_work":
        print("OK ALWAYS PUBLIC: continue the private cognitive stage on the public branch")
    elif effective == "translation_frozen":
        print("OK FROZEN: translation judgment is closed; transport may advance independently")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: operation mode and CI train contract are structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
