#!/usr/bin/env python3
"""キャラ単位の校正の反映。修正を locres に書き戻し、キャラ進捗を進める。
使い方: python3 _tools/apply_char.py 修正.json
修正.json 形式:
  {"reviewed": 200,                      # 今回レビューした件数(進捗前進量。監査時は0)
   "fixes": [{"target","ns","key","new_ja"}, ...]}
reviewed>0 のとき現在キャラの pos を進める。pos がそのキャラの全行に達したら次キャラへ。
"""
import sys, os, json, glob, struct, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres_write as L
P4 = os.path.join(ROOT, "_phase4_proofread")
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

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
    inbox = sys.argv[1]
    data = json.load(open(inbox, encoding="utf-8"))
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
            if i is None:
                continue
            cur = arr[i][0]
            if f.get("new_body") is not None:   # コスト削減: 本文のみ。接頭辞($@$まで)は現訳から再付与
                nv = (cur.split("$@$", 1)[0] + "$@$" + f["new_body"]) if "$@$" in cur else f["new_body"]
            elif f.get("new_ja"):               # 後方互換: 完全形(接頭辞込み)もそのまま受理
                nv = f["new_ja"]
            else:
                continue
            if cur != nv:
                arr[i][0] = nv; n += 1
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
    # 進捗
    prog = json.load(open(f"{P4}/char_progress.json", encoding="utf-8"))
    data_idx = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    order, lines = data_idx["order"], data_idx["lines"]
    note = ""
    if reviewed > 0:
        prog["pos"] += reviewed
        while prog["ci"] < len(order) and prog["pos"] >= len(lines[order[prog["ci"]]]):
            done = order[prog["ci"]]; note += f" / 「{done}」完了→次キャラへ"
            prog["ci"] += 1; prog["pos"] = 0
        json.dump(prog, open(f"{P4}/char_progress.json", "w"), ensure_ascii=False)
    cur = order[prog["ci"]] if prog["ci"] < len(order) else "(全完了)"
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f"{P4}/_prooflog.md", "a", encoding="utf-8") as f:
        f.write(f"- {ts}  [キャラ別] レビュー {reviewed} / 修正 {sum(n for _,n in touched)}{touched}"
                f" / 現在: {cur} (ci={prog['ci']},pos={prog['pos']}){note}\n")
    print(f"レビュー {reviewed}, 修正 {touched}, 現在キャラ {cur} (ci={prog['ci']}, pos={prog['pos']}){note}")
    # 反映済みinboxを削除。次バッチのWrite(「未読ファイルは上書き不可」制約)に毎回引っかからないように。
    try:
        os.remove(inbox)
    except OSError:
        pass

if __name__ == "__main__":
    main()
