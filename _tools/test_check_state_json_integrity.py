#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_state_json_integrity.py")
SPEC = importlib.util.spec_from_file_location("state_json_integrity", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def errors_for(data: bytes) -> list[str]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        path = root / "state.json"
        path.write_bytes(data)
        original = module.ROOT
        module.ROOT = root
        try:
            _, errors = module.read_object(path)
            return errors
        finally:
            module.ROOT = original


def owner_totals() -> dict[str, int]:
    return {
        "bundle_count": 1,
        "reviewed_rows": 62,
        "reviewed_keys": 62,
        "unique_reviewed_rows": 62,
        "fix_keys": 14,
        "unique_fix_rows": 14,
        "new_pair_keys": 7,
        "new_project_keys": 7,
        "cross_register_keys": 0,
        "existing_owner_updates": 7,
        "keep_only_bundles": 0,
    }


def main() -> None:
    valid = json.dumps({"ok": "日本語"}, ensure_ascii=False).encode("utf-8")
    assert errors_for(valid) == []
    assert any("BOM" in error for error in errors_for(b"\xef\xbb\xbf" + valid))
    assert any("invalid UTF-8" in error for error in errors_for(b'{"x":"\xff"}'))
    assert any("U+FFFD" in error for error in errors_for('{"x":"�"}'.encode("utf-8")))
    assert any("top level" in error for error in errors_for(b"[]"))

    totals = owner_totals()
    current = {"ci_train": {"totals": dict(totals)}}
    state = {"wave": {"encoding_summary": dict(totals)}}
    manifest = {"totals": dict(totals)}
    assert module.owner_summary_errors(current, state, manifest) == []

    state["wave"]["encoding_summary"]["new_pair_keys"] = 0
    mismatch = module.owner_summary_errors(current, state, manifest)
    assert any("new_pair_keys" in error and "PRIVATE_STAGE_STATE" in error for error in mismatch)

    current["ci_train"]["totals"]["existing_owner_updates"] = 6
    mismatch = module.owner_summary_errors(current, state, manifest)
    assert any("existing_owner_updates" in error and "CURRENT_WORK" in error for error in mismatch)

    print("OK: state JSON integrity rejects transfer corruption and owner-summary divergence")


if __name__ == "__main__":
    main()
