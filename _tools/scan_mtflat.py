# -*- coding: utf-8 -*-
"""MT臭(平板化): 高頻度安全側訳で文体が死ぬ型。zh原文併記。判定はしない・候補出し。
出力: $WS_TMP/mtflat.txt
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

PATS = {
 "臭い+人": re.compile(r"臭い(坊主|僧|和尚|道士|男|女|奴|野郎|商人|役人|餓鬼|ガキ|小僧|女狐|女)"),
 "良い+人系": re.compile(r"良い(兄弟|男|女|人|奴|子|仲間|姉妹|友|漢|連中|やつ|ヤツ)"),
 "軽形容詞+人系": re.compile(r"(悪い|大きい|小さい|強い|弱い)(男|女|人|兄弟|師匠|奴|者)"),
}
ADV = re.compile(r"非常に|十分に|直接|特別に|正常に|正式に")

def body(v): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", v.split("$@$",1)[1]) if "$@$" in v else re.sub(r"<[^>]*>|\{[^}]*\}|#nl","",v)
def zb(z): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl","",z.split("$@$",1)[1]) if z and "$@$" in z else (re.sub(r"<[^>]*>|\{[^}]*\}|#nl","",z) if z else "")

buckets = {k: [] for k in PATS}
adv_count = 0
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v: continue
        ns, k = nk.split("\x1f", 1)
        jb = body(v)
        for name, pat in PATS.items():
            m = pat.search(jb)
            if m:
                zh = zb(SRC.get(f"{tbl}\x1f{ns}\x1f{k}", ""))
                buckets[name].append((tbl, ns, k, m.group(0), zh, v))
        if ADV.search(jb): adv_count += 1

rep = os.path.join(TMP, "mtflat.txt")
with open(rep, "w", encoding="utf-8") as o:
    for name, rows in buckets.items():
        o.write(f"\n########## {name}  ({len(rows)}件) ##########\n")
        for tbl, ns, k, hit, zh, v in rows:
            o.write(f"[{tbl}|{ns}|{k}] <{hit}>\n  zh: {zh}\n  ja: {v}\n")
for name, rows in buckets.items():
    print(f"{name:14s}: {len(rows)}件")
print(f"(参考)副詞 非常に/十分に/直接/特別に/正常/正式 を含む行: {adv_count}件")
print(f"-> {rep}")
