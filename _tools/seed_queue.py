#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""機械置換表の種付けキュー表示。
処理順(by_character)で現在地以降の未完了キャラを、status と `## 機械置換` 節の有無つきで一覧する。
Opusの種付け作業用。使い方: python _tools/seed_queue.py [表示数=40]
"""
import os, sys, json, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")


def persona_info(name):
    md = os.path.join(ROOT, "10_人物", f"{name}.md")
    if not os.path.exists(md):
        return ("(md無)", False)
    t = open(md, encoding="utf-8").read()
    m = re.search(r"^status:\s*(\S+)", t, re.M)
    st = m.group(1) if m else "(なし)"
    has = bool(re.search(r"^##\s*機械置換", t, re.M))
    return (st, has)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    data = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    prog = json.load(open(f"{P4}/char_progress.json", encoding="utf-8"))
    order, lines = data["order"], data["lines"]
    ci = prog["ci"]
    print(f"現在 ci={ci} / 全{len(order)}キャラ / 残り {len(order)-ci}")
    print(f"{'#':>4} {'キャラ':<12} {'行数':>5} {'status':<8} {'機械置換':<6}")
    need = 0
    for i in range(ci, min(ci + n, len(order))):
        name = order[i]
        st, has = persona_info(name)
        cnt = len(lines[name])
        if st == "確定" and not has:
            need += 1
        print(f"{i:>4} {name:<12} {cnt:>5} {st:<8} {'✓' if has else '—':<6}")
    print(f"\n表示{n}体中、種付けが必要(確定かつ節なし) = {need}")


if __name__ == "__main__":
    main()
