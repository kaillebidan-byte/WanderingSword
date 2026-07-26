#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release基準commitと現HEADのfix ownerキー集合を比較する。"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
FIX_PREFIX = "_phase4_proofread/fixes_"
FIX_SUFFIX = ".json"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def owner_keys_from_objects(objects: list[tuple[str, dict[str, Any]]]) -> tuple[set[str], list[str]]:
    keys: set[str] = set()
    errors: list[str] = []
    for path, value in objects:
        for key in value:
            if not isinstance(key, str) or key.count("\x1f") != 2:
                errors.append(f"invalid full key in {path}: {key!r}")
                continue
            keys.add(key)
    return keys, errors


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
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise SystemExit(f"ERROR: git show failed for {ref}:{path}: {completed.stderr.strip()}")
    return completed.stdout


def base_owner_objects(ref: str) -> list[tuple[str, dict[str, Any]]]:
    completed = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "_phase4_proofread"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise SystemExit(f"ERROR: git ls-tree failed for {ref}: {completed.stderr.strip()}")
    paths = [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.startswith(FIX_PREFIX) and line.endswith(FIX_SUFFIX)
    ]
    result: list[tuple[str, dict[str, Any]]] = []
    for path in paths:
        value = json.loads(git_text(ref, path))
        if not isinstance(value, dict):
            raise SystemExit(f"ERROR: base owner file top level must be object: {path}")
        result.append((path, value))
    return result


def validate(base_keys: set[str], current_keys: set[str], expected_new: int, expected_total: int) -> list[str]:
    errors: list[str] = []
    removed = sorted(base_keys - current_keys)
    added = sorted(current_keys - base_keys)
    if removed:
        errors.append(f"owner keys removed from release base ({len(removed)}): {removed!r}")
    if len(added) != expected_new:
        errors.append(f"new owner key count mismatch: observed={len(added)} expected={expected_new}; added={added!r}")
    if len(current_keys) != expected_total:
        errors.append(f"current unique owner total mismatch: observed={len(current_keys)} expected={expected_total}")
    return errors


def main() -> int:
    current = load_object(CURRENT_PATH)
    manifest = load_object(MANIFEST_PATH)
    base_ref = current.get("translation_base_commit")
    if not isinstance(base_ref, str) or not base_ref:
        print("ERROR: CURRENT_WORK.translation_base_commit is missing")
        return 1
    base_keys, base_errors = owner_keys_from_objects(base_owner_objects(base_ref))
    current_keys, current_errors = owner_keys_from_objects(current_owner_objects())
    totals = manifest.get("totals", {})
    expected_new = totals.get("new_project_keys")
    base_checkpoint = manifest.get("base_checkpoint", {})
    base_total = base_checkpoint.get("project_applied_keys")
    errors = [*base_errors, *current_errors]
    if not isinstance(expected_new, int) or expected_new < 0:
        errors.append("manifest.totals.new_project_keys must be a non-negative integer")
        expected_new = 0
    if not isinstance(base_total, int) or base_total < 0:
        errors.append("manifest.base_checkpoint.project_applied_keys must be a non-negative integer")
        base_total = len(base_keys)
    if len(base_keys) != base_total:
        errors.append(f"release base owner total mismatch: measured={len(base_keys)} checkpoint={base_total}")
    errors.extend(validate(base_keys, current_keys, expected_new, base_total + expected_new))
    print("=== Fix owner delta ===")
    print(f"base ref: {base_ref}")
    print(f"base unique owners: {len(base_keys)}")
    print(f"current unique owners: {len(current_keys)}")
    print(f"declared new project owners: {expected_new}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: fix owner keys are monotonic from the verified release base")
    return 0


if __name__ == "__main__":
    sys.exit(main())
