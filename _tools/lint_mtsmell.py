# -*- coding: utf-8 -*-
"""MT臭・字形・制御タグの統合lint(回帰検出)。本校正の前後で実行し、件数が増えたら再発。
  python lint_mtsmell.py            # 現状の件数を表示
  python lint_mtsmell.py --baseline # 現状を基準として保存($WS_TMP/mtsmell_baseline.json)
  python lint_mtsmell.py --check    # 基準と比較し、増えたカテゴリを警告(回帰検出)
検出: 一人称重複/二人称重複/一人称複数重複/簡体字残存(説明)/$@$破損/南無冒頭脱落/英語混入。
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

ZH_FP = re.compile(r"我們|我们|本座|老夫|妾身|奴家|人家|在下|贫道|貧道|我|吾|咱|俺")
JA_FP = re.compile(r"(私|わたくし|わたし|俺|僕|わし|拙者|妾|某)(は|が|も)")
ZH_2P = re.compile(r"你們|你们|您|汝|尔|你")
JA_2P = re.compile(r"(あなた|お前|おまえ|貴様|そなた|貴方|汝)(は|が|を|に|も|の)")
PLZH = re.compile(r"我们|我們|咱们|咱們")
PLJA = re.compile(r"私たち|我々|俺たち|私達|わたしたち|我ら|我等")
CN_DESC = set("帮气复关冲阵飞华师术义疯枪鹰蛊莲胜极脉浑灵罗离纳纸红练级实战过风门问现张长车东书还进这个么谁说见们伤几对额获减敌马龙凤为弹击层产")
ALLOW = re.compile(r"HP|MP|CD|ZOC|BUFF|GM|Lv|EXP|kg|x\d", re.IGNORECASE)
AMIDA = re.compile(r"阿[弥彌]陀[仏佛]")
INIT = re.compile(r"^[\s「『（(…・、。!?！？]*阿[弥彌]陀[仏佛]")
SMELL = re.compile(r"(?<!乳)臭い(坊主|僧|和尚|道士|男|奴|野郎|小僧)")  # 罵倒の臭を字義誤訳(乳臭いは除外)

def body(v): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", v.split("$@$", 1)[1]) if "$@$" in v else re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", v)
def zb(z): return re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", z.split("$@$", 1)[1]) if z and "$@$" in z else (re.sub(r"<[^>]*>|\{[^}]*\}|#nl", "", z) if z else "")

def scan():
    c = {"1P_dup": [], "2P_dup": [], "PL_dup": [], "簡体字残": [], "$@$破損": [], "南無脱落": [], "英語混入": [], "臭い誤訳": []}
    for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
        tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
        for nk, v in locres.parse(f)[1].items():
            if not v: continue
            ns, k = nk.split("\x1f", 1); full = f"{tbl}|{ns}|{k}"
            if "@" in v.replace("$@$", ""): c["$@$破損"].append(full)
            if "$@$" in v:
                jb = body(v); zhb = zb(SRC.get(f"{tbl}\x1f{ns}\x1f{k}", ""))
                if zhb and len(ZH_FP.findall(zhb)) >= 2 and len(JA_FP.findall(jb)) >= 2: c["1P_dup"].append(full)
                if zhb and len(ZH_2P.findall(zhb)) >= 2 and len(JA_2P.findall(jb)) >= 2: c["2P_dup"].append(full)
                if zhb and len(PLZH.findall(zhb)) >= 2 and len(PLJA.findall(jb)) >= 2: c["PL_dup"].append(full)
                if ALLOW.sub("", re.sub(r"[ -~]", lambda m: "" if not m.group().strip() else m.group(), jb)) and re.search(r"[A-Za-z]", ALLOW.sub("", jb)): c["英語混入"].append(full)
                b2 = v.split("$@$", 1)[1]
                if AMIDA.search(b2) and INIT.match(re.sub(r"<[^>]*>", "", b2)): c["南無脱落"].append(full)
                if SMELL.search(jb): c["臭い誤訳"].append(full)
            else:
                if re.search(r"(Desc|Description|SpecialEffect|CastEffect|ViewName|Name)", k) and set(ch for ch in body(v) if ch in CN_DESC):
                    c["簡体字残"].append(full)
    return c

def main():
    c = scan(); counts = {k: len(v) for k, v in c.items()}
    bpath = os.path.join(TMP, "mtsmell_baseline.json")
    if "--baseline" in sys.argv:
        json.dump(counts, open(bpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("基準を保存:", counts); return
    print("=== MT臭/字形/タグ lint ===")
    for k, n in counts.items(): print(f"  {k:10s}: {n}")
    if "--check" in sys.argv and os.path.exists(bpath):
        base = json.load(open(bpath, encoding="utf-8")); reg = False
        print("\n--- 基準比較(回帰検出) ---")
        for k, n in counts.items():
            d = n - base.get(k, 0)
            mark = "  ⚠回帰" if d > 0 else ""
            if d != 0: print(f"  {k}: {base.get(k,0)} → {n} ({d:+d}){mark}")
            if d > 0: reg = True
        print("⚠ 回帰あり。本校正で再発した行がある。" if reg else "回帰なし。")

if __name__ == "__main__":
    main()
