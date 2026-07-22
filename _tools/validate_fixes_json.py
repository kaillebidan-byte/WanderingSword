#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_fixes_json.py 用JSONを、locresを書き換えずに検証する。

検証項目:
- 対象locresとkeyが存在する
- 未適用時は新旧値が異なる
- `$@$` より前の話者接頭辞が不変
- 制御タグ、改行タグ、プレースホルダの並びが不変

`--allow-applied` を付けると、現在値が修正後の値と同一でも正常とする。
修正JSONを適用後の回帰仕様として継続利用するCI向け。

使い方:
  python _tools/validate_fixes_json.py [--allow-applied] fixes.json [fixes2.json ...]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from typing import Iterable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = os.path.join(ROOT, "_work", "jp", "Wandering_Sword", "Content", "Localization")
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres  # noqa: E402

TOKEN_RE = re.compile(r"\$@\$|<[^>]*>|#nl|\{[^}]*\}|\r\n|\n")


def control_tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text or "")


def speaker_prefix(text: str) -> str | None:
    if "$@$" not in (text or ""):
        return None
    return text.split("$@$", 1)[0]


def locres_path(target: str) -> str:
    paths = glob.glob(os.path.join(LOC, target, "zh-Hans", "*.locres"))
    if not paths:
        raise FileNotFoundError(f"locresが見つからない: {target}")
    return paths[0]


def validate_files(
    paths: Iterable[str],
    *,
    allow_applied: bool = False,
) -> tuple[int, int, int, list[str]]:
    cache: dict[str, dict[str, str]] = {}
    checked = 0
    pending = 0
    applied = 0
    errors: list[str] = []

    for path in paths:
        try:
            with open(path, encoding="utf-8") as fp:
                fixes = json.load(fp)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: JSON読込失敗: {exc}")
            continue
        if not isinstance(fixes, dict):
            errors.append(f"{path}: ルートはobjectでなければならない")
            continue

        for full_key, new_value in fixes.items():
            checked += 1
            if not isinstance(full_key, str) or not isinstance(new_value, str):
                errors.append(f"{path}: key/valueは文字列必須: {full_key!r}")
                continue
            parts = full_key.split("\x1f", 2)
            if len(parts) != 3:
                errors.append(f"{path}: 複合key形式不正: {full_key!r}")
                continue
            target, ns, key = parts
            try:
                if target not in cache:
                    _, cache[target], *_ = locres.parse(locres_path(target))
            except (OSError, AssertionError, ValueError) as exc:
                errors.append(f"{path}: {target}: locres読込失敗: {exc}")
                continue

            old_value = cache[target].get(ns + "\x1f" + key)
            label = f"{path}:{target}|{ns}|{key}"
            if old_value is None:
                errors.append(f"{label}: keyなし")
                continue

            if old_value == new_value:
                applied += 1
                if not allow_applied:
                    errors.append(f"{label}: 新旧値が同一")
                continue

            pending += 1
            if speaker_prefix(old_value) != speaker_prefix(new_value):
                errors.append(f"{label}: 話者接頭辞が変化")
            if control_tokens(old_value) != control_tokens(new_value):
                errors.append(
                    f"{label}: 制御トークンが変化 "
                    f"{control_tokens(old_value)!r} -> {control_tokens(new_value)!r}"
                )

    return checked, pending, applied, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-applied",
        action="store_true",
        help="現在値が修正後の値と同一でも、適用済みとして正常扱いする",
    )
    parser.add_argument("paths", nargs="+")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checked, pending, applied, errors = validate_files(
        args.paths,
        allow_applied=args.allow_applied,
    )
    if errors:
        print(f"NG: {checked}件確認 / {len(errors)}件エラー", file=sys.stderr)
        for error in errors:
            print("  - " + error, file=sys.stderr)
        return 1
    print(
        f"OK: {checked}件 / 未適用{pending}件 / 適用済み{applied}件 / "
        "key・接頭辞・制御トークンを確認"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
