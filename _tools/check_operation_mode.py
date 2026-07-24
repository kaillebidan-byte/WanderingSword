#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳作業回と公開CI窓の宣言状態・実visibilityを検査する。"""

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
VALID_DERIVED_STATES = {"public_ci_window", "return_private_required"}
VALID_VISIBILITIES = {"private", "public"}
EXPECTED_PROTOCOL = "_phase4_proofread/PUBLIC_CI_WINDOW.md"
EXPECTED_VISIBILITY_SOURCE = "github_repository_metadata"
EXPECTED_VISIBILITY_ACTOR = "user"
REQUIRED_COMPLETION_CHECKS = {
    "relation_audit_success",
    "cross_register_success",
    "apply_curated_fixes_success",
    "zero_pending_fixes",
    "verified_checkpoint",
    "zero_unresolved_review_threads",
    "translation_pr_squash_merged",
    "post_merge_state_pr_squash_merged",
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
    """宣言状態とGitHub実visibilityから、その場で取るべき状態を返す。"""
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
        errors.append(
            "operation_mode.actual_visibility_source must be "
            f"{EXPECTED_VISIBILITY_SOURCE!r}"
        )
    if mode.get("visibility_change_actor") != EXPECTED_VISIBILITY_ACTOR:
        errors.append(
            f"operation_mode.visibility_change_actor must be {EXPECTED_VISIBILITY_ACTOR!r}"
        )

    phrases = mode.get("phrases")
    if not isinstance(phrases, dict):
        errors.append("operation_mode.phrases must be an object")
    else:
        for key in (
            "request_public",
            "confirm_public",
            "request_private",
            "confirm_private",
        ):
            value = phrases.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"operation_mode.phrases.{key} must be a non-empty string")

    checks = mode.get("public_ci_exit_checks")
    if not isinstance(checks, list) or any(not isinstance(item, str) for item in checks):
        errors.append("operation_mode.public_ci_exit_checks must be a string list")
    else:
        missing = sorted(REQUIRED_COMPLETION_CHECKS - set(checks))
        if missing:
            errors.append(f"operation_mode.public_ci_exit_checks missing: {missing!r}")

    if mode.get("open_pr_only_after_ready") is not True:
        errors.append("operation_mode.open_pr_only_after_ready must be true")
    if mode.get("public_translation_forbidden") is not True:
        errors.append("operation_mode.public_translation_forbidden must be true")
    if mode.get("deep_failure_returns_private") is not True:
        errors.append("operation_mode.deep_failure_returns_private must be true")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-visibility",
        choices=sorted(VALID_VISIBILITIES),
        help="GitHub repository metadataから取得した実visibility",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_current()
    errors = validate_operation_mode(current)
    mode = current.get("operation_mode", {})
    declared = str(mode.get("declared_state", ""))
    effective = resolve_effective_mode(declared, args.repository_visibility) if declared in VALID_DECLARED_STATES else "invalid"

    print("=== Operation mode ===")
    print(f"declared state: {declared}")
    print(f"repository visibility: {args.repository_visibility or 'not supplied'}")
    print(f"effective state: {effective}")

    if effective == "return_private_required":
        print("ACTION REQUIRED: public CI work is not active; ask the user to return the repository to private")
    elif effective == "ready_for_public_ci":
        print("ACTION REQUIRED: completed HEAD is waiting for the user to open the public CI window")
    elif effective == "public_ci_window":
        print("OK WINDOW: run CI and integration work only; do not begin translation")
    elif effective == "public_ci_blocked":
        print("BLOCKED PRIVATE: repair the deep failure while the repository is private")
    elif effective == "private_translation_work":
        print("OK PRIVATE: translation and preparation work may continue only when actual visibility is private")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: operation mode contract is structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
