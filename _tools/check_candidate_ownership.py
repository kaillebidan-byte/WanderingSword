#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Candidate packetの全fix owner実測snapshotを生成・検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
FIX_GLOB = "fixes_*.json"
FIELD_SEPARATOR = "\x1f"
DEFAULT_TARGET = "CG表"
DEFAULT_NAMESPACE = "QuestDlgs"


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def collect_fix_owners(p4: Path = P4) -> tuple[dict[str, list[str]], list[str]]:
    owners: dict[str, list[str]] = {}
    errors: list[str] = []
    root = p4.parent
    for path in sorted(p4.glob(FIX_GLOB)):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read ownership source {path.relative_to(root)}: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"ownership source must be object: {path.relative_to(root)}")
            continue
        rel = path.relative_to(root).as_posix()
        for full_key in value:
            if isinstance(full_key, str) and full_key.count(FIELD_SEPARATOR) == 2:
                owners.setdefault(full_key, []).append(rel)
    return owners, errors


def current_candidate_paths(state_path: Path = STATE_PATH) -> list[Path]:
    state = load_object(state_path)
    result: list[Path] = []
    for packet in state.get("wave", {}).get("packets", []):
        if not isinstance(packet, dict):
            continue
        path = packet.get("preparation_record", {}).get("candidate_packet")
        if isinstance(path, str) and path:
            result.append(state_path.parent.parent / path)
    return result


def candidate_source(candidate: dict[str, Any]) -> tuple[str, str]:
    source = candidate.get("source")
    if not isinstance(source, dict):
        source = {}
    return str(source.get("target") or DEFAULT_TARGET), str(source.get("namespace") or DEFAULT_NAMESPACE)


def full_key(target: str, namespace: str, short_key: str) -> str:
    return FIELD_SEPARATOR.join((target, namespace, short_key))


def compute_snapshot(candidate: dict[str, Any], *, p4: Path = P4) -> tuple[dict[str, Any], list[str]]:
    owners, errors = collect_fix_owners(p4)
    target, namespace = candidate_source(candidate)
    rows = candidate.get("rows")
    if not isinstance(rows, list):
        return {}, errors + ["candidate.rows must be a list"]

    grouped: dict[str, list[str]] = {}
    unowned: list[str] = []
    duplicates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("key"), str) or not row.get("key"):
            errors.append(f"candidate.rows[{index}].key must be a non-empty string")
            continue
        key = row["key"]
        if key in seen:
            errors.append(f"duplicate candidate row key: {key}")
            continue
        seen.add(key)
        observed = sorted(owners.get(full_key(target, namespace, key), []))
        if not observed:
            unowned.append(key)
        elif len(observed) == 1:
            grouped.setdefault(observed[0], []).append(key)
        else:
            duplicates.append({"key": key, "owners": observed})

    existing = [
        {"path": path, "keys": sorted(keys)}
        for path, keys in sorted(grouped.items())
    ]
    snapshot = {
        "schema_version": 1,
        "generated_from": "all_fixes_glob",
        "fix_glob": "_phase4_proofread/fixes_*.json",
        "target": target,
        "namespace": namespace,
        "row_count": len(seen),
        "existing": existing,
        "unowned": sorted(unowned),
        "duplicates": duplicates,
    }
    return snapshot, errors


def validate_candidate(candidate: dict[str, Any], *, p4: Path = P4, require_snapshot: bool) -> list[str]:
    expected, errors = compute_snapshot(candidate, p4=p4)
    actual = candidate.get("ownership_snapshot")
    if not require_snapshot and not isinstance(actual, dict):
        return errors
    if not isinstance(actual, dict):
        return errors + ["candidate.ownership_snapshot is required"]
    if actual != expected:
        errors.append("candidate.ownership_snapshot is stale or incomplete; run check_candidate_ownership.py --write")
    if expected.get("duplicates"):
        errors.append(f"candidate contains multiple fix owners: {expected['duplicates']!r}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--write", action="store_true", help="全fix owner実測snapshotを書き込む")
    parser.add_argument("--require-current-wave", action="store_true", help="現行wave候補へschema v2 snapshotを必須化する")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [path if path.is_absolute() else ROOT / path for path in args.paths]
    if not paths:
        paths = current_candidate_paths()
    if not paths:
        print("ERROR: no candidate packet paths found")
        return 1

    all_errors: list[str] = []
    checked = 0
    legacy_skipped = 0
    for path in paths:
        candidate = load_object(path)
        require = args.require_current_wave or int(candidate.get("schema_version", 1)) >= 2 or "ownership_snapshot" in candidate
        if args.write:
            snapshot, errors = compute_snapshot(candidate)
            all_errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in errors)
            if errors:
                continue
            candidate["schema_version"] = max(2, int(candidate.get("schema_version", 1)))
            candidate["ownership_snapshot"] = snapshot
            path.write_text(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            print(f"UPDATED: {path.relative_to(ROOT)}")
            checked += 1
            continue
        if not require:
            print(f"LEGACY SKIP: {path.relative_to(ROOT)}")
            legacy_skipped += 1
            continue
        errors = validate_candidate(candidate, require_snapshot=True)
        all_errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in errors)
        checked += 1
        if not errors:
            print(f"OK: {path.relative_to(ROOT)}")

    for error in all_errors:
        print(f"ERROR: {error}")
    print(f"candidate ownership: checked={checked}, legacy_skipped={legacy_skipped}, errors={len(all_errors)}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
