#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宇文逸校正の抜き取り検査用サンプラ。Opus検査セッション(yuwen_inspect_prompt.txt)が使う。

直近に反映した範囲(cursor直前のN本文)から無作為にK件を抽出し、
zh(原文)・ライブja(反映後の現訳)・reg・partner を表示する。
校正の「声」がペルソナに沿っているかをOpusが目視判定するための材料。

使い方:
  python _tools/yuwen_sample.py            # 直近360本文(≒12バッチ)から12件
  python _tools/yuwen_sample.py 500 20     # 直近500本文から20件
"""
import json, os, sys, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yuwen_pending as Y

def main():
    args = [a for a in sys.argv[1:] if a.isdigit()]
    window = int(args[0]) if len(args) > 0 else 360
    k = int(args[1]) if len(args) > 1 else 12
    items = Y.build_order()  # ja はライブ現訳
    cur = 0
    if os.path.exists(Y.PROG):
        cur = json.load(open(Y.PROG, encoding="utf-8")).get("cursor", 0)
    lo = max(0, cur - window)
    pool = items[lo:cur]
    if not pool:
        print(f"# 対象なし (cursor={cur})")
        return
    sample = random.sample(pool, min(k, len(pool)))
    sample.sort(key=lambda it: items.index(it))
    print(f"# 抜き取り {len(sample)}件 / 範囲 cursor {lo}〜{cur} (全{len(items)}本文)")
    for it in sample:
        pos = items.index(it)
        print(f"\n--- [{pos}] reg={it['reg']}  partner={it.get('partner')}  key={it['key']}")
        print(f"zh: {it['zh']}")
        print(f"ja: {it['ja']}")

if __name__ == "__main__":
    main()
