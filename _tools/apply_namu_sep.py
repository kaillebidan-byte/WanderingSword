# -*- coding: utf-8 -*-
"""南無付与(冒頭念仏129) + $@$破損修正(4) を locres に適用して repak。校正カーソルは触らない。
  --apply で実書込。無指定はプレビュー(差分表示のみ)。
"""
import os, re, sys, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

AMIDA = re.compile(r"阿[弥彌]陀[仏佛]")
LEAD = re.compile(r"^[\s「『（(…・、。!?！？]*")
INIT = re.compile(r"^(南[無无])?阿[弥彌]陀[仏佛]")

# --- 1) 南無付与対象を算出: 冒頭念仏で南無なし ---
def namu_edits():
    edits = []  # (tbl, ns, key, old, new)
    for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
        tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
        for nk, v in locres.parse(f)[1].items():
            if not v or "$@$" not in v or not AMIDA.search(v):
                continue
            ns, key = nk.split("\x1f", 1)
            head, body = v.split("$@$", 1)
            lead = LEAD.match(body).end()
            m = INIT.match(body[lead:])
            if m and not m.group(1):           # 冒頭(南無?)阿弥陀仏 で南無なし
                new_body = body[:lead] + "南無" + body[lead:]
                edits.append((tbl, ns, key, v, head + "$@$" + new_body))
    return edits

# --- 2) $@$破損の明示修正(old→new はユニーク) ---
SEP_FIXES = [
    ("CG表", "QuestDlgs", "5337_4_Dlgs_Index2_Text", "$@>", "$@$"),   # 道長: > 混入
    ("CG表", "QuestDlgs", "5203_7_Dlgs_Index4_Text", "$@恐", "$@$恐"),  # 末尾$欠落
    ("CG表", "QuestDlgs", "28508_2_Dlgs_Index2_Text", "$@《", "$@$《"),
    ("CG表", "QuestDlgs", "28509_2_Dlgs_Index2_Text", "$@《", "$@$《"),
    ("CG表", "QuestDlgs", "8529_1_Dlgs_Index5_Text", "$极@$", "$@$"),  # 簡体字割込
]
def sep_edits():
    edits = []
    cache = {}
    for tbl, ns, key, frm, to in SEP_FIXES:
        if tbl not in cache:
            cache[tbl] = locres.parse(glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0])[1]
        old = cache[tbl].get(ns + "\x1f" + key)
        if old is None or frm not in old:
            print(f"  ⚠ SKIP {tbl}|{ns}|{key}: '{frm}' が見つからない(既修正?) old={old!r}")
            continue
        edits.append((tbl, ns, key, old, old.replace(frm, to, 1)))
    return edits

# --- 3) 南無連打の畳み込み(南無×N → 南無)。前回校正の過剰挿入バグ修正 ---
REP = re.compile(r"(南[無无]){2,}")
def rep_edits():
    edits = []
    for f in sorted(glob.glob(f"{LOC}/*/zh-Hans/*.locres")):
        tbl = os.path.basename(os.path.dirname(os.path.dirname(f)))
        for nk, v in locres.parse(f)[1].items():
            if v and REP.search(v):
                ns, key = nk.split("\x1f", 1)
                edits.append((tbl, ns, key, v, REP.sub("南無", v)))
    return edits

def key_index_map(b):
    o = 17; (arr_off,) = struct.unpack_from('<q', b, o); o += 8
    o += 4; (nsc,) = struct.unpack_from('<I', b, o); o += 4
    def rf(b, o):
        (n,) = struct.unpack_from('<i', b, o); o += 4
        if n == 0: return '', o
        if n < 0:
            c = -n; return b[o:o+c*2].decode('utf-16-le').rstrip('\x00'), o+c*2
        return b[o:o+n].decode('utf-8').rstrip('\x00'), o+n
    m = {}
    for _ in range(nsc):
        o += 4; ns, o = rf(b, o); (kc,) = struct.unpack_from('<I', b, o); o += 4
        for _ in range(kc):
            o += 4; key, o = rf(b, o); o += 4; (idx,) = struct.unpack_from('<i', b, o); o += 4
            m[ns+'\x1f'+key] = idx
    return m, arr_off

def main():
    apply = "--apply" in sys.argv
    ne, se, re_ = namu_edits(), sep_edits(), rep_edits()
    print(f"南無付与: {len(ne)}件 / $@$修正: {len(se)}件 / 南無連打畳込: {len(re_)}件")
    for tbl, ns, k, o, n in re_:
        print(f"  [{k}] 南無x{o.count('南無')} → x{n.count('南無')}")
    print("\n--- 南無 先頭5例 ---")
    for tbl, ns, k, o, n in ne[:5]:
        print(f"  [{k}] {o.split('$@$',1)[1][:24]} → {n.split('$@$',1)[1][:26]}")
    print("--- $@$修正 ---")
    for tbl, ns, k, o, n in se:
        i = o.find("$"); print(f"  [{k}] …{o[i-4:i+8]}… → …{n[i-4:i+8]}…")

    by_t = {}
    for e in ne + se + re_:
        by_t.setdefault(e[0], []).append(e)
    if not apply:
        print("\n[プレビューのみ] 実書込は --apply を付けて再実行")
        return
    touched = []
    for tbl, es in by_t.items():
        lp = glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0]
        b = open(lp, "rb").read()
        kmap, arr_off = key_index_map(b)
        _, ver, _, arr, _ = L.load(lp)
        n = 0
        for tbl2, ns, key, old, new in es:
            i = kmap.get(ns + "\x1f" + key)
            if i is None:
                print(f"  ⚠ key無し {key}"); continue
            if arr[i][0] == new:
                continue                      # 共有indexで既に更新済み(重複文字列)
            if arr[i][0] == old:
                arr[i][0] = new; n += 1
            else:
                print(f"  ⚠ 不一致 {key}: 現在値が想定oldと違う old={old!r} now={arr[i][0]!r}")
        if n:
            open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
            touched.append((tbl, n))
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    if os.path.exists(outpak):
        try: os.remove(outpak)
        except PermissionError: open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11",
                    "--mount-point", "../../../"], check=True)
    print(f"\n✅ 書込 {touched} / repak -> {outpak}")

if __name__ == "__main__":
    main()
