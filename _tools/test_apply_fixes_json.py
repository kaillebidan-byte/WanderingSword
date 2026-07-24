#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Phase2 compatibility rerun anchor: validated PR head is not a squash SHA.
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_fixes_json as target  # noqa: E402


class ApplyFixesJsonTests(unittest.TestCase):
    def write_json(self, root: Path, name: str, payload: object) -> Path:
        path = root / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    @staticmethod
    def ansi_fstring(value: str) -> bytes:
        encoded = value.encode("ascii") + b"\x00"
        return struct.pack("<i", len(encoded)) + encoded

    def test_loads_multiple_files_and_accepts_same_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            key1 = "CG表\x1fQuestDlgs\x1f100_1_Text"
            key2 = "Npc\x1fNpcTalk\x1f200_1_Text"
            first = self.write_json(root, "a.json", {key1: "新訳A"})
            second = self.write_json(
                root,
                "b.json",
                {key1: "新訳A", key2: "新訳B"},
            )

            fixes, sources = target.load_fix_files([str(first), str(second)])

            self.assertEqual({key1: "新訳A", key2: "新訳B"}, fixes)
            self.assertEqual(str(first), sources[key1])
            self.assertEqual(str(second), sources[key2])

    def test_rejects_conflicting_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            key = "CG表\x1fQuestDlgs\x1f100_1_Text"
            first = self.write_json(root, "a.json", {key: "新訳A"})
            second = self.write_json(root, "b.json", {key: "新訳B"})

            with self.assertRaisesRegex(ValueError, "競合"):
                target.load_fix_files([str(first), str(second)])

    def test_rejects_malformed_compound_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_json(root, "bad.json", {"bad-key": "新訳"})

            with self.assertRaisesRegex(ValueError, "複合key形式不正"):
                target.load_fix_files([str(path)])

    def test_expands_glob_and_deduplicates_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.write_json(root, "a.json", {})
            second = self.write_json(root, "b.json", {})

            expanded = target.expand_paths(
                [str(root / "*.json"), str(first)]
            )

            self.assertEqual([str(first), str(second)], expanded)

    def test_rejects_missing_glob(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                target.expand_paths([str(Path(tmp) / "missing-*.json")])

    def test_selects_table_named_locres_from_multiple_candidates(self) -> None:
        candidates = [
            Path("CG表.backup.locres"),
            Path("CG表.locres"),
            Path("other.locres"),
        ]

        selected = target.select_locres("CG表", candidates)

        self.assertEqual(Path("CG表.locres"), selected)

    def test_selects_only_locres_as_fallback(self) -> None:
        selected = target.select_locres("CG表", [Path("only.locres")])

        self.assertEqual(Path("only.locres"), selected)

    def test_rejects_ambiguous_nonmatching_locres(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "一意に選べない"):
            target.select_locres(
                "CG表",
                [Path("first.locres"), Path("second.locres")],
            )

    def test_non_utf8_ansi_fstring_round_trips_without_replacement(self) -> None:
        raw = struct.pack("<i", 3) + b"\xbbA\x00"

        value, end = target.L.rd_fstr(raw, 0)
        rebuilt = target.L.wr_fstr(value)

        self.assertEqual(len(raw), end)
        self.assertIn("\udcbb", value)
        self.assertEqual(raw, rebuilt)

    def test_key_index_map_skips_source_hash_before_string_index(self) -> None:
        data = bytearray(b"\x00" * 17)
        data += struct.pack("<q", 256)  # string array offset
        data += struct.pack("<I", 1)  # extra entry count/hash field
        data += struct.pack("<I", 1)  # namespace count
        data += struct.pack("<I", 0x11111111)  # namespace hash
        data += self.ansi_fstring("QuestDlgs")
        data += struct.pack("<I", 1)  # key count
        data += struct.pack("<I", 0x22222222)  # key hash
        data += self.ansi_fstring("100_1_Text")
        data += struct.pack("<I", 0x33333333)  # source string hash
        data += struct.pack("<i", 7)  # localized string array index

        mapping, array_offset = target.key_index_map(bytes(data))

        self.assertEqual(256, array_offset)
        self.assertEqual({"QuestDlgs\x1f100_1_Text": 7}, mapping)

    def test_build_plans_records_pending_key_and_values(self) -> None:
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
                patch.object(target, "locate_locres", return_value=locres),
                patch.object(target, "key_index_map", return_value=(index_map, 0)),
                patch.object(
                    target.L,
                    "load",
                    return_value=(None, 1, None, values, None),
                ),
            ):
                plans, pending, applied = target.build_plans(fixes)

            self.assertEqual(1, pending)
            self.assertEqual(1, applied)
            self.assertEqual(
                [("CG表\x1fQuestDlgs\x1fkey_pending", "新訳B", "旧訳B")],
                plans[0].pending_details,
            )


if __name__ == "__main__":
    unittest.main()
