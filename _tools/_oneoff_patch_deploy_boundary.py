#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

path = Path("_tools/RUNBOOK_翻訳自動実行.md")
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

start = next(
    (i for i, line in enumerate(lines) if line.strip() == "## 仕上げ(毎回・両フェーズ共通)"),
    None,
)
if start is None:
    raise SystemExit("RUNBOOK finish heading not found")

handover = next(
    (
        i
        for i in range(start + 1, len(lines))
        if "**申し送り(2つに分けて書く・肥大化対策)**:" in lines[i]
    ),
    None,
)
if handover is None:
    raise SystemExit("RUNBOOK handover line not found")

new_lines = [
    "## 仕上げ(毎回・両フェーズ共通)\n",
    "1. 修正を適用し、locresを書き戻し、`_work/aaWanderingSword_JP_P.pak` を再生成する。修正JSONだけを準備して未適用で止めるのは、実行環境上適用不能・判断保留・提案のみ指定の場合に限る。\n",
    "2. タグ・改行・プレースホルダ・話者接頭辞・locres構造・lint・修正プレビューを検証し、ゲームへ配置可能なpakまで仕上げる。\n",
    "3. **デプロイ境界**: `_tools/deploy_to_game.py` は実行せず、Steamのゲームフォルダへpakをコピー・置換しない。ゲームフォルダへの配置とゲーム内確認はユーザー側で行う。詳細は `00_ルール/デプロイ境界.md`。\n",
    "4. **申し送り(2つに分けて書く・肥大化対策)**:\n",
]

patched = lines[:start] + new_lines + lines[handover + 1 :]
path.write_text("".join(patched), encoding="utf-8")
print(f"patched {path}: lines {start + 1}-{handover + 1}")
