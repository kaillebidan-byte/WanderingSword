#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release state JSONを厳格UTF-8で読み、転送破損と参照漏れを早期検出する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CORE_PATHS = (
    P4 / "CURRENT_WORK.json",
    P4 / "PRIVATE_STAGE_STATE.json",
    P4 / "CI_TRAIN_MANIFEST.json",
    P4 / "NEXT_TASK_PACKET.json",
    P4 / "audit_status.json",
    P4 / "VISIBILITY_PREFLIGHT_CONTRACT.json",
    P4 / "PROJECT_SCOPE_LOCK.json",
    P4 / "PRIVATE_TRANSLATION_STAGES.json",
    P4 / "EXECUTION_MODES.json",
    P4 / "PHASE_COMPLETION_SIGNAL.json",
    P4 / "REGULATED_PHASE_STATE.json",
)
OWNER_SUMMARY_KEYS = (
    "bundle_count",
    "reviewed_rows",
    "reviewed_keys",
    "unique_reviewed_rows",
    "fix_keys",
    "unique_fix_rows",
    "new_pair_keys",
    "new_project_keys",
    "cross_register_keys",
    "existing_owner_updates",
    "keep_only_bundles",
)


def read_object(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, [f"cannot read {path.relative_to(ROOT)}: {exc}"]
    rel = path.relative_to(ROOT).as_posix()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{rel}: UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return None, [f"{rel}: invalid UTF-8 at byte {exc.start}: {exc.reason}"]
    if "\x00" in text:
        errors.append(f"{rel}: NUL byte is forbidden")
    if "\ufffd" in text:
        errors.append(f"{rel}: replacement character U+FFFD is forbidden")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [*errors, f"{rel}: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}"]
    if not isinstance(value, dict):
        errors.append(f"{rel}: top level must be object")
        return None, errors
    return value, errors


def referenced_paths(current: dict[str, Any] | None, state: dict[str, Any] | None) -> list[Path]:
    paths: list[Path] = []
    if isinstance(current, dict):
        checkpoint = current.get("checkpoint")
        identity = checkpoint.get("release_identity") if isinstance(checkpoint, dict) else None
        evidence = identity.get("evidence") if isinstance(identity, dict) else None
        if isinstance(evidence, str) and evidence:
            paths.append(ROOT / evidence)
    if isinstance(state, dict):
        for packet in state.get("wave", {}).get("packets", []):
            if not isinstance(packet, dict):
                continue
            record = packet.get("preparation_record")
            candidate = record.get("candidate_packet") if isinstance(record, dict) else None
            if isinstance(candidate, str) and candidate:
                paths.append(ROOT / candidate)
    paths.extend(sorted(P4.glob("fixes_*.json")))
    return paths


def owner_summary_errors(
    current: dict[str, Any] | None,
    state: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
) -> list[str]:
    if not isinstance(current, dict) or not isinstance(state, dict) or not isinstance(manifest, dict):
        return []
    summary = state.get("wave", {}).get("encoding_summary")
    if summary is None:
        return []
    if not isinstance(summary, dict):
        return ["PRIVATE_STAGE_STATE.wave.encoding_summary must be an object"]
    manifest_totals = manifest.get("totals")
    current_totals = current.get("ci_train", {}).get("totals")
    errors: list[str] = []
    if not isinstance(manifest_totals, dict):
        errors.append("CI_TRAIN_MANIFEST.totals must be an object")
    if not isinstance(current_totals, dict):
        errors.append("CURRENT_WORK.ci_train.totals must be an object")
    if errors:
        return errors
    for key in OWNER_SUMMARY_KEYS:
        expected = manifest_totals.get(key)
        if current_totals.get(key) != expected:
            errors.append(f"owner summary mismatch for {key}: manifest={expected!r} CURRENT_WORK={current_totals.get(key)!r}")
        if summary.get(key) != expected:
            errors.append(f"owner summary mismatch for {key}: manifest={expected!r} PRIVATE_STAGE_STATE={summary.get(key)!r}")
    return errors


def validate(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    seen: set[Path] = set()
    cache: dict[Path, dict[str, Any] | None] = {}
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not path.is_file():
            errors.append(f"missing JSON file: {path.relative_to(ROOT)}")
            cache[path] = None
            continue
        value, current_errors = read_object(path)
        cache[path] = value
        errors.extend(current_errors)

    current = cache.get(P4 / "CURRENT_WORK.json")
    state = cache.get(P4 / "PRIVATE_STAGE_STATE.json")
    manifest = cache.get(P4 / "CI_TRAIN_MANIFEST.json")
    errors.extend(owner_summary_errors(current, state, manifest))
    for path in referenced_paths(current, state):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not path.is_file():
            errors.append(f"missing referenced JSON file: {path.relative_to(ROOT)}")
            continue
        _, current_errors = read_object(path)
        errors.extend(current_errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [
        path if path.is_absolute() else ROOT / path
        for path in args.paths
    ] or list(CORE_PATHS)
    errors = validate(paths)
    print("=== Release state JSON integrity ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: strict UTF-8 JSON, references, and owner summaries are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
