#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳作業回、CI列車、公開CI窓、phase2単一PR最終化を検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CURRENT_PATH = ROOT / "_phase4_proofread" / "CURRENT_WORK.json"

VALID_DECLARED_STATES = {
    "private_translation_work",
    "ready_for_public_ci",
    "public_ci_blocked",
}
VALID_VISIBILITIES = {"private", "public"}
VALID_TRAIN_STATUSES = {
    "accumulating",
    "ready_for_public_ci",
    "in_public_ci",
    "verified",
    "aborted",
}
EXPECTED_PROTOCOL = "_phase4_proofread/PUBLIC_CI_WINDOW.md"
EXPECTED_TRAIN_MANIFEST = "_phase4_proofread/CI_TRAIN_MANIFEST.json"
EXPECTED_VISIBILITY_SOURCE = "github_repository_metadata"
EXPECTED_VISIBILITY_ACTOR = "user"
PHASE1_POLICY = "_phase4_proofread/CI_TRAIN_PHASE1.md"
PHASE2_POLICY = "_phase4_proofread/CI_TRAIN_PHASE2.md"
PHASE1_COMPLETION_CHECKS = {
    "relation_audit_success",
    "cross_register_success",
    "apply_curated_fixes_success",
    "zero_pending_fixes",
    "verified_checkpoint",
    "zero_unresolved_review_threads",
    "translation_pr_squash_merged",
    "post_merge_state_pr_squash_merged",
}
PHASE2_COMPLETION_CHECKS = {
    "relation_audit_success",
    "cross_register_success",
    "apply_curated_fixes_success",
    "zero_pending_fixes",
    "release_evidence_verified",
    "single_pr_state_finalized",
    "verified_checkpoint",
    "zero_unresolved_review_threads",
    "translation_pr_squash_merged",
}


def load_current(path: Path = CURRENT_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("ERROR: CURRENT_WORK top level must be an object")
    return value


def resolve_effective_mode(declared_state: str, visibility: str | None) -> str:
    if visibility is None:
        return declared_state
    if visibility not in VALID_VISIBILITIES:
        raise ValueError(f"unsupported repository visibility: {visibility}")
    if declared_state == "ready_for_public_ci" and visibility == "public":
        return "public_ci_window"
    if declared_state in {"private_translation_work", "public_ci_blocked"} and visibility == "public":
        return "return_private_required"
    return declared_state


def validate_operation_mode(current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    mode = current.get("operation_mode")
    if not isinstance(mode, dict):
        return ["CURRENT_WORK.operation_mode must be an object"]

    declared = mode.get("declared_state")
    if declared not in VALID_DECLARED_STATES:
        errors.append(
            "operation_mode.declared_state must be one of "
            + ", ".join(sorted(VALID_DECLARED_STATES))
        )

    protocol = mode.get("protocol")
    if protocol != EXPECTED_PROTOCOL:
        errors.append(f"operation_mode.protocol must be {EXPECTED_PROTOCOL!r}")
    elif not (ROOT / protocol).is_file():
        errors.append(f"operation mode protocol does not exist: {protocol}")

    if mode.get("actual_visibility_source") != EXPECTED_VISIBILITY_SOURCE:
        errors.append("operation_mode.actual_visibility_source is invalid")
    if mode.get("visibility_change_actor") != EXPECTED_VISIBILITY_ACTOR:
        errors.append("operation_mode.visibility_change_actor is invalid")

    phrases = mode.get("phrases")
    if not isinstance(phrases, dict):
        errors.append("operation_mode.phrases must be an object")
    else:
        for key in ("request_public", "confirm_public", "request_private", "confirm_private"):
            if not isinstance(phrases.get(key), str) or not phrases.get(key, "").strip():
                errors.append(f"operation_mode.phrases.{key} must be non-empty")

    train = current.get("ci_train")
    if not isinstance(train, dict):
        errors.append("CURRENT_WORK.ci_train must be an object")
        return errors

    finalization_phase = train.get("finalization_phase", "phase1")
    if finalization_phase not in {"phase1", "phase2"}:
        errors.append("ci_train.finalization_phase must be phase1 or phase2")
        finalization_phase = "phase1"
    required_checks = (
        PHASE2_COMPLETION_CHECKS if finalization_phase == "phase2" else PHASE1_COMPLETION_CHECKS
    )
    checks = mode.get("public_ci_exit_checks")
    if not isinstance(checks, list) or any(not isinstance(item, str) for item in checks):
        errors.append("operation_mode.public_ci_exit_checks must be a string list")
    else:
        missing = sorted(required_checks - set(checks))
        if missing:
            errors.append(f"operation_mode.public_ci_exit_checks missing: {missing!r}")
        if finalization_phase == "phase2" and "post_merge_state_pr_squash_merged" in checks:
            errors.append("phase2 must not require post_merge_state_pr_squash_merged")

    for key in (
        "open_pr_only_after_ready",
        "draft_train_pr_allowed_while_private",
        "train_release_requires_manifest_ready",
        "public_translation_forbidden",
        "deep_failure_returns_private",
    ):
        if mode.get(key) is not True:
            errors.append(f"operation_mode.{key} must be true")

    if finalization_phase == "phase2":
        if mode.get("single_pr_finalization") is not True:
            errors.append("phase2 requires operation_mode.single_pr_finalization=true")
        if mode.get("post_merge_state_pr_required") is not False:
            errors.append("phase2 requires operation_mode.post_merge_state_pr_required=false")
    else:
        if mode.get("post_merge_state_pr_required") is False:
            errors.append("phase1 cannot disable post_merge_state_pr_required")

    if train.get("phase") != "phase1_pilot":
        errors.append("ci_train.phase must remain phase1_pilot for accumulation-schema compatibility")
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
    if train_status == "accumulating" and declared != "private_translation_work":
        errors.append("accumulating train requires private_translation_work")
    if train_status in {"ready_for_public_ci", "in_public_ci"} and declared != "ready_for_public_ci":
        errors.append("ready/in_public_ci train requires ready_for_public_ci")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-visibility", choices=sorted(VALID_VISIBILITIES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_current()
    errors = validate_operation_mode(current)
    mode = current.get("operation_mode", {})
    train = current.get("ci_train", {})
    declared = str(mode.get("declared_state", ""))
    effective = (
        resolve_effective_mode(declared, args.repository_visibility)
        if declared in VALID_DECLARED_STATES
        else "invalid"
    )

    print("=== Operation mode ===")
    print(f"declared state: {declared}")
    print(f"repository visibility: {args.repository_visibility or 'not supplied'}")
    print(f"effective state: {effective}")
    print(f"CI train: {train.get('train_id')} / {train.get('status')}")
    print(f"finalization: {train.get('finalization_phase', 'phase1')}")

    if effective == "return_private_required":
        print("ACTION REQUIRED: public CI is not active; return the repository to private")
    elif effective == "ready_for_public_ci":
        print("ACTION REQUIRED: a released CI train is waiting for the public window")
    elif effective == "public_ci_window":
        print("OK WINDOW: run CI and single-PR integration only")
    elif effective == "public_ci_blocked":
        print("BLOCKED PRIVATE: repair the deep failure while private")
    elif effective == "private_translation_work":
        print("OK PRIVATE: continue the active CI train while actual visibility is private")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: operation mode and CI train contract are structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
