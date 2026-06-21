# -*- coding: utf-8 -*-
"""MT臭 第2弾の規模調査。二人称・拡張一人称・JA構造的MT臭を計測し件数を出す。
出力: $WS_TMP/mtsmell_scope.txt(カテゴリ別・全件) + stdout 件数表。判定はしない。
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

# ZH 二人称(長い順)
ZH_2P = re.compile(r"你們|你们|您|汝|尔|你")
# ZH 拡張一人称(既存セットに無かった自称)
ZH_1P_EXT = re.compile(r"小人|小的|小生|晚辈|卑职|不才|老娘|本姑娘|奴婢|微臣|属下|草民|愚兄|为兄|為兄")
# JA 二人称(明示+助詞)
JA_2P = re.compile(r"(あなた|お前|おまえ|貴様|そなた|貴方|汝|お前さん|そち)(は|が|を|に|も|の)")
# JA 構造的MT臭
JA_CANDO = re.compile(r"(する|る)ことができ")
JA_TOIU = re.compile(r"という.{0,12}という")
JA_NODESU = re.compile(r"のです[。、].{0,18}のです")
JA_SOSHITE = re.compile(r"そして.{0,30}そして|それから.{0,30}それから")

def body(v):
    b = v.split("$@$", 1)[1] if "$@$" in v else v
    return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", b)
def zb(z):
    if not z: return ""
    b = z.split("$@$", 1)[1] if "$@$" in z else z
    return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", b)
def sp(v):
    m = re.match(r"^[\d\s]*-\s*(.*)$", v.split("$@$",1)[0].strip()); return m.group(1).strip() if m else ""

buckets = {k: [] for k in ["2P_CONFIRMED","2P_JAONLY","1P_EXT_ZH","CANDO2","TOIU","NODESU","SOSHITE"]}
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        jb = body(v); zhb = zb(SRC.get(f"{tbl}\x1f{ns}\x1f{k}", ""))
        row = (tbl, ns, k, sp(v), zhb, v)
        zh2 = len(ZH_2P.findall(zhb)) >= 2 if zhb else False
        ja2 = len(JA_2P.findall(jb)) >= 2
        if ja2 and zh2: buckets["2P_CONFIRMED"].append(row)
        elif ja2:        buckets["2P_JAONLY"].append(row)
        if zhb and len(ZH_1P_EXT.findall(zhb)) >= 1 and ZH_1P_EXT.search(zhb):
            # 拡張一人称が原文にあり、かつJAにも明示一人称が2回(=取りこぼしMT臭の温床)
            if len(re.findall(r"(私|わたくし|わたし|俺|僕|わし|拙者|妾|某)(は|が|も)", jb)) >= 2:
                buckets["1P_EXT_ZH"].append(row)
        if len(JA_CANDO.findall(jb)) >= 2: buckets["CANDO2"].append(row)
        if JA_TOIU.search(jb): buckets["TOIU"].append(row)
        if JA_NODESU.search(jb): buckets["NODESU"].append(row)
        if JA_SOSHITE.search(jb): buckets["SOSHITE"].append(row)

rep = os.path.join(TMP, "mtsmell_scope.txt")
LABEL = {
 "2P_CONFIRMED":"二人称 ZH重複×JA重複(最優先)",
 "2P_JAONLY":"二人称 JA明示重複のみ",
 "1P_EXT_ZH":"拡張一人称(小人/晚辈等)×JA一人称重複",
 "CANDO2":"『することができ』2回以上(直訳硬さ)",
 "TOIU":"『という…という』",
 "NODESU":"『のです。…のです』",
 "SOSHITE":"『そして…そして/それから…』",
}
with open(rep, "w", encoding="utf-8") as o:
    for key, rows in buckets.items():
        o.write(f"\n########## {LABEL[key]}  ({len(rows)}件) ##########\n")
        for tbl, ns, k, s, zhb, v in rows:
            o.write(f"[{tbl}|{ns}|{k}] 話者={s}\n  zh: {zhb}\n  ja: {v}\n")
from collections import Counter
print("=== 規模調査(件数) ===")
for key in buckets:
    rows = buckets[key]
    top = Counter(r[3] for r in rows).most_common(5)
    print(f"{LABEL[key]:32s}: {len(rows):4d}件  話者top={top}")
print(f"-> {rep}")
