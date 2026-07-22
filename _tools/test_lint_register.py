# -*- coding: utf-8 -*-
"""lint_register.py の純関数テスト。"""
import unittest

import lint_register as L


class RegisterLintTest(unittest.TestCase):
    def test_body_removes_prefix_and_control_tags(self):
        self.assertEqual(
            L.body("1 - 絶無心 $@$<Y>滚开！</>#nl"),
            "滚开！",
        )

    def test_hostile_source_and_polite_target(self):
        zh = L.body("1 - 絶無心 $@$牛鼻子，休想！")
        ja = L.body("1 - 絶無心 $@$ご安心ください。")
        self.assertEqual(
            L.matched_terms(zh, L.HOSTILE_TERMS),
            ["牛鼻子", "休想"],
        )
        self.assertTrue(L.has_polite_register(ja))

    def test_plain_register_is_not_polite(self):
        self.assertFalse(L.has_polite_register("安心しろ。"))

    def test_raw_yo_does_not_match_compounds(self):
        self.assertTrue(L.has_raw_yo("余は認めぬ。"))
        self.assertFalse(L.has_raw_yo("余裕はない。"))
        self.assertFalse(L.has_raw_yo("余計な真似はするな。"))

    def test_second_person_terms(self):
        self.assertEqual(
            L.find_second_person_terms("あなたには負けない、宇文逸。"),
            ["あなた", "宇文逸"],
        )


if __name__ == "__main__":
    unittest.main()
