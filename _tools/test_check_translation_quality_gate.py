#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳品質ゲートの低収穫・重複行・全keep再監査を回帰検証する。"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module():
    path = ROOT / "_tools" / "check_translation_quality_gate.py"
    spec = importlib.util.spec_from_file_location("check_translation_quality_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load quality gate checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_manifest(record: str) -> dict:
    return {
        "train_id": "test-train",
        "status": "ready_for_public_ci",
        "totals": {
            "bundle_count": 2,
            "reviewed_rows": 18,
            "reviewed_keys": 24,
            "unique_reviewed_rows": 18,
            "fix_keys": 3,
            "unique_fix_rows": 2,
            "new_pair_keys": 0,
            "keep_only_bundles": 1,
        },
        "bundles": [
            {
                "batch": 1,
                "reviewed_rows": 10,
                "reviewed_keys": 10,
                "unique_rows": 10,
                "fix_keys": 3,
                "unique_fix_rows": 2,
                "keep_keys": 7,
            },
            {
                "batch": 2,
                "reviewed_rows": 8,
                "reviewed_keys": 14,
                "unique_rows": 8,
                "fix_keys": 0,
                "unique_fix_rows": 0,
                "keep_keys": 14,
            },
        ],
        "quality_gate": {
            "schema_version": 1,
            "primary_objective": "repair_substantive_translation_defects",
            "throughput_metrics_role": "transport_only",
            "low_yield_threshold_percent": 15,
            "reviewed_keys": 24,
            "unique_reviewed_rows": 18,
            "fix_keys": 3,
            "unique_fix_rows": 2,
            "keep_only_bundles": 1,
            "pre_challenge_unique_fix_rows": 1,
            "low_yield_detected": True,
            "release_decision": "quality_passed",
            "challenge_pass": {
                "status": "complete",
                "scope": "all_initial_keep_unique_rows",
                "reviewed_candidate_keep_rows": 17,
                "findings_unique_rows": 1,
                "finding_keys": 2,
                "record": record,
            },
        },
    }


def main() -> None:
    checker = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        old_root = checker.ROOT
        checker.ROOT = Path(tmp)
        record = "_phase4_proofread/QUALITY_CHALLENGE_TEST.md"
        path = checker.ROOT / record
        path.parent.mkdir(parents=True)
        path.write_text("test", encoding="utf-8")

        manifest = sample_manifest(record)
        errors = checker.validate(manifest)
        assert errors == [], errors

        inflated = sample_manifest(record)
        inflated["totals"]["reviewed_rows"] = 24
        errors = checker.validate(inflated)
        assert any("reviewed_rows must equal" in error for error in errors), errors

        missing_challenge = sample_manifest(record)
        missing_challenge["quality_gate"]["challenge_pass"] = None
        errors = checker.validate(missing_challenge)
        assert any("requires challenge_pass" in error for error in errors), errors

        wrong_scope = sample_manifest(record)
        wrong_scope["quality_gate"]["challenge_pass"]["scope"] = "sampled_keep_rows"
        errors = checker.validate(wrong_scope)
        assert any("all initial keep" in error for error in errors), errors

        wrong_objective = sample_manifest(record)
        wrong_objective["quality_gate"]["primary_objective"] = "increase_reviewed_rows"
        errors = checker.validate(wrong_objective)
        assert any("primary_objective" in error for error in errors), errors

        checker.ROOT = old_root

    print("test_check_translation_quality_gate: OK")


if __name__ == "__main__":
    main()
