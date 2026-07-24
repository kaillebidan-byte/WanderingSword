#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正適用後に残った未反映キーを列挙し、QA artifactへ保存する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import apply_fixes_json as apply


def collect_pending(fixes: dict[str, str]) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[str, str, str, str]]] = {}
    for full_key, expected in fixes.items():
        table, namespace, key = full_key.split("\x1f", 2)
        grouped.setdefault(table, []).append((full_key, namespace, key, expected))

    rows: list[dict[str, Any]] = []
    for table in sorted(grouped):
        path = apply.locate_locres(table)
        index_map, _ = apply.key_index_map(path.read_bytes())
        _, _, _, values, _ = apply.L.load(str(path))
        for full_key, namespace, key, expected in grouped[table]:
            index = index_map.get(namespace + "\x1f" + key)
            if index is None:
                rows.append(
                    {
                        "full_key": full_key,
                        "table": table,
                        "namespace": namespace,
                        "key": key,
                        "status": "missing_key",
                        "expected": expected,
                        "observed": None,
                    }
                )
                continue
            observed = values[index][0]
            if observed != expected:
                rows.append(
                    {
                        "full_key": full_key,
                        "table": table,
                        "namespace": namespace,
                        "key": key,
                        "status": "pending",
                        "expected": expected,
                        "observed": observed,
                    }
                )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="修正JSON。globも指定可")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    fixes, sources = apply.load_fix_files(args.paths)
    rows = collect_pending(fixes)
    for row in rows:
        source = sources.get(row["full_key"], "")
        print(f"PENDING: {row['full_key']} ({source})")
        print(f"  expected: {row['expected']!r}")
        print(f"  observed: {row['observed']!r}")

    report = {
        "fix_count": len(fixes),
        "pending_count": len(rows),
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"pending fix report: {args.out} ({len(rows)} keys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
