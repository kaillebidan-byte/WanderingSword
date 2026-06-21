# -*- coding: utf-8 -*-
"""英語チェック(JA対話本文)。latinとnohiraの重なりも測る。何も削らない・分類して並べるだけ。
分類:
  GENUINE : タグ/プレースホルダ/既知略語/単位 を除いてもラテン英字が残る = 本物の英語混入候補
  ACRONYM : 残りが略語・単位のみ(HP/MP/CD/ZOC/BUFF/Lv/kg…) = ほぼ正当
信号:
  +NOHIRA : その行はひらがなを1字も含まない(=もう一方の検出集合とも重複)
出力: $WS_TMP/english_check.txt(GENUINE→ACRONYMの順・全件) + stdout 要約
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

LATIN = re.compile(r"[A-Za-z]")
ALLOW = re.compile(r"HP|MP|SP|CD|ZOC|BUFF|GM|BOSS|NPC|VS|OK|kg|km|cm|mm|Lv|Lvl|EXP|UI|ID|CG|PK|AI|DLC|FPS|RB|LB|RT|LT|RS|LS|WASD|ESC|x\d", re.IGNORECASE)
HIRA = lambda s: any(0x3041 <= ord(c) <= 0x309F for c in s)
def strip_ctl(v):
    v = re.sub(r"<[^>]*>|\{[^}]*\}", "", v)
    return v.replace("#nl", "").replace("\\r\\n", "")

genuine, acronym = [], []
latin_keys, nohira_keys = set(), set()
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        full = f"{tbl}|{ns}|{k}"
        body = v.split("$@$", 1)[1]
        bare = strip_ctl(body)
        nohira = not HIRA(bare)
        if nohira:
            nohira_keys.add(full)
        if not LATIN.search(bare):
            continue
        latin_keys.add(full)
        resid = LATIN.search(ALLOW.sub("", bare))
        zh = SRC.get(f"{tbl}\x1f{ns}\x1f{k}", "")
        row = (full, "NOHIRA" if nohira else "", zh, v)
        (genuine if resid else acronym).append(row)

rep = os.path.join(TMP, "english_check.txt")
with open(rep, "w", encoding="utf-8") as o:
    for title, rows in [("GENUINE 本物の英語混入候補", genuine), ("ACRONYM 略語/単位のみ(ほぼ正当)", acronym)]:
        o.write(f"\n########## {title}  ({len(rows)}件) ##########\n")
        for full, flag, zh, v in rows:
            o.write(f"[{full}]{' +'+flag if flag else ''}\n  zh: {zh}\n  ja: {v}\n")

inter = latin_keys & nohira_keys
print(f"latin(英字含む対話)   : {len(latin_keys)}件")
print(f"nohira(ひらがな無し)  : {len(nohira_keys)}件")
print(f"重なり latin∩nohira   : {len(inter)}件  (latin中の{len(inter)*100//max(len(latin_keys),1)}% / nohira中の{len(inter)*100//max(len(nohira_keys),1)}%)")
print(f"  → latinのうちひらがな有(=nohiraに無い): {len(latin_keys)-len(inter)}件")
print(f"\n英語分類: GENUINE {len(genuine)}件 / ACRONYM {len(acronym)}件 -> {rep}")
