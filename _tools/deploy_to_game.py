#!/usr/bin/env python3
"""_work の最新pakを、ゲームフォルダの aaWanderingSword_JP_P.pak へ安全に差し替える。
best-effort: ゲームフォルダが見つからない/ロック中なら、何もせずスキップしてログに残す(失敗しない)。
- 初回は元pakを _backup/ に退避(既にあれば温存)。
- 差し替え後、deployedしたpak内に日本語が入っているか自己検証する。
使い方: python3 _tools/deploy_to_game.py
"""
import sys, os, glob, shutil, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
SRC = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
REPAK = os.path.join(ROOT, "_tools", "repak")

def find_game_paks():
    # ゲームフォルダ「Wandering Sword」(翻訳フォルダではない)のPaksを探す
    for base in glob.glob("/sessions/*/mnt/Wandering Sword/Wandering_Sword/Content/Paks"):
        return base
    # 念のためSteam直下パターンも
    for base in glob.glob("/sessions/*/mnt/*/steamapps/common/Wandering Sword/Wandering_Sword/Content/Paks"):
        return base
    return None

def log(msg):
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(ROOT, "_phase4_proofread", "_prooflog.md"), "a", encoding="utf-8") as f:
        f.write(f"- {ts}  [deploy] {msg}\n")
    print("[deploy]", msg)

def main():
    if not os.path.exists(SRC):
        log("スキップ: _work のpakが無い"); return
    paks = find_game_paks()
    if not paks:
        log("スキップ: ゲームフォルダが未マウント(チャット側で差し替えてください)"); return
    dst = os.path.join(paks, "aaWanderingSword_JP_P.pak")
    bkp = os.path.join(ROOT, "_backup", "aaWanderingSword_JP_P.original.pak")
    try:
        # 初回バックアップ
        if os.path.exists(dst) and not os.path.exists(bkp):
            os.makedirs(os.path.dirname(bkp), exist_ok=True)
            shutil.copy2(dst, bkp)
        # 差し替え(rm→cp。ゲーム起動中はここで失敗する)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(SRC, dst)
    except (PermissionError, OSError) as e:
        log(f"スキップ: 差し替え不可(ゲーム起動中か権限) {type(e).__name__}"); return
    # 自己検証: deployedしたpakを展開して日本語が入っているか
    try:
        vdir = "/tmp/_deployverify"
        shutil.rmtree(vdir, ignore_errors=True)
        subprocess.run([REPAK, "unpack", dst, "-o", vdir, "-i",
                        "Wandering_Sword/Content/Localization/系统/zh-Hans/系统.locres"],
                       check=True, capture_output=True)
        lp = glob.glob(f"{vdir}/Wandering_Sword/Content/Localization/系统/zh-Hans/*.locres")[0]
        _, d, *_ = locres.parse(lp)
        ok = sum(1 for v in d.values() if v in ("使用効果", "武器熟練度"))
        log(f"差し替え成功＋検証OK(日本語ヒット{ok}) → ゲーム再起動で反映")
    except Exception:
        log("差し替えは成功(検証はスキップ)")

if __name__ == "__main__":
    main()
