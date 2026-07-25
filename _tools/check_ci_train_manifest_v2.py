#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI train manifestのkeep-only束を含むphase2互換検査。"""
from __future__ import annotations

import argparse
import sys
from typing import Any

import check_ci_train_manifest as legacy

CURRENT_PATH = legacy.CURRENT_PATH
MANIFEST_PATH = legacy.MANIFEST_PATH
load_object = legacy.load_object
release_state = legacy.release_state


def validate_manifest(
    manifest: dict[str, Any],
    current: dict[str, Any],
    *,
    require_ready: bool = False,
) -> list[str]:
    errors = legacy.validate_manifest(
        manifest,
        current,
        require_ready=require_ready,
    )

    bundles = manifest.get("bundles")
    if not isinstance(bundles, list):
        return errors

    removable: set[str] = set()
    for index, bundle in enumerate(bundles):
        if not isinstance(bundle, dict):
            continue
        fix_keys = bundle.get("fix_keys")
        fix_files = bundle.get("fix_files")
        legacy_error = f"bundles[{index}].fix_files must be a non-empty list"

        if fix_keys == 0 and fix_files == []:
            removable.add(legacy_error)
        elif fix_keys == 0 and isinstance(fix_files, list) and fix_files:
            errors.append(
                f"bundles[{index}] keep-only bundle must not declare fix_files"
            )

    return [error for error in errors if error not in removable]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="公開CIへ出す列車としてrelease可能な状態を要求する",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_object(CURRENT_PATH)
    manifest = load_object(MANIFEST_PATH)
    errors = validate_manifest(manifest, current, require_ready=args.require_ready)
    ready, reasons = release_state(manifest)

    totals = manifest.get("totals", {})
    print("=== CI train phase2-compatible manifest ===")
    print(f"train: {manifest.get('train_id')}")
    print(f"branch: {manifest.get('branch')}")
    print(f"status: {manifest.get('status')}")
    print(
        "totals: "
        f"{totals.get('bundle_count')} bundle(s), "
        f"{totals.get('reviewed_rows')} row(s), "
        f"{totals.get('fix_keys')} fix key(s)"
    )
    print(f"release ready: {ready}")
    if reasons:
        print("release reasons: " + ", ".join(reasons))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: CI train manifest is structurally valid, including keep-only bundles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
