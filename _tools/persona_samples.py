#!/usr/bin/env python3
"""指定話者の代表セリフを多めに抽出する(雛形ペルソナ埋め用)。
使い方: python3 _tools/persona_samples.py "話者名" [件数=15]
原文(zh)と訳(ja)を併記して出力。
"""
import sys, os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres

def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    name = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    src = {}
    p4 = os.path.join(ROOT, "_phase4_proofread", "source_zh.json")
    import json
    src = json.load(open(p4, encoding="utf-8")) if os.path.exists(p4) else {}
    pat = re.compile(r'^\s*\d+\s*-\s*(.+?)\s*\$@\$(.*)$', re.S)
    clean = re.compile(r'</?[A-Za-z]?[^>]*>|\\r|\\n|\r|\n')
    seen = set(); out = []
    for t in ["Quests任务表", "CG表", "Npc"]:
        _, ja, *_ = locres.parse(wlp(t))
        for k, v in ja.items():
            if not v or '$@$' not in v: continue
            m = pat.match(v)
            if not m or m.group(1).strip() != name: continue
            body = clean.sub('', m.group(2)).strip()
            if 6 <= len(body) <= 80 and body not in seen:
                seen.add(body)
                zh = src.get(t + "\x1f" + k, "")
                out.append((zh, body))
                if len(out) >= n: break
        if len(out) >= n: break
    print(f"# {name} のセリフ例 {len(out)}件 (原文 / 訳)")
    for zh, ja in out:
        print(f"- 原: {zh[:60]}")
        print(f"  訳: {ja[:60]}")

if __name__ == "__main__":
    main()
