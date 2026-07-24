#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXT_TASK_PACKETのfocus keyごとの実所有をQA artifactへ出力する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import check_next_task_packet as checker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    packet = checker.load(checker.PACKET_PATH)
    source = packet.get("source", {})
    flow = packet.get("scene_flow", [])
    ownership = packet.get("ownership_boundary", {})
    machine = ownership.get("machine_ownership", {}) if isinstance(ownership, dict) else {}

    declared: dict[str, dict[str, Any]] = {}
    for entry in machine.get("existing", []) if isinstance(machine, dict) else []:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        for key in entry.get("keys", []) if isinstance(entry.get("keys"), list) else []:
            if isinstance(key, str):
                declared[key] = {"status": "existing", "declared_owner": path}
    for entry in machine.get("unowned", []) if isinstance(machine, dict) else []:
        if not isinstance(entry, dict):
            continue
        key = entry.get("key")
        if isinstance(key, str):
            declared[key] = {
                "status": "unowned",
                "planned_owner": entry.get("planned_owner"),
            }

    collection_errors: list[str] = []
    owners = checker.collect_fix_owners(collection_errors)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for scene in flow if isinstance(flow, list) else []:
        if not isinstance(scene, dict):
            continue
        scene_name = scene.get("scene")
        for short_key in scene.get("focus_keys", []) if isinstance(scene.get("focus_keys"), list) else []:
            if not isinstance(short_key, str) or short_key in seen:
                continue
            seen.add(short_key)
            full = checker.full_key(source, short_key)
            row: dict[str, Any] = {
                "scene": scene_name,
                "key": short_key,
                "full_key": full,
                "observed_owners": owners.get(full, []),
            }
            row.update(declared.get(short_key, {"status": "undeclared"}))
            rows.append(row)

    report = {
        "task_id": packet.get("task_id"),
        "current_pair": packet.get("current_pair"),
        "scene_groups": packet.get("scene_groups"),
        "collection_errors": collection_errors,
        "focus_key_count": len(rows),
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"next-task ownership report: {args.out} ({len(rows)} keys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
