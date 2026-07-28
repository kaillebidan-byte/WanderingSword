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
        "checkpoint": {"status": "verified", "produced_by_pr": PR},
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
        "transport": {
            "status": "awaiting_private_merge",
            "pr": PR,
            "merge_sha": None,
        },
        "private_stage": {"transport_status": "awaiting_private_merge"},
    }


def main() -> None:
    c, s, m, changed = reconciler.reconcile_values(
        current(), state(), manifest(), pr_number=PR, merge_sha=SHA
    )
    assert changed is True
    assert c["translation_base_commit"] == SHA
    assert c["state_base_commit"] == SHA
    assert c["last_merged_translation_pr"] == PR
    assert c["ci_train"]["transport_status"] == "merged"
    assert c["ci_train"]["private_stage"]["cycle_checkpoint"] == "merged"
    assert "_phase4_proofread/PROJECT_SCOPE_LOCK.json" in c["mandatory_read_order"]
    assert "_phase4_proofread/REGULATED_PHASE_STATE.json" in c["mandatory_read_order"]
    assert s["transport"]["status"] == "merged"
    assert s["transport"]["merge_sha"] == SHA
    assert s["cycle_control"]["status"] == "target_reached"
    assert s["cycle_control"]["continuation_required"] is False
    assert s["cycle_control"]["last_safe_checkpoint"] == "merged"
    assert m["transport"] == {"status": "merged", "pr": PR, "merge_sha": SHA}
    assert m["private_stage"]["transport_status"] == "merged"

    c2, s2, m2, changed2 = reconciler.reconcile_values(
        c, s, m, pr_number=PR, merge_sha=SHA
    )
    assert changed2 is False
    assert c2 == c and s2 == s and m2 == m

    bad = manifest()
    bad["transport"]["pr"] = 999
    try:
        reconciler.reconcile_values(current(), state(), bad, pr_number=PR, merge_sha=SHA)
    except ValueError as exc:
        assert "PR mismatch" in str(exc)
    else:
        raise AssertionError("PR mismatch must fail")

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
