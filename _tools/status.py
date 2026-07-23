#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳・校正ステータスを1コマンドで要約表示する。

`char_progress.json` の完走は「初回キャラ校正を一巡した」ことだけを表す。
最終品質やペルソナ・関係性の正当性は `audit_status.json` の再監査段階で別管理する。
直ちに着手する作業は `CURRENT_WORK.json` を正本とする。
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")


def readlines(path: str) -> list[str]:
    try:
        return open(path, encoding="utf-8", errors="ignore").read().splitlines()
    except FileNotFoundError:
        return []


def load_json(path: str, default: Any = None) -> Any:
    try:
        with open(path, encoding="utf-8") as fp:
            return json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def main() -> None:
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
        current_char = order[ci]
        total = count[current_char]
        print(f"現在: {current_char}  pos {pos}/{total} ({pos * 100 // max(total, 1)}%)")
    else:
        print("現在: 一巡完了（最終品質保証ではない）")
    if total_lines:
        print(f"処理行: 約 {done_lines:,}/{total_lines:,} 行 ({done_lines * 100 // total_lines}%)")

    audit = load_json(f"{P4}/audit_status.json")
    work = load_json(f"{P4}/CURRENT_WORK.json")

    print("\n--- 品質再監査 ---")
    if not audit:
        print("未管理: audit_status.json なし、またはJSON不正")
    else:
        quality = audit.get("project", {}).get("quality_reaudit", {})
        audit_current = audit.get("current", {})
        latest_build = audit.get("project", {}).get("latest_build", {})
        print(f"状態: {quality.get('status', 'unknown')}")
        print(f"方式: {quality.get('strategy', '(未設定)')}")
        print(f"現在クラスタ: {audit_current.get('cluster', '(未設定)')}")
        print(f"現在ペア: {audit_current.get('pair', '(未設定)')}")
        print(f"段階: {audit_current.get('stage', '(未設定)')}")
        print(f"全体適用キー: {latest_build.get('applied_keys', '(未設定)')}")
        print(f"build: {latest_build.get('status', '(未設定)')}")
        print(f"game verification: {latest_build.get('game_verified', '(未設定)')}")

    print("\n--- 直ちに着手する作業 (CURRENT_WORK.json) ---")
    if not work:
        print("未管理: CURRENT_WORK.json なし、またはJSON不正")
    else:
        immediate = work.get("immediate_next", {})
        scenes = immediate.get("scene_groups", [])
        print(f"更新日: {work.get('updated_at', '(未設定)')}")
        print(f"現在ペア: {work.get('current_pair', '(未設定)')}")
        print(f"完了束: 第{work.get('last_completed_batch', '?')}束")
        print(f"人物ペア適用キー: {work.get('pair_applied_keys', '(未設定)')}")
        print(f"プロジェクト適用キー: {work.get('project_applied_keys', '(未設定)')}")
        print(f"対象場面: {', '.join(map(str, scenes)) if scenes else '(未設定)'}")
        print(f"次: {immediate.get('task', '(未設定)')}")
        print(f"境界: {immediate.get('boundary', '(未設定)')}")

    print("\n--- 整合警告 ---")
    warnings: list[str] = []
    if audit and work:
        audit_current = audit.get("current", {})
        latest_build = audit.get("project", {}).get("latest_build", {})
        pair_status = audit.get("pair_status", {}).get(work.get("current_pair"), {})
        if audit_current.get("pair") != work.get("current_pair"):
            warnings.append("CURRENT_WORK と audit_status の現在ペアが不一致")
        if latest_build.get("applied_keys") != work.get("project_applied_keys"):
            warnings.append("CURRENT_WORK と audit_status の全体適用キー数が不一致")
        if pair_status.get("applied_keys") != work.get("pair_applied_keys"):
            warnings.append("CURRENT_WORK と audit_status の人物ペア適用キー数が不一致")
        audit_next = audit_current.get("next_action")
        work_next = work.get("immediate_next", {}).get("task")
        if audit_next and work_next and audit_next != work_next:
            warnings.append("audit_status.current.next_action より CURRENT_WORK.immediate_next を優先")

    todo_lines = readlines(f"{P4}/_TODO.md")
    mowen_line = next((line for line in todo_lines if line.startswith("- [ ] **宇文逸↔莫問**")), "")
    match = re.search(r"計(\d+)キー", mowen_line)
    if match and work and int(match.group(1)) != work.get("pair_applied_keys"):
        warnings.append("_TODO.md の宇文逸↔莫問累計が古い。現在値は CURRENT_WORK/audit_status を参照")

    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    else:
        print("(なし)")

    print("\n--- 開いてる横断TODO (_TODO.md) ---")
    opens = [line for line in todo_lines if line.lstrip().startswith("- [ ]")]
    print("\n".join(opens) if opens else "(なし)")

    print("\n--- 履歴アーカイブ (_handover.md) ---")
    heads = [line for line in readlines(f"{P4}/_handover.md") if line.startswith("### ")]
    if heads:
        print("現在地ではない。必要な場合のみ履歴として参照:")
        for head in heads[:5]:
            print(head)
    else:
        print("(見出しなし)")

    print(
        "\n※ 現在地と即時作業は CURRENT_WORK.json、品質段階と累計は audit_status.json。"
        "ペルソナ・関係性マップ・TODO・過去ログは反例があれば改訂する。"
    )


if __name__ == "__main__":
    main()
