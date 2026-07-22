# -*- coding: utf-8 -*-
import unittest

import extract_relation_context as R


RELATION = {
    "left": {"name": "宇文逸", "aliases": ["宇文逸"]},
    "right": {"name": "清虚道長", "aliases": ["清虚", "清虚道长", "清虚道長"]},
    "left_to_right_markers": ["师父", "師父"],
    "right_to_left_markers": ["逸儿", "逸兒"],
}


class RelationContextTest(unittest.TestCase):
    def test_dialogue_parts(self):
        speaker, body = R.dialogue_parts("100 - 清虚道长 $@$<Y>逸儿</>，回来吧。#nl")
        self.assertEqual(speaker, "清虚道长")
        self.assertEqual(body, "逸儿，回来吧。")

    def test_dialogue_family(self):
        self.assertEqual(
            R.dialogue_family("12834_3_Dlgs_Index2_Text"),
            ("12834_3_Dlgs", 2),
        )
        self.assertEqual(R.dialogue_family("Standalone_Text"), ("Standalone_Text", None))

    def test_speaker_alias_normalization(self):
        self.assertTrue(R.speaker_matches("清虚道长", ["清虚道長"]))
        self.assertFalse(R.speaker_matches("清霄道长", ["清虚道長"]))

    def test_direct_exchange_wins(self):
        rows = [
            {"speaker": "宇文逸", "zh_body": "师父。", "ja_body": "師父。", "key": "a"},
            {"speaker": "清虚道长", "zh_body": "逸儿。", "ja_body": "逸児。", "key": "b"},
        ]
        result = R.classify_group(rows, RELATION)
        self.assertIsNotNone(result)
        self.assertEqual(result["kind"], "direct_exchange")

    def test_explicit_reference_without_both_speakers(self):
        rows = [
            {"speaker": "宇文逸", "zh_body": "师父说过。", "ja_body": "師父が言っていた。", "key": "a"},
        ]
        result = R.classify_group(rows, RELATION)
        self.assertIsNotNone(result)
        self.assertEqual(result["kind"], "explicit_reference")


if __name__ == "__main__":
    unittest.main()
