#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手動校正オーバーレイ(manual_edits.json)を locres に反映する。配置: _tools/手動校正/
LLM用 cursor.json は触らない（手動レビューは別系統）。

  python _tools/手動校正/apply_manual.py --deploy   # 検証→適用+再パック→ゲームPaksへ配置（一括）
  python _tools/手動校正/apply_manual.py --verify   # ゲーム不要のラウンドトリップ検証（_work非破壊）
  python _tools/手動校正/apply_manual.py            # _work の locres へ適用し pak を再パック
  python _tools/手動校正/apply_manual.py --no-pack  # locres へ適用するが再パックしない

検証(--verify)が確認すること:
  1) 各編集行が new_ja に正しく書き換わる（locres再parseで一致）
  2) 制御タグ/接頭辞($@$より前)が原文と不一致でない
  3) 編集していない行が1件も変化しない
"""
import sys, os, json, glob, struct, subprocess, shutil
# このファイルは _tools/手動校正/ にある → プロジェクトrootは3階層上
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
import locres_write as L
import proofread_server as PS   # validate / split_prefix / tag_multiset を再利用

P4   = os.path.join(ROOT, "_phase4_proofread")
WORK = os.path.join(ROOT, "_work", "jp")
OUTPAK = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
GAME_PAK = (r"C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword"
            r"\Wandering_Sword\Content\Paks\aaWanderingSword_JP_P.pak")
EDITS = os.path.join(P4, "manual_edits.json")
TMP  = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")
SEP = "\x1f"

def wlp(t):
    g = glob.glob(f"{WORK}/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")
    return g[0] if g else None

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
            m[ns + '\x1f' + key] = idx
    return m, arr_off

def load_edits():
    if not os.path.exists(EDITS):
        return {}
    return json.load(open(EDITS, encoding="utf-8"))

def by_target(edits):
    out = {}
    for fk, e in edits.items():
        if "new_ja" not in e:
            continue
        t, ns, key = fk.split(SEP)
        out.setdefault(t, []).append((ns, key, e["new_ja"]))
    return out

def apply_to_file(lp, fixes):
    """locres ファイル lp に fixes=[(ns,key,new_ja)] を適用し、書き換え件数を返す。"""
    b = open(lp, "rb").read()
    kmap, arr_off = key_index_map(b)
    _, ver, _, arr, _ = L.load(lp)
    n = 0
    for ns, key, new_ja in fixes:
        i = kmap.get(ns + "\x1f" + key)
        if i is not None and new_ja and arr[i][0] != new_ja:
            arr[i][0] = new_ja; n += 1
    if n:
        open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
    return n

def verify():
    edits = load_edits()
    bt = by_target(edits)
    if not bt:
        print("編集なし（manual_edits.json が空）。検証スキップ。"); return 0
    os.makedirs(TMP, exist_ok=True)
    fails = 0; newly = 0; already = 0
    for t, fixes in bt.items():
        src = wlp(t)
        if not src:
            print(f"[NG] target {t} の locres が見つからない"); fails += 1; continue
        _, before, *_ = locres.parse(src)             # 現在の locres（適用前）
        tmp = os.path.join(TMP, f"_verify_{t}.locres")
        shutil.copy(src, tmp)
        apply_to_file(tmp, fixes)
        _, after, *_ = locres.parse(tmp)              # 適用後
        edited_keys = set(ns + "\x1f" + key for ns, key, _ in fixes)
        for ns, key, new_ja in fixes:
            fkk = ns + "\x1f" + key
            fk = t + SEP + fkk
            # 旧訳: オーバーレイ記録 → 無ければ現locres（適用済みなら新訳と同じ）
            old = edits.get(fk, {}).get("orig_ja")
            in_locres = (before.get(fkk) == new_ja)   # 既に反映済みか
            if in_locres: already += 1
            else:         newly += 1
            ng = []
            if after.get(fkk) != new_ja:
                ng.append("反映不一致")
            ng += PS.validate(old if old is not None else before.get(fkk, ""), new_ja)
            mark = "NG" if ng else ("反映済" if in_locres else "新規")
            print(f"[{mark}] {t} / {key}")
            if old is not None and old != new_ja:
                print(f"     旧: {old[:60]}")
            elif in_locres and old is None:
                print(f"     旧: (適用済みのため未記録／現locres=新訳)")
            print(f"     新: {new_ja[:60]}")
            if ng:
                print(f"     ⚠ {' / '.join(ng)}"); fails += 1
        # 非編集行が不変か
        changed = [k for k in before
                   if k not in edited_keys and before[k] != after.get(k)]
        if changed:
            print(f"[NG] {t}: 非編集行が {len(changed)}件変化 例:{changed[:3]}"); fails += 1
        os.remove(tmp)
    print(f"\n編集 {len(edits)}件（新規にlocres書換 {newly} / 既に反映済 {already}）"
          f" / 対象target {len(bt)}")
    print("✅ 検証OK（ゲーム非破壊・タグ/接頭辞/非編集行すべて健全）"
          if fails == 0 else f"❌ NG {fails}件")
    return 1 if fails else 0

def apply_real(do_pack=True):
    edits = load_edits()
    bt = by_target(edits)
    touched = []
    for t, fixes in bt.items():
        lp = wlp(t)
        if not lp:
            print(f"warn: {t} locres なし"); continue
        n = apply_to_file(lp, fixes)
        if n:
            touched.append((t, n))
    print("適用:", touched)
    if do_pack and touched:
        outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
        if os.path.exists(outpak):
            try: os.remove(outpak)
            except PermissionError: open(outpak, "wb").close()
        subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11",
                        "--mount-point", "../../../"], check=True)
        print("再パック完了:", outpak)

def deploy():
    """検証 → locres適用+再パック → ゲームPaksへコピー を一括で行う。"""
    print("── ① 検証 ───────────────────────────")
    if verify() != 0:
        print("\n❌ 検証NG。デプロイを中止しました（ゲームは無変更）。")
        return 1
    print("\n── ② 適用＋再パック ─────────────────")
    apply_real(do_pack=True)
    if not os.path.exists(OUTPAK):
        print("❌ 再パックされた pak が無い。デプロイ中止。"); return 1
    print("\n── ③ ゲームへ配置 ───────────────────")
    if not os.path.isdir(os.path.dirname(GAME_PAK)):
        print(f"❌ ゲームの Paks フォルダが見つからない:\n   {os.path.dirname(GAME_PAK)}")
        return 1
    try:
        shutil.copy(OUTPAK, GAME_PAK)
    except PermissionError:
        print("❌ コピー失敗（アクセス拒否／ファイルロック）。")
        print("   ゲームを閉じてから再実行。まだ出るなら PowerShell を管理者として実行。")
        return 1
    s, d = os.path.getsize(OUTPAK), os.path.getsize(GAME_PAK)
    print(f"配置先: {GAME_PAK}")
    print(f"サイズ: _work {s} / game {d}  → {'一致' if s == d else '不一致!!'}")
    print("\n✅ デプロイ完了。ゲームを起動して確認してください。"
          if s == d else "\n❌ サイズ不一致。コピーを確認。")
    return 0 if s == d else 1

def main():
    if "--deploy" in sys.argv:
        sys.exit(deploy())
    if "--verify" in sys.argv:
        sys.exit(verify())
    apply_real(do_pack="--no-pack" not in sys.argv)

if __name__ == "__main__":
    main()
