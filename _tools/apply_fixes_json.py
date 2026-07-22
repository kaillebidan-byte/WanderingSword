#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正JSONをlocresへ安全に反映し、必要ならpakを一度だけ再生成する。

修正JSON形式::

    {"<table>\x1f<namespace>\x1f<key>": "新しい値全体", ...}

複数JSONを同時に渡せる。同一キーが複数ファイルにあり、値が異なる場合は
書き込み前に停止する。cursorは進めず、ゲームフォルダへdeployしない。

使い方::

    python _tools/apply_fixes_json.py fixes.json
    python _tools/apply_fixes_json.py fixes1.json fixes2.json --apply
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools"))

import locres_write as L  # noqa: E402

LOC = ROOT / "_work" / "jp" / "Wandering_Sword" / "Content" / "Localization"
WORK = ROOT / "_work" / "jp"
REPAK = ROOT / "_tools" / ("repak.exe" if os.name == "nt" else "repak")
OUTPAK = ROOT / "_work" / "aaWanderingSword_JP_P.pak"


@dataclass
class TargetPlan:
    table: str
    path: Path
    original: bytes
    array_offset: int
    version: int
    values: list
    pending: int
    applied: int


def key_index_map(data: bytes) -> tuple[dict[str, int], int]:
    offset = 17
    (array_offset,) = struct.unpack_from("<q", data, offset)
    offset += 12
    (namespace_count,) = struct.unpack_from("<I", data, offset)
    offset += 4

    def read_fstring(blob: bytes, pos: int) -> tuple[str, int]:
        (length,) = struct.unpack_from("<i", blob, pos)
        pos += 4
        if length == 0:
            return "", pos
        if length < 0:
            chars = -length
            end = pos + chars * 2
            return blob[pos:end].decode("utf-16-le").rstrip("\x00"), end
        end = pos + length
        return (
            blob[pos:end].decode("utf-8", "surrogateescape").rstrip("\x00"),
            end,
        )

    mapping: dict[str, int] = {}
    for _ in range(namespace_count):
        offset += 4
        namespace, offset = read_fstring(data, offset)
        (key_count,) = struct.unpack_from("<I", data, offset)
        offset += 4
        for _ in range(key_count):
            offset += 4
            key, offset = read_fstring(data, offset)
            (index,) = struct.unpack_from("<i", data, offset)
            offset += 4
            mapping[namespace + "\x1f" + key] = index
    return mapping, array_offset


def expand_paths(raw_paths: Iterable[str]) -> list[str]:
    """PowerShell等でもglobを使えるよう、引数内のワイルドカードを展開する。"""
    expanded: list[str] = []
    seen: set[str] = set()
    for raw in raw_paths:
        matches = sorted(glob.glob(raw)) if glob.has_magic(raw) else [raw]
        if not matches:
            raise FileNotFoundError(f"修正JSONが見つからない: {raw}")
        for match in matches:
            normalized = os.path.normpath(match)
            if normalized not in seen:
                seen.add(normalized)
                expanded.append(normalized)
    if not expanded:
        raise ValueError("修正JSONが指定されていない")
    return expanded


def load_fix_files(paths: Iterable[str]) -> tuple[dict[str, str], dict[str, str]]:
    """複数JSONを統合し、同一キーの競合を検出する。"""
    fixes: dict[str, str] = {}
    sources: dict[str, str] = {}
    for path in expand_paths(paths):
        try:
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}: JSON読込失敗: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: ルートはobjectでなければならない")

        for full_key, new_value in payload.items():
            if not isinstance(full_key, str) or not isinstance(new_value, str):
                raise ValueError(f"{path}: key/valueは文字列必須: {full_key!r}")
            if len(full_key.split("\x1f", 2)) != 3:
                raise ValueError(f"{path}: 複合key形式不正: {full_key!r}")
            if full_key in fixes and fixes[full_key] != new_value:
                raise ValueError(
                    "修正束間で同一キーの値が競合: "
                    f"{full_key!r}\n  - {sources[full_key]}\n  - {path}"
                )
            if full_key not in fixes:
                fixes[full_key] = new_value
                sources[full_key] = path
    return fixes, sources


def select_locres(table: str, matches: Iterable[Path]) -> Path:
    """同一ディレクトリに補助locresがあっても、テーブル同名の正本を選ぶ。"""
    candidates = sorted(matches)
    if not candidates:
        raise FileNotFoundError(f"{table}: locresが見つからない")
    exact = [path for path in candidates if path.stem == table]
    if len(exact) == 1:
        return exact[0]
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError(
        f"{table}: 正本locresを一意に選べない: "
        + ", ".join(str(path) for path in candidates)
    )


def locate_locres(table: str) -> Path:
    return select_locres(table, (LOC / table / "zh-Hans").glob("*.locres"))


def build_plans(fixes: dict[str, str]) -> tuple[list[TargetPlan], int, int]:
    grouped: dict[str, list[tuple[str, str, str]]] = {}
    for full_key, new_value in fixes.items():
        table, namespace, key = full_key.split("\x1f", 2)
        grouped.setdefault(table, []).append((namespace, key, new_value))

    plans: list[TargetPlan] = []
    total_pending = 0
    total_applied = 0
    missing: list[str] = []

    for table in sorted(grouped):
        path = locate_locres(table)
        original = path.read_bytes()
        index_map, array_offset = key_index_map(original)
        _, version, _, values, _ = L.load(str(path))
        pending = 0
        applied = 0

        for namespace, key, new_value in grouped[table]:
            index = index_map.get(namespace + "\x1f" + key)
            if index is None:
                missing.append(f"{table}|{namespace}|{key}")
                continue
            if values[index][0] == new_value:
                applied += 1
            else:
                values[index][0] = new_value
                pending += 1

        plans.append(
            TargetPlan(
                table=table,
                path=path,
                original=original,
                array_offset=array_offset,
                version=version,
                values=values,
                pending=pending,
                applied=applied,
            )
        )
        total_pending += pending
        total_applied += applied

    if missing:
        raise KeyError("locresに存在しないkey:\n  - " + "\n  - ".join(missing))
    return plans, total_pending, total_applied


def write_plans(plans: Iterable[TargetPlan]) -> None:
    """全targetの検査完了後にだけlocresを書き込む。"""
    for plan in plans:
        if plan.pending:
            rebuilt = plan.original[: plan.array_offset] + L.write_string_array(
                plan.values, plan.version
            )
            plan.path.write_bytes(rebuilt)


def repack() -> None:
    if not REPAK.is_file():
        raise FileNotFoundError(f"repak実体が見つからない: {REPAK}")
    if OUTPAK.exists():
        try:
            OUTPAK.unlink()
        except PermissionError:
            OUTPAK.write_bytes(b"")
    subprocess.run(
        [
            str(REPAK),
            "pack",
            str(WORK),
            str(OUTPAK),
            "--version",
            "V11",
            "--mount-point",
            "../../../",
        ],
        check=True,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="修正JSON。globも指定可")
    parser.add_argument("--apply", action="store_true", help="locresへ書き込む")
    parser.add_argument(
        "--no-pack",
        action="store_true",
        help="--apply時もpakを再生成しない。検査用途のみ",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        fixes, _ = load_fix_files(args.paths)
        plans, pending, applied = build_plans(fixes)
    except (FileNotFoundError, KeyError, ValueError, OSError, AssertionError) as exc:
        print(f"NG: {exc}", file=sys.stderr)
        return 1

    for plan in plans:
        print(f"  {plan.table}: 未適用{plan.pending}件 / 適用済み{plan.applied}件")

    if not args.apply:
        print(f"[プレビュー] 計{pending}件 / 適用済み{applied}件 / --apply で書込")
        return 0

    if pending == 0:
        print(f"[適用] 計0件 / 適用済み{applied}件 / 変更なし・repak省略")
        return 0

    try:
        write_plans(plans)
        if not args.no_pack:
            repack()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"NG: 書込またはrepak失敗: {exc}", file=sys.stderr)
        return 1

    suffix = "repak省略" if args.no_pack else f"repak -> {OUTPAK}"
    print(f"[適用] 計{pending}件書込 / 適用済み{applied}件 / {suffix}")
    print("deployは未実施")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
