#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人物資料還流後の状態正本をowner assignment証跡へ決定的に再封印する。"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
RESULT_PATH = P4 / "OWNER_ASSIGNMENT_RESULT.json"
STATE_PATHS = (
    P4 / "CI_TRAIN_MANIFEST.json",
    P4 / "PRIVATE_STAGE_STATE.json",
    P4 / "CURRENT_WORK.json",
)
ALLOWED_CHANGED_PATH = "_phase4_proofread/PRIVATE_STAGE_STATE.json"
ADAPTER = "_tools/refresh_owner_assignment_state_digests.py"


class RefreshError(ValueError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RefreshError(f"top level must be object: {path}")
    return value


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _feedback_records(state: dict[str, Any], root: Path) -> list[str]:
    packets = state.get("wave", {}).get("packets")
    if not isinstance(packets, list) or not packets:
        raise RefreshError("PRIVATE_STAGE_STATE wave packets are missing")
    records: list[str] = []
    for index, packet in enumerate(packets):
        if not isinstance(packet, dict):
            raise RefreshError(f"wave.packets[{index}] must be an object")
        marker = packet.get("source_document_feedback_record")
        if not isinstance(marker, dict) or marker.get("status") != "complete":
            raise RefreshError(f"wave.packets[{index}] lacks complete source feedback record")
        relative = marker.get("record")
        if not isinstance(relative, str) or not relative.startswith("_phase4_proofread/SOURCE_DOCUMENT_FEEDBACK_") or not relative.endswith(".json"):
            raise RefreshError(f"wave.packets[{index}] source feedback record path is invalid")
        if not (root / relative).is_file():
            raise RefreshError(f"source feedback record is missing: {relative}")
        records.append(relative)
    return sorted(set(records))


def refresh(root: Path = ROOT) -> dict[str, Any]:
    p4 = root / "_phase4_proofread"
    result_path = p4 / "OWNER_ASSIGNMENT_RESULT.json"
    state_paths = (
        p4 / "CI_TRAIN_MANIFEST.json",
        p4 / "PRIVATE_STAGE_STATE.json",
        p4 / "CURRENT_WORK.json",
    )
    result = load_object(result_path)
    if result.get("schema_version") not in {1, 2}:
        raise RefreshError("OWNER_ASSIGNMENT_RESULT schema_version must be 1 or 2")
    if result.get("generated_by") != "_tools/apply_owner_assignment_v2.py":
        raise RefreshError("OWNER_ASSIGNMENT_RESULT generated_by mismatch")

    stored = result.get("state_file_digests")
    if not isinstance(stored, dict):
        raise RefreshError("OWNER_ASSIGNMENT_RESULT.state_file_digests must be an object")
    current = {
        path.relative_to(root).as_posix(): digest_file(path)
        for path in state_paths
    }
    if set(stored) != set(current):
        raise RefreshError(
            "state_file_digests path set mismatch: "
            f"missing={sorted(set(current) - set(stored))} extra={sorted(set(stored) - set(current))}"
        )
    changed = sorted(path for path in current if stored[path] != current[path])
    unexpected = [path for path in changed if path != ALLOWED_CHANGED_PATH]
    if unexpected:
        raise RefreshError(f"unexpected state drift after owner assignment: {unexpected}")

    state = load_object(p4 / "PRIVATE_STAGE_STATE.json")
    records = _feedback_records(state, root)
    if not changed:
        return {
            "status": "already_current",
            "changed_paths": [],
            "feedback_records": records,
        }

    result["state_file_digests"] = current
    result["post_feedback_state_attestation"] = {
        "adapter": ADAPTER,
        "reason": "source_document_feedback_recorded_after_owner_assignment",
        "changed_paths": changed,
        "feedback_records": records,
    }
    atomic_write_json(result_path, result)
    return {
        "status": "refreshed",
        "changed_paths": changed,
        "feedback_records": records,
    }


def main() -> int:
    try:
        summary = refresh()
    except (OSError, json.JSONDecodeError, RefreshError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "owner_state_attestation_refresh_failed", "detail": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
