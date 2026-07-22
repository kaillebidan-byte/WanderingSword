#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import re

path = Path("_tools/RUNBOOK_翻訳自動実行.md")
text = path.read_text(encoding="utf-8")
pattern = re.compile(
    r"## 仕上げ\(毎回・両フェーズ共通\)\r?\n"
    r".*?"
    r"^2\. \*\*申し送り\(2つに分けて書く・肥大化対策\)\*\*:\r?\n",
    re.MULTILINE | re.DOTALL,
)
new = """## 仕上げ(毎回・両フェーズ共通)
1. 修正を適用し、locresを書き戻し、`_work/aaWanderingSword_JP_P.pak` を再生成する。修正JSONだけを準備して未適用で止めるのは、実行環境上適用不能・判断保留・提案のみ指定の場合に限る。
2. タグ・改行・プレースホルダ・話者接頭辞・locres構造・lint・修正プレビューを検証し、ゲームへ配置可能なpakまで仕上げる。
3. **デプロイ境界**: `_tools/deploy_to_game.py` は実行せず、Steamのゲームフォルダへpakをコピー・置換しない。ゲームフォルダへの配置とゲーム内確認はユーザー側で行う。詳細は `00_ルール/デプロイ境界.md`。
4. **申し送り(2つに分けて書く・肥大化対策)**:
"""
patched, count = pattern.subn(new, text, count=1)
if count != 1:
    raise SystemExit(f"RUNBOOK deployment block replacement count: {count}")
path.write_text(patched, encoding="utf-8")
print("patched", path)
