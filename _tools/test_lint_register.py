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

    def test_directed_hostility(self):
        self.assertEqual(
            L.directed_hostility("妖僧，你今日合该受死！"),
            ["second_person_threat", "hostile_vocative"],
        )
        self.assertEqual(
            L.directed_hostility("你这种无耻败类，也敢来此？"),
            ["second_person_insult"],
        )

    def test_hostility_excludes_third_party_and_humble_self_reference(self):
        self.assertEqual(L.directed_hostility("那些该死的山贼实在可恨。"), [])
        self.assertEqual(L.directed_hostility("杀得马匪屁滚尿流。"), [])
        self.assertEqual(L.directed_hostility("妾身万死难报。"), [])
        self.assertEqual(L.directed_hostility("我这种小人物不敢计较。"), [])
        self.assertEqual(L.directed_hostility("妖僧迦摩看似慈眉善目。"), [])

    def test_polite_register(self):
        self.assertTrue(L.has_polite_register("ご安心ください。"))
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
