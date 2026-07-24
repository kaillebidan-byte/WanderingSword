#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase2 checkpointがsquash SHAではなくrelease証跡で成立することを検証する。"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_handoff_consistency_v2.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_handoff_consistency_v2", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_handoff_consistency_v2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def current() -> dict:
    return {
        "schema_version": 7,
        "last_completed_batch": 61,
        "pair_applied_keys": 1166,
        "project_applied_keys": 1518,
        "checkpoint": {
            "status": "verified",
            "batch": 61,
            "pair_applied_keys": 1166,
            "project_applied_keys": 1518,
            "applied_record": "_phase4_proofread/APPLIED_FIXES_DEMO.md",
            "produced_by_pr": 106,
            "release_identity": {
                "kind": "pr_release_v1",
                "release_id": "demo-r1",
                "evidence": "_phase4_proofread/RELEASE_EVIDENCE_DEMO.json",
                "pr": 106,
                "validated_head": "b" * 40,
            },
        },
    }


def evidence() -> dict:
    return {
        "schema_version": 1,
        "status": "verified",
        "release_id": "demo-r1",
        "train_id": "demo-train",
        "pr": 106,
        "ci_head": "a" * 40,
        "asset_head": "b" * 40,
        "applied_record": "_phase4_proofread/APPLIED_FIXES_DEMO.md",
        "counts": {"batch": 61, "pair_applied_keys": 1166, "project_applied_keys": 1518, "pending_fixes": 0},
        "runs": {
            "relation": {"id": 1, "workflow": "Relation audit extraction", "head_sha": "a" * 40, "conclusion": "success"},
            "cross": {"id": 2, "workflow": "Cross register QA", "head_sha": "a" * 40, "conclusion": "success"},
            "apply": {"id": 3, "workflow": "Apply curated localization fixes", "head_sha": "a" * 40, "conclusion": "success"},
        },
        "lineage": {"mode": "branch_ancestor", "merge_sha": None},
    }


def main() -> None:
    module = load_module()
    record = ROOT / "_phase4_proofread" / "APPLIED_FIXES_DEMO.md"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("demo\n", encoding="utf-8")
    try:
        assert module.validate_checkpoint_and_evidence(current(), evidence(), require_verified=True) == []

        legacy = current()
        legacy["checkpoint"]["translation_head"] = "c" * 40
        errors = module.validate_checkpoint_and_evidence(legacy, evidence(), require_verified=True)
        assert any("must not depend" in error for error in errors)

        pending = current()
        pending["checkpoint"]["status"] = "pending_audit_sync"
        errors = module.validate_checkpoint_and_evidence(pending, evidence(), require_verified=True)
        assert any("verified checkpoint required" in error for error in errors)

        mismatch = copy.deepcopy(evidence())
        mismatch["pr"] = 107
        errors = module.validate_checkpoint_and_evidence(current(), mismatch, require_verified=False)
        assert any("release PR" in error for error in errors)
    finally:
        record.unlink(missing_ok=True)

    print("test_check_handoff_consistency_v2: OK")


if __name__ == "__main__":
    main()
