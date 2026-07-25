#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""turn入口のGitHub visibility preflight契約を検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "_phase4_proofread" / "VISIBILITY_PREFLIGHT_CONTRACT.json"

EXPECTED_DOCS = {
    "bootstrap": "_phase4_proofread/SESSION_BOOTSTRAP.md",
    "public_window": "_phase4_proofread/PUBLIC_CI_WINDOW.md",
    "cold_start_acceptance": "_phase4_proofread/COLD_START_ACCEPTANCE.md",
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


def validate_contract(contract: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if contract.get("gate_id") != "github-visibility-preflight-v1":
        errors.append("gate_id must be github-visibility-preflight-v1")
    if contract.get("source_of_truth") != "github_repository_metadata":
        errors.append("source_of_truth must be github_repository_metadata")

    ordering = contract.get("ordering")
    if not isinstance(ordering, dict):
        errors.append("ordering must be an object")
    else:
        if ordering.get("repository_metadata_is_first_external_check") is not True:
            errors.append("repository metadata must be the first external check")
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

    verdict = contract.get("verdict")
    if not isinstance(verdict, dict):
        errors.append("verdict must be an object")
    else:
        if verdict.get("first_user_visible_update_requires_effective_mode") is not True:
            errors.append("first user-visible update must require effective mode")
        if verdict.get("metadata_failure_allows_work_start_claim") is not False:
            errors.append("metadata failure must not allow a work-start claim")

    repair = contract.get("public_administrative_repair")
    if not isinstance(repair, dict):
        errors.append("public_administrative_repair must be an object")
    else:
        for key in (
            "allowed_only_in_public_ci_window",
            "translation_text_changes_forbidden",
            "fix_value_changes_forbidden",
            "persona_or_ownership_changes_forbidden",
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
    print("OK: visibility preflight contract is structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
