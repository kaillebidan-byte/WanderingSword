#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

path = Path("_tools/RUNBOOK_翻訳自動実行.md")
text = path.read_text(encoding="utf-8")
old = """## 仕上げ(毎回・両フェーズ共通)
1. `python3 _tools/deploy_to_game.py` を実行(最新pakをゲームへbest-effort差し替え＋日本語自己検証。
   ゲーム起動中/未マウントなら自動スキップしログに残す)。
2. **申し送り(2つに分けて書く・肥大化対策)**:
"""
new = """## 仕上げ(毎回・両フェーズ共通)
1. 修正を適用し、locresを書き戻し、`_work/aaWanderingSword_JP_P.pak` を再生成する。修正JSONだけを準備して未適用で止めるのは、実行環境上適用不能・判断保留・提案のみ指定の場合に限る。
2. タグ・改行・プレースホルダ・話者接頭辞・locres構造・lint・修正プレビューを検証し、ゲームへ配置可能なpakまで仕上げる。
3. **デプロイ境界**: `_tools/deploy_to_game.py` は実行せず、Steamのゲームフォルダへpakをコピー・置換しない。ゲームフォルダへの配置とゲーム内確認はユーザー側で行う。詳細は `00_ルール/デプロイ境界.md`。
4. **申し送り(2つに分けて書く・肥大化対策)**:
"""
if old not in text:
    raise SystemExit("expected RUNBOOK deployment block not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("patched", path)
