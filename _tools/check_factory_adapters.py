#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factory actionが恒久adapter・固定workflowへ接続されていることを検査する。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
FLOW_PATH = P4 / "FACTORY_FLOW_CONTRACT.json"
REQUEST_PATH = P4 / "FACTORY_REQUEST_CONTRACT.json"
EXPECTED = {
    "initializer": "_tools/fixed_cycle_initializer.py",
    "request_executor": "_tools/factory_request_executor.py",
    "request_workflow": ".github/workflows/translation-factory-execute.yml",
    "encoding": "_tools/fixed_encoding_pipeline.py",
    "encoding_executor": "_tools/factory_encoding_executor.py",
    "encoding_workflow": ".github/workflows/translation-factory-encode.yml",
}
DOCS = {"factory": P4 / "FACTORY_FLOW.md"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT)}")
    return value


def validate(flow: dict[str, Any], request: dict[str, Any], request_workflow: str, encoding_workflow: str, docs: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if flow.get("request_contract") != "_phase4_proofread/FACTORY_REQUEST_CONTRACT.json":
        errors.append("factory flow request_contract path mismatch")
    if flow.get("execution_workflow") != EXPECTED["request_workflow"]:
        errors.append("factory flow request workflow mismatch")
    if flow.get("encoding_workflow") != EXPECTED["encoding_workflow"]:
        errors.append("factory flow encoding workflow mismatch")

    init = flow.get("actions", {}).get("initialize_next_cycle_from_reservation", {})
    if init.get("executor") != "fixed_cycle_initializer" or init.get("adapter") != EXPECTED["initializer"]:
        errors.append("initialize action adapter mismatch")
    if init.get("request_operation") != "initialize_with_semantic_boundary":
        errors.append("initialize action request_operation mismatch")

    encode = flow.get("actions", {}).get("encode_recorded_decisions", {})
    expected_encode = {
        "executor": "fixed_encoding_pipeline",
        "adapter": EXPECTED["encoding"],
        "trigger_record": "_phase4_proofread/AUDIT_DECISIONS_*.json",
        "execution_workflow": EXPECTED["encoding_workflow"],
        "resulting_stage": "translation_frozen",
        "resulting_transport": "ready_for_public_ci",
    }
    if not isinstance(encode, dict):
        errors.append("encode_recorded_decisions action must be object")
        encode = {}
    for key, expected in expected_encode.items():
        if encode.get(key) != expected:
            errors.append(f"encoding action {key} mismatch")

    if request.get("schema_version") != 1 or request.get("contract_id") != "translation-factory-request-v1":
        errors.append("factory request contract identity mismatch")
    if request.get("execution_workflow") != EXPECTED["request_workflow"]:
        errors.append("factory request workflow mismatch")
    if request.get("executor") != EXPECTED["request_executor"]:
        errors.append("factory request executor mismatch")
    operation = request.get("allowed_operations", {}).get("initialize_with_semantic_boundary", {})
    if operation.get("adapter") != EXPECTED["initializer"]:
        errors.append("factory request initializer mismatch")

    request_markers = (
        "name: Translation factory executor",
        'paths:\n      - "_factory_requests/*.json"',
        "factory_request_executor.py",
        "translation_quality_audit",
        'git rm "${{ steps.request.outputs.request }}"',
    )
    for marker in request_markers:
        if marker not in request_workflow:
            errors.append(f"factory request workflow lacks marker: {marker}")

    encoding_markers = (
        "name: Translation factory encoding",
        'paths:\n      - "_phase4_proofread/AUDIT_DECISIONS_*.json"',
        "factory_encoding_executor.py",
        "fixed_encoding_pipeline.py",
        "apply_owner_assignment_v2",
        "check_batch_planning.py",
        "check_owner_assignment_result.py",
        "ready_for_public_ci",
        '[factory-encoding]',
    )
    # apply_owner_assignment_v2 is imported by adapter, not directly named by workflow.
    combined_encoding = encoding_workflow + "\n" + (ROOT / EXPECTED["encoding"]).read_text(encoding="utf-8")
    for marker in encoding_markers:
        if marker not in combined_encoding:
            errors.append(f"factory encoding path lacks marker: {marker}")

    for text in (request_workflow, encoding_workflow):
        for forbidden in ("oneoff", "web.run", "workflow_dispatch:"):
            if forbidden in text:
                errors.append(f"factory workflow contains forbidden fallback: {forbidden}")

    factory_doc = docs.get("factory", "")
    for marker in ("translation-factory-encode.yml", "fixed_encoding_pipeline.py", "complete_semantic_unit", "apply_owner_assignment_v2.py"):
        if marker not in factory_doc:
            errors.append(f"factory doc lacks encoding marker: {marker}")
    return errors


def main() -> int:
    try:
        flow = load(FLOW_PATH)
        request = load(REQUEST_PATH)
        for path in EXPECTED.values():
            if not (ROOT / path).is_file():
                raise ValueError(f"missing factory adapter resource: {path}")
        request_workflow = (ROOT / EXPECTED["request_workflow"]).read_text(encoding="utf-8")
        encoding_workflow = (ROOT / EXPECTED["encoding_workflow"]).read_text(encoding="utf-8")
        docs = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate(flow, request, request_workflow, encoding_workflow, docs)
    print("=== Translation factory adapters ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: initializer and recorded-decision encoding actions use permanent fixed adapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
