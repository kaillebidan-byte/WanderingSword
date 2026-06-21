# -*- coding: utf-8 -*-
"""キャラ/NPC名(Name表)の変更。表示名はName表が正本(対話プレフィックスは触らない=CLAUDE.md)。
deployはしない(_work repakまで)。--apply で書込。
"""
import os, sys, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

# (table, ns, key): 新名
NAME_FIXES = {
    ("Npc", "NPCs", "17101_Name"): "侍女",   # 丫鬟 → 侍女(6011は既に侍女・整合)
}

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
    by_t = {}
    for (tbl, ns, key), nv in NAME_FIXES.items():
        by_t.setdefault(tbl, []).append((ns, key, nv))
    for tbl, items in by_t.items():
        lp = glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0]
        cur = locres.parse(lp)[1]
        for ns, key, nv in items:
            print(f"[{tbl}|{ns}|{key}]  旧:{cur.get(ns+chr(0x1f)+key)!r} → 新:{nv!r}")
    if not apply:
        print("\n[プレビュー] --apply で書込(deployはしない)"); return
    for tbl, items in by_t.items():
        lp = glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0]
        b = open(lp, "rb").read()
        kmap, arr_off = key_index_map(b)
        _, ver, _, arr, _ = L.load(lp)
        n = 0
        for ns, key, nv in items:
            i = kmap.get(ns + "\x1f" + key)
            if i is not None and arr[i][0] != nv:
                arr[i][0] = nv; n += 1
        open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
        print(f"  {tbl}: {n}件書込")
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    if os.path.exists(outpak):
        try: os.remove(outpak)
        except PermissionError: open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11", "--mount-point", "../../../"], check=True)
    print(f"✅ repak -> {outpak}  (deployは未実施)")

if __name__ == "__main__":
    main()
