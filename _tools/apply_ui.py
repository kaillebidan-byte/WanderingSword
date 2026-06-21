# -*- coding: utf-8 -*-
"""UIラベル(系统/程序_导出 等)の文言変更。値を丸ごと置換。deployはしない(_work repakまで)。--apply で書込。
"""
import os, sys, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

# (table, ns, key): 新ラベル。ns は 系统 では "" (空)。
UI_FIXES = {
    ("系统", "", "A926DAD24FF7F1EB4F053F87F5B4B531"): "一括修練",      # 高速レベルアップ
    ("系统", "", "F99EBDEB4FFFF7A58E3B5B8C886B3031"): "悟りを記す",      # 感想を書く
    ("系统", "", "B4E4AB954135E543BE5BF28DFAECFF5B"): "一気通脈",      # ワンクリック突撃
    # 会心の一撃 → 会心率 (原文Hant=暴擊=能力値。標準ラベル5件。説明文12件は動作表現で温存)
    ("系统", "", "1D94D5B94678B200DE0F27BFDFFE9E05"): "会心率",
    ("系统", "", "A37464604414205E9E0040BCD1056888"): "会心率",
    ("系统", "", "FF58180941829D3159F328B8CA3F6957"): "会心率",
    ("系统", "", "947C78334A73ADC136BE0088823E75F0"): "会心率:",
    ("系统", "", "D03A76DC49E5399C26796C9CE3DDF005"): "会心率:",
    # 衝撃 → 点穴 で経脈UI統一(Q2: 全体統一)。一括衝撃(=全振り)は一気通脈に。
    ("系统", "", "B17DD2DA42C19B443B9123AB9DE13E33"): "点穴",            # 衝撃
    ("系统", "", "40753AC24911D118E06AFA9FF591EEFE"): "点穴後",          # 衝撃後
    ("系统", "", "EF9D38CB49B740A1495910800E673EEE"): "点穴完了",        # ツボ衝撃完了
    ("程序_导出", "JHNeoUI_Prime", "chongji_all_internal_error"): "一気通脈に失敗",
    ("程序_导出", "JHNeoUI_Prime", "chongji_all_config_error"): "一気通脈の設定に失敗",
    ("程序_导出", "JHNeoUI_Prime", "冲击条件不足"): "点穴条件を満たさない",
    # アンインストール → 装備解除 (原文=卸載。武学/装備の「外す」。装備(裝備)と対で揃える)
    ("系统", "", "0B0FD1C0406BE6157F48F39E3E7B15E8"): "装備解除",
    ("系统", "", "26FD2EBF4C5F69FD14E5E08330287BC3"): "装備解除",
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
    for (tbl, ns, key), nv in UI_FIXES.items():
        by_t.setdefault(tbl, []).append((ns, key, nv))
    for tbl, items in by_t.items():
        cur = locres.parse(glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0])[1]
        for ns, key, nv in items:
            print(f"[{tbl}|{ns}|{key[:16]}…]  旧:{cur.get(ns+chr(0x1f)+key)!r} → 新:{nv!r}")
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
            if i is None: print(f"  ⚠ key無し {key}"); continue
            if arr[i][0] != nv:
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
