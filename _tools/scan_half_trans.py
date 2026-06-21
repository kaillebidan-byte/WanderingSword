# -*- coding: utf-8 -*-
"""半端な未訳(JA文中に簡体字が残る)をSkills/Buffの説明系から洗う。包括的な簡体字集合で。"""
import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
# 包括的な簡体字(JA字形と別コードポイントのもの)。常用の主要簡体字を網羅。
CN = set(
 "帮师经练续罗离纳纸红级时实战过风门问间关应现认识论议张长车东书还进远连边难飞习样类节义"
 "乐买卖语读变丽华够带录术杀这个么什谁说见觉让们伤几对额获减敌马龙凤赵两为弹击层产轮净归价"
 "铁银单图题选举观养发复气后标负疯冲帜帅币阵队总际专业丝严乌乱争亿仅丛")
def strip(v): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl|\\r\\n|skill_flags|sufficient_lv|=|\"", "", v)

from collections import Counter
total = 0
char_count = Counter()
for tbl in ["Skills技能表", "Buff与道具"]:
    rows = []
    for nk, v in locres.parse(glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0])[1].items():
        if not v: continue
        k = nk.split("\x1f")[-1]
        if not re.search(r"(Desc|Description|SpecialEffect|CastEffect|ViewName)", k): continue
        hit = sorted(set(c for c in strip(v) if c in CN))
        if hit:
            rows.append((k, "".join(hit), v))
            for c in hit: char_count[c] += 1
    print(f"--- {tbl}: {len(rows)}件 ---")
    for k, h, v in rows[:60]:
        print(f"  [{k}]<{h}> {v[:64]}")
    total += len(rows)
print(f"\n計 {total}件 / 残存簡体字 top: {char_count.most_common(15)}")
