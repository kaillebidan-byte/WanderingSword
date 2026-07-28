#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳projectの外部read/write対象がWanderingSwordへ固定されていることを検査する。"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "PROJECT_SCOPE_LOCK.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
CANONICAL_REPOSITORY = "kaillebidan-byte/WanderingSword"
CANONICAL_URL = "https://github.com/kaillebidan-byte/WanderingSword"
RESUME_CONTROLLER = "_tools/resume_work_controller.py"
INSTITUTION_QUEUE = "_phase4_proofread/INSTITUTION_WORK_QUEUE.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT)}")
    return value


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("PROJECT_SCOPE_LOCK.schema_version must be 1")
    if contract.get("contract_id") != "wandering-sword-project-scope-lock-v1":
        errors.append("PROJECT_SCOPE_LOCK.contract_id mismatch")
    if contract.get("canonical_repository") != CANONICAL_REPOSITORY:
        errors.append("PROJECT_SCOPE_LOCK.canonical_repository mismatch")
    if contract.get("canonical_url") != CANONICAL_URL:
        errors.append("PROJECT_SCOPE_LOCK.canonical_url mismatch")
    if contract.get("resume_controller") != RESUME_CONTROLLER:
        errors.append("PROJECT_SCOPE_LOCK.resume_controller mismatch")
    if contract.get("institution_work_queue") != INSTITUTION_QUEUE:
        errors.append("PROJECT_SCOPE_LOCK.institution_work_queue mismatch")
    for key in ("allowed_repository_reads", "allowed_repository_writes"):
        if contract.get(key) != [CANONICAL_REPOSITORY]:
            errors.append(f"PROJECT_SCOPE_LOCK.{key} must contain only the canonical repository")
    required_true = (
        "cross_repository_discovery_forbidden",
        "project_history_from_other_repositories_is_non_authoritative",
        "resume_must_not_infer_browser_or_userscript_work",
    )
    for key in required_true:
        if contract.get(key) is not True:
            errors.append(f"PROJECT_SCOPE_LOCK.{key} must be true")
    override = contract.get("override")
    if not isinstance(override, dict):
        errors.append("PROJECT_SCOPE_LOCK.override must be an object")
    else:
        if override.get("allowed_only_when_user_explicitly_names_another_repository_for_the_current_task") is not True:
            errors.append("PROJECT_SCOPE_LOCK override must require an explicit current-task repository")
        if override.get("conversation_history_alone_is_not_an_override") is not True:
            errors.append("PROJECT_SCOPE_LOCK history must not override scope")
    violation = contract.get("scope_violation")
    if not isinstance(violation, dict):
        errors.append("PROJECT_SCOPE_LOCK.scope_violation must be an object")
    else:
        if violation.get("stop_before_external_read_or_write") is not True:
            errors.append("scope violation must stop before external read/write")
        if violation.get("repository_mutation_forbidden") is not True:
            errors.append("scope violation must forbid repository mutation")
        if violation.get("stop_reason") != "project_scope_violation":
            errors.append("scope violation stop_reason mismatch")
    return errors


def validate_current(current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if current.get("repository") != CANONICAL_REPOSITORY:
        errors.append("CURRENT_WORK.repository must match the project scope lock")
    session = current.get("session_bootstrap")
    if not isinstance(session, dict):
        errors.append("CURRENT_WORK.session_bootstrap must be an object")
    else:
        if session.get("same_project_repository_known") is not True:
            errors.append("session_bootstrap.same_project_repository_known must be true")
        if session.get("ask_repository_again") is not False:
            errors.append("session_bootstrap.ask_repository_again must be false")
    return errors


def validate_requested_repository(repository: str | None) -> list[str]:
    if repository is None:
        return []
    normalized = repository.strip().removesuffix(".git")
    if normalized.startswith("https://github.com/"):
        normalized = normalized[len("https://github.com/"):].strip("/")
    if normalized != CANONICAL_REPOSITORY:
        return [
            f"project scope violation: requested repository {repository!r} is not {CANONICAL_REPOSITORY!r}"
        ]
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load(CONTRACT_PATH)
        current = load(CURRENT_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = [
        *validate_contract(contract),
        *validate_current(current),
        *validate_requested_repository(args.repository),
    ]
    print("=== Project scope lock ===")
    print(f"canonical repository: {CANONICAL_REPOSITORY}")
    print(f"requested repository: {args.repository or 'not supplied'}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: external repository scope is locked to WanderingSword")
    return 0


if __name__ == "__main__":
    sys.exit(main())
