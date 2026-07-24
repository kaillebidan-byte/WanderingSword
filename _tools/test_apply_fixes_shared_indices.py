#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_fixes_json as target  # noqa: E402


class SharedLocresIndexTests(unittest.TestCase):
    def test_splits_shared_index_when_one_key_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            locres = Path(tmp) / "CG表.locres"
            original = bytearray(b"\x00" * 12)
            struct.pack_into("<i", original, 4, 0)
            struct.pack_into("<i", original, 8, 0)
            locres.write_bytes(original)
            fixes = {"CG表\x1fQuestDlgs\x1fkey_new": "はい、師兄。"}
            records = {
                "QuestDlgs\x1fkey_old": target.KeyIndexRecord(0, 4),
                "QuestDlgs\x1fkey_new": target.KeyIndexRecord(0, 8),
            }
            values = [["分かりました、師兄。", 2]]

            with (
                patch.object(target, "locate_locres", return_value=locres),
                patch.object(target, "key_index_records", return_value=(records, 12)),
                patch.object(
                    target.L,
                    "load",
                    return_value=(None, 3, None, values, None),
                ),
            ):
                plans, pending, applied = target.build_plans(fixes)

            plan = plans[0]
            self.assertEqual((1, 0), (pending, applied))
            self.assertEqual(["分かりました、師兄。", 1], plan.values[0])
            self.assertEqual(["はい、師兄。", 1], plan.values[1])
            self.assertEqual(0, struct.unpack_from("<i", plan.original, 4)[0])
            self.assertEqual(1, struct.unpack_from("<i", plan.original, 8)[0])

    def test_splits_shared_index_for_two_different_new_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            locres = Path(tmp) / "CG表.locres"
            original = bytearray(b"\x00" * 8)
            struct.pack_into("<i", original, 0, 0)
            struct.pack_into("<i", original, 4, 0)
            locres.write_bytes(original)
            fixes = {
                "CG表\x1fQuestDlgs\x1fkey_a": "新訳A",
                "CG表\x1fQuestDlgs\x1fkey_b": "新訳B",
            }
            records = {
                "QuestDlgs\x1fkey_a": target.KeyIndexRecord(0, 0),
                "QuestDlgs\x1fkey_b": target.KeyIndexRecord(0, 4),
            }
            values = [["旧訳", 2]]

            with (
                patch.object(target, "locate_locres", return_value=locres),
                patch.object(target, "key_index_records", return_value=(records, 8)),
                patch.object(
                    target.L,
                    "load",
                    return_value=(None, 3, None, values, None),
                ),
            ):
                plans, pending, applied = target.build_plans(fixes)

            plan = plans[0]
            self.assertEqual((2, 0), (pending, applied))
            self.assertEqual(["新訳A", 1], plan.values[0])
            self.assertEqual(["新訳B", 1], plan.values[1])
            self.assertEqual(0, struct.unpack_from("<i", plan.original, 0)[0])
            self.assertEqual(1, struct.unpack_from("<i", plan.original, 4)[0])


if __name__ == "__main__":
    unittest.main()
