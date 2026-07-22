# -*- coding: utf-8 -*-
"""話者区切り $@$ の破損を総ざらい(全locres・全件)。
判定: 正常な '$@$' を全部消した後に '@' が残る = 区切りが壊れている。
  例 '$@恐れ'(末尾$欠落) / '$@><Y>'(>混入) / '$极@$'(簡体字割込)
使い方: PYTHONIOENCODING=utf-8 python _tools/scan_sep_broken.py
"""
import os, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
hits = []
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    _, d, *_ = locres.parse(f)
    for nk, v in d.items():
        if not v or "@" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        if "@" in v.replace("$@$", ""):     # 正常区切りを除いて@が残れば破損
            i = v.find("@")
            frag = v[max(0, i - 4):i + 4]
            hits.append((tbl, ns, k, frag, v))
print(f"$@$破損: {len(hits)}件")
for tbl, ns, k, frag, v in hits:
    print(f"[壊れ『{frag}』] {tbl}|{ns}|{k}\n  ja: {v}")
