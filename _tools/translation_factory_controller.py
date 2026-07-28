#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻訳外工程を一意の作業指示へ変換する決定論的controller。"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "FACTORY_FLOW_CONTRACT.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
PACKET_PATH = P4 / "NEXT_TASK_PACKET.json"
VALID_VISIBILITIES = {"private", "public"}
EXPECTED_HUMAN_STATIONS = {"semantic_bundle_boundary", "translation_quality_audit"}


class FactoryStateError(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FactoryStateError("factory_invalid_json_shape", f"top level must be object: {path}")
    return value


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if contract.get("contract_id") != "translation-factory-flow-v1":
        errors.append("contract_id mismatch")
    stations = contract.get("human_judgment_stations")
    station_ids = {
        item.get("station_id")
        for item in stations
        if isinstance(item, dict) and isinstance(item.get("station_id"), str)
    } if isinstance(stations, list) else set()
    if station_ids != EXPECTED_HUMAN_STATIONS:
        errors.append(
            "human judgment stations must be exactly "
            + ", ".join(sorted(EXPECTED_HUMAN_STATIONS))
        )
    actions = contract.get("actions")
    if not isinstance(actions, dict) or not actions:
        errors.append("actions must be a non-empty object")
    else:
        for action, definition in actions.items():
            if not isinstance(definition, dict):
                errors.append(f"actions.{action} must be an object")
                continue
            if definition.get("station_type") not in {"machine", "human"}:
                errors.append(f"actions.{action}.station_type is invalid")
            if not isinstance(definition.get("executor"), str) or not definition.get("executor"):
                errors.append(f"actions.{action}.executor is required")
    retry = contract.get("retry_policy")
    if not isinstance(retry, dict):
        errors.append("retry_policy must be an object")
    else:
        if retry.get("known_transient_max_retries") != 1:
            errors.append("known transient retries must equal 1")
        if retry.get("unknown_failure_max_retries") != 0:
            errors.append("unknown failure retries must equal 0")
        if retry.get("same_arguments_retry_forbidden") is not True:
            errors.append("same-argument retry must be forbidden")
    forbidden = set(contract.get("forbidden_fallbacks", []))
    required_forbidden = {
        "web_search_for_github_api_usage",
        "ad_hoc_workflow_generation",
        "alternate_trigger_experiments",
        "unmapped_api_experiments",
        "same_failed_arguments_retry",
    }
    missing = required_forbidden - forbidden
    if missing:
        errors.append("missing forbidden fallbacks: " + ", ".join(sorted(missing)))
    return errors


def state_fingerprint(
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
) -> str:
    payload = json.dumps(
        {
            "current": current,
            "state": state,
            "manifest": manifest,
            "packet": packet,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _transport_values(
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[Any, Any, Any]:
    return (
        current.get("ci_train", {}).get("transport_status"),
        state.get("transport", {}).get("status"),
        manifest.get("transport", {}).get("status"),
    )


def derive_action(
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
) -> tuple[str, str]:
    transports = _transport_values(current, state, manifest)
    if len(set(transports)) != 1:
        raise FactoryStateError(
            "factory_state_mismatch",
            f"transport mismatch: current={transports[0]!r}, state={transports[1]!r}, manifest={transports[2]!r}",
        )

    control = state.get("cycle_control")
    if not isinstance(control, dict):
        raise FactoryStateError("factory_state_mismatch", "PRIVATE_STAGE_STATE.cycle_control must be an object")
    cycle_status = control.get("status")
    stage = state.get("stage")
    transport = transports[0]

    if cycle_status == "paused":
        exact = control.get("exact_next_action")
        if not isinstance(exact, str) or not exact.strip():
            raise FactoryStateError("factory_state_mismatch", "paused cycle requires exact_next_action")
        return "resume_recorded_checkpoint", exact.strip()

    reservation = packet.get("reservation")
    if (
        transport == "merged"
        and cycle_status == "target_reached"
        and isinstance(reservation, dict)
        and reservation.get("status") == "reserved_only"
        and reservation.get("preparation_started") is False
    ):
        return "initialize_next_cycle_from_reservation", "merged cycle with clean minimal reservation"

    if stage == "private_preparation":
        wave = state.get("wave")
        queue_status = wave.get("queue_status") if isinstance(wave, dict) else None
        if queue_status == "sealed":
            return "advance_to_quality_audit", "semantic wave boundary is already sealed"
        return "semantic_bundle_boundary", "semantic boundary decision is the only permitted human station"

    if stage == "private_quality_audit":
        return "translation_quality_audit", "prepared packets require translation judgment"

    if stage == "private_encoding":
        return "encode_recorded_decisions", "encoding may only consume recorded audit decisions"

    if stage == "translation_frozen":
        if transport == "not_ready":
            return "run_release_preflight", "translation is frozen and transport needs preflight"
        if transport in {"ready_for_public_ci", "in_public_ci"}:
            return "run_release_train", f"transport is {transport}"
        if transport == "verified":
            return "finalize_release_state", "release train is verified but state finalization is pending"
        if transport == "awaiting_private_merge":
            return "verify_phase2_and_merge", "verified frozen HEAD is ready for phase2 and merge"
        if transport == "merged":
            return "reconcile_merged_cycle", "merge exists but cycle has not reached target_reached"

    raise FactoryStateError(
        "factory_unknown_state",
        f"no action for cycle_status={cycle_status!r}, stage={stage!r}, transport={transport!r}",
    )


def build_work_order(
    contract: dict[str, Any],
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    repository_visibility: str,
) -> dict[str, Any]:
    if repository_visibility not in VALID_VISIBILITIES:
        raise FactoryStateError("factory_invalid_visibility", repository_visibility)
    errors = validate_contract(contract)
    if errors:
        raise FactoryStateError("factory_contract_invalid", "; ".join(errors))
    action, reason = derive_action(current, state, manifest, packet)
    actions = contract.get("actions", {})
    definition = actions.get(action)
    if not isinstance(definition, dict):
        raise FactoryStateError("factory_unmapped_action", action)

    station_type = definition.get("station_type")
    station_id = action if station_type == "human" else None
    if station_type == "human" and station_id not in EXPECTED_HUMAN_STATIONS:
        raise FactoryStateError("factory_contract_invalid", f"unexpected human station: {station_id}")

    retry = contract.get("retry_policy", {})
    return {
        "schema_version": 1,
        "contract_id": contract.get("contract_id"),
        "state_fingerprint": state_fingerprint(current, state, manifest, packet),
        "repository_visibility": repository_visibility,
        "action": action,
        "station_type": station_type,
        "station_id": station_id,
        "executor": definition.get("executor"),
        "reason": reason,
        "recorded_exact_next_action": (
            state.get("cycle_control", {}).get("exact_next_action")
            if action == "resume_recorded_checkpoint"
            else None
        ),
        "retry_limit": (
            retry.get("known_transient_max_retries")
            if station_type == "machine"
            else 0
        ),
        "forbidden_fallbacks": contract.get("forbidden_fallbacks", []),
        "worker_rule": (
            "このactionだけを実行し、別API・別workflow・別triggerを考案しない。"
            if station_type == "machine"
            else "指定された意味判断だけを返し、GitHub・状態・輸送操作を行わない。"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-visibility", choices=sorted(VALID_VISIBILITIES), required=True)
    parser.add_argument("--validate-contract-only", action="store_true")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_object(CONTRACT_PATH)
        errors = validate_contract(contract)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        if args.validate_contract_only:
            print("OK: translation factory contract is valid")
            return 0
        work_order = build_work_order(
            contract,
            load_object(CURRENT_PATH),
            load_object(STATE_PATH),
            load_object(MANIFEST_PATH),
            load_object(PACKET_PATH),
            args.repository_visibility,
        )
    except (OSError, json.JSONDecodeError, FactoryStateError) as exc:
        code = exc.code if isinstance(exc, FactoryStateError) else "factory_input_error"
        detail = exc.detail if isinstance(exc, FactoryStateError) else str(exc)
        print(json.dumps({"status": "blocked", "error_code": code, "detail": detail}, ensure_ascii=False))
        return 1

    text = json.dumps(work_order, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
