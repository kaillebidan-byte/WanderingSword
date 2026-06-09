#!/usr/bin/env python3
"""フェーズ2(校正)の反映。修正だけを locres に書き戻し、カーソルを進める。
使い方: python3 _tools/apply_proofread.py 修正.json
修正.json 形式:
  {"reviewed": 60,
   "fixes": [{"target":"Quests任务表","ns":"...","key":"...","new_ja":"修正後の訳"}, ...]}
reviewed = 今回レビューした件数(=pending_proofreadで提示された件数)。修正が無い行も進める。
"""
import sys, os, json, glob, struct, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres_write as L
P4 = os.path.join(ROOT, "_phase4_proofread")
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak")

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

def wlp(t):
    return glob.glob(f"{WORK}/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    reviewed = int(data.get("reviewed", 0))
    fixes = data.get("fixes", [])
    by_t = {}
    for f in fixes:
        by_t.setdefault(f["target"], []).append(f)
    touched = []
    for t, fs in by_t.items():
        lp = wlp(t); b = open(lp, "rb").read()
        kmap, arr_off = key_index_map(b)
        _, ver, _, arr, _ = L.load(lp)
        n = 0
        for f in fs:
            i = kmap.get(f["ns"] + "\x1f" + f["key"])
            if i is not None and f["new_ja"] and arr[i][0] != f["new_ja"]:
                arr[i][0] = f["new_ja"]; n += 1
        if n:
            open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
            touched.append((t, n))
    # 再パック
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    if os.path.exists(outpak):
        try: os.remove(outpak)
        except PermissionError: open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11",
                    "--mount-point", "../../../"], check=True)
    # カーソル前進
    cur = json.load(open(f"{P4}/cursor.json", encoding="utf-8"))
    cur["pos"] += reviewed
    json.dump(cur, open(f"{P4}/cursor.json", "w"), ensure_ascii=False)
    total = len(json.load(open(f"{P4}/queue.json", encoding="utf-8")))
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f"{P4}/_prooflog.md", "a", encoding="utf-8") as f:
        f.write(f"- {ts}  レビュー {reviewed}件 / 修正 {sum(n for _,n in touched)}件 {touched} / "
                f"カーソル {cur['pos']}/{total}\n")
    print(f"レビュー {reviewed}件, 修正 {touched}, カーソル {cur['pos']}/{total}")

if __name__ == "__main__":
    main()
