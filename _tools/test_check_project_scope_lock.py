#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_project_scope_lock as checker


def contract() -> dict:
    return {
        "schema_version": 1,
        "contract_id": "wandering-sword-project-scope-lock-v1",
        "canonical_repository": checker.CANONICAL_REPOSITORY,
        "canonical_url": checker.CANONICAL_URL,
        "resume_controller": checker.RESUME_CONTROLLER,
        "institution_work_queue": checker.INSTITUTION_QUEUE,
        "allowed_repository_reads": [checker.CANONICAL_REPOSITORY],
        "allowed_repository_writes": [checker.CANONICAL_REPOSITORY],
        "cross_repository_discovery_forbidden": True,
        "project_history_from_other_repositories_is_non_authoritative": True,
        "resume_must_not_infer_browser_or_userscript_work": True,
        "override": {
            "allowed_only_when_user_explicitly_names_another_repository_for_the_current_task": True,
            "conversation_history_alone_is_not_an_override": True,
        },
        "scope_violation": {
            "stop_before_external_read_or_write": True,
            "stop_reason": "project_scope_violation",
            "repository_mutation_forbidden": True,
        },
    }


def current() -> dict:
    return {
        "repository": checker.CANONICAL_REPOSITORY,
        "session_bootstrap": {
            "same_project_repository_known": True,
            "ask_repository_again": False,
        },
    }


def main() -> None:
    assert checker.validate_contract(contract()) == []
    assert checker.validate_current(current()) == []
    assert checker.validate_requested_repository(checker.CANONICAL_REPOSITORY) == []
    assert checker.validate_requested_repository(checker.CANONICAL_URL) == []

    assert checker.validate_requested_repository("kaillebidan-byte/chatgpt-userscripts")
    assert checker.validate_requested_repository("https://github.com/other/repo")

    bad = copy.deepcopy(contract())
    bad["allowed_repository_writes"].append("kaillebidan-byte/chatgpt-userscripts")
    assert any("allowed_repository_writes" in error for error in checker.validate_contract(bad))

    bad = copy.deepcopy(contract())
    bad["resume_controller"] = "_tools/translation_factory_controller.py"
    assert any("resume_controller" in error for error in checker.validate_contract(bad))

    bad = copy.deepcopy(contract())
    bad["institution_work_queue"] = "_phase4_proofread/NEXT_TASK_PACKET.json"
    assert any("institution_work_queue" in error for error in checker.validate_contract(bad))

    bad_current = current()
    bad_current["repository"] = "kaillebidan-byte/chatgpt-userscripts"
    assert any("CURRENT_WORK.repository" in error for error in checker.validate_current(bad_current))

    print("test_check_project_scope_lock: OK")


if __name__ == "__main__":
    main()
