#!/usr/bin/env python3
"""次に訳すべき物語系の未訳原文を、重複排除して出力する。
使い方: python3 _tools/pending.py [件数=40]
未訳判定: target_ja が空 かつ 「不翻译」印が無い。
既に他ファイルで訳された原文(翻訳メモリ)は除外(後でapply時に自動流用)。
出力: JSON配列 [{"source_zh","occurrences","targets"}] を標準出力へ。
"""
import json, re, sys, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAP = os.path.join(ROOT, "_phase3_gaps")
STORY = ["Npc", "CG表", "Quests任务表"]
ALL = ["Buff与道具","CG表","Npc","Quests任务表","Skills技能表","系统","门派地图与提示"]
NOTL = re.compile(r'不翻译|不翻譯')

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    # 翻訳メモリ: 全ファイルで既に訳が入っている原文
    memory = set()
    for t in ALL:
        for r in json.load(open(f"{GAP}/gaps_{t}.json", encoding="utf-8")):
            if r.get("target_ja"):
                memory.add(r["source_zh"])
    # 物語系の未訳をユニーク集計
    uniq = {}
    for t in STORY:
        for r in json.load(open(f"{GAP}/gaps_{t}.json", encoding="utf-8")):
            s = r["source_zh"]
            if r.get("target_ja") or NOTL.search(s) or s in memory:
                continue
            u = uniq.setdefault(s, {"source_zh": s, "occurrences": 0, "targets": set()})
            u["occurrences"] += 1; u["targets"].add(t)
    rows = sorted(uniq.values(), key=lambda x: -x["occurrences"])
    out = [{"source_zh": r["source_zh"], "occurrences": r["occurrences"],
            "targets": sorted(r["targets"])} for r in rows[:n]]
    total = len(uniq)
    sys.stderr.write(f"未訳ユニーク残: {total} / 今回提示: {len(out)} / 翻訳メモリ既知: {len(memory)}\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
