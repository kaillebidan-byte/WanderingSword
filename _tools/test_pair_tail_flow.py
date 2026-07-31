#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pair_tail_common import TailError, validate_exact_tail
from pair_tail_post_merge import EXACT_NEXT, seal

ROOT = Path(__file__).resolve().parent.parent


class PairTailFlowTests(unittest.TestCase):
    def artifact(self):
        return {
            "groups": [
                {
                    "family": "reviewed_Dlgs",
                    "kind": "explicit_reference",
                    "target": "CG表",
                    "ns": "QuestDlgs",
                    "rows": [{"key": "reviewed_Dlgs_Index0_Text", "speaker": "宇文逸", "zh": "z", "ja": "j"}],
                },
                {
                    "family": "tail_Dlgs",
                    "kind": "explicit_reference",
                    "target": "CG表",
                    "ns": "QuestDlgs",
                    "rows": [{"key": "tail_Dlgs_Index0_Text", "speaker": "宇文逸", "zh": "z", "ja": "j"}],
                },
                {
                    "family": "tail_RequestDlgs_Index0_Text",
                    "kind": "explicit_reference",
                    "target": "Quests任务表",
                    "ns": "Quests",
                    "rows": [{"key": "tail_RequestDlgs_Index0_Text", "speaker": "宇文逸", "zh": "z", "ja": "j"}],
                },
                {
                    "family": "ordinary_Dlgs",
                    "kind": "co_presence",
                    "target": "CG表",
                    "ns": "QuestDlgs",
                    "rows": [{"key": "ordinary_Dlgs_Index0_Text", "speaker": "宇文逸", "zh": "z", "ja": "j"}],
                },
            ]
        }

    def fixture(self, *, include_non_explicit: bool = False):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        p4 = root / "_phase4_proofread"
        p4.mkdir()
        rows = [{"key": "reviewed_Dlgs_Index0_Text"}]
        if include_non_explicit:
            rows.append({"key": "ordinary_Dlgs_Index0_Text"})
        candidate = p4 / "CANDIDATE_REVIEWED.json"
        candidate.write_text(json.dumps({"rows": rows}), encoding="utf-8")
        return temporary, root, candidate.relative_to(root).as_posix()

    def completion_fixture(self, *, merged: bool = True):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        p4 = root / "_phase4_proofread"
        p4.mkdir()
        status = "merged" if merged else "awaiting_private_merge"
        values = {
            "CURRENT_WORK.json": {
                "current_pair": "宇文逸↔莫問",
                "checkpoint": {
                    "batch": 213,
                    "pair_applied_keys": 1438,
                    "project_applied_keys": 1814,
                    "release_identity": {"release_id": "yuwen-mowen-train-81-r1"},
                },
                "ci_train": {
                    "transport_status": status,
                    "private_stage": {"cycle_status": "target_reached", "cycle_checkpoint": "merged"},
                },
                "immediate_next": {},
            },
            "PRIVATE_STAGE_STATE.json": {
                "cycle_control": {"status": "target_reached", "exact_next_action": None},
                "transport": {"status": status},
            },
            "CI_TRAIN_MANIFEST.json": {
                "train_id": "yuwen-mowen-train-81",
                "transport": {"status": status, "pr": 239},
                "next_release": {"reservation_status": "pair_complete_pending_merge"},
            },
            "NEXT_TASK_PACKET.json": {
                "release_candidate": {"status": status},
                "pair_completion": {
                    "status": "complete",
                    "pair": "宇文逸↔莫問",
                    "reason": "explicit_reference_tail_exhausted",
                    "remaining_explicit_reference_rows": 0,
                    "transition": "post_merge_pair_completion_checkpoint",
                },
            },
            "audit_status.json": {"pair_status": {"宇文逸↔莫問": {}}},
        }
        for name, value in values.items():
            (p4 / name).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return temporary, p4

    def packets(self):
        return [
            {"target": "CG表", "namespace": "QuestDlgs", "families": ["tail_Dlgs"]},
            {"target": "Quests任务表", "namespace": "Quests", "families": ["tail_RequestDlgs_Index0_Text"]},
        ]

    def test_exact_residual_accepts_target_separated_packets(self):
        temporary, root, candidate = self.fixture()
        self.addCleanup(temporary.cleanup)
        packets = validate_exact_tail(self.artifact(), root, [candidate], self.packets())
        self.assertEqual(sum(len(rows) for _, rows in packets), 2)
        self.assertEqual(packets[0][1][0]["namespace"], "QuestDlgs")
        self.assertEqual(packets[1][1][0]["namespace"], "Quests")

    def test_non_explicit_reviewed_rows_do_not_pollute_coverage(self):
        temporary, root, candidate = self.fixture(include_non_explicit=True)
        self.addCleanup(temporary.cleanup)
        packets = validate_exact_tail(self.artifact(), root, [candidate], self.packets())
        self.assertEqual(sum(len(rows) for _, rows in packets), 2)

    def test_omitted_residual_key_fails_closed(self):
        temporary, root, candidate = self.fixture()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(TailError, "must equal exact"):
            validate_exact_tail(self.artifact(), root, [candidate], self.packets()[:1])

    def test_mixed_target_packet_fails_closed(self):
        temporary, root, candidate = self.fixture()
        self.addCleanup(temporary.cleanup)
        packets = [{"target": "CG表", "namespace": "QuestDlgs", "families": ["tail_Dlgs", "tail_RequestDlgs_Index0_Text"]}]
        with self.assertRaisesRegex(TailError, "target/namespace mismatch"):
            validate_exact_tail(self.artifact(), root, [candidate], packets)

    def test_merged_pair_completion_is_sealed_once(self):
        temporary, p4 = self.completion_fixture()
        self.addCleanup(temporary.cleanup)
        self.assertTrue(seal(p4))
        state = json.loads((p4 / "PRIVATE_STAGE_STATE.json").read_text(encoding="utf-8"))
        manifest = json.loads((p4 / "CI_TRAIN_MANIFEST.json").read_text(encoding="utf-8"))
        audit = json.loads((p4 / "audit_status.json").read_text(encoding="utf-8"))
        handoff = (p4 / "CURRENT_HANDOFF.md").read_text(encoding="utf-8")
        self.assertEqual(state["cycle_control"]["status"], "paused")
        self.assertEqual(state["cycle_control"]["exact_next_action"], EXACT_NEXT)
        self.assertEqual(manifest["next_release"]["reservation_status"], "pair_complete")
        self.assertEqual(
            audit["pair_status"]["宇文逸↔莫問"]["residual_candidates"],
            "none_in_explicit_reference_artifact",
        )
        self.assertIn("paused / merged_pair_complete", handoff)
        self.assertFalse(seal(p4))

    def test_unmerged_pair_completion_is_noop(self):
        temporary, p4 = self.completion_fixture(merged=False)
        self.addCleanup(temporary.cleanup)
        self.assertFalse(seal(p4))
        state = json.loads((p4 / "PRIVATE_STAGE_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["cycle_control"]["status"], "target_reached")

    def test_registered_files_exist(self):
        required = [
            "_phase4_proofread/PAIR_TAIL_FLOW_CONTRACT.json",
            "_tools/pair_tail_common.py",
            "_tools/pair_tail_initializer.py",
            "_tools/pair_tail_quality_context.py",
            "_tools/pair_tail_encoding_pipeline.py",
            "_tools/pair_tail_release_finalizer.py",
            "_tools/pair_tail_post_merge.py",
            ".github/workflows/reconcile-merged-cycle.yml",
            ".github/workflows/translation-tail-execute.yml",
            ".github/workflows/translation-tail-encode.yml",
            ".github/workflows/translation-tail-finalize.yml",
            ".github/workflows/translation-tail-post-merge.yml",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
