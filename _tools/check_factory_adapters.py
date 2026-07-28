#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factory actionが恒久adapter・request契約・固定workflowへ接続されていることを検査する。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
FLOW_PATH = P4 / "FACTORY_FLOW_CONTRACT.json"
REQUEST_PATH = P4 / "FACTORY_REQUEST_CONTRACT.json"
EXPECTED = {
    "adapter": "_tools/fixed_cycle_initializer.py",
    "executor": "_tools/factory_request_executor.py",
    "workflow": ".github/workflows/translation-factory-execute.yml",
}
DOCS = {
    "readme": ROOT / "README.md",
    "session": P4 / "SESSION_BOOTSTRAP.md",
    "factory": P4 / "FACTORY_FLOW.md",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT)}")
    return value


def validate(flow: dict[str, Any], request: dict[str, Any], workflow_text: str, docs: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if flow.get("request_contract") != "_phase4_proofread/FACTORY_REQUEST_CONTRACT.json":
        errors.append("factory flow request_contract path mismatch")
    if flow.get("execution_workflow") != EXPECTED["workflow"]:
        errors.append("factory flow execution_workflow path mismatch")
    action = flow.get("actions", {}).get("initialize_next_cycle_from_reservation", {})
    if not isinstance(action, dict):
        errors.append("initialize action must be an object")
        action = {}
    if action.get("executor") != "fixed_cycle_initializer":
        errors.append("initialize action executor mismatch")
    if action.get("adapter") != EXPECTED["adapter"]:
        errors.append("initialize action adapter mismatch")
    if action.get("request_operation") != "initialize_with_semantic_boundary":
        errors.append("initialize action request_operation mismatch")

    if request.get("schema_version") != 1 or request.get("contract_id") != "translation-factory-request-v1":
        errors.append("factory request contract identity mismatch")
    if request.get("execution_workflow") != EXPECTED["workflow"]:
        errors.append("factory request workflow mismatch")
    if request.get("executor") != EXPECTED["executor"]:
        errors.append("factory request executor mismatch")
    operation = request.get("allowed_operations", {}).get("initialize_with_semantic_boundary", {})
    if not isinstance(operation, dict):
        errors.append("factory request initialize operation must be an object")
        operation = {}
    if operation.get("adapter") != EXPECTED["adapter"]:
        errors.append("factory request adapter mismatch")
    if operation.get("expected_controller_action") != "initialize_next_cycle_from_reservation":
        errors.append("factory request expected action mismatch")
    if operation.get("resulting_station") != "translation_quality_audit":
        errors.append("factory request resulting station mismatch")
    for key in ("translation_content_writes_forbidden", "owner_writes_forbidden", "formal_batch_writes_forbidden"):
        if operation.get(key) is not True:
            errors.append(f"factory request {key} must be true")

    required_workflow = (
        "name: Translation factory executor",
        'branches:\n      - "agent/yuwen-mowen-train-*"',
        "pull_request:",
        "github.event.pull_request.head.repo.full_name == github.repository",
        'paths:\n      - "_factory_requests/*.json"',
        "github.actor != 'github-actions[bot]'",
        "gh run download",
        "factory_request_executor.py",
        "check_private_translation_stage.py",
        "check_next_task_packet.py",
        "translation_quality_audit",
        'git rm "${{ steps.request.outputs.request }}"',
        'git push origin "HEAD:${branch_name}"',
    )
    for needle in required_workflow:
        if needle not in workflow_text:
            errors.append(f"factory execution workflow lacks marker: {needle}")
    for forbidden in ("oneoff", "web.run", "workflow_dispatch:"):
        if forbidden in workflow_text:
            errors.append(f"factory execution workflow contains forbidden fallback: {forbidden}")

    required_docs = {
        "readme": ("translation-factory-execute.yml", "FACTORY_REQUEST_CONTRACT.json"),
        "session": ("fixed_cycle_initializer.py", "factory_adapter_missing"),
        "factory": ("FACTORY_REQUEST_CONTRACT.json", "translation-factory-execute.yml", "factory_adapter_missing"),
    }
    for label, needles in required_docs.items():
        for needle in needles:
            if needle not in docs.get(label, ""):
                errors.append(f"{label} lacks permanent factory adapter marker: {needle}")
    legacy = "select_cycle_execution_mode.py --repository-visibility <private|public> --write"
    if legacy in docs.get("session", ""):
        errors.append("session retains manual mode-lock command after fixed initializer wiring")
    return errors


def main() -> int:
    try:
        flow = load(FLOW_PATH)
        request = load(REQUEST_PATH)
        for path in EXPECTED.values():
            if not (ROOT / path).is_file():
                raise ValueError(f"missing factory adapter resource: {path}")
        workflow_text = (ROOT / EXPECTED["workflow"]).read_text(encoding="utf-8")
        docs = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate(flow, request, workflow_text, docs)
    print("=== Translation factory adapters ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: controller action is connected to a permanent fixed adapter and request workflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
