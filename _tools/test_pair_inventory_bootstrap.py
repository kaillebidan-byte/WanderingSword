# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pair_inventory_bootstrap as B


PREVIOUS = "宇文逸↔莫問"
NEXT = "宇文逸↔莫棄"


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class BootstrapTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        p4 = root / "_phase4_proofread"
        p4.mkdir()
        current = {
            "current_cluster": "wudang_core",
            "current_pair": PREVIOUS,
            "checkpoint": {
                "status": "verified",
                "batch": 213,
                "pair_applied_keys": 1438,
                "project_applied_keys": 1814,
            },
            "ci_train": {"transport_status": "merged"},
        }
        state = {
            "cycle_control": {
                "status": "paused",
                "stop_reason": "pair_scope_exhausted",
                "last_safe_checkpoint": "merged_pair_complete",
            },
            "transport": {"status": "merged"},
        }
        manifest = {"transport": {"status": "merged", "pr": 239}}
        packet = {
            "current_pair": PREVIOUS,
            "scene_groups": [B.PAIR_SENTINEL],
            "pair_completion": {"status": "complete", "pair": PREVIOUS},
        }
        audit = {
            "queue": [
                {
                    "id": "wudang_core",
                    "pairs": [PREVIOUS, NEXT, "宇文逸↔元啓"],
                }
            ],
            "pair_status": {PREVIOUS: {"pair_completion_checkpoint": {"batch": 213}}},
            "current": {"cluster": "wudang_core", "pair": PREVIOUS},
        }
        queue = {
            "schema_version": 2,
            "current": "yuwen_mowen",
            "items": [
                {
                    "id": "yuwen_mowen",
                    "left": {"name": "宇文逸", "aliases": ["宇文逸"]},
                    "right": {"name": "莫問", "aliases": ["莫問", "莫问"]},
                    "status": "high_confidence_pass_complete",
                }
            ],
        }
        request = {
            "schema_version": 1,
            "contract_id": B.CONTRACT_ID,
            "expected_controller_action": B.EXPECTED_ACTION,
            "date": "2026-08-01",
            "previous_pair": PREVIOUS,
            "next_pair": NEXT,
            "relation": {
                "id": "yuwen_moqi",
                "left": {"name": "宇文逸", "aliases": ["宇文逸"]},
                "right": {"name": "莫棄", "aliases": ["莫弃", "莫棄"]},
                "left_to_right_markers": ["莫棄", "莫棄師兄"],
                "right_to_left_markers": ["小逸", "宇文逸"],
                "direct_exchange_inventory_markers": ["莫棄", "小逸", "師兄"],
                "status": "extracting",
                "notes": ["primary evidence first"],
                "audit_questions": ["呼称はどう変わるか"],
            },
            "output": {
                "record": "_phase4_proofread/PAIR_INVENTORY_YUWEN_MOQI_2026-08-01.json"
            },
        }
        for name, value in (
            ("CURRENT_WORK.json", current),
            ("PRIVATE_STAGE_STATE.json", state),
            ("CI_TRAIN_MANIFEST.json", manifest),
            ("NEXT_TASK_PACKET.json", packet),
            ("audit_status.json", audit),
            ("relation_audit_queue.json", queue),
        ):
            write_json(p4 / name, value)
        request_path = root / "_pair_inventory_requests/bootstrap-yuwen-moqi.json"
        write_json(request_path, request)
        return temporary, root, request_path

    def report(self):
        return {
            "schema_version": 2,
            "relation": {
                "id": "yuwen_moqi",
                "left": {"name": "宇文逸"},
                "right": {"name": "莫棄"},
            },
            "counts": {
                "raw_groups": 3,
                "unique_groups": 2,
                "duplicate_groups": 1,
                "direct_exchange_groups": 1,
                "explicit_reference_groups": 1,
                "unique_rows": 7,
                "duplicate_locations": 1,
            },
            "speaker_inventory": {"宇文逸": 3, "莫棄": 2},
            "selection_marker_inventory": {"小逸": 1},
            "direct_exchange_marker_inventory": {"師兄": 1},
            "groups": [{"family": "a"}, {"family": "b"}],
        }

    def args(self):
        return SimpleNamespace(
            relation_id="yuwen_moqi",
            artifact_run=123,
            artifact_id=456,
            artifact_name="pair-inventory-yuwen-moqi",
            artifact_digest="sha256:" + "a" * 64,
            artifact_head="b" * 40,
        )

    def test_prepare_and_finalize(self):
        temporary, root, request_path = self.fixture()
        self.addCleanup(temporary.cleanup)
        prepared = B.prepare(root, request_path)
        self.assertEqual(prepared["next_pair"], NEXT)
        queue = B.load_object(root / "_phase4_proofread/relation_audit_queue.json")
        self.assertEqual(queue["current"], "yuwen_moqi")
        report_path = root / "_ws_tmp/report.json"
        write_json(report_path, self.report())
        result = B.finalize(root, request_path, report_path, self.args())
        self.assertEqual(result["counts"]["unique_rows"], 7)
        state = B.load_object(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json")
        self.assertEqual(state["cycle_control"]["last_safe_checkpoint"], "pair_inventory_ready")
        self.assertEqual(state["pair_transition"]["next_pair"], NEXT)
        current = B.load_object(root / "_phase4_proofread/CURRENT_WORK.json")
        self.assertEqual(current.get("current_pair"), PREVIOUS)
        self.assertEqual(current["next_pair_inventory"]["next_pair"], NEXT)
        audit = B.load_object(root / "_phase4_proofread/audit_status.json")
        self.assertEqual(audit["pair_status"][NEXT]["evidence_inventory"], "complete")
        handoff = (root / "_phase4_proofread/CURRENT_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("PR #239: merged", handoff)

    def test_missing_merged_pr_fails(self):
        temporary, root, request_path = self.fixture()
        self.addCleanup(temporary.cleanup)
        B.prepare(root, request_path)
        manifest_path = root / "_phase4_proofread/CI_TRAIN_MANIFEST.json"
        manifest = B.load_object(manifest_path)
        manifest["transport"].pop("pr")
        write_json(manifest_path, manifest)
        report_path = root / "_ws_tmp/report.json"
        write_json(report_path, self.report())
        with self.assertRaisesRegex(B.BootstrapError, "merged PR evidence missing"):
            B.finalize(root, request_path, report_path, self.args())

    def test_wrong_next_pair_fails(self):
        temporary, root, request_path = self.fixture()
        self.addCleanup(temporary.cleanup)
        request = B.load_object(request_path)
        request["next_pair"] = "宇文逸↔元啓"
        request["relation"]["right"]["name"] = "元啓"
        write_json(request_path, request)
        with self.assertRaisesRegex(B.BootstrapError, "not deterministic"):
            B.prepare(root, request_path)

    def test_unmerged_transport_fails(self):
        temporary, root, request_path = self.fixture()
        self.addCleanup(temporary.cleanup)
        state_path = root / "_phase4_proofread/PRIVATE_STAGE_STATE.json"
        state = B.load_object(state_path)
        state["transport"]["status"] = "verified"
        write_json(state_path, state)
        with self.assertRaisesRegex(B.BootstrapError, "merged transport"):
            B.prepare(root, request_path)

    def test_non_paused_checkpoint_fails(self):
        temporary, root, request_path = self.fixture()
        self.addCleanup(temporary.cleanup)
        state_path = root / "_phase4_proofread/PRIVATE_STAGE_STATE.json"
        state = B.load_object(state_path)
        state["cycle_control"]["status"] = "target_reached"
        write_json(state_path, state)
        with self.assertRaisesRegex(B.BootstrapError, "paused merged_pair_complete"):
            B.prepare(root, request_path)

    def test_empty_report_fails(self):
        temporary, root, request_path = self.fixture()
        self.addCleanup(temporary.cleanup)
        B.prepare(root, request_path)
        report = self.report()
        report["counts"]["raw_groups"] = 0
        report["counts"]["unique_groups"] = 0
        report["counts"]["duplicate_groups"] = 0
        report["counts"]["direct_exchange_groups"] = 0
        report["counts"]["explicit_reference_groups"] = 0
        report["counts"]["unique_rows"] = 0
        report["groups"] = []
        report_path = root / "_ws_tmp/report.json"
        write_json(report_path, report)
        with self.assertRaisesRegex(B.BootstrapError, "must contain evidence"):
            B.finalize(root, request_path, report_path, self.args())


if __name__ == "__main__":
    unittest.main()
