#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from update_audit_status import update_status


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixes = root / "proofread"
        fixes.mkdir()
        status_path = fixes / "audit_status.json"
        write_json(
            status_path,
            {
                "updated_at": "2000-01-01",
                "project": {"latest_build": {"applied_keys": 0}},
                "pair_status": {
                    "宇文逸↔莫問": {
                        "applied_keys": 0,
                        "translation_reaudited": "in_progress",
                        "build_verified": "not_started",
                    }
                },
            },
        )
        write_json(fixes / "fixes_cross_register_20260723.json", {"a": "1", "b": "2"})
        write_json(fixes / "fixes_relation_yuwen_mowen_20260723_batch1.json", {"c": "3"})
        write_json(fixes / "fixes_relation_yuwen_mowen_20260723_batch2.json", {"d": "4", "e": "5"})

        assert update_status(status_path, fixes) is True
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["project"]["latest_build"]["applied_keys"] == 5
        pair = status["pair_status"]["宇文逸↔莫問"]
        assert pair["applied_keys"] == 3
        assert pair["translation_reaudited"] == "batch2_complete_next_scenes_pending"
        assert pair["build_verified"] == "batch2_complete"
        assert update_status(status_path, fixes) is False

        # 新しい人物ペアJSONがない再改訂・cross-registerのみの束でも、
        # 適用記録があれば完了束を進める。キー件数は増えない。
        (fixes / "APPLIED_FIXES_YUWEN_MOWEN_BATCH3_2026-07-24.md").write_text(
            "# zero-new-key batch\n", encoding="utf-8"
        )
        assert update_status(status_path, fixes) is True
        status = json.loads(status_path.read_text(encoding="utf-8"))
        pair = status["pair_status"]["宇文逸↔莫問"]
        assert pair["applied_keys"] == 3
        assert pair["translation_reaudited"] == "batch3_complete_next_scenes_pending"
        assert pair["build_verified"] == "batch3_complete"
        assert (
            "proofread/APPLIED_FIXES_YUWEN_MOWEN_BATCH3_2026-07-24.md"
            in status["project"]["latest_build"]["record_index"]
        )
        assert update_status(status_path, fixes) is False

    print("update_audit_status tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
