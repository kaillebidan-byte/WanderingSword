#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""private翻訳四段階の権限・遷移・指標遮断を回帰検証する。"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


def load_module(root: Path):
    path = root / "_tools" / "check_private_translation_stage.py"
    spec = importlib.util.spec_from_file_location("check_private_translation_stage", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load private stage checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract() -> dict:
    required = {
        "private_preparation": [
            "source_artifact", "scene_context", "ownership_inventory", "candidate_packet"
        ],
        "private_quality_audit": [
            "audit_record", "fix_candidates", "challenged_keeps"
        ],
        "private_encoding": [
            "audit_record", "fix_files", "review_records", "ownership_records"
        ],
        "ready_for_public_ci": [
            "quality_gate", "manifest", "next_task_packet"
        ],
    }
    permissions = {
        "private_preparation": ("private_translation_work", False, False, False, False, True),
        "private_quality_audit": ("private_translation_work", True, False, False, False, True),
        "private_encoding": ("private_translation_work", False, True, True, True, False),
        "ready_for_public_ci": ("ready_for_public_ci", False, False, False, True, False),
    }
    allowed = {
        "private_preparation": ["private_quality_audit"],
        "private_quality_audit": ["private_encoding"],
        "private_encoding": ["private_quality_audit", "ready_for_public_ci"],
        "ready_for_public_ci": ["private_quality_audit"],
    }
    stages = []
    for stage in (
        "private_preparation",
        "private_quality_audit",
        "private_encoding",
        "ready_for_public_ci",
    ):
        op, judgment, fix, encoding, visible, frozen = permissions[stage]
        stages.append({
            "id": stage,
            "operation_state": op,
            "translation_judgment_allowed": judgment,
            "fix_writes_allowed": fix,
            "encoding_writes_allowed": encoding,
            "throughput_metrics_visible": visible,
            "metrics_frozen": frozen,
            "required_evidence": required[stage],
            "allowed_next": allowed[stage],
        })
    return {
        "schema_version": 1,
        "transition_order": [
            "private_preparation",
            "private_quality_audit",
            "private_encoding",
            "ready_for_public_ci",
        ],
        "stages": stages,
    }


def evidence(stage: str) -> dict:
    common = "_phase4_proofread/EVIDENCE.md"
    return {
        "private_preparation": {
            "source_artifact": "github-actions:1",
            "scene_context": common,
            "ownership_inventory": common,
            "candidate_packet": common,
        },
        "private_quality_audit": {
            "audit_record": common,
            "fix_candidates": common,
            "challenged_keeps": common,
        },
        "private_encoding": {
            "audit_record": common,
            "fix_files": common,
            "review_records": common,
            "ownership_records": common,
        },
        "ready_for_public_ci": {
            "quality_gate": common,
            "manifest": common,
            "next_task_packet": common,
        },
    }[stage]


def sample(stage: str) -> tuple[dict, dict, dict]:
    order = [
        "private_preparation",
        "private_quality_audit",
        "private_encoding",
        "ready_for_public_ci",
    ]
    permissions = {
        "private_preparation": {
            "translation_judgment_allowed": False,
            "fix_writes_allowed": False,
            "encoding_writes_allowed": False,
            "throughput_metrics_visible": False,
            "metrics_frozen": True,
        },
        "private_quality_audit": {
            "translation_judgment_allowed": True,
            "fix_writes_allowed": False,
            "encoding_writes_allowed": False,
            "throughput_metrics_visible": False,
            "metrics_frozen": True,
        },
        "private_encoding": {
            "translation_judgment_allowed": False,
            "fix_writes_allowed": True,
            "encoding_writes_allowed": True,
            "throughput_metrics_visible": True,
            "metrics_frozen": False,
        },
        "ready_for_public_ci": {
            "translation_judgment_allowed": False,
            "fix_writes_allowed": False,
            "encoding_writes_allowed": False,
            "throughput_metrics_visible": True,
            "metrics_frozen": False,
        },
    }
    history = []
    for item in order[: order.index(stage) + 1]:
        history.append({
            "stage": item,
            "status": "active" if item == stage else "complete",
            "evidence": evidence(item),
        })
    totals = {
        "bundle_count": 3,
        "reviewed_rows": 47,
        "reviewed_keys": 53,
        "unique_reviewed_rows": 47,
        "fix_keys": 7,
        "unique_fix_rows": 6,
    }
    state = {
        "schema_version": 1,
        "contract": "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json",
        "train_id": "test-train",
        "stage": stage,
        "permissions": permissions[stage],
        "history": history,
        "audit_separation": {
            "pair_keys_follow_judgment": True,
            "bundle_number_assigned_in_encoding": True,
            "audit_metrics_suppressed": True,
            "public_reopens_judgment": False,
        },
    }
    if permissions[stage]["throughput_metrics_visible"]:
        state["metrics_snapshot"] = totals.copy()
    manifest_status = "ready_for_public_ci" if stage == "ready_for_public_ci" else "accumulating"
    manifest = {
        "train_id": "test-train",
        "status": manifest_status,
        "totals": totals,
    }
    current = {
        "operation_mode": {
            "declared_state": (
                "ready_for_public_ci"
                if stage == "ready_for_public_ci"
                else "private_translation_work"
            )
        },
        "ci_train": {"status": manifest_status},
    }
    return state, current, manifest


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    checker = load_module(here)
    with tempfile.TemporaryDirectory() as tmp:
        old_root = checker.ROOT
        checker.ROOT = Path(tmp)
        evidence_file = checker.ROOT / "_phase4_proofread" / "EVIDENCE.md"
        evidence_file.parent.mkdir(parents=True)
        evidence_file.write_text("test", encoding="utf-8")

        for stage in checker.STAGE_ORDER:
            state, current, manifest = sample(stage)
            errors = checker.validate(contract(), state, current, manifest)
            assert errors == [], (stage, errors)

        state, current, manifest = sample("ready_for_public_ci")
        state["history"] = [state["history"][0], state["history"][-1]]
        state["history"][0]["status"] = "complete"
        errors = checker.validate(contract(), state, current, manifest)
        assert any("illegal transition" in error for error in errors), errors

        state, current, manifest = sample("private_quality_audit")
        state["metrics_snapshot"] = manifest["totals"].copy()
        errors = checker.validate(contract(), state, current, manifest)
        assert any("must not expose metrics_snapshot" in error for error in errors), errors

        state, current, manifest = sample("private_encoding")
        state["permissions"]["translation_judgment_allowed"] = True
        errors = checker.validate(contract(), state, current, manifest)
        assert any("translation_judgment_allowed" in error for error in errors), errors

        state, current, manifest = sample("ready_for_public_ci")
        current["operation_mode"]["declared_state"] = "private_translation_work"
        errors = checker.validate(contract(), state, current, manifest)
        assert any("operation_mode.declared_state" in error for error in errors), errors

        checker.ROOT = old_root

    print("test_check_private_translation_stage: OK")


if __name__ == "__main__":
    main()
