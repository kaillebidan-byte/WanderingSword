#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳・校正ステータスを1コマンドで要約表示する。

`char_progress.json` の完走は「初回キャラ校正を一巡した」ことだけを表す。
最終品質やペルソナ・関係性の正当性は `audit_status.json` の再監査段階で別管理する。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")


def readlines(path):
    try:
        return open(path, encoding="utf-8", errors="ignore").read().splitlines()
    except FileNotFoundError:
        return []


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError:
        return default


def main():
    bc = load_json(f"{P4}/by_character.json", {"order": [], "count": {}})
    order, count = bc["order"], bc["count"]
    prog = load_json(f"{P4}/char_progress.json", {"ci": 0, "pos": 0})
    ci, pos = prog["ci"], prog["pos"]
    done = order[:ci]
    total_lines = sum(count.values())
    done_lines = sum(count[c] for c in done) + pos

    print("=== Wandering Sword 翻訳品質ステータス ===")
    print("\n--- 初回キャラ校正（一巡） ---")
    print(f"一巡済み: {ci}キャラ / 全{len(order)}キャラ")
    if ci < len(order):
        current = order[ci]
        total = count[current]
        print(f"現在: {current}  pos {pos}/{total} ({pos * 100 // max(total, 1)}%)")
    else:
        print("現在: 一巡完了（最終品質保証ではない）")
    if total_lines:
        print(f"処理行: 約 {done_lines:,}/{total_lines:,} 行 ({done_lines * 100 // total_lines}%)")

    audit = load_json(f"{P4}/audit_status.json")
    print("\n--- 品質再監査 ---")
    if not audit:
        print("未管理: audit_status.json なし")
    else:
        quality = audit.get("project", {}).get("quality_reaudit", {})
        current = audit.get("current", {})
        print(f"状態: {quality.get('status', 'unknown')}")
        print(f"方式: {quality.get('strategy', '(未設定)')}")
        print(f"現在クラスタ: {current.get('cluster', '(未設定)')}")
        print(f"現在ペア: {current.get('pair', '(未設定)')}")
        print(f"段階: {current.get('stage', '(未設定)')}")
        print(f"次: {current.get('next_action', '(未設定)')}")
        print("\n再監査キュー:")
        for item in audit.get("queue", []):
            print(f"  - [{item.get('status', '?')}] {item.get('label', item.get('id', '?'))}")

    print("\n--- 開いてるTODO (_TODO.md) ---")
    opens = [line for line in readlines(f"{P4}/_TODO.md") if line.lstrip().startswith("- [ ]")]
    print("\n".join(opens) if opens else "(なし)")

    print("\n--- 直近の実行ログ見出し (_handover.md) ---")
    heads = [line for line in readlines(f"{P4}/_handover.md") if line.startswith("### ")]
    for head in heads[:5]:
        print(head)

    print(
        "\n※ `status: 確定` は初回作業の着手可能を示すだけ。"
        "ペルソナ・関係性・既訳の正当性は再監査の段階を参照する。"
    )


if __name__ == "__main__":
    main()
