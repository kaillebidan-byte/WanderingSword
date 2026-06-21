# -*- coding: utf-8 -*-
"""Skills/Buffの説明・名称に残る簡体字をJA標準字形へ正規化(半端未訳の字形統一)。
JA非対応の簡体字のみ写像。flagged(=不変でない)エントリだけ書込。--apply で書込+_work repak(deployなし)。
"""
import os, re, glob, sys, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

# JA非対応の簡体字 → JA標準字形(乱/争/什 等のJA共用字は入れない)
M = {
 "帮":"幇","气":"気","复":"復","关":"関","冲":"衝","阵":"陣","飞":"飛","华":"華","师":"師","术":"術",
 "单":"単","义":"義","疯":"瘋","枪":"槍","鹰":"鷹","蛊":"蠱","莲":"蓮","胜":"勝","极":"極","帜":"幟",
 "帅":"帥","币":"幣","际":"際","专":"専","业":"業","严":"厳","乌":"烏","亿":"億","仅":"僅","丛":"叢",
 "时":"時","实":"実","战":"戦","过":"過","风":"風","门":"門","问":"問","间":"間","应":"応","现":"現",
 "认":"認","识":"識","论":"論","议":"議","张":"張","长":"長","车":"車","东":"東","书":"書","还":"還",
 "进":"進","远":"遠","连":"連","边":"辺","难":"難","习":"習","样":"様","类":"類","节":"節","乐":"楽",
 "买":"買","卖":"売","语":"語","读":"読","变":"変","丽":"麗","够":"夠","带":"帯","录":"録","杀":"殺",
 "这":"這","个":"個","谁":"誰","说":"説","见":"見","觉":"覚","让":"譲","伤":"傷","几":"幾","对":"対",
 "额":"額","获":"獲","减":"減","敌":"敵","马":"馬","龙":"龍","凤":"鳳","赵":"趙","两":"両","为":"為",
 "弹":"弾","击":"撃","层":"層","产":"産","轮":"輪","净":"浄","归":"帰","价":"価","铁":"鉄","银":"銀",
 "图":"図","题":"題","选":"選","举":"挙","观":"観","养":"養","发":"発","后":"後","标":"標","负":"負",
 "脉":"脈","浑":"渾","灵":"霊","云":"雲","罗":"羅","离":"離","纳":"納","纸":"紙","红":"紅","经":"経",
 "练":"練","续":"続","级":"級","强":"強","队":"隊","总":"総","历":"歴","协":"協","纷":"紛","纲":"綱",
 "纪":"紀","约":"約","绝":"絶","给":"給","统":"統","绿":"緑","维":"維","细":"細","织":"織","终":"終",
 "绕":"繞","绳":"縄","绪":"緒","绍":"紹","继":"継","缘":"縁","缠":"纏","纤":"繊","荣":"栄","药":"薬",
 "宝":"宝","显":"顕","贵":"貴","贱":"賤","质":"質","赏":"賞","贼":"賊","贯":"貫","赞":"賛","赖":"頼",
 "蚬":"蜆","鱼":"魚","鸟":"鳥","鸡":"鶏","鸭":"鴨","龟":"亀","贝":"貝","虾":"蝦","鳗":"鰻","鲜":"鮮",
 "饭":"飯","饼":"餅","饮":"飲","馆":"館","骨":"骨","闷":"悶","团":"団","图":"図","圆":"円","锦":"錦",
}
TRIG = set("帮气复关冲阵飞华师术单义疯枪鹰蛊莲胜极帜帅币际专业严乌亿仅丛脉浑灵罗离纳纸红经练续级队总历协绝统维显贵质赏贼蚬鱼鸟鸡鸭龟贝虾鳗鲜饭饼饮馆闷团圆")  # これを含めば未訳確定
def strip(v): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl|\\r\\n|skill_flags|sufficient_lv|=|\"", "", v)

def main():
    apply = "--apply" in sys.argv
    fixes = {}   # full -> new
    for tbl in ["Skills技能表", "Buff与道具"]:
        for nk, v in locres.parse(glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0])[1].items():
            if not v: continue
            k = nk.split("\x1f")[-1]
            if not re.search(r"(Desc|Description|SpecialEffect|CastEffect|ViewName|Name)", k): continue
            s = strip(v)
            if not (set(c for c in s if c in TRIG)):   # 確実な未訳トリガが無ければ触らない
                continue
            nv = "".join(M.get(c, c) for c in v)
            if nv != v:
                fixes[f"{tbl}\x1f{nk}"] = (v, nv)
    print(f"字形正規化対象: {len(fixes)}件")
    for full, (o, n) in list(fixes.items())[:60]:
        print(f"  [{full.split(chr(0x1f))[0]}|{full.split(chr(0x1f))[-1]}] {o[:40]} → {n[:40]}")
    if not apply:
        print("\n[プレビュー] --apply で書込"); return
    # 適用
    import json
    flat = {full: n for full, (o, n) in fixes.items()}
    tmp = os.path.join(os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp")), "fixes_jaforms.json")
    json.dump(flat, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    subprocess.run([sys.executable, os.path.join(ROOT, "_tools", "apply_fixes_json.py"), tmp, "--apply"],
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})

if __name__ == "__main__":
    main()
