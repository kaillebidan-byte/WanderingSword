#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI manifestと実owner件数からAPPLIED_FIXES記録を冪等生成する。"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
PAIR_CONFIG = {
    "宇文逸↔莫問": ("YUWEN_MOWEN", "fixes_relation_yuwen_mowen_*_batch*.json"),
    "宇文逸↔清虚道長": ("YUWEN_QINGXU", "fixes_relation_yuwen_qingxu_*_batch*.json"),
    "宇文逸↔清霄道長": ("YUWEN_QINGXIAO", "fixes_relation_yuwen_qingxiao_*_batch*.json"),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def count_keys(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"fix file must be object: {path}")
        total += len(value)
    return total


def render(manifest: dict[str, Any], current: dict[str, Any], *, date_text: str, fixes_dir: Path) -> tuple[Path, str]:
    bundles = manifest.get("bundles")
    if not isinstance(bundles, list) or not bundles:
        raise ValueError("manifest.bundles must be non-empty")
    batches = [item.get("batch") for item in bundles if isinstance(item, dict)]
    if any(not isinstance(value, int) for value in batches):
        raise ValueError("all bundle batches must be integers")
    first_batch = min(batches)
    final_batch = max(batches)
    pair = current.get("current_pair")
    if pair not in PAIR_CONFIG:
        raise ValueError(f"unsupported current_pair: {pair!r}")
    slug, pair_glob = PAIR_CONFIG[pair]
    totals = manifest.get("totals", {})
    pair_total = count_keys(sorted(fixes_dir.glob(pair_glob)))
    project_total = count_keys(sorted(fixes_dir.glob("fixes_*.json")))
    reviewed = int(totals.get("reviewed_keys", totals.get("reviewed_rows", 0)))
    unique_rows = int(totals.get("unique_reviewed_rows", totals.get("reviewed_rows", 0)))
    fixes = int(totals.get("fix_keys", 0))
    keeps = max(0, reviewed - fixes)
    train_id = str(manifest.get("train_id"))
    release_id = f"{train_id}-r1"
    pr = manifest.get("draft_pr")
    scenes: list[str] = []
    for bundle in bundles:
        if isinstance(bundle, dict):
            scenes.extend(str(item) for item in bundle.get("scene_groups", []) if isinstance(item, str))

    lines = [
        f"# {pair} 第{first_batch}〜{final_batch}束 適用記録",
        "",
        f"- 日付: {date_text}",
        f"- PR: #{pr}",
        f"- CI列車: `{train_id}`",
        f"- release: `{release_id}`",
        f"- release evidence: `{manifest.get('release_evidence')}`",
        f"- 場面: " + " / ".join(f"`{scene}`" for scene in scenes),
        f"- reviewed keys: {reviewed}",
        f"- unique reviewed rows: {unique_rows}",
        f"- 修正キー: {fixes}",
        f"- 現訳保持キー: {keeps}",
        f"- 人物ペア新規: {totals.get('new_pair_keys', 0)}",
        f"- プロジェクト新規: {totals.get('new_project_keys', 0)}",
        f"- cross-register収録: {totals.get('cross_register_keys', 0)}",
        f"- 既存owner更新: {totals.get('existing_owner_updates', 0)}",
        f"- 人物ペア累計: {pair_total}",
        f"- プロジェクト全体累計: {project_total}",
        "- status: `applied_and_pak_built`",
        "- build: `verified_not_deployed`",
        "- game verification: `not_started`",
        "",
        "この記録はApply workflowがmanifestと実owner件数から自動生成した。CI run ID、CI HEAD、asset HEADはrelease evidenceで確定する。",
        "",
        "## 正式束",
        "",
    ]
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        batch = bundle.get("batch")
        bundle_scenes = " + ".join(str(item) for item in bundle.get("scene_groups", []))
        lines.extend([
            f"### 第{batch}束 `{bundle_scenes}`",
            "",
            f"- reviewed rows: {bundle.get('reviewed_rows', 0)}",
            f"- fix keys: {bundle.get('fix_keys', 0)}",
            f"- keep keys: {bundle.get('keep_keys', 0)}",
            f"- existing owner updates: {bundle.get('existing_owner_updates', 0)}",
            f"- cross-register keys: {bundle.get('ownership_summary', {}).get('cross_register_keys', 0)}",
            f"- review record: `{bundle.get('review_record')}`",
            "",
        ])
    lines.extend([
        "## 機械検証",
        "",
        "- Relation / Crossを同一release HEADで成功させた後にApplyを実行する",
        "- 未適用差分0件、locres、pak、LFS、lint、関係抽出、回帰を確認する",
        "- この記録を生成してからaudit_status.jsonを更新する",
        "- final run IDとHEADはrelease evidenceおよびCURRENT_WORKへ固定する",
        "",
    ])
    path = fixes_dir / f"APPLIED_FIXES_{slug}_BATCH{final_batch}_{date_text}.md"
    return path, "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--current", type=Path, default=CURRENT_PATH)
    parser.add_argument("--fixes-dir", type=Path, default=P4)
    parser.add_argument("--date", dest="date_text")
    args = parser.parse_args()
    manifest = load(args.manifest)
    current = load(args.current)
    date_text = args.date_text or datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    path, content = render(manifest, current, date_text=date_text, fixes_dir=args.fixes_dir)
    if manifest.get("status") == "verified" and path.exists():
        print(f"applied record preserved for verified release: {path.relative_to(ROOT)}")
        return 0
    before = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(content, encoding="utf-8")
    print(f"applied record {'unchanged' if before == content else 'updated'}: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
