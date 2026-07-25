#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visibility preflight契約の必須ゲートを検証する。"""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_visibility_preflight_contract.py"
CONTRACT_PATH = ROOT / "_phase4_proofread" / "VISIBILITY_PREFLIGHT_CONTRACT.json"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "check_visibility_preflight_contract", MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_visibility_preflight_contract.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_module()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert module.validate_contract(contract) == []

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for relative in module.EXPECTED_DOCS.values():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test\n", encoding="utf-8")

        bad = json.loads(json.dumps(contract))
        bad["ordering"]["user_visible_update_before_verdict"] = "allowed"
        errors = module.validate_contract(bad, root=root)
        assert any("user_visible_update_before_verdict" in error for error in errors)

        bad = json.loads(json.dumps(contract))
        bad["user_visibility_report"]["authority"] = "authoritative"
        errors = module.validate_contract(bad, root=root)
        assert any("hint_only" in error for error in errors)

        bad = json.loads(json.dumps(contract))
        bad["verdict"]["metadata_failure_allows_work_start_claim"] = True
        errors = module.validate_contract(bad, root=root)
        assert any("must not allow" in error for error in errors)

    print("test_check_visibility_preflight_contract: OK")


if __name__ == "__main__":
    main()
