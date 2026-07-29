#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人物資料還流後のowner状態証跡refreshが恒久factoryへ接続されているか検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOW_PATH = ROOT / "_phase4_proofread/FACTORY_FLOW_CONTRACT.json"
WORKFLOW_PATH = ROOT / ".github/workflows/translation-factory-encode.yml"
ADAPTER_REL = "_tools/refresh_owner_assignment_state_digests.py"
ADAPTER_PATH = ROOT / ADAPTER_REL


def main() -> int:
    errors: list[str] = []
    try:
        flow = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        adapter = ADAPTER_PATH.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    action = flow.get("actions", {}).get("encode_recorded_decisions", {})
    if action.get("post_feedback_attestation_adapter") != ADAPTER_REL:
        errors.append("factory flow post_feedback_attestation_adapter mismatch")

    feedback_marker = "python _tools/source_document_feedback.py"
    refresh_marker = "python _tools/refresh_owner_assignment_state_digests.py"
    owner_check_marker = "python _tools/check_owner_assignment_result.py"
    positions = [workflow.find(marker) for marker in (feedback_marker, refresh_marker, owner_check_marker)]
    if any(position < 0 for position in positions):
        errors.append("encoding workflow lacks source feedback, attestation refresh, or owner checker")
    elif not positions[0] < positions[1] < positions[2]:
        errors.append("encoding workflow must refresh owner state attestation after feedback and before owner verification")

    for marker in (
        "unexpected state drift after owner assignment",
        "source_document_feedback_record",
        "post_feedback_state_attestation",
        "atomic_write_json",
    ):
        if marker not in adapter:
            errors.append(f"attestation refresh adapter lacks marker: {marker}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: post-feedback owner state attestation refresh is wired and fail-closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
