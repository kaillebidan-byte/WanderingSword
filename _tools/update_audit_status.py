#!/usr/bin/env python3
"""Curated fix filesからaudit_status.jsonの機械的集計値を更新する。"""

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
BATCH_RE = re.compile(r"_batch(\d+)\.json$")


def load_fix_count(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"fix file must be a JSON object: {path}")
    return len(data)


def latest_batch(paths: list[Path]) -> int | None:
    batches = []
    for path in paths:
        match = BATCH_RE.search(path.name)
        if match:
            batches.append(int(match.group(1)))
    return max(batches) if batches else None


def update_status(status_path: Path, fixes_dir: Path) -> bool:
    status: dict[str, Any] = json.loads(status_path.read_text(encoding="utf-8"))
    before = json.dumps(status, ensure_ascii=False, sort_keys=True)

    all_fixes = sorted(fixes_dir.glob("fixes_*.json"))
    total = sum(load_fix_count(path) for path in all_fixes)
    status["project"]["latest_build"]["applied_keys"] = total
    status["updated_at"] = datetime.now(timezone(timedelta(hours=9))).date().isoformat()

    pair_status = status.get("pair_status", {})
    for pair, pattern in PAIR_PATTERNS.items():
        if pair not in pair_status:
            continue
        paths = sorted(fixes_dir.glob(pattern))
        if not paths:
            continue
        count = sum(load_fix_count(path) for path in paths)
        batch = latest_batch(paths)
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
