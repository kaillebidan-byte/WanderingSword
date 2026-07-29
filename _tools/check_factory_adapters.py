#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factory actionが恒久adapter・固定workflow・資料還流契約へ接続されていることを検査する。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
FLOW = P4 / "FACTORY_FLOW_CONTRACT.json"
REQUEST = P4 / "FACTORY_REQUEST_CONTRACT.json"
SOURCE_FEEDBACK = P4 / "QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"
RESOURCES = {
    "initializer": "_tools/fixed_cycle_initializer.py",
    "context": "_tools/quality_audit_context.py",
    "request_executor": "_tools/factory_request_executor.py",
    "request_workflow": ".github/workflows/translation-factory-execute.yml",
    "encoding": "_tools/fixed_encoding_pipeline.py",
    "source_feedback": "_tools/source_document_feedback.py",
    "source_feedback_checker": "_tools/check_quality_audit_source_feedback.py",
    "encoding_executor": "_tools/factory_encoding_executor.py",
    "encoding_workflow": ".github/workflows/translation-factory-encode.yml",
    "finalizer": "_tools/fixed_release_finalizer.py",
    "finalization_workflow": ".github/workflows/translation-factory-finalize.yml",
    "readme": "README.md",
    "factory_doc": "_phase4_proofread/FACTORY_FLOW.md",
    "session_doc": "_phase4_proofread/SESSION_BOOTSTRAP.md",
    "pair_runbook": "_phase4_proofread/RUNBOOK_人物ペア再監査.md",
}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT)}")
    return value


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"factory resource is not strict UTF-8: {path.relative_to(ROOT)}: {exc}"
        ) from exc


def validate(
    flow: dict[str, Any],
    request: dict[str, Any],
    source_feedback: dict[str, Any],
    texts: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    expected_top = {
        "request_contract": "_phase4_proofread/FACTORY_REQUEST_CONTRACT.json",
        "quality_audit_source_feedback_contract": (
            "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"
        ),
        "quality_audit_context_adapter": RESOURCES["context"],
        "execution_workflow": RESOURCES["request_workflow"],
        "encoding_workflow": RESOURCES["encoding_workflow"],
        "finalization_workflow": RESOURCES["finalization_workflow"],
    }
    for key, expected in expected_top.items():
        if flow.get(key) != expected:
            errors.append(f"factory flow {key} mismatch")

    actions = flow.get("actions", {})
    expected_actions = {
        "initialize_next_cycle_from_reservation": {
            "executor": "fixed_cycle_initializer",
            "adapter": RESOURCES["initializer"],
            "quality_audit_context_adapter": RESOURCES["context"],
            "resulting_candidate_schema": 3,
        },
        "translation_quality_audit": {
            "source_feedback_contract": (
                "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"
            ),
            "required_candidate_schema": 3,
            "required_audit_decision_schema": 2,
        },
        "encode_recorded_decisions": {
            "executor": "fixed_encoding_pipeline",
            "adapter": RESOURCES["encoding"],
            "source_feedback_adapter": RESOURCES["source_feedback"],
            "execution_workflow": RESOURCES["encoding_workflow"],
        },
        "finalize_release_state": {
            "executor": "fixed_release_finalizer",
            "adapter": RESOURCES["finalizer"],
            "request_pattern": "_factory_requests/finalize-release-*.json",
            "execution_workflow": RESOURCES["finalization_workflow"],
            "resulting_transport": "awaiting_private_merge",
        },
    }
    for name, expected in expected_actions.items():
        item = actions.get(name)
        if not isinstance(item, dict):
            errors.append(f"action {name} missing")
            continue
        for key, value in expected.items():
            if item.get(key) != value:
                errors.append(f"action {name}.{key} mismatch")

    quality_station = next(
        (
            item
            for item in flow.get("human_judgment_stations", [])
            if isinstance(item, dict)
            and item.get("station_id") == "translation_quality_audit"
        ),
        None,
    )
    if not isinstance(quality_station, dict):
        errors.append("translation_quality_audit station missing")
    else:
        outputs = set(quality_station.get("required_outputs", []))
        if not {"reading_attestation", "source_document_decisions"} <= outputs:
            errors.append("translation_quality_audit source feedback outputs missing")
        if quality_station.get("source_feedback_adapter") != RESOURCES["source_feedback"]:
            errors.append("translation_quality_audit source feedback adapter mismatch")

    if (
        request.get("contract_id") != "translation-factory-request-v1"
        or request.get("executor") != RESOURCES["request_executor"]
    ):
        errors.append("factory request contract mismatch")
    if source_feedback.get("contract_id") != "quality-audit-source-feedback-v1":
        errors.append("source feedback contract mismatch")
    if source_feedback.get("candidate_schema_version") != 3:
        errors.append("source feedback candidate schema mismatch")
    if source_feedback.get("audit_decision_schema_version") != 2:
        errors.append("source feedback decision schema mismatch")

    workflow_markers = {
        "request": (
            "name: Translation factory executor",
            "factory_request_executor.py",
            "quality_audit_context.py",
            "required_candidate_schema",
            "git rm",
        ),
        "encoding": (
            "name: Translation factory encoding",
            "factory_encoding_executor.py",
            "check_quality_audit_source_feedback.py",
            "source_document_feedback.py",
            "git add _phase4_proofread 10_人物",
        ),
        "finalization": (
            "name: Translation factory finalization",
            "fixed_release_finalizer.py",
            "finalization-inputs.json",
            "check_release_evidence.py",
            "git rm",
        ),
    }
    for key, markers in workflow_markers.items():
        for marker in markers:
            if marker not in texts[key]:
                errors.append(f"{key} workflow lacks marker: {marker}")

    combined = "\n".join(
        (
            texts["context_code"],
            texts["source_feedback_code"],
            texts["source_feedback_checker_code"],
            texts["encoding_code"],
            texts["encoding_executor_code"],
        )
    )
    for marker in (
        "quality_audit_context",
        "source_document_targets",
        "source_document_decisions",
        "reading_attestation",
        "apply_owner_assignment_v2",
        "ready_for_public_ci",
    ):
        if marker not in combined:
            errors.append(f"factory adapter path lacks marker: {marker}")

    document_markers = {
        "readme": (
            "source_document_decisions",
            "人物資料",
            "QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json",
        ),
        "factory_doc": (
            "reading_attestation",
            "source_document_decisions",
            "source_document_feedback.py",
        ),
        "session_doc": (
            "reading_attestation",
            "source_document_decisions",
            "人物資料は固定正解ではない",
        ),
        "pair_runbook": (
            "reading_attestation",
            "keep/revise/create/unresolved",
            "人物資料の決定的適用",
        ),
    }
    for label, markers in document_markers.items():
        for marker in markers:
            if marker not in texts[label]:
                errors.append(f"{label} lacks source feedback marker: {marker}")

    finalization_path = texts["finalization"] + "\n" + texts["finalizer_code"]
    if "awaiting_private_merge" not in finalization_path:
        errors.append("finalization path lacks resulting transport marker")

    for text in (texts["request"], texts["encoding"], texts["finalization"]):
        for forbidden in ("oneoff", "web.run", "workflow_dispatch:"):
            if forbidden in text:
                errors.append(f"workflow contains forbidden fallback: {forbidden}")
    return errors


def main() -> int:
    try:
        flow = load_object(FLOW)
        request = load_object(REQUEST)
        source_feedback = load_object(SOURCE_FEEDBACK)
        for resource in RESOURCES.values():
            path = ROOT / resource
            if not path.is_file():
                raise ValueError(f"missing factory resource: {resource}")
        texts = {
            "request": read_utf8(ROOT / RESOURCES["request_workflow"]),
            "encoding": read_utf8(ROOT / RESOURCES["encoding_workflow"]),
            "finalization": read_utf8(ROOT / RESOURCES["finalization_workflow"]),
            "context_code": read_utf8(ROOT / RESOURCES["context"]),
            "encoding_code": read_utf8(ROOT / RESOURCES["encoding"]),
            "source_feedback_code": read_utf8(ROOT / RESOURCES["source_feedback"]),
            "source_feedback_checker_code": read_utf8(
                ROOT / RESOURCES["source_feedback_checker"]
            ),
            "encoding_executor_code": read_utf8(
                ROOT / RESOURCES["encoding_executor"]
            ),
            "finalizer_code": read_utf8(ROOT / RESOURCES["finalizer"]),
            "readme": read_utf8(ROOT / RESOURCES["readme"]),
            "factory_doc": read_utf8(ROOT / RESOURCES["factory_doc"]),
            "session_doc": read_utf8(ROOT / RESOURCES["session_doc"]),
            "pair_runbook": read_utf8(ROOT / RESOURCES["pair_runbook"]),
        }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate(flow, request, source_feedback, texts)
    print("=== Translation factory adapters ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(
        "OK: initializer context, persona feedback, encoding, and finalization use permanent adapters"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
