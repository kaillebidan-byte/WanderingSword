#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import refresh_owner_assignment_state_digests as refresh


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fixture() -> Path:
    root = Path(tempfile.mkdtemp())
    p4 = root / "_phase4_proofread"
    manifest = {"train_id": "train-40", "status": "ready_for_public_ci"}
    current = {"ci_train": {"train_id": "train-40", "status": "ready_for_public_ci"}}
    state = {"wave": {"packets": [{"packet_id": "p1"}]}}
    write_json(p4 / "CI_TRAIN_MANIFEST.json", manifest)
    write_json(p4 / "CURRENT_WORK.json", current)
    write_json(p4 / "PRIVATE_STAGE_STATE.json", state)
    stored = {
        path.relative_to(root).as_posix(): refresh.digest_file(path)
        for path in (
            p4 / "CI_TRAIN_MANIFEST.json",
            p4 / "PRIVATE_STAGE_STATE.json",
            p4 / "CURRENT_WORK.json",
        )
    }
    write_json(
        p4 / "OWNER_ASSIGNMENT_RESULT.json",
        {
            "schema_version": 1,
            "generated_by": "_tools/apply_owner_assignment_v2.py",
            "state_file_digests": stored,
        },
    )
    record = "_phase4_proofread/SOURCE_DOCUMENT_FEEDBACK_TRAIN40.json"
    write_json(root / record, {"status": "applied"})
    state["wave"]["packets"][0]["source_document_feedback_record"] = {
        "status": "complete",
        "record": record,
    }
    write_json(p4 / "PRIVATE_STAGE_STATE.json", state)
    return root


def expect_failure(root: Path, marker: str) -> None:
    try:
        refresh.refresh(root)
    except refresh.RefreshError as exc:
        assert marker in str(exc), str(exc)
    else:
        raise AssertionError(f"expected failure: {marker}")


def main() -> None:
    root = fixture()
    summary = refresh.refresh(root)
    assert summary["status"] == "refreshed"
    assert summary["changed_paths"] == [refresh.ALLOWED_CHANGED_PATH]
    result = refresh.load_object(root / "_phase4_proofread/OWNER_ASSIGNMENT_RESULT.json")
    current_state_digest = refresh.digest_file(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json")
    assert result["state_file_digests"][refresh.ALLOWED_CHANGED_PATH] == current_state_digest
    assert result["post_feedback_state_attestation"]["adapter"] == refresh.ADAPTER
    assert refresh.refresh(root)["status"] == "already_current"

    root = fixture()
    current_path = root / "_phase4_proofread/CURRENT_WORK.json"
    current = refresh.load_object(current_path)
    current["unexpected"] = True
    write_json(current_path, current)
    expect_failure(root, "unexpected state drift")

    root = fixture()
    state_path = root / "_phase4_proofread/PRIVATE_STAGE_STATE.json"
    state = refresh.load_object(state_path)
    state["wave"]["packets"][0].pop("source_document_feedback_record")
    write_json(state_path, state)
    expect_failure(root, "lacks complete source feedback record")

    root = fixture()
    result_path = root / "_phase4_proofread/OWNER_ASSIGNMENT_RESULT.json"
    result = refresh.load_object(result_path)
    result["generated_by"] = "unexpected"
    write_json(result_path, result)
    expect_failure(root, "generated_by mismatch")

    root = fixture()
    result_path = root / "_phase4_proofread/OWNER_ASSIGNMENT_RESULT.json"
    result = refresh.load_object(result_path)
    result["state_file_digests"].pop("_phase4_proofread/CURRENT_WORK.json")
    write_json(result_path, result)
    expect_failure(root, "path set mismatch")

    print("test_refresh_owner_assignment_state_digests: OK")


if __name__ == "__main__":
    main()
