# -*- coding: utf-8 -*-
"""MT臭検出: ZH原文の一人称重複 と JA明示主語重複 を突き合わせる。
JAセリフ($@$本文)が対象。判定はせず候補を出す。
出力: $WS_TMP/mtsmell.txt
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

# --- ZH 一人称(長い順。我们が我を二重計上しないように) ---
ZH_FP = re.compile(
    r"我們|我们|本座|本宮|本宫|本王|本官|本帥|本帅|本将|老夫|老身|老朽|妾身|奴家|人家|"
    r"在下|鄙人|贫道|貧道|贫僧|貧僧|洒家|某家|微臣|末将|寡人|哀家|为师|為師|小女子|"
    r"我|吾|咱|俺|朕|某")
# --- JA 明示主語(一人称+は/が/も) ---
JA_FP = re.compile(
    r"(私|わたくし|わたし|あたし|あたい|俺|おれ|僕|ぼく|わし|拙者|某|それがし|"
    r"わらわ|妾|小生|某|手前)(は|が|も)")

def body(v):
    b = v.split("$@$", 1)[1] if "$@$" in v else v
    return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", b)

def zh_body(zh):
    if not zh: return ""
    b = zh.split("$@$", 1)[1] if "$@$" in zh else zh
    return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", b)

def speaker(v):
    h = v.split("$@$", 1)[0]
    m = re.match(r"^[\d\s]*-\s*(.*)$", h.strip())
    return m.group(1).strip() if m else h.strip()

confirmed, ja_only, zh_only = [], [], []
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        jb = body(v)
        zb = zh_body(SRC.get(f"{tbl}\x1f{ns}\x1f{k}", ""))
        zh_dup = len(ZH_FP.findall(zb)) >= 2 if zb else False
        ja_dup = len(JA_FP.findall(jb)) >= 2
        if not (zh_dup or ja_dup):
            continue
        row = (tbl, ns, k, speaker(v), zb, v)
        if zh_dup and ja_dup:
            confirmed.append(row)
        elif ja_dup:
            ja_only.append(row)
        else:
            zh_only.append(row)

def dump(o, title, rows):
    o.write(f"\n########## {title}  ({len(rows)}件) ##########\n")
    for tbl, ns, k, sp, zb, v in rows:
        o.write(f"[{tbl}|{ns}|{k}] 話者={sp}\n  zh: {zb}\n  ja: {v}\n")

rep = os.path.join(TMP, "mtsmell.txt")
with open(rep, "w", encoding="utf-8") as o:
    dump(o, "CONFIRMED ZH一人称重複 かつ JA明示主語重複(最優先)", confirmed)
    dump(o, "JA_DUP JA明示主語重複(ZH不問)", ja_only)
    dump(o, "ZH_DUP ZH一人称重複(JAは要確認)", zh_only)

from collections import Counter
print(f"CONFIRMED(ZH重複×JA重複): {len(confirmed)}件")
print(f"JA_DUP(JA明示主語重複)    : {len(ja_only)}件")
print(f"ZH_DUP(ZH一人称重複のみ)  : {len(zh_only)}件")
print(f"-> {rep}")
print("\n[CONFIRMED 話者別 top10]", Counter(r[3] for r in confirmed).most_common(10))
print("[JA_DUP 話者別 top10]", Counter(r[3] for r in ja_only).most_common(10))
