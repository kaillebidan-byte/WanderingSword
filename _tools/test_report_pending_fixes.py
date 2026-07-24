#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_pending_fixes as target  # noqa: E402


class ReportPendingFixesTests(unittest.TestCase):
    def test_collects_only_mismatching_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            locres = Path(tmp) / "CG表.locres"
            locres.write_bytes(b"dummy")
            fixes = {
                "CG表\x1fQuestDlgs\x1fkey_ok": "新訳A",
                "CG表\x1fQuestDlgs\x1fkey_pending": "新訳B",
            }
            index_map = {
                "QuestDlgs\x1fkey_ok": 0,
                "QuestDlgs\x1fkey_pending": 1,
            }
            values = [["新訳A"], ["旧訳B"]]

            with (
                patch.object(target.apply, "locate_locres", return_value=locres),
                patch.object(target.apply, "key_index_map", return_value=(index_map, 0)),
                patch.object(
                    target.apply.L,
                    "load",
                    return_value=(None, 1, None, values, None),
                ),
            ):
                rows = target.collect_pending(fixes)

            self.assertEqual(1, len(rows))
            self.assertEqual("QuestDlgs", rows[0]["namespace"])
            self.assertEqual("key_pending", rows[0]["key"])
            self.assertEqual("新訳B", rows[0]["expected"])
            self.assertEqual("旧訳B", rows[0]["observed"])

    def test_reports_missing_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            locres = Path(tmp) / "CG表.locres"
            locres.write_bytes(b"dummy")
            fixes = {"CG表\x1fQuestDlgs\x1fmissing": "新訳"}

            with (
                patch.object(target.apply, "locate_locres", return_value=locres),
                patch.object(target.apply, "key_index_map", return_value=({}, 0)),
                patch.object(
                    target.apply.L,
                    "load",
                    return_value=(None, 1, None, [], None),
                ),
            ):
                rows = target.collect_pending(fixes)

            self.assertEqual(1, len(rows))
            self.assertEqual("missing_key", rows[0]["status"])
            self.assertIsNone(rows[0]["observed"])


if __name__ == "__main__":
    unittest.main()
