# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import check_story_context_contract_paths as C

ROOT = Path(__file__).resolve().parents[1]


class Tests(unittest.TestCase):
    def contract(self):
        return json.loads((ROOT / C.CONTRACT).read_text(encoding="utf-8"))

    def test_live_contract_shape(self):
        C.validate_contract_shape(self.contract())

    def test_live_tree(self):
        result = C.validate(ROOT)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["current_stage"], "reference_ready")

    def test_old_manifest_layout_is_rejected(self):
        contract = copy.deepcopy(self.contract())
        contract["stage_artifacts"]["event_manifest_ready"] = [
            "_story_context/manifests/*.json"
        ]
        with self.assertRaisesRegex(C.ContractPathError, "stage_artifacts mismatch"):
            C.validate_contract_shape(contract)

    def test_trial_checker_path_is_pinned(self):
        contract = copy.deepcopy(self.contract())
        contract["trial_checker"] = "_tools/other_trial_checker.py"
        with self.assertRaisesRegex(C.ContractPathError, "trial_checker"):
            C.validate_contract_shape(contract)


if __name__ == "__main__":
    unittest.main()
