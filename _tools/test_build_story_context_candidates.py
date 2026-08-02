# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import build_story_context_candidates as B


def fk(target: str, namespace: str, key: str) -> str:
    return "\x1f".join((target, namespace, key))


class CandidateBuilderTests(unittest.TestCase):
    def source(self) -> dict[str, str]:
        return {
            fk("Quests任务表", "Quests", "100_Name"): "0 - 系统 $@$白鹿旧事",
            fk("Quests任务表", "Quests", "100_RequestDlgs_Index0_Text"): "1 - 宇文逸 $@$我们去找白鹿。",
            fk("Quests任务表", "Quests", "100_FinishingDlgs_Index0_Text"): "1 - 宇文逸 $@$我们去找白鹿。",
            fk("Quests任务表", "Quests", "200_Name"): "0 - 系统 $@$白鹿旧事",
            fk("CG表", "QuestDlgs", "100_1_Dlgs_Index0_Text"): "1 - 宇文逸 $@$同一数字根。",
            fk("CG表", "QuestDlgs", "300_2_Dlgs_Index0_Text"): "1 - 宇文逸 $@$我们去找白鹿。",
            fk("CG表", "QuestDlgs", "400_1_Dlgs_Index0_Text"): "2 - 莫問 $@$白鹿旧事仍未结束。",
        }

    def inventory(self):
        source = self.source()
        raw = json.dumps(source, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return B.build_inventory(source, "_phase4_proofread/source_zh.json", hashlib.sha256(raw).hexdigest())

    def test_candidate_reasons_without_order(self):
        inventory = self.inventory()
        links = {
            (row["quest_id"], row["scene_family_id"]): set(row["reasons"])
            for row in inventory["candidate_links"]
        }
        self.assertIn("same_numeric_root", links[("100", "100_1")])
        self.assertIn("shared_dialogue_fingerprint", links[("100", "300_2")])
        self.assertIn("quest_title_mention", links[("100", "400_1")])
        self.assertIn("quest_title_mention", links[("200", "400_1")])
        self.assertFalse(inventory["policy"]["ordering_declared"])
        self.assertFalse(inventory["policy"]["formal_reference_allowed"])
        self.assertTrue(all(row["order_inference_allowed"] is False for row in inventory["candidate_links"]))

    def test_duplicate_title_cluster(self):
        inventory = self.inventory()
        cluster = inventory["duplicate_title_clusters"][0]
        self.assertEqual(cluster["title"], "白鹿旧事")
        self.assertEqual(cluster["quest_ids"], ["100", "200"])

    def test_deterministic_output(self):
        source = self.source()
        digest = hashlib.sha256(b"fixture").hexdigest()
        first = B.build_inventory(source, "source.json", digest)
        second = B.build_inventory(dict(reversed(list(source.items()))), "source.json", digest)
        self.assertEqual(first, second)

    def test_malformed_full_key_blocks(self):
        with self.assertRaisesRegex(B.CandidateBuildError, "malformed source key"):
            B.build_inventory({"bad": "1 - A $@$x"}, "source.json", hashlib.sha256(b"x").hexdigest())

    def test_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_path = root / "source.json"
            output_path = root / "candidate.json"
            source_path.write_text(json.dumps(self.source(), ensure_ascii=False), encoding="utf-8")
            source = B.load_source(source_path)
            inventory = B.build_inventory(
                source,
                source_path.as_posix(),
                hashlib.sha256(source_path.read_bytes()).hexdigest(),
            )
            B.write_inventory(output_path, inventory)
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["summary"]["quest_group_count"], 2)
            self.assertEqual(loaded["summary"]["scene_family_count"], 3)


if __name__ == "__main__":
    unittest.main()
