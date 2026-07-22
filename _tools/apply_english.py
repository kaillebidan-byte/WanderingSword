# -*- coding: utf-8 -*-
"""英語混入(及时→timely)の修正。--apply で書込+repak。語は『速やか』。
"""
import os, re, sys, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

TARGETS = [
    ("CG表", "QuestDlgs", "5417_1_Dlgs_Index14_Text"),
    ("CG表", "QuestDlgs", "5417_2_Dlgs_Index13_Text"),
    ("CG表", "QuestDlgs", "7143_2_Dlgs_Index0_Text"),
]
SUB = re.compile(r"\s*timely\s*")
NEW = "速やか"

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
    cache = {}
    edits = {}
    for tbl, ns, key in TARGETS:
        if tbl not in cache:
            cache[tbl] = locres.parse(glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0])[1]
        old = cache[tbl].get(ns + "\x1f" + key)
        if not old or "timely" not in old:
            print(f"  ⚠ SKIP {key}: timely無し old={old!r}"); continue
        new = SUB.sub(NEW, old)
        edits.setdefault(tbl, []).append((ns, key, old, new))
        print(f"[{key}]\n  旧: {old.split('$@$',1)[1]}\n  新: {new.split('$@$',1)[1]}")
    if not apply:
        print("\n[プレビュー] --apply で書込"); return
    touched = []
    for tbl, es in edits.items():
        lp = glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0]
        b = open(lp, "rb").read()
        kmap, arr_off = key_index_map(b)
        _, ver, _, arr, _ = L.load(lp)
        n = 0
        for ns, key, old, new in es:
            i = kmap.get(ns + "\x1f" + key)
            if i is None or arr[i][0] == new: continue
            if arr[i][0] == old:
                arr[i][0] = new; n += 1
            else:
                print(f"  ⚠ 不一致 {key}")
        if n:
            open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
            touched.append((tbl, n))
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    if os.path.exists(outpak):
        try: os.remove(outpak)
        except PermissionError: open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11", "--mount-point", "../../../"], check=True)
    print(f"\n✅ 書込 {touched} / repak -> {outpak}")

if __name__ == "__main__":
    main()
