# -*- coding: utf-8 -*-
"""非対話($@$無し)の未訳(中国語残り)を全テーブルから確定抽出。全文を $WS_TMP/nondlg_untrans.txt に。"""
import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
# 確実な簡体字(JAと別コードポイント)
CN = set("时实战经过风门问间关应现认识论议张长书还进远连边难飞习样类买卖语读变丽华够录杀红级觉让这个么什谁说见们伤几对额获减敌马龙凤赵两为弹击层产强术轮净归仅价")
# 中国語文法/専用語(JA説明文では使わない)
GRAM = re.compile(r"使用.{0,6}时|产生|额外|几率|目标|消耗|添加|强化|气血|真气|内力|招式|伤害|反弹|暴击|普攻|为自身|每攻击|所有|可为|若自身|则使|本技能|本招式")
def strip(v):
    return re.sub(r"<[^>]*>|\{[^}]*\}|#nl|\\r\\n", "", v)

rows = []
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" in v:
            continue
        ns, k = nk.split("\x1f", 1)
        b = strip(v)
        cn = set(c for c in b if c in CN)
        if cn and GRAM.search(b):
            rows.append((tbl, ns, k, v))

from collections import Counter
print(f"非対話・未訳濃厚 計 {len(rows)}件")
print("テーブル別:", dict(Counter(r[0] for r in rows)))
rep = os.path.join(TMP, "nondlg_untrans.txt")
with open(rep, "w", encoding="utf-8") as o:
    for tbl, ns, k, v in rows:
        o.write(f"[{tbl}|{ns}|{k}]\n  {v}\n")
print("->", rep)
