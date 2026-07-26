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


def main() -> None:
    valid = json.dumps({"ok": "日本語"}, ensure_ascii=False).encode("utf-8")
    assert errors_for(valid) == []
    assert any("BOM" in error for error in errors_for(b"\xef\xbb\xbf" + valid))
    assert any("invalid UTF-8" in error for error in errors_for(b'{"x":"\xff"}'))
    assert any("U+FFFD" in error for error in errors_for('{"x":"�"}'.encode("utf-8")))
    assert any("top level" in error for error in errors_for(b"[]"))
    print("OK: state JSON integrity rejects transfer corruption and non-object roots")


if __name__ == "__main__":
    main()
