#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""turn入口と最終応答のGitHub preflight v4 scope・mode・phase consumer・merge契約を検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "_phase4_proofread" / "VISIBILITY_PREFLIGHT_CONTRACT.json"

EXPECTED_DOCS = {
    "bootstrap": "_phase4_proofread/SESSION_BOOTSTRAP.md",
    "final_response_gate": "_phase4_proofread/FINAL_RESPONSE_GATE.md",
    "manual_public_window": "_phase4_proofread/PUBLIC_CI_WINDOW.md",
    "always_public_pipeline": "_phase4_proofread/ALWAYS_PUBLIC_FULL_PIPELINE.md",
    "cold_start_acceptance": "_phase4_proofread/COLD_START_ACCEPTANCE.md",
}
REQUIRED_APPLIES_TO = {
    "new_chat_resume",
    "continue_work",
    "visibility_change_report",
    "public_ci_entry",
    "private_translation_entry",
    "cycle_mode_selection",
    "final_response_send",
    "automation_terminal_detection",
    "merged_cycle_reconciliation",
}
EXPECTED_PROJECT_SCOPE = {
    "contract": "_phase4_proofread/PROJECT_SCOPE_LOCK.json",
    "canonical_repository": "kaillebidan-byte/WanderingSword",
    "scope_check_precedes_repository_metadata": True,
    "cross_repository_discovery_forbidden": True,
    "scope_violation_stops_before_external_read_or_write": True,
}
EXPECTED_CYCLE = {
    "contract": "_phase4_proofread/EXECUTION_MODES.json",
    "selection_time": "new_cycle_start_only",
    "selection_source": "repository_visibility_at_cycle_start",
    "private_selects": "manual_visibility_cycle",
    "public_selects": "always_public_full_pipeline",
    "active_cycle_mode_change_forbidden": True,
    "state_authorities_must_match": True,
    "same_continue_phrase_for_all_modes": True,
}
EXPECTED_SIGNAL = {
    "contract": "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
    "runtime_state": "_phase4_proofread/REGULATED_PHASE_STATE.json",
    "agent_gate": "_phase4_proofread/FINAL_RESPONSE_GATE.md",
    "python_validator": "_tools/check_phase_completion_signal.py",
    "javascript_consumer": "_tools/regulated_phase_terminal_consumer.js",
    "dynamic_authorization_required": True,
    "authorization_event_id_line_required": True,
    "required_on_phase_success": True,
    "required_on_phase_error": True,
    "last_nonempty_line": "規定フェイズ完了",
    "result_line_immediately_precedes_marker": True,
    "authorization_line_immediately_precedes_result": True,
    "marker_only_is_terminal": False,
    "live_state_match_required": True,
    "live_state_unavailable_behavior": "reject_terminal",
    "release_phase2_is_not_regulated_phase": True,
    "train_or_merge_completion_does_not_emit": True,
    "routine_pause_does_not_emit": True,
}
EXPECTED_MERGED_CYCLE = {
    "tool": "_tools/reconcile_merged_cycle.py",
    "workflow": ".github/workflows/reconcile-merged-cycle.yml",
    "state_authorities": [
        "_phase4_proofread/CURRENT_WORK.json",
        "_phase4_proofread/PRIVATE_STAGE_STATE.json",
        "_phase4_proofread/CI_TRAIN_MANIFEST.json",
    ],
    "next_chat_repair_is_not_normal_completion": True,
    "idempotent": True,
}


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("ERROR: visibility preflight contract must be an object")
    return value


def _validate_exact_object(
    value: Any,
    expected: dict[str, Any],
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append(f"{label}.{key} mismatch")


def validate_contract(contract: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    if contract.get("schema_version") != 4:
        errors.append("schema_version must be 4")
    if contract.get("gate_id") != "github-preflight-v4-scope-mode-phase-consumer-merge":
        errors.append("gate_id must be github-preflight-v4-scope-mode-phase-consumer-merge")
    if contract.get("source_of_truth") != "github_repository_metadata":
        errors.append("source_of_truth must be github_repository_metadata")

    applies_to = contract.get("applies_to")
    if not isinstance(applies_to, list) or set(applies_to) != REQUIRED_APPLIES_TO:
        errors.append("applies_to must contain the complete v4 entry-point set")

    _validate_exact_object(
        contract.get("project_scope"), EXPECTED_PROJECT_SCOPE, "project_scope", errors
    )
    scope_path = root / EXPECTED_PROJECT_SCOPE["contract"]
    if not scope_path.is_file():
        errors.append(f"missing project scope contract: {EXPECTED_PROJECT_SCOPE['contract']}")

    ordering = contract.get("ordering")
    if not isinstance(ordering, dict):
        errors.append("ordering must be an object")
    else:
        if ordering.get("project_scope_lock_is_first_internal_check") is not True:
            errors.append("project scope lock must be the first internal check")
        if ordering.get("repository_metadata_is_first_external_check") is not True:
            errors.append("repository metadata must be the first external check")
        if ordering.get("final_response_gate_precedes_send") is not True:
            errors.append("final response gate must precede send")
        for key in (
            "user_visible_update_before_verdict",
            "work_start_claim_before_verdict",
            "branch_or_batch_start_claim_before_verdict",
        ):
            if ordering.get(key) != "forbidden":
                errors.append(f"ordering.{key} must be forbidden")

    report = contract.get("user_visibility_report")
    if not isinstance(report, dict):
        errors.append("user_visibility_report must be an object")
    else:
        if report.get("authority") != "hint_only":
            errors.append("user visibility report must be hint_only")
        if report.get("requires_metadata_confirmation") is not True:
            errors.append("user visibility report must require metadata confirmation")

    _validate_exact_object(contract.get("cycle_mode"), EXPECTED_CYCLE, "cycle_mode", errors)
    _validate_exact_object(
        contract.get("phase_completion_signal"),
        EXPECTED_SIGNAL,
        "phase_completion_signal",
        errors,
    )
    _validate_exact_object(
        contract.get("merged_cycle"), EXPECTED_MERGED_CYCLE, "merged_cycle", errors
    )
    for relative in (
        EXPECTED_SIGNAL["contract"],
        EXPECTED_SIGNAL["runtime_state"],
        EXPECTED_SIGNAL["agent_gate"],
        EXPECTED_SIGNAL["python_validator"],
        EXPECTED_SIGNAL["javascript_consumer"],
        EXPECTED_MERGED_CYCLE["tool"],
        EXPECTED_MERGED_CYCLE["workflow"],
    ):
        if not (root / relative).is_file():
            errors.append(f"missing v4 contract dependency: {relative}")

    verdict = contract.get("verdict")
    if not isinstance(verdict, dict):
        errors.append("verdict must be an object")
    else:
        if verdict.get("first_user_visible_update_requires_effective_mode") is not True:
            errors.append("first user-visible update must require effective mode")
        if verdict.get("metadata_failure_allows_work_start_claim") is not False:
            errors.append("metadata failure must not allow a work-start claim")
        if verdict.get("terminal_acceptance_requires_consumer_accept") is not True:
            errors.append("terminal acceptance must require consumer accepted=true")

    repair = contract.get("public_administrative_repair")
    if not isinstance(repair, dict):
        errors.append("public_administrative_repair must be an object")
    else:
        for key in (
            "manual_mode_allowed_only_in_public_ci_window",
            "always_public_mode_preserves_locked_stage_permissions",
            "translation_text_changes_outside_quality_and_encoding_stages_forbidden",
            "fix_value_changes_after_translation_frozen_forbidden",
            "persona_or_ownership_changes_after_translation_frozen_forbidden",
            "tracking_issue_record_required",
            "affected_gates_must_rerun",
        ):
            if repair.get(key) is not True:
                errors.append(f"public_administrative_repair.{key} must be true")

    documents = contract.get("documents")
    if not isinstance(documents, dict):
        errors.append("documents must be an object")
    else:
        for key, expected in EXPECTED_DOCS.items():
            if documents.get(key) != expected:
                errors.append(f"documents.{key} must be {expected!r}")
            elif not (root / expected).is_file():
                errors.append(f"missing contract document: {expected}")

    return errors


def main() -> int:
    contract = load_contract()
    errors = validate_contract(contract)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: visibility preflight v4 scope, mode, phase consumer, and merge contract is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
