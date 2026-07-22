# -*- coding: utf-8 -*-
import os, glob, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
TERMS = sys.argv[1:] if len(sys.argv) > 1 else ["睡夢", "睡梦", "睡眠"]
HIRA = lambda s: any(0x3041 <= ord(c) <= 0x309F for c in s)
def strip(v): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", v)
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" in v: continue
        if any(t in v for t in TERMS):
            k = nk.split("\x1f", 1)[-1]
            b = strip(v)
            untr = "★未訳?" if (b and not HIRA(b) and len(b) > 4 and "ViewName" not in k and "Name" not in k) else ""
            print(f"[{tbl}|{k}] {untr}\n  {v[:90]}")
