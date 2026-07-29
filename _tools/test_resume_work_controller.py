#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
from pathlib import Path

import resume_work_controller as resume

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
QUEUE = json.loads((P4 / "INSTITUTION_WORK_QUEUE.json").read_text(encoding="utf-8"))
FACTORY = json.loads((P4 / "FACTORY_FLOW_CONTRACT.json").read_text(encoding="utf-8"))


def translation_fixtures():
    current = {
        "operation_mode": {"execution_mode": "always_public_full_pipeline"},
        "ci_train": {"transport_status": "merged"},
    }
    state = {
        "stage": "translation_frozen",
        "cycle_control": {"status": "target_reached", "exact_next_action": None},
        "transport": {"status": "merged"},
    }
    manifest = {"transport": {"status": "merged"}}
    packet = {"reservation": {"status": "reserved_only", "preparation_started": False}}
    return current, state, manifest, packet


def completed_queue() -> dict:
    queue = copy.deepcopy(QUEUE)
    for index, task in enumerate(queue["tasks"], start=1):
        task["status"] = "completed"
        task.pop("audit_scope", None)
        task.pop("completion_conditions", None)
        task.pop("forbidden", None)
        task["completion"] = {"pr": 200 + index}
    return queue


def main() -> None:
    assert resume.validate_queue(QUEUE) == []
    current, state, manifest, packet = translation_fixtures()
    order = resume.build_resume_work_order(QUEUE, FACTORY, current, state, manifest, packet, "public")
    expected_pending = resume.first_pending_task(QUEUE)
    assert expected_pending is not None
    assert order["route"] == "institution_repair"
    assert order["task_id"] == expected_pending["task_id"]
    assert order["translation_cycle_allowed"] is False
    assert order["completion_update"]["apply_in_same_implementing_pr"] is True
    assert order["completion_update"]["record_pr_number_in_implementing_pr"] is True
    assert order["completion_update"]["verify_merge_sha_from_github_after_merge"] is True

    delegated = resume.build_resume_work_order(
        completed_queue(), FACTORY, current, state, manifest, packet, "public"
    )
    assert delegated["route"] == "translation_factory"
    assert delegated["translation_cycle_allowed"] is True
    assert delegated["action"] == "initialize_next_cycle_from_reservation"

    try:
        resume.build_resume_work_order(QUEUE, FACTORY, current, state, manifest, packet, "private")
    except resume.ResumeStateError as exc:
        assert exc.code == "resume_institution_visibility_mismatch"
    else:
        raise AssertionError("private visibility must not start always-public institution work")

    bad = copy.deepcopy(QUEUE)
    bad["standard_trigger"] = "別の文"
    assert any("standard_trigger" in error for error in resume.validate_queue(bad))

    bad = copy.deepcopy(QUEUE)
    bad["tasks"][0]["status"] = "pending"
    bad["tasks"][0].pop("completion", None)
    bad["tasks"][0]["audit_scope"] = ["demo"]
    bad["tasks"][0]["completion_conditions"] = ["demo"]
    bad["tasks"][0]["forbidden"] = ["demo"]
    bad["tasks"][1]["status"] = "completed"
    bad["tasks"][1]["completion"] = {"pr": 2}
    assert any("completed task appears after pending" in error for error in resume.validate_queue(bad))

    valid_without_merge_sha = copy.deepcopy(QUEUE)
    valid_without_merge_sha["tasks"][0]["completion"] = {"pr": 176}
    assert resume.validate_queue(valid_without_merge_sha) == []

    bad = copy.deepcopy(QUEUE)
    bad["tasks"][0]["completion"]["merge_sha"] = "short"
    assert any("merge_sha" in error for error in resume.validate_queue(bad))

    bad = copy.deepcopy(QUEUE)
    bad["tasks"][0]["completion"] = {"merge_sha": "b" * 40}
    assert any("completion.pr" in error for error in resume.validate_queue(bad))

    print("test_resume_work_controller: OK")


if __name__ == "__main__":
    main()
