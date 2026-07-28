#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""private翻訳wave、翻訳凍結、CI輸送軸の分離を検査する。"""
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
    "translation_frozen",
)
TRANSPORT_ORDER = (
    "not_ready",
    "ready_for_public_ci",
    "in_public_ci",
    "verified",
    "awaiting_private_merge",
    "merged",
)
PACKET_STATUSES = {
    "prepared",
    "audited",
    "encoded",
    "needs_repreparation",
    "needs_reaudit",
}
SEAL_REASONS = {
    "packet_threshold",
    "unique_reviewed_rows_threshold",
    "scope_exhausted",
}
REPLENISHMENT_REASONS = {
    "packet_invalidated",
    "duplicate_normalization_reduced_scope",
    "needs_context_unresolved",
    "prepared_source_became_stale",
    "scope_boundary_corrected",
}
NORMAL_TRANSITIONS = {
    "private_preparation": {"private_quality_audit"},
    "private_quality_audit": {"private_encoding"},
    "private_encoding": {"private_quality_audit", "translation_frozen"},
    "translation_frozen": {"private_quality_audit"},
}
EXPECTED = {
    "private_preparation": {
        "operation_state": "private_translation_work",
        "translation_judgment_allowed": False,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": False,
        "metrics_frozen": True,
    },
    "private_quality_audit": {
        "operation_state": "private_translation_work",
        "translation_judgment_allowed": True,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": False,
        "metrics_frozen": True,
    },
    "private_encoding": {
        "operation_state": "private_translation_work",
        "translation_judgment_allowed": False,
        "fix_writes_allowed": True,
        "encoding_writes_allowed": True,
        "throughput_metrics_visible": True,
        "metrics_frozen": False,
    },
    "translation_frozen": {
        "operation_state": "translation_frozen",
        "translation_judgment_allowed": False,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": True,
        "metrics_frozen": False,
    },
}
FORBIDDEN_AUDIT_METRIC_KEYS = {
    "metrics_snapshot",
    "release_remaining",
    "release_threshold",
    "thresholds",
    "caps",
    "totals",
    "reviewed_rows",
    "unique_reviewed_rows",
    "fix_keys",
    "bundle_count",
}
FORBIDDEN_PREPARATION_JUDGMENT_KEYS = {
    "translation_judgment",
    "decision",
    "fix_candidate",
    "fix_candidates",
    "challenged_keep",
    "challenged_keeps",
    "fix_json",
    "new_owner",
    "formal_batch",
}


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


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 2:
        errors.append("contract.schema_version must be 2")
    if contract.get("transition_order") != list(STAGE_ORDER):
        errors.append("contract.transition_order mismatch")
    if contract.get("transport", {}).get("statuses") != list(TRANSPORT_ORDER):
        errors.append("contract.transport.statuses mismatch")
    policy = contract.get("wave_policy")
    if not isinstance(policy, dict):
        errors.append("contract.wave_policy must be an object")
    else:
        if policy.get("normal_seal") != {"packet_count": 4, "unique_reviewed_rows": 40}:
            errors.append("contract.wave_policy.normal_seal mismatch")
        if policy.get("standard_reviewed_rows") != {"min": 40, "max": 60}:
            errors.append("contract.wave_policy.standard_reviewed_rows mismatch")
        if policy.get("caps") != {"packet_count": 6, "unique_reviewed_rows": 80}:
            errors.append("contract.wave_policy.caps mismatch")
        if policy.get("semantic_extension") != {
            "allowed": True,
            "after_standard_max": 60,
            "hard_max": 80,
            "reason": "complete_semantic_unit",
            "fill_to_hard_max_required": False,
        }:
            errors.append("contract.wave_policy.semantic_extension mismatch")
        if set(policy.get("seal_reasons", [])) != SEAL_REASONS:
            errors.append("contract.wave_policy.seal_reasons mismatch")
        if set(policy.get("replenishment_reasons", [])) != REPLENISHMENT_REASONS:
            errors.append("contract.wave_policy.replenishment_reasons mismatch")

    stages = contract.get("stages")
    if not isinstance(stages, list):
        return errors + ["contract.stages must be a list"]
    by_id = {
        item.get("id"): item
        for item in stages
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if set(by_id) != set(STAGE_ORDER):
        return errors + ["contract stage ids mismatch"]
    for stage_id, expected in EXPECTED.items():
        item = by_id[stage_id]
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append(f"contract {stage_id}.{key} mismatch")
        if set(item.get("allowed_next", [])) != NORMAL_TRANSITIONS[stage_id]:
            errors.append(f"contract {stage_id}.allowed_next mismatch")
    return errors


def _validate_history(state: dict[str, Any], errors: list[str]) -> None:
    history = state.get("history")
    if not isinstance(history, list) or not history:
        errors.append("state.history must be a non-empty list")
        return
    previous: str | None = None
    for index, entry in enumerate(history):
        label = f"history[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        stage = entry.get("stage")
        if stage not in EXPECTED:
            errors.append(f"{label}.stage invalid")
            continue
        expected_status = "active" if index == len(history) - 1 else "complete"
        if entry.get("status") != expected_status:
            errors.append(f"{label}.status must be {expected_status}")
        if previous is not None:
            if previous == "private_encoding" and stage == "private_preparation":
                reason = entry.get("replenishment_reason")
                if reason not in REPLENISHMENT_REASONS:
                    errors.append("encoding -> preparation requires replenishment reason")
                if index == len(history) - 1 and state.get("replenishment_reason") != reason:
                    errors.append("state.replenishment_reason must match active replenishment")
            elif stage not in NORMAL_TRANSITIONS[previous]:
                errors.append(f"illegal transition: {previous} -> {stage}")
        previous = stage
    if previous != state.get("stage"):
        errors.append("last history stage must equal state.stage")
    if not (
        len(history) >= 2
        and history[-2].get("stage") == "private_encoding"
        and history[-1].get("stage") == "private_preparation"
    ) and state.get("replenishment_reason") is not None:
        errors.append("replenishment_reason is only allowed on active encoding -> preparation")


def _validate_transport(state: dict[str, Any], errors: list[str]) -> None:
    transport = state.get("transport")
    if not isinstance(transport, dict):
        errors.append("state.transport must be an object")
        return
    status = transport.get("status")
    if status not in TRANSPORT_ORDER:
        errors.append("transport.status invalid")
    history = transport.get("history")
    if not isinstance(history, list) or not history:
        errors.append("transport.history must be a non-empty list")
        return
    previous: str | None = None
    for index, entry in enumerate(history):
        if not isinstance(entry, dict):
            errors.append(f"transport.history[{index}] must be an object")
            continue
        current = entry.get("status")
        if current not in TRANSPORT_ORDER:
            errors.append(f"transport.history[{index}].status invalid")
            continue
        if previous is not None and TRANSPORT_ORDER.index(current) != TRANSPORT_ORDER.index(previous) + 1:
            errors.append(f"illegal transport transition: {previous} -> {current}")
        if current != "not_ready" and entry.get("translation_stage") != "translation_frozen":
            errors.append(f"transport {current} must keep translation_stage=translation_frozen")
        previous = current
    if previous != status:
        errors.append("last transport history status must equal transport.status")


def _validate_packet_shape(packet: Any, index: int, errors: list[str]) -> dict[str, Any]:
    label = f"wave.packets[{index}]"
    if not isinstance(packet, dict):
        errors.append(f"{label} must be an object")
        return {}
    if not _nonempty_string(packet.get("packet_id")):
        errors.append(f"{label}.packet_id must be non-empty")
    scenes = packet.get("scene_groups")
    if not isinstance(scenes, list) or not scenes or any(not _nonempty_string(x) for x in scenes):
        errors.append(f"{label}.scene_groups must be a non-empty string list")
    if packet.get("status") not in PACKET_STATUSES:
        errors.append(f"{label}.status invalid")
    prep = packet.get("preparation_record")
    if not isinstance(prep, dict) or not _nonempty_string(prep.get("candidate_packet")) or not _nonempty_string(prep.get("context_record")):
        errors.append(f"{label}.preparation_record must identify candidate_packet and context_record")
    return packet


def _validate_wave(state: dict[str, Any], stage: str, errors: list[str]) -> None:
    wave = state.get("wave")
    if not isinstance(wave, dict):
        errors.append("state.wave must be an object")
        return
    if not _nonempty_string(wave.get("wave_id")):
        errors.append("wave.wave_id must be non-empty")
    queue_status = wave.get("queue_status")
    if queue_status not in {"open", "sealed"}:
        errors.append("wave.queue_status invalid")
    packets = wave.get("packets")
    if not isinstance(packets, list) or not packets:
        errors.append("wave.packets must be a non-empty list")
        return
    if len(packets) > 6:
        errors.append("wave packet cap exceeded")

    packet_ids: set[str] = set()
    scenes: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(packets):
        packet = _validate_packet_shape(raw, index, errors)
        normalized.append(packet)
        packet_id = packet.get("packet_id")
        if isinstance(packet_id, str):
            if packet_id in packet_ids:
                errors.append(f"duplicate packet_id: {packet_id}")
            packet_ids.add(packet_id)
        for scene in packet.get("scene_groups", []) if isinstance(packet.get("scene_groups"), list) else []:
            if scene in scenes:
                errors.append(f"scene appears in multiple packets: {scene}")
            scenes.add(scene)

    seal_reason = wave.get("seal_reason")
    if queue_status == "open":
        if seal_reason is not None:
            errors.append("open queue must not have seal_reason")
    else:
        if seal_reason not in SEAL_REASONS:
            errors.append("sealed queue requires valid seal_reason")
        if len(packets) < 4 and seal_reason == "packet_threshold":
            errors.append("preparation_underfilled: packet threshold not reached")
        if len(packets) < 4 and seal_reason == "unique_reviewed_rows_threshold" and not _nonempty_string(wave.get("seal_attestation")):
            errors.append("preparation_underfilled: row-threshold seal needs attestation")
        if seal_reason == "scope_exhausted" and not _nonempty_string(wave.get("seal_attestation")):
            errors.append("scope_exhausted seal requires attestation")

    if stage == "private_preparation":
        summary = wave.get("preparation_summary")
        if queue_status == "sealed":
            if not isinstance(summary, dict):
                errors.append("sealed preparation requires preparation_summary")
            else:
                count = summary.get("packet_count")
                rows = summary.get("unique_reviewed_rows")
                if count != len(packets):
                    errors.append("preparation_summary.packet_count mismatch")
                if not _nonnegative_int(rows):
                    errors.append("preparation_summary.unique_reviewed_rows must be non-negative")
                    rows = 0
                if rows > 80:
                    errors.append("wave row cap exceeded")
                normal = len(packets) >= 4 or rows >= 40
                exhausted = seal_reason == "scope_exhausted" and _nonempty_string(wave.get("seal_attestation"))
                if not normal and not exhausted:
                    errors.append("preparation_underfilled")
        for index, packet in enumerate(normalized):
            if packet.get("status") != "prepared":
                errors.append(f"wave.packets[{index}] must be prepared during preparation")
            if packet.get("formal_batch") is not None:
                errors.append(f"wave.packets[{index}] formal_batch forbidden during preparation")
            bad = FORBIDDEN_PREPARATION_JUDGMENT_KEYS & set(_walk_keys(packet.get("preparation_record", {})))
            if bad:
                errors.append(f"wave.packets[{index}] preparation contains translation judgment fields: {sorted(bad)!r}")

    elif stage == "private_quality_audit":
        if queue_status != "sealed":
            errors.append("quality audit requires sealed queue")
        bad_metrics = FORBIDDEN_AUDIT_METRIC_KEYS & set(_walk_keys(wave))
        if bad_metrics:
            errors.append(f"quality audit exposes transport metrics: {sorted(bad_metrics)!r}")
        for index, packet in enumerate(normalized):
            status = packet.get("status")
            if status not in {"prepared", "audited", "needs_repreparation"}:
                errors.append(f"wave.packets[{index}] invalid status during quality audit")
            if packet.get("formal_batch") is not None:
                errors.append(f"wave.packets[{index}] formal_batch forbidden during quality audit")
            if packet.get("review_record") is not None:
                errors.append(f"wave.packets[{index}] review_record forbidden during quality audit")
            if status == "audited" and not isinstance(packet.get("audit_record"), dict):
                errors.append(f"wave.packets[{index}] audited packet requires audit_record")

    elif stage == "private_encoding":
        if queue_status != "sealed":
            errors.append("encoding requires sealed queue")
        for index, packet in enumerate(normalized):
            status = packet.get("status")
            if status not in {"audited", "encoded", "needs_reaudit"}:
                errors.append(f"wave.packets[{index}] unaudited packet blocks encoding")
            if status in {"audited", "encoded", "needs_reaudit"} and not isinstance(packet.get("audit_record"), dict):
                errors.append(f"wave.packets[{index}] requires audit_record during encoding")
            if status == "encoded":
                if not _positive_int(packet.get("formal_batch")):
                    errors.append(f"wave.packets[{index}] encoded packet requires formal_batch")
                if not isinstance(packet.get("review_record"), dict):
                    errors.append(f"wave.packets[{index}] encoded packet requires review_record")
            elif packet.get("formal_batch") is not None:
                errors.append(f"wave.packets[{index}] formal_batch requires encoded status")

    elif stage == "translation_frozen":
        if queue_status != "sealed":
            errors.append("translation freeze requires sealed queue")
        batches: set[int] = set()
        for index, packet in enumerate(normalized):
            if packet.get("status") != "encoded":
                errors.append(f"wave.packets[{index}] must be encoded before translation freeze")
            batch = packet.get("formal_batch")
            if not _positive_int(batch):
                errors.append(f"wave.packets[{index}] translation freeze requires formal_batch")
            elif batch in batches:
                errors.append(f"duplicate formal_batch: {batch}")
            else:
                batches.add(batch)
            if not isinstance(packet.get("audit_record"), dict):
                errors.append(f"wave.packets[{index}] translation freeze requires audit_record")
            if not isinstance(packet.get("review_record"), dict):
                errors.append(f"wave.packets[{index}] translation freeze requires review_record")


def _validate_manifest_boundary(state: dict[str, Any], manifest: dict[str, Any], errors: list[str]) -> None:
    if "candidate_packets" in manifest:
        errors.append("candidate packets must live in PRIVATE_STAGE_STATE, not CI_TRAIN_MANIFEST")
    bundles = manifest.get("bundles")
    if not isinstance(bundles, list):
        errors.append("manifest.bundles must be a list")
        return
    formal_batches = {
        packet.get("formal_batch")
        for packet in state.get("wave", {}).get("packets", [])
        if isinstance(packet, dict) and packet.get("status") == "encoded"
    }
    for index, bundle in enumerate(bundles):
        if not isinstance(bundle, dict):
            continue
        if bundle.get("status") == "reviewed_pending_ci":
            errors.append(f"manifest.bundles[{index}] must split review_status and apply_status")
        if bundle.get("review_status") != "complete":
            errors.append(f"manifest.bundles[{index}].review_status must be complete")
        if bundle.get("apply_status") not in {"pending", "verified"}:
            errors.append(f"manifest.bundles[{index}].apply_status invalid")
        if bundle.get("batch") not in formal_batches:
            errors.append(f"manifest.bundles[{index}] has no encoded wave packet")


def validate(
    contract: dict[str, Any],
    state: dict[str, Any],
    current: dict[str, Any],
    manifest: dict[str, Any],
) -> list[str]:
    errors = validate_contract(contract)
    if state.get("schema_version") != 2:
        errors.append("state.schema_version must be 2")
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
    for key, value in expected.items():
        if key == "operation_state":
            continue
        if permissions.get(key) != value:
            errors.append(f"state.permissions.{key} mismatch for {stage}")

    operation = current.get("operation_mode")
    if not isinstance(operation, dict) or operation.get("declared_state") != expected["operation_state"]:
        errors.append(f"operation_mode.declared_state must be {expected['operation_state']!r}")

    transport_status = state.get("transport", {}).get("status")
    if stage != "translation_frozen" and transport_status != "not_ready":
        errors.append(f"{stage} requires transport.status=not_ready")
    current_train = current.get("ci_train")
    if not isinstance(current_train, dict):
        errors.append("CURRENT_WORK.ci_train must be an object")
    else:
        if current_train.get("status") != manifest.get("status"):
            errors.append("CURRENT_WORK.ci_train.status must match manifest.status")
        if current_train.get("transport_status") != transport_status:
            errors.append("CURRENT_WORK.ci_train.transport_status must match state.transport.status")

    _validate_history(state, errors)
    _validate_transport(state, errors)
    _validate_wave(state, stage, errors)
    _validate_manifest_boundary(state, manifest, errors)
    return errors


def main() -> int:
    contract = load_object(CONTRACT_PATH)
    state = load_object(STATE_PATH)
    current = load_object(CURRENT_PATH)
    manifest = load_object(MANIFEST_PATH)
    errors = validate(contract, state, current, manifest)
    permissions = state.get("permissions", {})
    print("=== Private translation wave ===")
    print(f"train: {state.get('train_id')}")
    print(f"stage: {state.get('stage')}")
    print(f"wave: {state.get('wave', {}).get('wave_id')}")
    print(f"queue: {state.get('wave', {}).get('queue_status')}")
    print(f"transport: {state.get('transport', {}).get('status')}")
    print(f"translation judgment: {permissions.get('translation_judgment_allowed')}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: wave stages, translation freeze, and CI transport are separated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
