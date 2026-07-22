# -*- coding: utf-8 -*-
"""ひらがな無し対話の内訳＋疑い検証。何も削らない。
検証:
  (1) タグ影響: ひらがな判定を「タグ除去後」と「生body」で比較し、判定が変わる行数を出す
      (=タグが原因の誤検出が無いか。latinバグの再発チェック)
  (2) 漢字≥5プール(untrans_ranked対象)との重なり
内訳バケット(タグ除去後body):
  SYM    記号のみ(……！？等) = ほぼ正当
  KATA   カナ有(平仮名無し)   = 擬音/外来語、多くは正当
  K1_4   漢字1-4字           = 短い呼びかけ/人名/中国語語彙(姑娘等) ← 新規の疑いはここ
  K5     漢字5+              = 既出プール(典故等で処理中)
K1_4 は中国語信号(CN専用字/口語/古典助詞)で未翻訳濃厚を上位表示。
出力: $WS_TMP/nohira_breakdown.txt
"""
import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"

HIRA = lambda s: any(0x3041 <= ord(c) <= 0x309F for c in s)
KATA = lambda s: any(0x30A1 <= ord(c) <= 0x30FA for c in s)
CJKc = lambda c: 0x4E00 <= ord(c) <= 0x9FFF
def strip_ctl(v):
    v = re.sub(r"<[^>]*>|\{[^}]*\}", "", v)
    return v.replace("#nl", "").replace("\\r\\n", "")
CN_HARD = set("你妳们們吗嗎呢咱啥咋哪怎麼么什谁这這个説说见觉让时实战经过风门问间关应现认识论议张长车东书还进远连边难飞习样类节乐买卖语读变丽华虽够带师从录术杀红纸级姑娘")
CN_VERN = re.compile(r"什么|怎么|这个|那个|我们|你们|他们|没有|为什么|不是|这样|哪里|姑娘|江湖|相公|公子")
CLASSIC = set("乎哉矣焉兮耳")

rows = []
tag_diff = 0
inter5 = 0
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        raw = v.split("$@$", 1)[1]
        bare = strip_ctl(raw)
        if HIRA(bare):
            continue
        # (1) タグ影響: 生bodyだとひらがな有→除去で無になった行(=タグ内に平仮名)
        if HIRA(raw) and not HIRA(bare):
            tag_diff += 1
        kanji = sum(1 for c in bare if CJKc(c))
        if kanji >= 5:
            bucket = "K5"; inter5 += 1
        elif kanji >= 1:
            bucket = "K1_4"
        elif KATA(bare):
            bucket = "KATA"
        else:
            bucket = "SYM"
        # K1_4 の中国語信号
        score = 0; sig = []
        if bucket == "K1_4":
            hard = sorted(set(c for c in bare if c in CN_HARD))
            if hard: score += 4*len(hard); sig.append("CN字:"+"".join(hard))
            if CN_VERN.search(bare): score += 5; sig.append("口語:"+"/".join(CN_VERN.findall(bare)))
            cl = sorted(set(c for c in bare if c in CLASSIC))
            if cl: score += 2*len(cl); sig.append("古典:"+"".join(cl))
        rows.append((bucket, score, tbl, ns, k, v, " ".join(sig)))

from collections import Counter
bc = Counter(r[0] for r in rows)
print(f"ひらがな無し対話 計 {len(rows)}件")
print(f"  内訳: K5(漢字5+)={bc['K5']}  K1_4(漢字1-4)={bc['K1_4']}  KATA(カナ)={bc['KATA']}  SYM(記号)={bc['SYM']}")
print(f"  (1)タグ検証: 生bodyでは平仮名有→タグ除去で無 になった行 = {tag_diff}件 (これがタグ原因の疑い)")
print(f"  (2)漢字≥5プールとの重なり = {inter5}件 (=untrans_ranked対象。既に処理中)")

k14 = sorted([r for r in rows if r[0] == "K1_4"], key=lambda r: -r[1])
rep = os.path.join(TMP, "nohira_breakdown.txt")
with open(rep, "w", encoding="utf-8") as o:
    o.write(f"# ひらがな無し {len(rows)}件 内訳\n")
    for b in ["K1_4", "KATA", "SYM", "K5"]:
        rs = [r for r in rows if r[0] == b]
        if b == "K1_4":
            rs = sorted(rs, key=lambda r: -r[1])
        o.write(f"\n########## {b}  ({len(rs)}件) ##########\n")
        for bucket, score, tbl, ns, k, v, sig in rs:
            o.write(f"[{b} s{score}] {tbl}|{ns}|{k}  {sig}\n  {v}\n")
print(f"\n-> {rep}")
print("\n--- K1_4 中国語信号 上位15(新規の疑い) ---")
for bucket, score, tbl, ns, k, v, sig in k14[:15]:
    print(f"  [s{score}] {v[:46]}  | {sig}")
