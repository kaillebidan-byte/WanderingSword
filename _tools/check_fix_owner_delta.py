#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release基準と現HEADのfix owner集合・訳値・監査範囲・構造を比較する。"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
FIX_PREFIX = "_phase4_proofread/fixes_"
FIX_SUFFIX = ".json"
FIELD_SEPARATOR = "\x1f"
DEFAULT_TARGET = "CG表"
DEFAULT_NAMESPACE = "QuestDlgs"
sys.path.insert(0, str(ROOT / "_tools"))
import locres  # noqa: E402
from validate_fixes_json import locres_path, validate_files  # noqa: E402


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def owner_map_from_objects(
    objects: list[tuple[str, dict[str, Any]]],
) -> tuple[dict[str, str], dict[str, list[str]], list[str]]:
    values: dict[str, str] = {}
    owners: dict[str, list[str]] = {}
    errors: list[str] = []
    for path, value in objects:
        for key, text in value.items():
            if not isinstance(key, str) or key.count(FIELD_SEPARATOR) != 2:
                errors.append(f"invalid full key in {path}: {key!r}")
                continue
            if not isinstance(text, str):
                errors.append(f"owner value must be string in {path}: {key!r}")
                continue
            owners.setdefault(key, []).append(path)
            values.setdefault(key, text)
            if values[key] != text:
                errors.append(f"conflicting owner values for {key!r}: {owners[key]!r}")
    return values, owners, errors


def current_owner_objects() -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(P4.glob("fixes_*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise SystemExit(f"ERROR: owner file top level must be object: {path.relative_to(ROOT)}")
        result.append((path.relative_to(ROOT).as_posix(), value))
    return result


def git_text(ref: str, path: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, check=False,
        capture_output=True, text=True, encoding="utf-8",
    )
    if completed.returncode != 0:
        raise SystemExit(f"ERROR: git show failed for {ref}:{path}: {completed.stderr.strip()}")
    return completed.stdout


def git_bytes(ref: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"ERROR: git show failed for {ref}:{path}: {message}")
    return completed.stdout


def base_owner_objects(ref: str) -> list[tuple[str, dict[str, Any]]]:
    completed = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "_phase4_proofread"],
        cwd=ROOT, check=False, capture_output=True, text=True, encoding="utf-8",
    )
    if completed.returncode != 0:
        raise SystemExit(f"ERROR: git ls-tree failed for {ref}: {completed.stderr.strip()}")
    paths = [
        line.strip() for line in completed.stdout.splitlines()
        if line.startswith(FIX_PREFIX) and line.endswith(FIX_SUFFIX)
    ]
    result: list[tuple[str, dict[str, Any]]] = []
    for path in paths:
        value = json.loads(git_text(ref, path))
        if not isinstance(value, dict):
            raise SystemExit(f"ERROR: base owner file top level must be object: {path}")
        result.append((path, value))
    return result


def base_translation_values(ref: str, keys: set[str]) -> tuple[dict[str, str], list[str]]:
    """前回releaseのlocresから、owner keyごとの実際の基準訳値を読む。"""
    errors: list[str] = []
    targets = sorted({key.split(FIELD_SEPARATOR, 1)[0] for key in keys})
    target_values: dict[str, dict[str, str]] = {}
    with tempfile.TemporaryDirectory(prefix="ws-owner-base-") as temp_dir:
        for index, target in enumerate(targets):
            try:
                current_path = Path(locres_path(target))
                relative = current_path.relative_to(ROOT).as_posix()
                data = git_bytes(ref, relative)
                temp_path = Path(temp_dir) / f"{index}.locres"
                temp_path.write_bytes(data)
                _, values, *_ = locres.parse(str(temp_path))
                target_values[target] = values
            except (FileNotFoundError, OSError, AssertionError, ValueError) as exc:
                errors.append(f"cannot load release-base locres for {target}: {exc}")

    result: dict[str, str] = {}
    for full_key in sorted(keys):
        parts = full_key.split(FIELD_SEPARATOR, 2)
        if len(parts) != 3:
            errors.append(f"invalid full key while reading base locres: {full_key!r}")
            continue
        target, namespace, key = parts
        value = target_values.get(target, {}).get(namespace + FIELD_SEPARATOR + key)
        if value is None:
            errors.append(f"release-base locres lacks key: {full_key!r}")
            continue
        result[full_key] = value
    return result, errors


def current_candidate_keys() -> tuple[set[str], list[str]]:
    state = load_object(STATE_PATH)
    keys: set[str] = set()
    errors: list[str] = []
    for packet in state.get("wave", {}).get("packets", []):
        if not isinstance(packet, dict):
            continue
        rel = packet.get("preparation_record", {}).get("candidate_packet")
        if not isinstance(rel, str) or not rel:
            errors.append("current wave packet lacks candidate_packet")
            continue
        candidate = load_object(ROOT / rel)
        source = candidate.get("source") if isinstance(candidate.get("source"), dict) else {}
        target = str(source.get("target") or DEFAULT_TARGET)
        namespace = str(source.get("namespace") or DEFAULT_NAMESPACE)
        rows = candidate.get("rows")
        if not isinstance(rows, list):
            errors.append(f"{rel}: candidate.rows must be a list")
            continue
        for index, row in enumerate(rows):
            short = row.get("key") if isinstance(row, dict) else None
            if not isinstance(short, str) or not short:
                errors.append(f"{rel}: rows[{index}].key must be non-empty")
                continue
            keys.add(FIELD_SEPARATOR.join((target, namespace, short)))
    return keys, errors


def validate_integrity(
    base_owner_values: dict[str, str],
    base_translation: dict[str, str],
    current_values: dict[str, str],
    current_owners: dict[str, list[str]],
    candidate_keys: set[str],
    *,
    expected_new: int,
    expected_total: int,
    expected_changed: int,
) -> list[str]:
    errors: list[str] = []
    duplicates = {key: paths for key, paths in current_owners.items() if len(paths) != 1}
    if duplicates:
        errors.append(f"duplicate fix owners ({len(duplicates)}): {duplicates!r}")
    removed = sorted(set(base_owner_values) - set(current_values))
    added = sorted(set(current_values) - set(base_owner_values))
    changed_translation = sorted(
        key for key, value in current_values.items()
        if key in base_translation and base_translation[key] != value
    )
    outside = sorted(set(changed_translation) - candidate_keys)
    if removed:
        errors.append(f"owner keys removed from release base ({len(removed)}): {removed!r}")
    if len(added) != expected_new:
        errors.append(f"new owner key count mismatch: observed={len(added)} expected={expected_new}; added={added!r}")
    if len(current_values) != expected_total:
        errors.append(f"current unique owner total mismatch: observed={len(current_values)} expected={expected_total}")
    if len(changed_translation) != expected_changed:
        errors.append(
            "translation fix count mismatch against release-base locres: "
            f"observed={len(changed_translation)} expected={expected_changed}; "
            f"changed={changed_translation!r}"
        )
    if outside:
        errors.append(f"translation values changed outside current audited candidate rows ({len(outside)}): {outside!r}")
    return errors


def main() -> int:
    current = load_object(CURRENT_PATH)
    manifest = load_object(MANIFEST_PATH)
    base_ref = current.get("translation_base_commit")
    if not isinstance(base_ref, str) or not base_ref:
        print("ERROR: CURRENT_WORK.translation_base_commit is missing")
        return 1

    base_owner_values, _, base_errors = owner_map_from_objects(base_owner_objects(base_ref))
    current_objects = current_owner_objects()
    current_values, current_owners, current_errors = owner_map_from_objects(current_objects)
    base_translation, translation_errors = base_translation_values(base_ref, set(current_values))
    candidate_keys, candidate_errors = current_candidate_keys()
    totals = manifest.get("totals", {})
    expected_new = totals.get("new_project_keys")
    expected_changed = totals.get("fix_keys")
    base_total = manifest.get("base_checkpoint", {}).get("project_applied_keys")
    errors = [*base_errors, *current_errors, *translation_errors, *candidate_errors]
    for label, value in (("new_project_keys", expected_new), ("fix_keys", expected_changed), ("base project_applied_keys", base_total)):
        if not isinstance(value, int) or value < 0:
            errors.append(f"manifest {label} must be a non-negative integer")
    if not isinstance(expected_new, int) or expected_new < 0:
        expected_new = 0
    if not isinstance(expected_changed, int) or expected_changed < 0:
        expected_changed = 0
    if not isinstance(base_total, int) or base_total < 0:
        base_total = len(base_owner_values)
    if len(base_owner_values) != base_total:
        errors.append(f"release base owner total mismatch: measured={len(base_owner_values)} checkpoint={base_total}")
    errors.extend(validate_integrity(
        base_owner_values, base_translation, current_values, current_owners, candidate_keys,
        expected_new=expected_new,
        expected_total=base_total + expected_new,
        expected_changed=expected_changed,
    ))

    paths = [str(ROOT / path) for path, _ in current_objects]
    checked, pending, applied, structure_errors = validate_files(paths, allow_applied=True)
    errors.extend(structure_errors)

    print("=== Private fix integrity ===")
    print(f"base ref: {base_ref}")
    print(f"base unique owners: {len(base_owner_values)}")
    print(f"current unique owners: {len(current_values)}")
    print(f"release-base translation keys: {len(base_translation)}")
    print(f"audited candidate keys: {len(candidate_keys)}")
    print(f"fix structure: checked={checked} pending={pending} applied={applied}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: owner history, audited translation scope, and control-token structure are intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
