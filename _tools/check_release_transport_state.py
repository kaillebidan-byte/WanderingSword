#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply前の輸送状態を検査する。最終release証跡はphase2へ委ねる。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
TRIGGER = "現状把握して作業の続きを"


def load(name: str) -> dict[str, Any]:
    value = json.loads((P4 / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name}: top level must be object")
    return value


def validate(current: dict[str, Any], manifest: dict[str, Any], stage: dict[str, Any], packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if current.get("operation_mode", {}).get("declared_state") != "translation_frozen":
        errors.append("operation mode must be translation_frozen")
    if stage.get("stage") != "translation_frozen":
        errors.append("private stage must be translation_frozen")

    train = current.get("ci_train")
    if not isinstance(train, dict):
        errors.append("CURRENT_WORK.ci_train must be an object")
        train = {}
    for key in ("phase", "train_id", "branch", "status"):
        if train.get(key) != manifest.get(key):
            errors.append(f"ci_train.{key} mismatch")

    transport = stage.get("transport", {}).get("status")
    if transport not in {"ready_for_public_ci", "in_public_ci", "verified", "awaiting_private_merge", "merged"}:
        errors.append("transport is not release-safe")
    if train.get("transport_status") != transport:
        errors.append("ci_train.transport_status mismatch")

    checkpoint = current.get("checkpoint")
    if not isinstance(checkpoint, dict) or checkpoint.get("status") not in {"verified", "pending_audit_sync"}:
        errors.append("checkpoint must be verified or pending_audit_sync")

    bootstrap = current.get("session_bootstrap")
    if not isinstance(bootstrap, dict):
        errors.append("session_bootstrap must be an object")
    else:
        expected = {
            "protocol": "_phase4_proofread/SESSION_BOOTSTRAP.md",
            "trigger_phrase": TRIGGER,
            "same_project_repository_known": True,
            "ask_repository_again": False,
            "resume_work_in_same_response": True,
            "open_pr_triage_required": True,
            "next_task_packet_required": True,
            "next_task_packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
        }
        for key, value in expected.items():
            if bootstrap.get(key) != value:
                errors.append(f"session_bootstrap.{key} mismatch")

    immediate = current.get("immediate_next")
    if not isinstance(immediate, dict) or not immediate.get("scene_groups") or not immediate.get("task"):
        errors.append("immediate_next is incomplete")
    if packet.get("current_pair") != current.get("current_pair"):
        errors.append("NEXT_TASK_PACKET current_pair mismatch")
    if not isinstance(packet.get("scene_groups"), list) or not packet.get("scene_groups"):
        errors.append("NEXT_TASK_PACKET scene_groups must be non-empty")
    return errors


def main() -> int:
    current = load("CURRENT_WORK.json")
    manifest = load("CI_TRAIN_MANIFEST.json")
    stage = load("PRIVATE_STAGE_STATE.json")
    packet = load("NEXT_TASK_PACKET.json")
    errors = validate(current, manifest, stage, packet)
    for name in ("CURRENT_HANDOFF.md", "SESSION_BOOTSTRAP.md"):
        if TRIGGER not in (P4 / name).read_text(encoding="utf-8"):
            errors.append(f"{name} lacks restart phrase")
    print("=== Release transport state ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: pre-Apply transport state is complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
