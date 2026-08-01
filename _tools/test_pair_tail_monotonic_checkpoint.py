#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pair_tail_common import TailError
from pair_tail_post_merge import INVENTORY_CHECKPOINT, INVENTORY_STATUS, seal


PAIR = "宇文逸↔莫問"
NEXT_PAIR = "宇文逸↔莫棄"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class PairTailMonotonicCheckpointTests(unittest.TestCase):
    def fixture(self, *, partial: bool = False):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        p4 = root / "_phase4_proofread"
        p4.mkdir()
        transition = {
            "status": INVENTORY_STATUS,
            "previous_pair": PAIR,
            "next_pair": NEXT_PAIR,
            "relation_id": "yuwen_moqi",
            "inventory_record": "_phase4_proofread/PAIR_INVENTORY_YUWEN_MOQI_2026-08-01.json",
            "translation_started": False,
        }
        current = {
            "current_pair": PAIR,
            "checkpoint": {
                "batch": 213,
                "pair_applied_keys": 1438,
                "project_applied_keys": 1814,
                "release_identity": {"release_id": "yuwen-mowen-train-81-r1"},
            },
            "ci_train": {
                "transport_status": "merged",
                "private_stage": {
                    "cycle_status": "pair_complete",
                    "cycle_checkpoint": "merged_pair_complete",
                },
            },
            "next_pair_inventory": dict(transition),
            "immediate_next": {"task": "inventory-ready task"},
        }
        state = {
            "cycle_control": {
                "status": "paused" if not partial else "target_reached",
                "stop_reason": "pair_inventory_bootstrapped" if not partial else None,
                "last_safe_checkpoint": INVENTORY_CHECKPOINT if not partial else "merged_pair_complete",
                "exact_next_action": "inventory-ready action",
            },
            "transport": {"status": "merged"},
        }
        if not partial:
            state["pair_transition"] = dict(transition)
        manifest = {
            "train_id": "yuwen-mowen-train-81",
            "transport": {"status": "merged", "pr": 239},
            "next_release": {"reservation_status": "pair_complete"},
        }
        packet = {
            "release_candidate": {"status": "merged"},
            "pair_completion": {"status": "complete", "pair": PAIR},
            "next_pair_inventory": dict(transition),
            "do_not_do": ["inventory-ready prohibition"],
        }
        if not partial:
            manifest["pair_transition"] = dict(transition)
        values = {
            "CURRENT_WORK.json": current,
            "PRIVATE_STAGE_STATE.json": state,
            "CI_TRAIN_MANIFEST.json": manifest,
            "NEXT_TASK_PACKET.json": packet,
            "audit_status.json": {"pair_status": {PAIR: {}, NEXT_PAIR: {"evidence_inventory": "complete"}}},
        }
        for name, value in values.items():
            write_json(p4 / name, value)
        (p4 / "CURRENT_HANDOFF.md").write_text("inventory-ready handoff\n", encoding="utf-8")
        return temporary, p4

    def test_later_inventory_checkpoint_is_noop_and_byte_stable(self):
        temporary, p4 = self.fixture()
        self.addCleanup(temporary.cleanup)
        paths = sorted(p4.iterdir())
        before = {path.name: path.read_bytes() for path in paths}
        self.assertFalse(seal(p4))
        after = {path.name: path.read_bytes() for path in paths}
        self.assertEqual(after, before)

    def test_partial_inventory_checkpoint_fails_closed(self):
        temporary, p4 = self.fixture(partial=True)
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(TailError, "downstream pair inventory checkpoint"):
            seal(p4)


if __name__ == "__main__":
    unittest.main()
