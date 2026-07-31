#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ensure_pair_tail_handoff_restart import HandoffError, RESTART, ensure


class EnsurePairTailHandoffRestartTests(unittest.TestCase):
    def test_missing_phrase_is_inserted_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "CURRENT_HANDOFF.md"
            path.write_text("# 現在の引継ぎ\n\n- train: tail\n", encoding="utf-8")
            self.assertTrue(ensure(path))
            text = path.read_text(encoding="utf-8")
            self.assertIn(RESTART, text)
            self.assertEqual(text.count(RESTART), 1)
            self.assertFalse(ensure(path))
            self.assertEqual(path.read_text(encoding="utf-8").count(RESTART), 1)

    def test_existing_phrase_is_noop(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "CURRENT_HANDOFF.md"
            original = f"# 現在の引継ぎ\n\n> 再開指示: `{RESTART}`\n"
            path.write_text(original, encoding="utf-8")
            self.assertFalse(ensure(path))
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_unexpected_heading_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "CURRENT_HANDOFF.md"
            path.write_text("# different\n", encoding="utf-8")
            with self.assertRaisesRegex(HandoffError, "must start"):
                ensure(path)


if __name__ == "__main__":
    unittest.main()
