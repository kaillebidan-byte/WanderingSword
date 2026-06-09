#!/usr/bin/env python3
"""翻訳マッピングを反映し、locres書き戻し→pak再パックまで行う。
使い方: python3 _tools/apply_translations.py 翻訳マッピング.json
マッピング形式: {"原文中国語": "日本語訳", ...}

処理:
 1) 全gaps_*.jsonの target_ja を、マッピングに一致する原文に対して充填(翻訳メモリ流用)
 2) _work/jp 内の該当locresの文字列だけ差し替え(構造はバイト無傷)
 3) _work/jp を V11 で再パック -> _work/aaWanderingSword_JP_P.pak
 4) _phase3_gaps/_runlog.md に追記
ゲームフォルダへの差し替えは行わない(チャット側で実施)。
"""
import json, re, sys, os, glob, struct, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres_write as L
GAP = os.path.join(ROOT, "_phase3_gaps")
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak")
ALL = ["Buff与道具","CG表","Npc","Quests任务表","Skills技能表","系统","门派地图与提示"]

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

def locp(t):
    return glob.glob(f"{WORK}/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    mapping = json.load(open(sys.argv[1], encoding="utf-8"))
    mapping = {k: v for k, v in mapping.items() if v}
    filled_total = 0; touched_targets = set()
    for t in ALL:
        gf = f"{GAP}/gaps_{t}.json"
        rows = json.load(open(gf, encoding="utf-8"))
        changed = False; pending = {}
        for r in rows:
            if not r.get("target_ja") and r["source_zh"] in mapping:
                r["target_ja"] = mapping[r["source_zh"]]; changed = True; filled_total += 1
        if changed:
            json.dump(rows, open(gf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # locresへ反映(このファイルで target_ja があり、まだ原文のままのキー)
        lp = locp(t); b = open(lp, "rb").read()
        kmap, arr_off = key_index_map(b)
        _, ver, _, arr, _ = L.load(lp)
        n = 0
        for r in rows:
            if not r.get("target_ja"): continue
            fk = r["namespace"] + '\x1f' + r["key"]
            i = kmap.get(fk)
            if i is not None and arr[i][0] != r["target_ja"]:
                arr[i][0] = r["target_ja"]; n += 1
        if n:
            open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
            touched_targets.add(t)
    # 再パック
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    # マウント上では os.remove が権限エラーになるため、内容を空にして上書きさせる
    if os.path.exists(outpak):
        try:
            os.remove(outpak)
        except PermissionError:
            open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11",
                    "--mount-point", "../../../"], check=True)
    # ログ
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f"{GAP}/_runlog.md", "a", encoding="utf-8") as f:
        f.write(f"- {ts}  訳語充填 {filled_total}件 / locres更新 {sorted(touched_targets)} / pak再生成OK\n")
    print(f"充填 {filled_total}件, locres更新 {sorted(touched_targets)}, pak -> {outpak}")

if __name__ == "__main__":
    main()
