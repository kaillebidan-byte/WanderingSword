#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import write_applied_record as writer


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixes = root / "_phase4_proofread"
        fixes.mkdir()
        (fixes / "fixes_relation_yuwen_mowen_20260723_batch1.json").write_text(json.dumps({"a": "x", "b": "y"}), encoding="utf-8")
        (fixes / "fixes_cross_register_test.json").write_text(json.dumps({"c": "z"}), encoding="utf-8")
        manifest = {
            "train_id": "yuwen-mowen-train-99",
            "draft_pr": 999,
            "release_evidence": "_phase4_proofread/RELEASE_EVIDENCE_TEST.json",
            "totals": {"reviewed_keys": 5, "unique_reviewed_rows": 5, "fix_keys": 2, "new_pair_keys": 0, "new_project_keys": 1, "cross_register_keys": 1, "existing_owner_updates": 1},
            "bundles": [
                {"batch": 1, "scene_groups": ["a"], "reviewed_rows": 2, "fix_keys": 1, "keep_keys": 1, "existing_owner_updates": 1, "ownership_summary": {"cross_register_keys": 0}, "review_record": "_phase4_proofread/REVIEW_1.md"},
                {"batch": 2, "scene_groups": ["b"], "reviewed_rows": 3, "fix_keys": 1, "keep_keys": 2, "existing_owner_updates": 0, "ownership_summary": {"cross_register_keys": 1}, "review_record": "_phase4_proofread/REVIEW_2.md"},
            ],
        }
        current = {"current_pair": "宇文逸↔莫問"}
        path, content = writer.render(manifest, current, date_text="2026-07-26", fixes_dir=fixes)
        assert path.name == "APPLIED_FIXES_YUWEN_MOWEN_BATCH2_2026-07-26.md"
        assert "人物ペア累計: 2" in content
        assert "プロジェクト全体累計: 3" in content
        assert "第1〜2束" in content
        assert "第2束 `b`" in content
    print("OK: applied record is generated from manifest and measured owner counts")


if __name__ == "__main__":
    main()
