#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

from release_orchestrator_guard import evaluate

SHA = "a" * 40
PR = 180
TRAIN = "yuwen-mowen-train-29"
BRANCH = "agent/yuwen-mowen-train-29"


def fixtures() -> tuple[dict, dict, dict, dict]:
    current = {
        "operation_mode": {"declared_state": "translation_frozen"},
        "immediate_next": {"task": "release-ci labelでRelease train orchestratorを起動する。"},
        "ci_train": {
            "train_id": TRAIN,
            "branch": BRANCH,
            "draft_pr": PR,
            "status": "ready_for_public_ci",
            "transport_status": "ready_for_public_ci",
            "private_stage": {
                "stage": "translation_frozen",
                "status": "complete",
                "transport_status": "ready_for_public_ci",
            },
        },
    }
    manifest = {
        "train_id": TRAIN,
        "branch": BRANCH,
        "draft_pr": PR,
        "status": "ready_for_public_ci",
        "transport": {
            "status": "ready_for_public_ci",
            "translation_stage": "translation_frozen",
            "pr": PR,
        },
        "private_stage": {
            "stage": "translation_frozen",
            "status": "complete",
            "transport_status": "ready_for_public_ci",
        },
    }
    stage = {
        "train_id": TRAIN,
        "stage": "translation_frozen",
        "transport": {"status": "ready_for_public_ci", "pr": PR},
        "cycle_control": {"last_safe_checkpoint": "ready_for_public_ci"},
    }
    packet = {
        "reservation": {"status": "encoded"},
        "release_candidate": {"train_id": TRAIN, "pr": PR, "status": "ready_for_public_ci"},
        "ci_train": {"train_id": TRAIN},
    }
    return current, manifest, stage, packet


def run(*, action: str = "labeled", label: str = "release-ci", event_head: str = SHA, live_head: str = SHA, current=None, manifest=None, stage=None, packet=None):
    base = fixtures()
    return evaluate(
        current or base[0],
        manifest or base[1],
        stage or base[2],
        packet or base[3],
        event_action=action,
        event_label=label,
        event_head=event_head,
        current_pr_head=live_head,
        head_ref=BRANCH,
        pr_number=PR,
    )


def main() -> None:
    ready = run()
    assert ready["status"] == "proceed"
    assert ready["proceed"] is True
    assert ready["remove_release_labels"] is False
    assert ready["reasons"] == []

    stale_head = run(live_head="b" * 40)
    assert stale_head["status"] == "stale_noop"
    assert "event_head_is_stale" in stale_head["reasons"]

    synchronize = run(action="synchronize", label="")
    assert synchronize["status"] == "stale_noop"
    assert synchronize["reasons"][0] == "synchronize_requires_explicit_relabel"
    assert synchronize["remove_release_labels"] is True

    current, manifest, stage, packet = fixtures()
    regressed = copy.deepcopy(stage)
    regressed["transport"]["status"] = "not_ready"
    stale_state = run(current=current, manifest=manifest, stage=regressed, packet=packet)
    assert stale_state["status"] == "stale_noop"
    assert any("PRIVATE_STAGE_STATE.transport.status" in reason for reason in stale_state["reasons"])

    current, manifest, stage, packet = fixtures()
    stale_packet = copy.deepcopy(packet)
    stale_packet["release_candidate"]["pr"] = PR - 1
    stale_lineage = run(current=current, manifest=manifest, stage=stage, packet=stale_packet)
    assert stale_lineage["status"] == "stale_noop"
    assert any("release candidate PR lineage" in reason for reason in stale_lineage["reasons"])

    print("test_release_orchestrator_guard: OK")


if __name__ == "__main__":
    main()
