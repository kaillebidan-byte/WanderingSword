#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import reconcile_merged_cycle as reconciler

PR = 146
SHA = "fda4734c01bee3bc891ca6d1db2888d8b1a53539"


def current() -> dict:
    return {
        "translation_base_commit": "0" * 40,
        "state_base_commit": "0" * 40,
        "last_merged_translation_pr": 145,
        "current_pair": "A↔B",
        "checkpoint": {
            "status": "verified",
            "produced_by_pr": PR,
            "batch": 20,
            "pair_applied_keys": 30,
            "project_applied_keys": 40,
        },
        "ci_train": {
            "draft_pr": PR,
            "transport_status": "awaiting_private_merge",
            "private_stage": {
                "transport_status": "awaiting_private_merge",
                "cycle_status": "running",
                "cycle_checkpoint": "awaiting_private_merge",
            },
        },
        "immediate_next": {"task": "merge", "boundary": "frozen"},
        "mandatory_read_order": [
            "README.md",
            "AGENTS.md",
            "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
            "_phase4_proofread/SESSION_BOOTSTRAP.md",
        ],
    }


def state() -> dict:
    return {
        "stage": "translation_frozen",
        "cycle_control": {
            "status": "running",
            "continuation_required": True,
            "stop_reason": None,
            "exact_next_action": "merge",
            "last_safe_checkpoint": "awaiting_private_merge",
        },
        "transport": {
            "status": "awaiting_private_merge",
            "pr": PR,
            "history": [{"status": "awaiting_private_merge", "pr": PR}],
        },
    }


def manifest() -> dict:
    return {
        "train_id": "train-test",
        "transport": {"status": "awaiting_private_merge", "pr": PR, "merge_sha": None},
        "private_stage": {"transport_status": "awaiting_private_merge"},
    }


def packet() -> dict:
    return {
        "schema_version": 6,
        "scene_groups": ["scene-1"],
        "release_candidate": {"pr": PR, "status": "verified", "merge_sha": None},
        "do_not_do": ["PR統合前に開始しない"],
    }


def main() -> None:
    c, s, m, changed = reconciler.reconcile_values(current(), state(), manifest(), pr_number=PR, merge_sha=SHA)
    assert changed is True
    p, h, companion_changed = reconciler.reconcile_companions(
        c, m, packet(), "old handoff", pr_number=PR, merge_sha=SHA
    )
    assert companion_changed is True
    assert p["release_candidate"] == {"pr": PR, "status": "merged", "merge_sha": SHA}
    assert "PR #146: merged" in h
    assert "transport: `merged`" in h
    assert all("統合前" not in item for item in p["do_not_do"])

    p2, h2, changed2 = reconciler.reconcile_companions(c, m, p, h, pr_number=PR, merge_sha=SHA)
    assert changed2 is False and p2 == p and h2 == h

    institution_handoff = "# 制度キュー\nworkflow_duplicate_run_serialization\n"
    pending_queue = {"tasks": [{"task_id": "repair", "status": "pending"}]}
    p3, h3, changed3 = reconciler.reconcile_companions(
        c,
        m,
        packet(),
        institution_handoff,
        pr_number=PR,
        merge_sha=SHA,
        institution_queue=pending_queue,
    )
    assert changed3 is True
    assert p3["release_candidate"]["status"] == "merged"
    assert h3 == institution_handoff

    completed_queue = {"tasks": [{"task_id": "repair", "status": "completed"}]}
    _, h4, _ = reconciler.reconcile_companions(
        c,
        m,
        packet(),
        institution_handoff,
        pr_number=PR,
        merge_sha=SHA,
        institution_queue=completed_queue,
    )
    assert "PR #146: merged" in h4

    c2, s2, m2, changed4 = reconciler.reconcile_values(c, s, m, pr_number=PR, merge_sha=SHA)
    assert changed4 is False and c2 == c and s2 == s and m2 == m

    bad = manifest()
    bad["transport"]["pr"] = 999
    try:
        reconciler.reconcile_values(current(), state(), bad, pr_number=PR, merge_sha=SHA)
    except ValueError as exc:
        assert "PR mismatch" in str(exc)
    else:
        raise AssertionError("PR mismatch must fail")

    bad_packet = packet()
    bad_packet["release_candidate"]["pr"] = 999
    try:
        reconciler.reconcile_companions(c, m, bad_packet, h, pr_number=PR, merge_sha=SHA)
    except ValueError as exc:
        assert "PR mismatch" in str(exc)
    else:
        raise AssertionError("packet PR mismatch must fail")

    bad_current = copy.deepcopy(current())
    bad_current["checkpoint"]["status"] = "unverified"
    try:
        reconciler.reconcile_values(bad_current, state(), manifest(), pr_number=PR, merge_sha=SHA)
    except ValueError as exc:
        assert "checkpoint" in str(exc)
    else:
        raise AssertionError("unverified checkpoint must fail")

    print("test_reconcile_merged_cycle: OK")


if __name__ == "__main__":
    main()
