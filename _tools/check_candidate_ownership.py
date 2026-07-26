#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Candidate packetのowner snapshotを生成し、private厳密一致またはrelease時live実測を検査する。"""
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
SNAPSHOT_IDENTITY_FIELDS = (
    "schema_version",
    "generated_from",
    "fix_glob",
    "target",
    "namespace",
    "row_count",
)


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


def current_candidate_paths(state_path: Path = STATE_PATH) -> tuple[list[Path], set[str]]:
    state = load_object(state_path)
    policy = state.get("ownership_policy", {})
    legacy = set(policy.get("legacy_candidate_paths", [])) if isinstance(policy, dict) else set()
    result: list[Path] = []
    for packet in state.get("wave", {}).get("packets", []):
        if not isinstance(packet, dict):
            continue
        path = packet.get("preparation_record", {}).get("candidate_packet")
        if isinstance(path, str) and path:
            result.append(state_path.parent.parent / path)
    return result, legacy


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


def _snapshot_partition(snapshot: dict[str, Any]) -> tuple[list[str], list[str]]:
    keys: list[str] = []
    errors: list[str] = []
    existing = snapshot.get("existing")
    if not isinstance(existing, list):
        errors.append("candidate.ownership_snapshot.existing must be a list")
        existing = []
    for index, item in enumerate(existing):
        if not isinstance(item, dict):
            errors.append(f"candidate.ownership_snapshot.existing[{index}] must be an object")
            continue
        path = item.get("path")
        item_keys = item.get("keys")
        if not isinstance(path, str) or not path.startswith("_phase4_proofread/fixes_"):
            errors.append(f"candidate.ownership_snapshot.existing[{index}].path is invalid")
        if not isinstance(item_keys, list) or any(not isinstance(key, str) or not key for key in item_keys):
            errors.append(f"candidate.ownership_snapshot.existing[{index}].keys must be a string list")
            continue
        keys.extend(item_keys)

    unowned = snapshot.get("unowned")
    if not isinstance(unowned, list) or any(not isinstance(key, str) or not key for key in unowned):
        errors.append("candidate.ownership_snapshot.unowned must be a string list")
    else:
        keys.extend(unowned)

    duplicates = snapshot.get("duplicates")
    if not isinstance(duplicates, list):
        errors.append("candidate.ownership_snapshot.duplicates must be a list")
    else:
        for index, item in enumerate(duplicates):
            key = item.get("key") if isinstance(item, dict) else None
            owner_paths = item.get("owners") if isinstance(item, dict) else None
            if not isinstance(key, str) or not key:
                errors.append(f"candidate.ownership_snapshot.duplicates[{index}].key is invalid")
                continue
            if not isinstance(owner_paths, list) or len(owner_paths) < 2 or any(not isinstance(path, str) for path in owner_paths):
                errors.append(f"candidate.ownership_snapshot.duplicates[{index}].owners is invalid")
            keys.append(key)
    return keys, errors


def _candidate_row_keys(candidate: dict[str, Any]) -> tuple[list[str], list[str]]:
    rows = candidate.get("rows")
    if not isinstance(rows, list):
        return [], ["candidate.rows must be a list"]
    keys: list[str] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        key = row.get("key") if isinstance(row, dict) else None
        if not isinstance(key, str) or not key:
            errors.append(f"candidate.rows[{index}].key must be a non-empty string")
            continue
        keys.append(key)
    return keys, errors


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


def validate_candidate_live(
    candidate: dict[str, Any],
    *,
    p4: Path = P4,
) -> tuple[dict[str, Any], list[str], bool]:
    """Release時は現在ownerを正本にし、保存snapshotは監査時点の構造記録として検査する。"""
    expected, errors = compute_snapshot(candidate, p4=p4)
    actual = candidate.get("ownership_snapshot")
    if not isinstance(actual, dict):
        return expected, errors + ["candidate.ownership_snapshot is required"], False

    for field in SNAPSHOT_IDENTITY_FIELDS:
        if actual.get(field) != expected.get(field):
            errors.append(
                f"candidate.ownership_snapshot.{field} mismatch: "
                f"stored={actual.get(field)!r} live={expected.get(field)!r}"
            )

    stored_keys, stored_errors = _snapshot_partition(actual)
    row_keys, row_errors = _candidate_row_keys(candidate)
    errors.extend(stored_errors)
    errors.extend(row_errors)
    if len(stored_keys) != len(set(stored_keys)):
        errors.append("candidate.ownership_snapshot contains duplicate row keys")
    if sorted(stored_keys) != sorted(row_keys):
        errors.append("candidate.ownership_snapshot row partition does not match candidate.rows")

    if expected.get("duplicates"):
        errors.append(f"candidate contains multiple live fix owners: {expected['duplicates']!r}")
    return expected, errors, actual != expected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="全fix owner実測snapshotを書き込む")
    mode.add_argument(
        "--release-live",
        action="store_true",
        help="release時はlive ownerを正本にし、保存snapshot差は警告として扱う",
    )
    parser.add_argument("--require-current-wave", action="store_true", help="現行wave候補へschema v2 snapshotを必須化する")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [path if path.is_absolute() else ROOT / path for path in args.paths]
    legacy_paths: set[str] = set()
    if not paths:
        paths, legacy_paths = current_candidate_paths()
    if not paths:
        print("ERROR: no candidate packet paths found")
        return 1

    all_errors: list[str] = []
    checked = 0
    legacy_skipped = 0
    drifted = 0
    for path in paths:
        candidate = load_object(path)
        rel = path.relative_to(ROOT).as_posix()
        is_legacy = rel in legacy_paths
        require = (
            args.release_live
            or (args.require_current_wave and not is_legacy)
            or int(candidate.get("schema_version", 1)) >= 2
            or "ownership_snapshot" in candidate
        )
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
        drift = False
        if args.release_live:
            live, errors, drift = validate_candidate_live(candidate)
            if drift and not errors:
                drifted += 1
                existing_count = sum(
                    len(item.get("keys", []))
                    for item in live.get("existing", [])
                    if isinstance(item, dict)
                )
                print(
                    f"LIVE DRIFT: {path.relative_to(ROOT)} "
                    f"stored snapshot differs; live existing={existing_count} "
                    f"unowned={len(live.get('unowned', []))}"
                )
        else:
            errors = validate_candidate(candidate, require_snapshot=True)
        all_errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in errors)
        checked += 1
        if not errors and not drift:
            print(f"OK: {path.relative_to(ROOT)}")

    for error in all_errors:
        print(f"ERROR: {error}")
    print(
        "candidate ownership: "
        f"checked={checked}, legacy_skipped={legacy_skipped}, "
        f"live_drifted={drifted}, errors={len(all_errors)}"
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
