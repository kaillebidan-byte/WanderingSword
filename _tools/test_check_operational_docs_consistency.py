#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from check_operational_docs_consistency import validate_snapshot

SHA = "a" * 40


def completion_contract() -> dict:
    return {
        "task_is_completed_only_in_implementing_pr": True,
        "completed_entry_requires_pr_number": True,
        "merge_sha_is_verified_from_github_after_merge": True,
        "requires_root_cause": True,
        "requires_permanent_fix": True,
        "requires_normal_and_failure_regressions": True,
        "requires_institution_ci": True,
        "requires_live_checker_success": True,
        "requires_zero_unresolved_review_threads": True,
        "requires_squash_merge": True,
        "requires_main_revalidation": True,
        "requires_open_pr_triage": True,
    }


def fixtures():
    current = {
        "operation_mode": {"execution_mode": "always_public_full_pipeline"},
        "ci_train": {"transport_status": "merged"},
    }
    state = {
        "transport": {"status": "merged"},
        "cycle_control": {
            "status": "target_reached",
            "last_safe_checkpoint": "merged",
        },
    }
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
            {"task_id": "done", "status": "completed", "completion": {"pr": 1}},
            {"task_id": "next", "status": "pending"},
        ],
        "completion_contract": completion_contract(),
    }
    factory_markers = "translation_factory_controller.py semantic_bundle_boundary translation_quality_audit"
    evidence_markers = "PR番号 merge SHA GitHub metadata"
    resume_markers = "resume_work_controller.py INSTITUTION_WORK_QUEUE.json " + factory_markers + " " + evidence_markers
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
        "always_public": "INSTITUTION_WORK_QUEUE.json " + evidence_markers,
    }
    return current, state, manifest, packet, queue, texts


def main() -> None:
    args = fixtures()
    assert validate_snapshot(*args) == []

    current, state, manifest, packet, queue, texts = fixtures()
    state["cycle_control"] = {
        "status": "paused",
        "last_safe_checkpoint": "merged_pair_complete",
    }
    texts["handoff"] = texts["handoff"].replace(
        "cycle: `target_reached / merged`",
        "cycle: `paused / merged_pair_complete`",
    )
    assert validate_snapshot(current, state, manifest, packet, queue, texts) == []

    current, state, manifest, packet, queue, texts = fixtures()
    state["cycle_control"] = {
        "status": "paused",
        "last_safe_checkpoint": "pair_inventory_ready",
    }
    texts["handoff"] = texts["handoff"].replace(
        "cycle: `target_reached / merged`",
        "cycle: `paused / pair_inventory_ready`",
    )
    assert validate_snapshot(current, state, manifest, packet, queue, texts) == []

    current, state, manifest, packet, queue, texts = fixtures()
    texts["handoff"] = texts["handoff"].replace("target_reached / merged", "paused / merged_pair_complete")
    assert any("target_reached / merged" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    packet["release_candidate"]["status"] = "verified"
    assert any("status=merged" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    texts["handoff"] += "open / ready / mergeable"
    assert any("stale pre-merge" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    texts["handoff"] += "- main: PR #1\n"
    assert any("must not pin" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

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
    assert any("completion evidence" in error for error in errors)

    current, state, manifest, packet, queue, texts = fixtures()
    texts["handoff"] = texts["handoff"].replace("next", "other")
    assert any("current institution task" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    queue["tasks"][0]["status"] = "pending"
    queue["tasks"][1]["status"] = "completed"
    queue["tasks"][1]["completion"] = {"pr": 2}
    assert any("completed task appears after pending" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    queue["tasks"][0]["completion"]["merge_sha"] = "short"
    assert any("invalid optional merge SHA" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    current, state, manifest, packet, queue, texts = fixtures()
    queue["completion_contract"]["merge_sha_is_verified_from_github_after_merge"] = False
    assert any("completion contract flag" in error for error in validate_snapshot(current, state, manifest, packet, queue, texts))

    print("test_check_operational_docs_consistency: OK")


if __name__ == "__main__":
    main()
