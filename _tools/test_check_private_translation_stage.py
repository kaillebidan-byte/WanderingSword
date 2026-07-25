#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""private翻訳wave v2の段階・輸送分離を回帰検証する。"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_checker():
    path = ROOT / "_tools" / "check_private_translation_stage.py"
    spec = importlib.util.spec_from_file_location("check_private_translation_stage", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract() -> dict:
    permissions = {
        "private_preparation": ("private_translation_work", False, False, False, False, True),
        "private_quality_audit": ("private_translation_work", True, False, False, False, True),
        "private_encoding": ("private_translation_work", False, True, True, True, False),
        "translation_frozen": ("translation_frozen", False, False, False, True, False),
    }
    allowed = {
        "private_preparation": ["private_quality_audit"],
        "private_quality_audit": ["private_encoding"],
        "private_encoding": ["private_quality_audit", "translation_frozen"],
        "translation_frozen": ["private_quality_audit"],
    }
    stages = []
    for stage in (
        "private_preparation",
        "private_quality_audit",
        "private_encoding",
        "translation_frozen",
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
            "allowed_next": allowed[stage],
        })
    return {
        "schema_version": 2,
        "transition_order": [
            "private_preparation",
            "private_quality_audit",
            "private_encoding",
            "translation_frozen",
        ],
        "transport": {
            "statuses": [
                "not_ready",
                "ready_for_public_ci",
                "in_public_ci",
                "verified",
                "awaiting_private_merge",
                "merged",
            ]
        },
        "wave_policy": {
            "normal_seal": {"packet_count": 4, "unique_reviewed_rows": 40},
            "caps": {"packet_count": 6, "unique_reviewed_rows": 60},
            "seal_reasons": [
                "packet_threshold",
                "unique_reviewed_rows_threshold",
                "scope_exhausted",
            ],
            "replenishment_reasons": [
                "packet_invalidated",
                "duplicate_normalization_reduced_scope",
                "needs_context_unresolved",
                "prepared_source_became_stale",
                "scope_boundary_corrected",
            ],
        },
        "stages": stages,
    }


def permissions(stage: str) -> dict:
    return {
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
        "translation_frozen": {
            "translation_judgment_allowed": False,
            "fix_writes_allowed": False,
            "encoding_writes_allowed": False,
            "throughput_metrics_visible": True,
            "metrics_frozen": False,
        },
    }[stage]


def packet(index: int, status: str) -> dict:
    value = {
        "packet_id": f"packet-{index}",
        "scene_groups": [f"scene-{index}"],
        "status": status,
        "preparation_record": {
            "candidate_packet": f"_phase4_proofread/CANDIDATE_{index}.json",
            "context_record": f"_phase4_proofread/PREPARATION_{index}.md",
        },
        "audit_record": None,
        "review_record": None,
        "formal_batch": None,
    }
    if status in {"audited", "encoded", "needs_reaudit"}:
        value["audit_record"] = {
            "record": f"_phase4_proofread/AUDIT_{index}.md",
            "fix_candidates": [],
            "challenged_keeps": [],
            "needs_context": [],
            "fact_doubts": [],
            "allusion_reviews": [],
        }
    if status == "encoded":
        value["review_record"] = {"record": f"_phase4_proofread/REVIEW_{index}.md"}
        value["formal_batch"] = 80 + index
    return value


def stage_history(stage: str) -> list[dict]:
    order = [
        "private_preparation",
        "private_quality_audit",
        "private_encoding",
        "translation_frozen",
    ]
    return [
        {"stage": item, "status": "active" if item == stage else "complete"}
        for item in order[: order.index(stage) + 1]
    ]


def transport_history(status: str) -> list[dict]:
    order = [
        "not_ready",
        "ready_for_public_ci",
        "in_public_ci",
        "verified",
        "awaiting_private_merge",
        "merged",
    ]
    result = []
    for item in order[: order.index(status) + 1]:
        entry = {"status": item}
        if item != "not_ready":
            entry["translation_stage"] = "translation_frozen"
        result.append(entry)
    return result


def sample(stage: str, *, count: int = 4, transport_status: str | None = None):
    status_by_stage = {
        "private_preparation": "prepared",
        "private_quality_audit": "audited",
        "private_encoding": "audited",
        "translation_frozen": "encoded",
    }
    packet_status = status_by_stage[stage]
    wave = {
        "wave_id": "test-wave",
        "queue_status": "sealed",
        "seal_reason": "packet_threshold",
        "packets": [packet(index + 1, packet_status) for index in range(count)],
    }
    if stage == "private_preparation":
        wave["preparation_summary"] = {
            "packet_count": count,
            "unique_reviewed_rows": count * 10,
        }
    status = transport_status or ("not_ready" if stage != "translation_frozen" else "ready_for_public_ci")
    state = {
        "schema_version": 2,
        "contract": "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json",
        "train_id": "test-train",
        "stage": stage,
        "wave": wave,
        "transport": {"status": status, "history": transport_history(status)},
        "permissions": permissions(stage),
        "history": stage_history(stage),
        "replenishment_reason": None,
    }
    operation = "translation_frozen" if stage == "translation_frozen" else "private_translation_work"
    manifest = {
        "train_id": "test-train",
        "status": "verified" if stage == "translation_frozen" else "accumulating",
        "bundles": [],
    }
    if stage == "translation_frozen":
        manifest["bundles"] = [
            {
                "batch": item["formal_batch"],
                "review_status": "complete",
                "apply_status": "verified",
            }
            for item in wave["packets"]
        ]
    current = {
        "operation_mode": {"declared_state": operation},
        "ci_train": {
            "status": manifest["status"],
            "transport_status": status,
        },
    }
    return state, current, manifest


def errors(checker, state, current, manifest):
    return checker.validate(contract(), state, current, manifest)


def main() -> None:
    checker = load_checker()

    # 1. 一packet・閾値未満で通常sealしたら失敗
    state, current, manifest = sample("private_preparation", count=1)
    assert any("preparation_underfilled" in error for error in errors(checker, state, current, manifest))

    # 2. 複数packetを準備してsealしたら成功
    state, current, manifest = sample("private_preparation")
    assert errors(checker, state, current, manifest) == []

    # 3. queue未sealedでquality auditへ進んだら失敗
    state, current, manifest = sample("private_quality_audit")
    state["wave"]["queue_status"] = "open"
    state["wave"]["seal_reason"] = None
    assert any("quality audit requires sealed queue" in error for error in errors(checker, state, current, manifest))

    # 4. 未監査packetを残してencodingへ進んだら失敗
    state, current, manifest = sample("private_encoding")
    state["wave"]["packets"][0] = packet(1, "prepared")
    assert any("unaudited packet blocks encoding" in error for error in errors(checker, state, current, manifest))

    # 5. 監査済みpacketの一部を未encodingで凍結したら失敗
    state, current, manifest = sample("translation_frozen")
    state["wave"]["packets"][0] = packet(1, "audited")
    assert any("must be encoded before translation freeze" in error for error in errors(checker, state, current, manifest))

    # 6. preparation・quality audit中に正式束番号が付いたら失敗
    for stage in ("private_preparation", "private_quality_audit"):
        state, current, manifest = sample(stage)
        state["wave"]["packets"][0]["formal_batch"] = 81
        assert any("formal_batch forbidden" in error for error in errors(checker, state, current, manifest))

    # 7. quality audit中にmetrics snapshotやrelease残量を露出したら失敗
    state, current, manifest = sample("private_quality_audit")
    state["wave"]["metrics_snapshot"] = {"bundle_count": 4}
    state["wave"]["release_remaining"] = 0
    assert any("exposes transport metrics" in error for error in errors(checker, state, current, manifest))

    # 8. encoding中にtranslation judgmentを許可したら失敗
    state, current, manifest = sample("private_encoding")
    state["permissions"]["translation_judgment_allowed"] = True
    assert any("translation_judgment_allowed" in error for error in errors(checker, state, current, manifest))

    # 9. encoding -> preparationにreplenishment理由がなければ失敗
    state, current, manifest = sample("private_preparation")
    state["history"] = [
        {"stage": "private_preparation", "status": "complete"},
        {"stage": "private_quality_audit", "status": "complete"},
        {"stage": "private_encoding", "status": "complete"},
        {"stage": "private_preparation", "status": "active"},
    ]
    assert any("requires replenishment reason" in error for error in errors(checker, state, current, manifest))

    # 10. 理由付き例外replenishmentは成功
    state["history"][-1]["replenishment_reason"] = "packet_invalidated"
    state["replenishment_reason"] = "packet_invalidated"
    assert errors(checker, state, current, manifest) == []

    # 11. 翻訳凍結段階とCI輸送statusが独立して遷移できる
    for status in (
        "not_ready",
        "ready_for_public_ci",
        "in_public_ci",
        "verified",
        "awaiting_private_merge",
        "merged",
    ):
        state, current, manifest = sample("translation_frozen", transport_status=status)
        assert errors(checker, state, current, manifest) == [], status

    # 12. ready -> public -> verified -> awaiting merge -> mergedを凍結のまま通せる
    state, current, manifest = sample("translation_frozen", transport_status="merged")
    assert [entry["status"] for entry in state["transport"]["history"]] == [
        "not_ready",
        "ready_for_public_ci",
        "in_public_ci",
        "verified",
        "awaiting_private_merge",
        "merged",
    ]
    assert all(
        entry.get("translation_stage") == "translation_frozen"
        for entry in state["transport"]["history"][1:]
    )
    assert errors(checker, state, current, manifest) == []

    print("test_check_private_translation_stage: OK")


if __name__ == "__main__":
    main()
