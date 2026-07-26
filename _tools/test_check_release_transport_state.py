#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

import check_release_transport_state as checker


def sample() -> tuple[dict, dict, dict, dict]:
    current = {
        "current_pair": "宇文逸↔莫問",
        "operation_mode": {"declared_state": "translation_frozen"},
        "checkpoint": {"status": "pending_audit_sync"},
        "session_bootstrap": {
            "protocol": "_phase4_proofread/SESSION_BOOTSTRAP.md",
            "trigger_phrase": "現状把握して作業の続きを",
            "same_project_repository_known": True,
            "ask_repository_again": False,
            "resume_work_in_same_response": True,
            "open_pr_triage_required": True,
            "next_task_packet_required": True,
            "next_task_packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
        },
        "immediate_next": {"scene_groups": ["next"], "task": "finalize transport"},
        "ci_train": {
            "phase": "phase1_wave",
            "train_id": "train",
            "branch": "agent/train",
            "status": "in_public_ci",
            "transport_status": "in_public_ci",
        },
    }
    manifest = {
        "phase": "phase1_wave",
        "train_id": "train",
        "branch": "agent/train",
        "status": "in_public_ci",
        "transport": {"status": "in_public_ci"},
    }
    stage = {"stage": "translation_frozen", "transport": {"status": "in_public_ci"}}
    packet = {"current_pair": "宇文逸↔莫問", "scene_groups": ["next"]}
    return current, manifest, stage, packet


def main() -> None:
    current, manifest, stage, packet = sample()
    assert checker.validate(current, manifest, stage, packet) == []

    strict_evidence_is_absent = copy.deepcopy(current)
    strict_evidence_is_absent["checkpoint"].pop("release_identity", None)
    assert checker.validate(strict_evidence_is_absent, manifest, stage, packet) == []

    bad = copy.deepcopy(current)
    bad["ci_train"]["transport_status"] = "verified"
    assert any("transport_status mismatch" in error for error in checker.validate(bad, manifest, stage, packet))

    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["transport"]["status"] = "verified"
    assert any("manifest.transport.status mismatch" in error for error in checker.validate(current, bad_manifest, stage, packet))

    bad_mode = copy.deepcopy(current)
    bad_mode["operation_mode"]["declared_state"] = "private_translation_work"
    assert any("translation_frozen" in error for error in checker.validate(bad_mode, manifest, stage, packet))
    print("OK: pre-Apply transport check allows unfinished release evidence and rejects state drift")


if __name__ == "__main__":
    main()
