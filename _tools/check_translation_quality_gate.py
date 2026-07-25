#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""束数・通読量の目的化を防ぐ翻訳品質ゲートを検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import check_private_translation_stage as private_stage

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "_phase4_proofread" / "CI_TRAIN_MANIFEST.json"
OBJECTIVE = "repair_substantive_translation_defects"
METRIC_ROLE = "transport_only"
LOW_YIELD_PERCENT = 15
RELEASE_STATUSES = {"ready_for_public_ci", "in_public_ci", "verified"}


def load_object(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("ERROR: CI_TRAIN_MANIFEST top level must be an object")
    return value


def nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bundles = manifest.get("bundles")
    if not isinstance(bundles, list):
        return ["bundles must be a list"]

    calculated = {
        "reviewed_keys": 0,
        "unique_reviewed_rows": 0,
        "fix_keys": 0,
        "unique_fix_rows": 0,
        "keep_only_bundles": 0,
    }

    for index, bundle in enumerate(bundles):
        label = f"bundles[{index}]"
        if not isinstance(bundle, dict):
            errors.append(f"{label} must be an object")
            continue
        values: dict[str, int] = {}
        for key in ("reviewed_keys", "unique_rows", "fix_keys", "unique_fix_rows"):
            value = bundle.get(key)
            if not nonnegative_int(value):
                errors.append(f"{label}.{key} must be a non-negative integer")
                value = 0
            values[key] = value
        if values["reviewed_keys"] < values["unique_rows"]:
            errors.append(f"{label}.reviewed_keys must be >= unique_rows")
        if values["fix_keys"] > values["reviewed_keys"]:
            errors.append(f"{label}.fix_keys must be <= reviewed_keys")
        if values["unique_fix_rows"] > values["unique_rows"]:
            errors.append(f"{label}.unique_fix_rows must be <= unique_rows")
        keep_keys = bundle.get("keep_keys")
        if not nonnegative_int(keep_keys):
            errors.append(f"{label}.keep_keys must be a non-negative integer")
        elif keep_keys + values["fix_keys"] != values["reviewed_keys"]:
            errors.append(f"{label}.keep_keys + fix_keys must equal reviewed_keys")
        calculated["reviewed_keys"] += values["reviewed_keys"]
        calculated["unique_reviewed_rows"] += values["unique_rows"]
        calculated["fix_keys"] += values["fix_keys"]
        calculated["unique_fix_rows"] += values["unique_fix_rows"]
        if values["fix_keys"] == 0:
            calculated["keep_only_bundles"] += 1

    totals = manifest.get("totals")
    if not isinstance(totals, dict):
        errors.append("totals must be an object")
        totals = {}
    for key, expected in calculated.items():
        observed = totals.get(key)
        if observed != expected:
            errors.append(f"totals.{key} mismatch: {observed!r} != {expected!r}")
    if totals.get("reviewed_rows") != calculated["unique_reviewed_rows"]:
        errors.append("totals.reviewed_rows must equal unique_reviewed_rows")

    gate = manifest.get("quality_gate")
    if not isinstance(gate, dict):
        return errors + ["quality_gate must be an object"]
    if gate.get("schema_version") != 1:
        errors.append("quality_gate.schema_version must be 1")
    if gate.get("primary_objective") != OBJECTIVE:
        errors.append(f"quality_gate.primary_objective must be {OBJECTIVE!r}")
    if gate.get("throughput_metrics_role") != METRIC_ROLE:
        errors.append(f"quality_gate.throughput_metrics_role must be {METRIC_ROLE!r}")
    if gate.get("low_yield_threshold_percent") != LOW_YIELD_PERCENT:
        errors.append(f"quality_gate.low_yield_threshold_percent must be {LOW_YIELD_PERCENT}")

    for key in (
        "reviewed_keys",
        "unique_reviewed_rows",
        "fix_keys",
        "unique_fix_rows",
        "keep_only_bundles",
    ):
        if gate.get(key) != calculated[key]:
            errors.append(f"quality_gate.{key} mismatch")

    pre_fix = gate.get("pre_challenge_unique_fix_rows")
    if not nonnegative_int(pre_fix) or pre_fix > calculated["unique_fix_rows"]:
        errors.append("quality_gate.pre_challenge_unique_fix_rows is invalid")
        pre_fix = calculated["unique_fix_rows"]
    low_yield = (
        calculated["unique_reviewed_rows"] > 0
        and pre_fix * 100 < calculated["unique_reviewed_rows"] * LOW_YIELD_PERCENT
    )
    if gate.get("low_yield_detected") is not low_yield:
        errors.append("quality_gate.low_yield_detected mismatch")

    status = manifest.get("status")
    if status in RELEASE_STATUSES and gate.get("release_decision") != "quality_passed":
        errors.append("release status requires quality_gate.release_decision=quality_passed")

    challenge = gate.get("challenge_pass")
    if low_yield:
        if not isinstance(challenge, dict):
            errors.append("low-yield release requires challenge_pass")
        else:
            if challenge.get("status") != "complete":
                errors.append("challenge_pass.status must be complete")
            if challenge.get("scope") != "all_initial_keep_unique_rows":
                errors.append("challenge_pass.scope must cover all initial keep unique rows")
            initial_keep = calculated["unique_reviewed_rows"] - pre_fix
            if challenge.get("reviewed_candidate_keep_rows") != initial_keep:
                errors.append("challenge_pass.reviewed_candidate_keep_rows mismatch")
            findings_unique = challenge.get("findings_unique_rows")
            finding_keys = challenge.get("finding_keys")
            if not nonnegative_int(findings_unique):
                errors.append("challenge_pass.findings_unique_rows must be non-negative")
                findings_unique = 0
            if not nonnegative_int(finding_keys) or finding_keys < findings_unique:
                errors.append("challenge_pass.finding_keys is invalid")
            if pre_fix + findings_unique != calculated["unique_fix_rows"]:
                errors.append("challenge findings must reconcile to final unique_fix_rows")
            record = challenge.get("record")
            if (
                not isinstance(record, str)
                or not record.startswith("_phase4_proofread/QUALITY_CHALLENGE_")
                or not record.endswith(".md")
                or not (ROOT / record).is_file()
            ):
                errors.append("challenge_pass.record is invalid or missing")
    return errors


def main() -> int:
    manifest = load_object()
    errors = validate(manifest)

    contract = private_stage.load_object(private_stage.CONTRACT_PATH)
    state = private_stage.load_object(private_stage.STATE_PATH)
    current = private_stage.load_object(private_stage.CURRENT_PATH)
    stage_manifest = private_stage.load_object(private_stage.MANIFEST_PATH)
    stage_errors = private_stage.validate(contract, state, current, stage_manifest)
    errors.extend(f"private stage: {error}" for error in stage_errors)

    gate = manifest.get("quality_gate", {})
    print("=== Translation quality gate ===")
    print(f"train: {manifest.get('train_id')}")
    print(f"objective: {gate.get('primary_objective')}")
    print(f"unique rows: {gate.get('unique_reviewed_rows')}")
    print(f"reviewed keys: {gate.get('reviewed_keys')}")
    print(f"unique fixes: {gate.get('unique_fix_rows')}")
    print(f"fix keys: {gate.get('fix_keys')}")
    print(f"low yield: {gate.get('low_yield_detected')}")
    print(f"private stage: {state.get('stage')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: translation quality and private-stage separation are complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
