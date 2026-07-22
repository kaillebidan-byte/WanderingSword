#!/usr/bin/env python3
"""校正ステータスを1コマンドで要約表示。チャット側がここだけ読めば全体が分かる。"""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")

def readlines(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read().splitlines()
    except FileNotFoundError:
        return []

def main():
    bc = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    order, count = bc["order"], bc["count"]
    prog = json.load(open(f"{P4}/char_progress.json", encoding="utf-8"))
    ci, pos = prog["ci"], prog["pos"]
    done = order[:ci]
    total_lines = sum(count.values())
    done_lines = sum(count[c] for c in done) + pos
    print("=== Wandering Sword 校正ステータス ===")
    print(f"完了: {ci}キャラ / 全{len(order)}キャラ")
    if done:
        print(f"  直近完了: {'、'.join(done[-6:])}" + ("…" if len(done) > 6 else ""))
    if ci < len(order):
        cur = order[ci]; tot = count[cur]
        print(f"現在: {cur}  pos {pos}/{tot} ({pos*100//max(tot,1)}%)")
    else:
        print("現在: 全キャラ完了")
    print(f"進捗: 約 {done_lines:,}/{total_lines:,} 行 ({done_lines*100//total_lines}%)")
    print("\n--- 開いてるTODO (_TODO.md) ---")
    opens = [l for l in readlines(f"{P4}/_TODO.md") if l.lstrip().startswith("- [ ]")]
    print("\n".join(opens) if opens else "(なし)")
    print("\n--- 直近の実行ログ見出し (_handover.md) ---")
    heads = [l for l in readlines(f"{P4}/_handover.md") if l.startswith("### ")]
    for h in heads[:5]:
        print(h)
    print("\n※詳細は _handover.md を見出しでgrep。普段は本ダッシュボードのみでよい。")

if __name__ == "__main__":
    main()
