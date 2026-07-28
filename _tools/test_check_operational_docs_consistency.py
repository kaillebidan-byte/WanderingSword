#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

from check_operational_docs_consistency import validate_snapshot

SHA = "a" * 40


def fixtures():
    current = {
        "operation_mode": {"execution_mode": "always_public_full_pipeline"},
        "ci_train": {"transport_status": "merged"},
    }
    state = {"transport": {"status": "merged"}}
    manifest = {"transport": {"status": "merged", "pr": 12, "merge_sha": SHA}}
    packet = {
        "release_candidate": {"status": "merged", "merge_sha": SHA},
        "do_not_do": ["mode lock前に開始しない"],
    }
    queue = {
        "schema_version": 1,
        "contract_id": "resume-work-queue-v1",
        "standard_trigger": "現状把握して作業の続きを",
        "required_visibility": "public",
        "mode_scope": ["always_public_full_pipeline"],
        "translation_policy": "blocked_while_institution_tasks_pending",
        "task_order": ["done", "next"],
        "tasks": [
            {"task_id": "done", "status": "completed", "completion": {"pr": 1, "merge_sha": SHA}},
            {"task_id": "next", "status": "pending"},
        ],
    }
    factory_markers = "translation_factory_controller.py semantic_bundle_boundary translation_quality_audit"
    resume_markers = "resume_work_controller.py INSTITUTION_WORK_QUEUE.json " + factory_markers
    texts = {
        "handoff": (
            "PR #12: merged\ntransport: `merged`\ncycle: `target_reached / merged`\n"
            "next\n翻訳cycleを開始しない\n"
        ),
        "cold": "public + `private_translation_work` + `always_public_full_pipeline`",
        "phase1": "manual public CI窓",
        "phase2": "mode-neutral release",
        "runbook": "post-merge状態専用PRは作らない",
        "public_window": "manual_visibility_cycle専用",
        "readme": resume_markers,
        "session": resume_markers,
        "factory": factory_markers,
        "private_stages": "encoding後に上書きしない",
        "always_public": "INSTITUTION_WORK_QUEUE.json",
    }
    return current, state, manifest, packet, queue, texts


def main() -> None:
    args = fixtures()
    assert validate_snapshot(*args) == []

    current, state, manifest, packet, queue, texts = fixtures()
    packet["release_candidate"]["status"] = "verified"
    assert any("status=merged" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    texts["handoff"] += "open / ready / mergeable"
    assert any("stale pre-merge" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    texts["cold"] = "private_translation_work + publicなら、翻訳を開始せずprivate復帰を依頼する"
    assert any("legacy public=>private" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    texts["runbook"] += "\npost-merge状態PRを作成する"
    assert any("legacy instruction" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    texts["session"] = "translation_factory_controller.py semantic_bundle_boundary"
    errors = validate_snapshot(current, state, manifest, packet, queue, texts)
    assert any("resume_work_controller.py" in error for error in errors)
    assert any("translation_quality_audit" in error for error in errors)

    current, state, manifest, packet, queue, texts = fixtures()
    texts["handoff"] = texts["handoff"].replace("next", "other")
    assert any("current institution task" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    queue["tasks"][0]["status"] = "pending"
    queue["tasks"][1]["status"] = "completed"
    queue["tasks"][1]["completion"] = {"pr": 2, "merge_sha": SHA}
    assert any("completed task appears after pending" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    print("test_check_operational_docs_consistency: OK")


if __name__ == "__main__":
    main()
