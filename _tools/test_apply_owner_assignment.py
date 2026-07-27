#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import apply_owner_assignment as target


class OwnerAssignmentTests(unittest.TestCase):
    def test_train15_regression_existing_38_new_12(self) -> None:
        packet1 = [
            "6151_2_Dlgs_Index0_Text", "6151_2_Dlgs_Index1_Text", "6151_2_Dlgs_Index2_Text",
            "6151_3_Dlgs_Index0_Text", "6151_3_Dlgs_Index1_Text", "6151_3_Dlgs_Index2_Text",
            "6151_3_Dlgs_Index3_Text", "6151_3_Dlgs_Index4_Text", "6151_3_Dlgs_Index5_Text",
            "6151_3_Dlgs_Index6_Text", "6151_3_Dlgs_Index8_Text", "6151_3_Dlgs_Index9_Text",
            "6151_3_Dlgs_Index10_Text", "6151_3_Dlgs_Index11_Text", "6151_3_Dlgs_Index12_Text",
            "6151_3_Dlgs_Index14_Text", "6151_3_Dlgs_Index15_Text", "6151_3_Dlgs_Index16_Text",
            "6151_3_Dlgs_Index17_Text", "6151_3_Dlgs_Index18_Text", "6151_3_Dlgs_Index19_Text",
            "6151_3_Dlgs_Index20_Text", "6151_3_Dlgs_Index21_Text", "6151_3_Dlgs_Index22_Text",
            "6151_3_Dlgs_Index23_Text",
        ]
        unowned1 = {
            "6151_2_Dlgs_Index1_Text", "6151_3_Dlgs_Index0_Text", "6151_3_Dlgs_Index9_Text",
            "6151_3_Dlgs_Index15_Text", "6151_3_Dlgs_Index16_Text", "6151_3_Dlgs_Index19_Text",
        }
        packet2 = [
            "6155_1_Dlgs_Index0_Text", "6155_1_Dlgs_Index1_Text", "6155_1_Dlgs_Index2_Text",
            "6155_1_Dlgs_Index3_Text", "6155_1_Dlgs_Index4_Text", "6155_3_Dlgs_Index0_Text",
            "6155_3_Dlgs_Index1_Text", "6155_3_Dlgs_Index2_Text", "6155_3_Dlgs_Index3_Text",
            "6155_3_Dlgs_Index5_Text", "6155_3_Dlgs_Index6_Text", "6155_3_Dlgs_Index7_Text",
            "6155_3_Dlgs_Index8_Text", "6155_3_Dlgs_Index9_Text", "6158_5_Dlgs_Index0_Text",
            "6158_5_Dlgs_Index1_Text", "6158_5_Dlgs_Index2_Text", "6158_5_Dlgs_Index3_Text",
            "6158_5_Dlgs_Index4_Text", "6158_5_Dlgs_Index5_Text", "6171_5_Dlgs_Index0_Text",
            "6171_5_Dlgs_Index1_Text", "6171_5_Dlgs_Index2_Text", "6171_5_Dlgs_Index3_Text",
            "6171_5_Dlgs_Index5_Text",
        ]
        unowned2 = {
            "6155_1_Dlgs_Index2_Text", "6155_3_Dlgs_Index0_Text", "6155_3_Dlgs_Index1_Text",
            "6158_5_Dlgs_Index1_Text", "6158_5_Dlgs_Index2_Text", "6171_5_Dlgs_Index1_Text",
        }
        owner_map: dict[str, list[str]] = {}
        for key in packet1:
            if key not in unowned1:
                owner_map[target.full_key("CG表", "QuestDlgs", key)] = ["old21.json"]
        for key in packet2:
            if key not in unowned2:
                owner_map[target.full_key("CG表", "QuestDlgs", key)] = ["old21or22.json"]

        summary1 = target.classify_keys(packet1, owner_map, unowned1, set())
        summary2 = target.classify_keys(packet2, owner_map, unowned2, {"6158_5_Dlgs_Index1_Text"})
        self.assertEqual(summary1["existing_keys"], 19)
        self.assertEqual(summary1["new_keys"], 6)
        self.assertEqual(summary1["unowned_kept"], 6)
        self.assertEqual(summary2["existing_keys"], 19)
        self.assertEqual(summary2["new_keys"], 6)
        self.assertEqual(summary2["unowned_kept"], 5)
        self.assertEqual(summary1["existing_keys"] + summary2["existing_keys"], 38)
        self.assertEqual(summary1["new_keys"] + summary2["new_keys"], 12)

    def test_apply_plan_updates_existing_and_creates_new_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            p4 = root / "_phase4_proofread"
            p4.mkdir()
            candidate_rel = "_phase4_proofread/CANDIDATE.json"
            candidate = {
                "source": {"target": "CG表", "namespace": "QuestDlgs"},
                "rows": [{"key": key} for key in ("k1", "k2", "k3", "k4")],
            }
            (root / candidate_rel).write_text(json.dumps(candidate), encoding="utf-8")
            old_rel = "_phase4_proofread/fixes_old.json"
            old = {target.full_key("CG表", "QuestDlgs", key): f"old-{key}" for key in ("k1", "k2", "k3")}
            (root / old_rel).write_text(json.dumps(old), encoding="utf-8")
            manifest = {
                "totals": {},
                "bundles": [{"reviewed_rows": 4}],
            }
            state = {
                "wave": {
                    "packets": [{"preparation_record": {"candidate_packet": candidate_rel}}],
                    "encoding_summary": {},
                }
            }
            work = {"ci_train": {"totals": {}}}
            for name, value in (
                ("CI_TRAIN_MANIFEST.json", manifest),
                ("PRIVATE_STAGE_STATE.json", state),
                ("CURRENT_WORK.json", work),
            ):
                (p4 / name).write_text(json.dumps(value), encoding="utf-8")
            plan_rel = "_phase4_proofread/OWNER_ASSIGNMENT_PLAN.json"
            plan = {
                "schema_version": 1,
                "packets": [{
                    "candidate": candidate_rel,
                    "new_owner_file": "_phase4_proofread/fixes_new.json",
                    "values": {"k1": "new-k1", "k4": "new-k4"},
                    "fix_keys": ["k1", "k4"],
                }],
            }
            (root / plan_rel).write_text(json.dumps(plan), encoding="utf-8")
            result = target.apply_plan(root, root / plan_rel, p4 / "OWNER_ASSIGNMENT_RESULT.json")

            updated_old = json.loads((root / old_rel).read_text(encoding="utf-8"))
            new_owner = json.loads((p4 / "fixes_new.json").read_text(encoding="utf-8"))
            self.assertEqual(updated_old[target.full_key("CG表", "QuestDlgs", "k1")], "new-k1")
            self.assertEqual(new_owner, {target.full_key("CG表", "QuestDlgs", "k4"): "new-k4"})
            self.assertEqual(result["counts"], {
                "existing_owner_updates": 3,
                "new_project_keys": 1,
                "fix_keys": 2,
            })
            manifest_after = json.loads((p4 / "CI_TRAIN_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest_after["totals"]["existing_owner_updates"], 3)
            self.assertEqual(manifest_after["totals"]["new_project_keys"], 1)
            self.assertEqual(manifest_after["bundles"][0]["fix_files"], [old_rel, "_phase4_proofread/fixes_new.json"])


if __name__ == "__main__":
    unittest.main()
