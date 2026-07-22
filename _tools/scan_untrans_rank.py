# -*- coding: utf-8 -*-
"""漢字オンリー対話本文を「未翻訳(中国語残り)らしさ」でランク分け。行は消さない・判断は人間。
信号(加点):
  CN_HARD   : 簡体字/中国語専用字(日本語では使わない字)。+4/種
  CN_VERN   : 中国語口語パターン(什么/怎么/这个/我们/没有/为什么…)。+5
  CLASSIC   : 古典助詞 乎哉矣焉兮耳(漢詩にも出るので弱)。+1
  ZH_EQ     : zh原文とほぼ一致(丸ごと未訳)。+8
ラベル(参考・除外しない):
  念仏/経    : 南無/阿弥陀/菩薩/善哉/経 等 → 正当の可能性
使い方: PYTHONIOENCODING=utf-8 python _tools/scan_untrans_rank.py [--min 5]
出力: $WS_TMP/untrans_ranked.txt(スコア降順・全件)
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))
MIN = int(sys.argv[sys.argv.index("--min")+1]) if "--min" in sys.argv else 5

# 日本語では使わない簡体字/中国語専用字(scan_untranslated.py を拡張)
CN_HARD = set("你妳们們吗嗎呢咱啥咋哪怎麼么什谁这這个説说见觉让时实战经过风门问间关应现认识论议张长车东书还进远连边难飞习样类节乐买卖语读变丽华虽够带师从录术杀红纸级")
# 中国語口語の連語(日本語にまず出ない)
CN_VERN = re.compile(r"什么|怎么|这个|那个|我们|你们|他们|她们|没有|为什么|不是|知道|这样|那样|这里|那里|哪里|一个|这些|那些|多少|可以|不会|不能")
CLASSIC = set("乎哉矣焉兮耳")          # 強い古典助詞(現代日本語にまず出ない) +3/種
CLASSIC2 = set("也之其者夫")           # 弱い(JAにも稀に出る) +1/種
NEG_CN = re.compile(r"不[一-龥]")        # 中国語否定 不X +2
DEVOT = re.compile(r"南無|阿[弥彌]陀|菩薩|善哉|往生|涅槃|般若|波羅蜜|諸法|如来")  # 念仏/経マーカー

HIRA = lambda s: any(0x3041 <= ord(c) <= 0x309F for c in s)
KATA = lambda s: any(0x30A1 <= ord(c) <= 0x30FA for c in s)
CJK = lambda c: 0x4E00 <= ord(c) <= 0x9FFF
def strip_ctl(v):
    v = re.sub(r"<[^>]*>|\{[^}]*\}", "", v)
    return v.replace("#nl", "").replace("\\r\\n", "")
def zh_body(zh):
    if not zh: return ""
    b = zh.split("$@$", 1)[1] if "$@$" in zh else zh
    return re.sub(r"<[^>]*>|\{[^}]*\}|#nl|[\s，。、！？…—~〜·・]", "", b)

rows = []
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    for nk, v in locres.parse(f)[1].items():
        if not v or "$@$" not in v:
            continue
        ns, k = nk.split("\x1f", 1)
        body = strip_ctl(v.split("$@$", 1)[1])
        if HIRA(body) or KATA(body):
            continue
        if sum(1 for c in body if CJK(c)) < MIN:
            continue
        zh = SRC.get(tbl + "\x1f" + ns + "\x1f" + k, "")
        sig, score = [], 0
        hard = sorted(set(c for c in body if c in CN_HARD))
        if hard:
            score += 4 * len(hard); sig.append("CN字:" + "".join(hard))
        if CN_VERN.search(body):
            score += 5; sig.append("口語:" + "/".join(CN_VERN.findall(body)))
        cl = sorted(set(c for c in body if c in CLASSIC))
        if cl:
            score += 3 * len(cl); sig.append("古典助詞:" + "".join(cl))
        cl2 = sorted(set(c for c in body if c in CLASSIC2))
        if cl2:
            score += len(cl2); sig.append("古典字:" + "".join(cl2))
        if NEG_CN.search(body):
            score += 2; sig.append("中国語否定:" + NEG_CN.search(body).group(0))
        zb = zh_body(zh)
        jb = re.sub(r"[\s，。、！？…—~〜·・]", "", body)
        if zb and jb and (jb == zb or (len(jb) >= 6 and jb == zb[:len(jb)])):
            score += 8; sig.append("zh一致(丸ごと未訳)")
        label = "念仏/経" if DEVOT.search(v) else ""
        rows.append((score, label, tbl, ns, k, zh, v, " ".join(sig)))

rows.sort(key=lambda r: (-r[0],))
rep = os.path.join(TMP, "untrans_ranked.txt")
with open(rep, "w", encoding="utf-8") as o:
    o.write(f"# 漢字オンリー{len(rows)}件 / スコア降順(上位=未翻訳濃厚)\n")
    for score, label, tbl, ns, k, zh, v, sig in rows:
        lab = f" <{label}>" if label else ""
        o.write(f"[score {score}{lab}] {tbl}|{ns}|{k}  {sig}\n  zh: {zh}\n  ja: {v}\n")

hi = [r for r in rows if r[0] >= 4 and not r[1]]
dv = [r for r in rows if r[1]]
print(f"全{len(rows)}件 -> {rep}")
print(f"  未翻訳濃厚(score>=4・非念仏): {len(hi)}件")
print(f"  念仏/経ラベル              : {len(dv)}件")
print(f"  低スコア(0-3)              : {len(rows)-len(hi)-len([r for r in rows if r[0]>=4 and r[1]])}件")
print("\n--- 上位15 ---")
for score, label, tbl, ns, k, zh, v, sig in rows[:15]:
    print(f"  [{score}{' '+label if label else ''}] {v[:50]}  | {sig}")
