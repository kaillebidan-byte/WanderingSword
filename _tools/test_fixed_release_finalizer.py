#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "fixed_release_finalizer", ROOT / "fixed_release_finalizer.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fixture(p4: Path) -> tuple[dict, dict, str]:
    train_id = "yuwen-mowen-train-27"
    branch = "agent/yuwen-mowen-train-27"
    pr = 166
    ci_head = "1" * 40
    asset_head = "2" * 40
    current = {
        "schema_version": 8,
        "updated_at": "2026-07-28",
        "translation_base_commit": "3" * 40,
        "state_base_commit": "4" * 40,
        "current_cluster": "wudang_core",
        "current_pair": "宇文逸↔莫問",
        "stage": "translation_reaudit_in_progress",
        "status": "verified",
        "last_completed_batch": 157,
        "last_reviewed_batch": 157,
        "pair_applied_keys": 1351,
        "project_applied_keys": 1727,
        "build_status": "verified_not_deployed",
        "game_verified": "not_started",
        "last_merged_translation_pr": 162,
        "checkpoint": {},
        "operation_mode": {},
        "pr_continuity": {},
        "session_bootstrap": {},
        "mandatory_read_order": [],
        "ci_train": {
            "phase": "phase1_wave",
            "train_id": train_id,
            "branch": branch,
            "draft_pr": pr,
            "status": "ready_for_public_ci",
            "transport_status": "ready_for_public_ci",
            "private_stage": {
                "stage": "translation_frozen",
                "status": "complete",
                "transport_status": "ready_for_public_ci",
                "cycle_status": "running",
                "cycle_checkpoint": "ready_for_public_ci",
            },
            "totals": {
                "bundle_count": 1,
                "reviewed_rows": 62,
                "fix_keys": 3,
            },
        },
        "release_evidence": "old",
    }
    state = {
        "train_id": train_id,
        "stage": "translation_frozen",
        "cycle_control": {},
        "wave": {
            "packets": [
                {"review_record": {"apply_status": "pending"}}
            ]
        },
        "transport": {
            "status": "ready_for_public_ci",
            "pr": pr,
            "history": [{"status": "ready_for_public_ci", "pr": pr}],
        },
    }
    manifest = {
        "schema_version": 2,
        "phase": "phase1_wave",
        "train_id": train_id,
        "branch": branch,
        "draft_pr": pr,
        "status": "ready_for_public_ci",
        "transport": {"status": "ready_for_public_ci", "pr": pr},
        "bundles": [
            {
                "batch": 158,
                "apply_status": "pending",
                "scene_groups": ["5296_7", "5302_4"],
                "keep_keys": 59,
            }
        ],
        "totals": {
            "bundle_count": 1,
            "reviewed_rows": 62,
            "fix_keys": 3,
        },
        "private_stage": {
            "status": "complete",
            "transport_status": "ready_for_public_ci",
        },
        "next_release": {},
    }
    audit = {
        "project": {
            "latest_build": {
                "applied_keys": 1727,
                "record_index": [
                    "_phase4_proofread/APPLIED_FIXES_YUWEN_MOWEN_BATCH158_2026-07-29.md"
                ],
            }
        },
        "pair_status": {"宇文逸↔莫問": {"applied_keys": 1351}},
    }
    for name, value in (
        ("CURRENT_WORK.json", current),
        ("PRIVATE_STAGE_STATE.json", state),
        ("CI_TRAIN_MANIFEST.json", manifest),
        ("audit_status.json", audit),
    ):
        write_json(p4 / name, value)
    (p4 / "APPLIED_FIXES_YUWEN_MOWEN_BATCH158_2026-07-29.md").write_text(
        "ok\n", encoding="utf-8"
    )
    request = {
        "schema_version": 1,
        "contract_id": "release-finalization-request-v1",
        "operation": "finalize_release_state",
        "executor": "fixed_release_finalizer",
        "branch": branch,
        "pr": pr,
        "orchestrator_run_id": 10,
        "ci_head": ci_head,
        "asset_head": asset_head,
        "apply_changed": True,
        "date": "2026-07-29",
        "next_scene": "5331_2",
        "next_source": {
            "artifact_workflow": "Release train orchestrator",
            "artifact_name": "relation-audit-evidence",
            "artifact_file": "yuwen_mowen.json",
            "artifact_run": 10,
            "artifact_id": 11,
            "artifact_digest": "sha256:test",
            "artifact_head": ci_head,
            "freshness_rule": "統合後の次cycle開始時に再確認する。",
        },
        "notes": ["fixture"],
    }
    artifact = {
        "schema_version": 1,
        "pr": pr,
        "orchestrator_run_id": 10,
        "ci_head": ci_head,
        "asset_head": asset_head,
        "apply_changed": True,
    }
    return request, artifact, branch


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        p4 = root / "_phase4_proofread"
        p4.mkdir()
        request, artifact, branch = fixture(p4)
        result = MODULE.finalize(request, artifact, branch=branch, p4=p4)

        assert result["batch"] == 158
        assert result["next_scene"] == "5331_2"
        assert result["transport_status"] == "awaiting_private_merge"

        current = json.loads((p4 / "CURRENT_WORK.json").read_text(encoding="utf-8"))
        assert current["checkpoint"]["status"] == "verified"
        assert current["checkpoint"]["batch"] == 158
        assert current["ci_train"]["transport_status"] == "awaiting_private_merge"
        assert current["release_evidence"].endswith("_TRAIN_27.json")

        state = json.loads(
            (p4 / "PRIVATE_STAGE_STATE.json").read_text(encoding="utf-8")
        )
        assert state["transport"]["status"] == "awaiting_private_merge"
        assert state["verified_result"]["asset_head"] == "2" * 40
        assert state["wave"]["packets"][0]["review_record"]["apply_status"] == "verified"

        manifest = json.loads(
            (p4 / "CI_TRAIN_MANIFEST.json").read_text(encoding="utf-8")
        )
        assert manifest["status"] == "verified"
        assert manifest["bundles"][0]["apply_status"] == "verified"
        assert manifest["next_release"]["candidate_scene"] == ["5331_2"]

        packet = json.loads(
            (p4 / "NEXT_TASK_PACKET.json").read_text(encoding="utf-8")
        )
        assert packet["reservation"]["status"] == "reserved_only"
        assert packet["scene_groups"] == ["5331_2"]
        assert "batch_planning" not in packet

        handoff = (p4 / "CURRENT_HANDOFF.md").read_text(encoding="utf-8")
        assert "現状把握して作業の続きを" in handoff
        assert "awaiting_private_merge" in handoff
        assert "5331_2" in handoff

        evidence = json.loads(
            (p4 / "RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_27.json").read_text(
                encoding="utf-8"
            )
        )
        assert evidence["asset_head"] == "2" * 40
        assert evidence["counts"]["pending_fixes"] == 0

        bad_artifact = dict(artifact)
        bad_artifact["asset_head"] = "9" * 40
        try:
            MODULE.validate_inputs(request, bad_artifact, branch)
        except MODULE.FinalizerError:
            pass
        else:
            raise AssertionError("artifact mismatch must fail")

    print("test_fixed_release_finalizer: OK")


if __name__ == "__main__":
    main()
