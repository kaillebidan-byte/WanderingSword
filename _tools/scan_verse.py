#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""韻文(漢詩・偈・對聯・古典引用)候補を全zhから洗い出す。読み下し化の対象選定用。
信号: ①對句(，/、で区切った2節以上が同字数4-7) ②「曰：」古典引用 ③「兮」 ④「之/也/矣/焉/乎」を含む文語連。
技名(・/·区切りの固有名詞)は除外気味に。判定は人(Opus)が最終。
出力: $WS_TMP/verse.txt
"""
import os, re, glob, json, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
src = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))
bychar = json.load(open(f"{ROOT}/_phase4_proofread/by_character.json", encoding="utf-8"))

JC = {}
def ja_of(t, ns, k):
    if t not in JC:
        JC[t] = locres.parse(glob.glob(f"{ROOT}/_work/jp/**/{t}/zh-Hans/*.locres", recursive=True)[0])[1]
    return JC[t].get(ns + "\x1f" + k, "")

def body(v):
    if "$@$" in v: v = v.split("$@$", 1)[1]
    v = re.sub(r"<[^>]*>", "", v); v = re.sub(r"\{[^}]*\}", "", v)
    return v.replace("#nl", "").strip()

def cjk_len(s):
    return sum(1 for c in s if 0x4E00 <= ord(c) <= 0x9FFF)

WEN = set("之也矣焉乎兮哉耶")  # 文語助字
def verse_reason(zb):
    z = zb.strip().strip("（）()「」『』《》……？！。 ")
    if "·" in zb or "・" in zb:  # 技名・固有名詞は除外気味
        return None
    if "曰" in zb and "：" in zb:
        return "古典引用(〜曰：)"
    # 對句: ，または、で割って、字数同じ節が2つ以上(4-7字)
    clauses = [c for c in re.split(r"[，、,]", z) if cjk_len(c) >= 4]
    if len(clauses) >= 2:
        lens = [cjk_len(c) for c in clauses]
        from collections import Counter
        L, n = Counter(lens).most_common(1)[0]
        if n >= 2 and 4 <= L <= 8:
            return f"對句({n}節×{L}字)"
    # 文語助字を2つ以上含む長め
    if cjk_len(z) >= 8 and sum(1 for c in z if c in WEN) >= 2:
        return "文語助字"
    return None

def main():
    seen = set(); hits = []
    for c, items in bychar["lines"].items():
        for t, ns, k in items:
            kk = t + "\x1f" + ns + "\x1f" + k
            zb = body(src.get(kk, ""))
            if not zb or kk in seen: continue
            r = verse_reason(zb)
            if r:
                seen.add(kk); hits.append((c, t, ns, k, r, zb, body(ja_of(t, ns, k))))
    rep = os.path.join(TMP, "verse.txt")
    with open(rep, "w", encoding="utf-8") as f:
        for c, t, ns, k, r, zh, ja in hits:
            f.write(f"[{r}] {c} {t}|{ns}|{k}\n  zh: {zh}\n  ja: {ja}\n")
    print(f"韻文候補 {len(hits)}件 -> {rep}")
    from collections import Counter
    print("理由別:", Counter(h[4].split('(')[0] for h in hits).most_common())

if __name__ == "__main__":
    main()
