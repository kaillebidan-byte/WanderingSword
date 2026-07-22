# -*- coding: utf-8 -*-
"""全件ダンプ版。判断はしない。生データを全部出す。
出力(全件・truncなし):
  $WS_TMP/nohira_dialogue.txt  : 本文(=$@$以降)にひらがなが1字も無い対話行 を全件。zh併記。
  $WS_TMP/latin_all.txt        : 本文にラテン英字 [A-Za-z] を含む対話行 を全件(間引き無し)。zh併記。
  $WS_TMP/tag_broken.txt       : タグ整合の機械チェックで異常を検出した行(対話/非対話とも)。

タグ整合チェック(=「破損」の実際の根拠):
  - 色タグ <X> の開き数 と </> の閉じ数 の不一致
  - '<' と '>' の個数不一致(閉じ忘れ/開き忘れ)
  - 既知でないタグ名( <Y> <B> <G> <R> <P> <C> </> 以外の <…> )
  - '$@$' を含むのに 'ID - 名 $@$本文' の形になっていない
  - '#n'/'#l' 等 '#nl' の打ち損じ疑い

使い方: PYTHONIOENCODING=utf-8 python _tools/scan_untrans_full.py
"""
import os, re, glob, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
os.makedirs(TMP, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
SRC = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))

HIRA = lambda s: any(0x3041 <= ord(c) <= 0x309F for c in s)
KATA = lambda s: any(0x30A1 <= ord(c) <= 0x30FA for c in s)
CJK  = lambda s: any(0x4E00 <= ord(c) <= 0x9FFF for c in s)
LATIN = re.compile(r"[A-Za-z]")
KNOWN_TAGS = {"Y", "B", "G", "R", "P", "C", "/", "Y2", "O", "W"}  # 色/制御。未知は破損候補

def strip_ctl(v):
    v = re.sub(r"<[^>]*>", "", v)
    v = re.sub(r"\{[^}]*\}", "", v)
    return v.replace("#nl", "").replace("\\r\\n", "").replace("\r", "").replace("\n", "")

def body_of(v):
    return v.split("$@$", 1)[1] if "$@$" in v else None

def tag_issues(v):
    iss = []
    opens = re.findall(r"<([^/>][^>]*)>", v)   # 開きタグ名
    closes = len(re.findall(r"</>", v))
    # 既知でないタグ
    unk = [t for t in opens if t not in KNOWN_TAGS]
    if unk:
        iss.append("未知タグ<%s>" % ",".join(sorted(set(unk))))
    if len(opens) != closes:
        iss.append(f"色タグ開閉不一致(開{len(opens)}/閉{closes})")
    if v.count("<") != v.count(">"):
        iss.append(f"山括弧不一致(<{v.count('<')}/>{v.count('>')})")
    if "$@$" in v:
        head = v.split("$@$", 1)[0]
        if not re.match(r"^[\d\s]+-\s*\S", head):
            iss.append("話者頭が『ID - 名』形でない")
    # #nl の打ち損じ: '#' があるのに '#nl' でない並び
    for m in re.finditer(r"#(.{0,2})", v):
        frag = m.group(0)
        if not frag.startswith("#nl"):
            iss.append(f"#nl打ち損じ疑い『{frag}』")
            break
    return iss

def main():
    nohira, latin, broken = [], [], []
    for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
        tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
        _, d, *_ = locres.parse(f)
        for nk, v in d.items():
            if not v:
                continue
            ns, k = nk.split("\x1f", 1)
            zh = SRC.get(tbl + "\x1f" + ns + "\x1f" + k, "")
            # --- タグ整合(全行) ---
            iss = tag_issues(v)
            if iss:
                broken.append((tbl, ns, k, " / ".join(iss), zh, v))
            # --- 対話行のみ: 本文判定 ---
            b = body_of(v)
            if b is None:
                continue
            bare = strip_ctl(b)
            if not HIRA(bare):
                tag = []
                if KATA(bare): tag.append("カナ有")
                if CJK(bare): tag.append("漢字有")
                if LATIN.search(bare): tag.append("英字有")
                if not tag: tag.append("記号のみ")
                nohira.append((tbl, ns, k, "/".join(tag), zh, v))
            if LATIN.search(b):
                latin.append((tbl, ns, k, zh, v))

    def w(path, rows, cols5=False):
        with open(path, "w", encoding="utf-8") as o:
            o.write(f"# 全{len(rows)}件\n")
            for r in rows:
                if cols5:
                    tbl, ns, k, flag, zh, v = r
                    o.write(f"[{flag}] {tbl}|{ns}|{k}\n  zh: {zh}\n  ja: {v}\n")
                else:
                    tbl, ns, k, zh, v = r
                    o.write(f"{tbl}|{ns}|{k}\n  zh: {zh}\n  ja: {v}\n")
    w(os.path.join(TMP, "nohira_dialogue.txt"), nohira, cols5=True)
    w(os.path.join(TMP, "latin_all.txt"), latin)
    w(os.path.join(TMP, "tag_broken.txt"), broken, cols5=True)

    print(f"ひらがな無し対話行   : {len(nohira)}件 -> {TMP}\\nohira_dialogue.txt")
    print(f"英字含む対話行(全件) : {len(latin)}件 -> {TMP}\\latin_all.txt")
    print(f"タグ整合NG(全行)     : {len(broken)}件 -> {TMP}\\tag_broken.txt")
    from collections import Counter
    print("\n[ひらがな無し: 分類内訳]", Counter(r[3] for r in nohira).most_common())
    print("[タグ整合NG: 種類内訳]")
    c = Counter()
    for r in broken:
        for part in r[3].split(" / "):
            c[re.sub(r"[0-9（(].*$", "", part)] += 1
    for kk, vv in c.most_common():
        print(f"   {vv:5d}  {kk}")

if __name__ == "__main__":
    main()
