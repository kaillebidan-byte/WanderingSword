#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宇文逸校正ワーカー用コンテキストパック生成。

正本(ペルソナ+ルール)から必要な節だけを抜粋して _ws_tmp/yuwen_pack.md に組み立てる。
ワーカー(使い捨てサブエージェント)は起動時にこの1ファイルだけ読めばよい＝起動コスト削減。
正本を更新したら再実行するだけ(パックは生成物。直接編集しない＝重複を増やさない)。

使い方: python _tools/yuwen_pack.py
"""
import os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS_TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
OUT = os.path.join(WS_TMP, "yuwen_pack.md")

# (相対パス, [抜粋するH2見出しの前方一致] または "ALL"=frontmatter以外全部)
SPEC = [
    ("10_人物/宇文逸.md", [
        "## 声の核", "## ★一人称", "## モード（register）一覧",
        "## ★二人称・呼称", "## 完成例", "## 典故・固有名",
        "## 注意事項",
    ]),
    ("00_ルール/基本翻訳ルール.md", [
        "## 意訳を恐れない", "## MT臭",
    ]),
    ("00_ルール/世界観口調指針.md", "ALL"),
    ("00_ルール/関係性・呼称マップ.md", [
        "## B. ",
    ]),
]


def strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1:]
    return lines


def extract(lines, prefixes):
    """H2見出し前方一致で節を抜く(次の H1/H2 まで)。見つからない prefix は警告。"""
    out, missing = [], []
    for p in prefixes:
        start = None
        for i, ln in enumerate(lines):
            if ln.startswith(p):
                start = i
                break
        if start is None:
            missing.append(p)
            continue
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## ") or lines[j].startswith("# "):
                end = j
                break
        out.extend(lines[start:end])
        if out and out[-1].strip():
            out.append("")
    return out, missing


def main():
    parts = [
        "# 宇文逸 校正コンテキストパック（生成物・直接編集禁止）",
        f"> `python _tools/yuwen_pack.py` が正本から自動生成（{datetime.date.today()}）。",
        "> 正本: `10_人物/宇文逸.md`／`00_ルール/`。**修正は正本へ**行い、本ファイルは再生成する。",
        "> 古典引用が出た行のみ `00_ルール/典故・古典引用ノート.md` を別途参照（本パック非収録）。",
        "",
    ]
    warn = []
    for rel, spec in SPEC:
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        lines = strip_frontmatter(lines)
        parts.append(f"---\n<!-- 出典: {rel} -->")
        if spec == "ALL":
            parts.extend(lines)
            parts.append("")
        else:
            got, missing = extract(lines, spec)
            parts.extend(got)
            for m in missing:
                warn.append(f"{rel}: 見出し '{m}' が見つからない(正本改編?)")
    os.makedirs(WS_TMP, exist_ok=True)
    body = "\n".join(parts) + "\n"
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print(f"-> {OUT}  {len(body)}文字 / 約{len(body.splitlines())}行")
    for w in warn:
        print(f"⚠ {w}")
    if warn:
        sys.exit(1)


if __name__ == "__main__":
    main()
