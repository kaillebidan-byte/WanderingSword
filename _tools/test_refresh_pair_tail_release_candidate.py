#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from refresh_pair_tail_release_candidate import RefreshError, refresh


class RefreshPairTailReleaseCandidateTests(unittest.TestCase):
    def fixture(self, *, packet_train: str = "yuwen-mowen-train-81"):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        p4 = root / "_phase4_proofread"
        p4.mkdir()
        values = {
            "CURRENT_WORK.json": {
                "ci_train": {
                    "train_id": "yuwen-mowen-train-81",
                    "draft_pr": 239,
                    "status": "ready_for_public_ci",
                    "transport_status": "ready_for_public_ci"
                }
            },
            "CI_TRAIN_MANIFEST.json": {
                "train_id": "yuwen-mowen-train-81",
                "draft_pr": 239,
                "status": "ready_for_public_ci",
                "transport": {"status": "ready_for_public_ci"}
            },
            "PRIVATE_STAGE_STATE.json": {
                "train_id": "yuwen-mowen-train-81",
                "stage": "translation_frozen",
                "transport": {"status": "ready_for_public_ci", "pr": 239}
            },
            "NEXT_TASK_PACKET.json": {
                "reservation": {"status": "encoded"},
                "ci_train": {"train_id": packet_train},
                "release_candidate": {
                    "train_id": "yuwen-mowen-train-80",
                    "release_id": "yuwen-mowen-train-80-r1",
                    "pr": 237,
                    "status": "merged"
                }
            }
        }
        for name, value in values.items():
            (p4 / name).write_text(json.dumps(value), encoding="utf-8")
        return temporary, p4

    def test_refresh_replaces_stale_lineage(self):
        temporary, p4 = self.fixture()
        self.addCleanup(temporary.cleanup)
        result = refresh(p4)
        self.assertEqual(
            result,
            {
                "train_id": "yuwen-mowen-train-81",
                "release_id": "yuwen-mowen-train-81-r1",
                "pr": 239,
                "status": "ready_for_public_ci"
            },
        )
        packet = json.loads((p4 / "NEXT_TASK_PACKET.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["release_candidate"], result)

    def test_packet_train_mismatch_fails_closed(self):
        temporary, p4 = self.fixture(packet_train="yuwen-mowen-train-80")
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(RefreshError, "packet train lineage mismatch"):
            refresh(p4)

    def test_not_ready_state_fails_closed(self):
        temporary, p4 = self.fixture()
        self.addCleanup(temporary.cleanup)
        current = json.loads((p4 / "CURRENT_WORK.json").read_text(encoding="utf-8"))
        current["ci_train"]["status"] = "accumulating"
        (p4 / "CURRENT_WORK.json").write_text(json.dumps(current), encoding="utf-8")
        with self.assertRaisesRegex(RefreshError, "not ready"):
            refresh(p4)


if __name__ == "__main__":
    unittest.main()
