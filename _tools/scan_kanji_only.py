# -*- coding: utf-8 -*-
"""漢字オンリー(仮名ゼロ)の対話本文を抽出。本文の漢字数が閾値以下(既定4)は除外=単純呼びかけを落とす。
zh原文を併記(source_zh)。意味では間引かない。
使い方: PYTHONIOENCODING=utf-8 python _tools/scan_kanji_only.py [--min 5]
出力: $WS_TMP/kanji_only.txt
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

MIN = int(sys.argv[sys.argv.index("--min")+1]) if "--min" in sys.argv else 5  # 漢字数>=MIN を残す(=4字以内除外)
HIRA = lambda s: any(0x3041 <= ord(c) <= 0x309F for c in s)
KATA = lambda s: any(0x30A1 <= ord(c) <= 0x30FA for c in s)
CJK = lambda c: 0x4E00 <= ord(c) <= 0x9FFF
def strip_ctl(v):
    v = re.sub(r"<[^>]*>|\{[^}]*\}", "", v)
    return v.replace("#nl", "").replace("\\r\\n", "")

rows = []
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        body = strip_ctl(v.split("$@$", 1)[1])
        if HIRA(body) or KATA(body):       # 仮名があれば対象外
            continue
        kanji = sum(1 for c in body if CJK(c))
        if kanji < MIN:                    # 漢字4字以内は除外
            continue
        zh = SRC.get(tbl + "\x1f" + ns + "\x1f" + k, "")
        rows.append((kanji, tbl, ns, k, zh, v))

rows.sort(key=lambda r: (-r[0],))
rep = os.path.join(TMP, "kanji_only.txt")
with open(rep, "w", encoding="utf-8") as o:
    o.write(f"# 漢字オンリー(仮名0)・漢字数>={MIN} の対話本文  全{len(rows)}件\n")
    for kanji, tbl, ns, k, zh, v in rows:
        o.write(f"[漢字{kanji}] {tbl}|{ns}|{k}\n  zh: {zh}\n  ja: {v}\n")
print(f"漢字オンリー(漢字数>={MIN}=4字以内除外): {len(rows)}件 -> {rep}")
zc = sum(1 for r in rows if not r[4])
print(f"  うち zh原文あり {len(rows)-zc}件 / zh無し {zc}件")
