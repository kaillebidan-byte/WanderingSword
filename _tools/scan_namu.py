# -*- coding: utf-8 -*-
"""南無 脱落/不揃い検出(ja直接走査)。『阿弥陀仏』系を全件出し、南無の有無と"位置"で分類。
意味では一切間引かない。位置はあくまで参考ラベル。
  CHANT  : 発話冒頭(=$@$直後、先頭の……「等を除いて)に阿弥陀仏 → 念仏。南無脱落の本命。
  MIDTXT : 文中の阿弥陀仏 → 仏名(主語等)のことが多いが判断は人間に委ねる。
出力: $WS_TMP/namu_candidates.txt(全件) + stdout 要約。
"""
import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"

AMIDA = re.compile(r"阿[弥彌]陀[仏佛]")
LEAD = re.compile(r"^[\s「『（(…・、。!?！？]*")          # 発話冒頭の飾り
INIT = re.compile(r"^(南[無无])?阿[弥彌]陀[仏佛]")      # 冒頭の(南無?)阿弥陀仏

rows = []   # (chant?, namu?, tbl, ns, k, v)
for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
    tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
    _, d, *_ = locres.parse(f)
    for nk, v in d.items():
        if not v:
            continue
        ns, k = nk.split("\x1f", 1)
        if not AMIDA.search(v):
            continue
        body = v.split("$@$", 1)[1] if "$@$" in v else v
        lead = LEAD.match(body).end()
        im = INIT.match(body[lead:])              # 冒頭に(南無?)阿弥陀仏 が来るか
        chant = bool(im)
        has_namu = bool(im and im.group(1)) if chant else ("南無" in v or "南无" in v)
        rows.append((chant, has_namu, tbl, ns, k, v))

def grp(chant, namu): return [r for r in rows if r[0] == chant and r[1] == namu]
c_no  = grp(True, False)   # 念仏位置・南無なし ← 最重要
c_yes = grp(True, True)    # 念仏位置・南無あり(正)
m_no  = grp(False, False)  # 文中・南無なし
m_yes = grp(False, True)   # 文中・南無あり

print(f"阿弥陀仏系 全 {len(rows)}件")
print(f"  CHANT(冒頭念仏) 南無なし ★本命 : {len(c_no)}")
print(f"  CHANT(冒頭念仏) 南無あり(正)    : {len(c_yes)}")
print(f"  MIDTXT(文中)    南無なし        : {len(m_no)}")
print(f"  MIDTXT(文中)    南無あり        : {len(m_yes)}")

rep = os.path.join(TMP, "namu_candidates.txt")
with open(rep, "w", encoding="utf-8") as o:
    def dump(title, rs):
        o.write(f"\n########## {title}  ({len(rs)}件) ##########\n")
        for chant, namu, tbl, ns, k, v in rs:
            o.write(f"[{tbl}|{ns}|{k}]\n  {v}\n")
    dump("CHANT 冒頭念仏・南無なし(★南無付与の本命)", c_no)
    dump("MIDTXT 文中・南無なし(仏名の可能性/要確認)", m_no)
    dump("CHANT 冒頭念仏・南無あり(参考:正しい形)", c_yes)
    dump("MIDTXT 文中・南無あり(参考)", m_yes)
print(f"-> {rep}")
