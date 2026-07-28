#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factory actionが恒久adapter・固定workflowへ接続されていることを検査する。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
FLOW = P4 / "FACTORY_FLOW_CONTRACT.json"
REQUEST = P4 / "FACTORY_REQUEST_CONTRACT.json"
RESOURCES = {
    "initializer": "_tools/fixed_cycle_initializer.py",
    "request_executor": "_tools/factory_request_executor.py",
    "request_workflow": ".github/workflows/translation-factory-execute.yml",
    "encoding": "_tools/fixed_encoding_pipeline.py",
    "encoding_executor": "_tools/factory_encoding_executor.py",
    "encoding_workflow": ".github/workflows/translation-factory-encode.yml",
    "finalizer": "_tools/fixed_release_finalizer.py",
    "finalization_workflow": ".github/workflows/translation-factory-finalize.yml",
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
    texts: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    expected_top = {
        "request_contract": "_phase4_proofread/FACTORY_REQUEST_CONTRACT.json",
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
        },
        "encode_recorded_decisions": {
            "executor": "fixed_encoding_pipeline",
            "adapter": RESOURCES["encoding"],
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

    if (
        request.get("contract_id") != "translation-factory-request-v1"
        or request.get("executor") != RESOURCES["request_executor"]
    ):
        errors.append("factory request contract mismatch")

    workflow_markers = {
        "request": (
            "name: Translation factory executor",
            "factory_request_executor.py",
            "git rm",
        ),
        "encoding": (
            "name: Translation factory encoding",
            "factory_encoding_executor.py",
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

    finalization_path = texts["finalization"] + "\n" + texts["finalizer_code"]
    if "awaiting_private_merge" not in finalization_path:
        errors.append("finalization path lacks resulting transport marker")

    encoding_path = (
        texts["encoding"]
        + "\n"
        + texts["encoding_code"]
        + "\n"
        + texts["encoding_executor_code"]
    )
    for marker in (
        "fixed_encoding_pipeline",
        "apply_owner_assignment_v2",
        "check_batch_planning.py",
        "ready_for_public_ci",
    ):
        if marker not in encoding_path:
            errors.append(f"encoding path lacks marker: {marker}")

    for text in (texts["request"], texts["encoding"], texts["finalization"]):
        for forbidden in ("oneoff", "web.run", "workflow_dispatch:"):
            if forbidden in text:
                errors.append(f"workflow contains forbidden fallback: {forbidden}")
    return errors


def main() -> int:
    try:
        flow = load_object(FLOW)
        request = load_object(REQUEST)
        for resource in RESOURCES.values():
            path = ROOT / resource
            if not path.is_file():
                raise ValueError(f"missing factory resource: {resource}")
        texts = {
            "request": read_utf8(ROOT / RESOURCES["request_workflow"]),
            "encoding": read_utf8(ROOT / RESOURCES["encoding_workflow"]),
            "finalization": read_utf8(ROOT / RESOURCES["finalization_workflow"]),
            "encoding_code": read_utf8(ROOT / RESOURCES["encoding"]),
            "encoding_executor_code": read_utf8(
                ROOT / RESOURCES["encoding_executor"]
            ),
            "finalizer_code": read_utf8(ROOT / RESOURCES["finalizer"]),
        }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate(flow, request, texts)
    print("=== Translation factory adapters ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(
        "OK: initializer, encoding, and release finalization use permanent fixed adapters"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
