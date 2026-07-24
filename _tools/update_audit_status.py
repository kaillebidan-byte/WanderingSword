#!/usr/bin/env python3
"""Curated fix filesと適用記録からaudit_status.jsonの機械的集計値を更新する。"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PAIR_PATTERNS = {
    "宇文逸↔清虚道長": "fixes_relation_yuwen_qingxu_*_batch*.json",
    "宇文逸↔清霄道長": "fixes_relation_yuwen_qingxiao_*_batch*.json",
    "宇文逸↔莫問": "fixes_relation_yuwen_mowen_*_batch*.json",
}
PAIR_RECORD_PATTERNS = {
    "宇文逸↔清虚道長": "APPLIED_FIXES_YUWEN_QINGXU_BATCH*_*.md",
    "宇文逸↔清霄道長": "APPLIED_FIXES_YUWEN_QINGXIAO_BATCH*_*.md",
    "宇文逸↔莫問": "APPLIED_FIXES_YUWEN_MOWEN_BATCH*_*.md",
}
FIX_BATCH_RE = re.compile(r"_batch(\d+)\.json$")
RECORD_BATCH_RE = re.compile(r"_BATCH(\d+)_")


def load_fix_count(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"fix file must be a JSON object: {path}")
    return len(data)


def latest_batch(paths: list[Path], pattern: re.Pattern[str]) -> int | None:
    batches: list[int] = []
    for path in paths:
        match = pattern.search(path.name)
        if match:
            batches.append(int(match.group(1)))
    return max(batches) if batches else None


def latest_completed_batch(fix_paths: list[Path], record_paths: list[Path]) -> int | None:
    """修正JSONまたは適用記録のうち、最も先へ進んだ完了束を返す。

    再改訂やcross-registerだけで人物ペア新規キーが0件の束は、新しい
    relation fix JSONを作らない。その場合も適用記録が正本として束完了を示す。
    """

    candidates = [
        latest_batch(fix_paths, FIX_BATCH_RE),
        latest_batch(record_paths, RECORD_BATCH_RE),
    ]
    observed = [value for value in candidates if value is not None]
    return max(observed) if observed else None


def relative_record_paths(fixes_dir: Path) -> list[str]:
    root = fixes_dir.parent
    records = sorted(fixes_dir.glob("APPLIED_FIXES_*.md"))
    return [path.relative_to(root).as_posix() for path in records]


def update_status(status_path: Path, fixes_dir: Path) -> bool:
    status: dict[str, Any] = json.loads(status_path.read_text(encoding="utf-8"))
    before = json.dumps(status, ensure_ascii=False, sort_keys=True)

    all_fixes = sorted(fixes_dir.glob("fixes_*.json"))
    total = sum(load_fix_count(path) for path in all_fixes)
    latest_build = status["project"]["latest_build"]
    latest_build["applied_keys"] = total
    latest_build["record_index"] = relative_record_paths(fixes_dir)
    status["updated_at"] = datetime.now(timezone(timedelta(hours=9))).date().isoformat()

    pair_status = status.get("pair_status", {})
    for pair, fix_pattern in PAIR_PATTERNS.items():
        if pair not in pair_status:
            continue
        fix_paths = sorted(fixes_dir.glob(fix_pattern))
        if not fix_paths:
            continue
        count = sum(load_fix_count(path) for path in fix_paths)
        record_pattern = PAIR_RECORD_PATTERNS.get(pair)
        record_paths = sorted(fixes_dir.glob(record_pattern)) if record_pattern else []
        batch = latest_completed_batch(fix_paths, record_paths)
        pair_status[pair]["applied_keys"] = count
        if batch is not None and pair_status[pair].get("translation_reaudited") != "high_confidence_pass_complete":
            pair_status[pair]["translation_reaudited"] = f"batch{batch}_complete_next_scenes_pending"
            pair_status[pair]["build_verified"] = f"batch{batch}_complete"

    after = json.dumps(status, ensure_ascii=False, sort_keys=True)
    if after == before:
        print(f"audit status unchanged: {total} keys")
        return False

    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"audit status updated: {total} keys")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", type=Path, default=Path("_phase4_proofread/audit_status.json"))
    parser.add_argument("--fixes-dir", type=Path, default=Path("_phase4_proofread"))
    args = parser.parse_args()
    update_status(args.status, args.fixes_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
