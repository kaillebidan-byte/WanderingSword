#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""private翻訳作業の準備・品質監査・収録・CI待ち分離を検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "PRIVATE_TRANSLATION_STAGES.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"

STAGE_ORDER = (
    "private_preparation",
    "private_quality_audit",
    "private_encoding",
    "ready_for_public_ci",
)
EXPECTED = {
    "private_preparation": {
        "operation_state": "private_translation_work",
        "translation_judgment_allowed": False,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": False,
        "metrics_frozen": True,
        "required_evidence": {
            "source_artifact",
            "scene_context",
            "ownership_inventory",
            "candidate_packet",
        },
    },
    "private_quality_audit": {
        "operation_state": "private_translation_work",
        "translation_judgment_allowed": True,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": False,
        "metrics_frozen": True,
        "required_evidence": {
            "audit_record",
            "fix_candidates",
            "challenged_keeps",
        },
    },
    "private_encoding": {
        "operation_state": "private_translation_work",
        "translation_judgment_allowed": False,
        "fix_writes_allowed": True,
        "encoding_writes_allowed": True,
        "throughput_metrics_visible": True,
        "metrics_frozen": False,
        "required_evidence": {
            "audit_record",
            "fix_files",
            "review_records",
            "ownership_records",
        },
    },
    "ready_for_public_ci": {
        "operation_state": "ready_for_public_ci",
        "translation_judgment_allowed": False,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": True,
        "metrics_frozen": False,
        "required_evidence": {
            "quality_gate",
            "manifest",
            "next_task_packet",
        },
    },
}
ALLOWED_TRANSITIONS = {
    "private_preparation": {"private_quality_audit"},
    "private_quality_audit": {"private_encoding"},
    "private_encoding": {"private_quality_audit", "ready_for_public_ci"},
    "ready_for_public_ci": {"private_quality_audit"},
}
METRIC_KEYS = (
    "bundle_count",
    "reviewed_rows",
    "reviewed_keys",
    "unique_reviewed_rows",
    "fix_keys",
    "unique_fix_rows",
)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(nonempty(item) for item in value)
    return False


def repo_paths(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.startswith(("_phase4_proofread/", "_tools/", ".github/")) else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(repo_paths(item))
        return result
    return []


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("contract.schema_version must be 1")
    if contract.get("transition_order") != list(STAGE_ORDER):
        errors.append("contract.transition_order mismatch")
    stages = contract.get("stages")
    if not isinstance(stages, list):
        return errors + ["contract.stages must be a list"]
    by_id = {
        item.get("id"): item
        for item in stages
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if set(by_id) != set(STAGE_ORDER):
        errors.append("contract stage ids mismatch")
        return errors
    for stage_id, expected in EXPECTED.items():
        item = by_id[stage_id]
        for key in (
            "operation_state",
            "translation_judgment_allowed",
            "fix_writes_allowed",
            "encoding_writes_allowed",
            "throughput_metrics_visible",
            "metrics_frozen",
        ):
            if item.get(key) != expected[key]:
                errors.append(f"contract {stage_id}.{key} mismatch")
        if set(item.get("required_evidence", [])) != expected["required_evidence"]:
            errors.append(f"contract {stage_id}.required_evidence mismatch")
        if set(item.get("allowed_next", [])) != ALLOWED_TRANSITIONS[stage_id]:
            errors.append(f"contract {stage_id}.allowed_next mismatch")
    return errors


def validate(
    contract: dict[str, Any],
    state: dict[str, Any],
    current: dict[str, Any],
    manifest: dict[str, Any],
) -> list[str]:
    errors = validate_contract(contract)
    if state.get("schema_version") != 1:
        errors.append("state.schema_version must be 1")
    if state.get("contract") != "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json":
        errors.append("state.contract path mismatch")
    if state.get("train_id") != manifest.get("train_id"):
        errors.append("state.train_id must match manifest.train_id")

    stage = state.get("stage")
    if stage not in EXPECTED:
        return errors + [f"state.stage invalid: {stage!r}"]
    expected = EXPECTED[stage]
    permissions = state.get("permissions")
    if not isinstance(permissions, dict):
        errors.append("state.permissions must be an object")
        permissions = {}
    for key in (
        "translation_judgment_allowed",
        "fix_writes_allowed",
        "encoding_writes_allowed",
        "throughput_metrics_visible",
        "metrics_frozen",
    ):
        if permissions.get(key) != expected[key]:
            errors.append(f"state.permissions.{key} mismatch for {stage}")

    operation = current.get("operation_mode")
    if not isinstance(operation, dict) or operation.get("declared_state") != expected["operation_state"]:
        errors.append(f"operation_mode.declared_state must be {expected['operation_state']!r}")

    expected_manifest_status = (
        "ready_for_public_ci" if stage == "ready_for_public_ci" else "accumulating"
    )
    if manifest.get("status") != expected_manifest_status:
        errors.append(
            f"manifest.status must be {expected_manifest_status!r} during {stage}"
        )
    ci_train = current.get("ci_train")
    if not isinstance(ci_train, dict) or ci_train.get("status") != expected_manifest_status:
        errors.append("CURRENT_WORK.ci_train.status must match stage-derived manifest status")

    history = state.get("history")
    if not isinstance(history, list) or not history:
        return errors + ["state.history must be a non-empty list"]
    previous: str | None = None
    for index, entry in enumerate(history):
        label = f"history[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        entry_stage = entry.get("stage")
        if entry_stage not in EXPECTED:
            errors.append(f"{label}.stage invalid")
            continue
        status = entry.get("status")
        is_last = index == len(history) - 1
        expected_status = "active" if is_last else "complete"
        if status != expected_status:
            errors.append(f"{label}.status must be {expected_status}")
        if previous is not None and entry_stage not in ALLOWED_TRANSITIONS[previous]:
            errors.append(f"illegal transition: {previous} -> {entry_stage}")
        previous = entry_stage

        evidence = entry.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{label}.evidence must be an object")
            evidence = {}
        missing = EXPECTED[entry_stage]["required_evidence"] - set(evidence)
        if missing:
            errors.append(f"{label}.evidence missing: {sorted(missing)!r}")
        for key in EXPECTED[entry_stage]["required_evidence"]:
            value = evidence.get(key)
            if not nonempty(value):
                errors.append(f"{label}.evidence.{key} must be non-empty")
                continue
            for path in repo_paths(value):
                if not (ROOT / path).exists():
                    errors.append(f"{label}.evidence.{key} missing path: {path}")
    if previous != stage:
        errors.append("last history stage must equal state.stage")

    metrics = state.get("metrics_snapshot")
    if expected["throughput_metrics_visible"]:
        if not isinstance(metrics, dict):
            errors.append(f"{stage} requires metrics_snapshot")
            metrics = {}
        totals = manifest.get("totals")
        if not isinstance(totals, dict):
            totals = {}
        for key in METRIC_KEYS:
            if metrics.get(key) != totals.get(key):
                errors.append(f"metrics_snapshot.{key} must match manifest totals")
    elif metrics is not None:
        errors.append(f"{stage} must not expose metrics_snapshot")

    audit_separation = state.get("audit_separation")
    if not isinstance(audit_separation, dict):
        errors.append("state.audit_separation must be an object")
    else:
        if audit_separation.get("pair_keys_follow_judgment") is not True:
            errors.append("pair keys must follow quality judgment")
        if audit_separation.get("bundle_number_assigned_in_encoding") is not True:
            errors.append("bundle numbers must be assigned in encoding")
        if audit_separation.get("audit_metrics_suppressed") is not True:
            errors.append("quality-audit metrics must be suppressed")
        if audit_separation.get("public_reopens_judgment") is not False:
            errors.append("public CI must not reopen translation judgment")

    return errors


def main() -> int:
    contract = load_object(CONTRACT_PATH)
    state = load_object(STATE_PATH)
    current = load_object(CURRENT_PATH)
    manifest = load_object(MANIFEST_PATH)
    errors = validate(contract, state, current, manifest)
    permissions = state.get("permissions", {})
    print("=== Private translation stage ===")
    print(f"train: {state.get('train_id')}")
    print(f"stage: {state.get('stage')}")
    print(f"translation judgment: {permissions.get('translation_judgment_allowed')}")
    print(f"encoding writes: {permissions.get('encoding_writes_allowed')}")
    print(f"throughput metrics visible: {permissions.get('throughput_metrics_visible')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: preparation, quality audit, encoding, and CI transport are separated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
