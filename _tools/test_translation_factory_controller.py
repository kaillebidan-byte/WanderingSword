#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
from pathlib import Path

from translation_factory_controller import (
    FactoryStateError,
    build_work_order,
    validate_contract,
)

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = json.loads((ROOT / "_phase4_proofread" / "FACTORY_FLOW_CONTRACT.json").read_text(encoding="utf-8"))


def fixtures():
    current = {
        "ci_train": {"transport_status": "merged"},
    }
    state = {
        "stage": "translation_frozen",
        "cycle_control": {
            "status": "target_reached",
            "exact_next_action": None,
        },
        "transport": {"status": "merged"},
    }
    manifest = {"transport": {"status": "merged"}}
    packet = {
        "reservation": {
            "status": "reserved_only",
            "preparation_started": False,
        }
    }
    return current, state, manifest, packet


def order(current, state, manifest, packet):
    return build_work_order(CONTRACT, current, state, manifest, packet, "public")


def main() -> None:
    assert validate_contract(CONTRACT) == []
    human = {
        item["station_id"]
        for item in CONTRACT["human_judgment_stations"]
    }
    assert human == {"semantic_bundle_boundary", "translation_quality_audit"}

    args = fixtures()
    assert order(*args)["action"] == "initialize_next_cycle_from_reservation"
    assert order(*args)["station_type"] == "machine"

    current, state, manifest, packet = fixtures()
    for item in (current["ci_train"], state["transport"], manifest["transport"]):
        item["transport_status" if item is current["ci_train"] else "status"] = "not_ready"
    state["stage"] = "private_preparation"
    state["cycle_control"]["status"] = "running"
    state["wave"] = {"queue_status": "open"}
    result = order(current, state, manifest, packet)
    assert result["action"] == "semantic_bundle_boundary"
    assert result["station_type"] == "human"

    state["wave"]["queue_status"] = "sealed"
    assert order(current, state, manifest, packet)["action"] == "advance_to_quality_audit"

    state["stage"] = "private_quality_audit"
    result = order(current, state, manifest, packet)
    assert result["action"] == "translation_quality_audit"
    assert result["station_type"] == "human"

    state["stage"] = "private_encoding"
    assert order(current, state, manifest, packet)["action"] == "encode_recorded_decisions"

    state["stage"] = "translation_frozen"
    for item in (current["ci_train"], state["transport"], manifest["transport"]):
        item["transport_status" if item is current["ci_train"] else "status"] = "awaiting_private_merge"
    assert order(current, state, manifest, packet)["action"] == "verify_phase2_and_merge"

    current, state, manifest, packet = fixtures()
    state["cycle_control"] = {
        "status": "paused",
        "exact_next_action": "rerun failed checker X once",
    }
    result = order(current, state, manifest, packet)
    assert result["action"] == "resume_recorded_checkpoint"
    assert result["recorded_exact_next_action"] == "rerun failed checker X once"

    current, state, manifest, packet = fixtures()
    state["transport"]["status"] = "verified"
    try:
        order(current, state, manifest, packet)
    except FactoryStateError as exc:
        assert exc.code == "factory_state_mismatch"
    else:
        raise AssertionError("transport mismatch must block")

    bad = copy.deepcopy(CONTRACT)
    bad["human_judgment_stations"].append({"station_id": "github_strategy"})
    assert any("exactly" in error for error in validate_contract(bad))

    print("test_translation_factory_controller: OK")


if __name__ == "__main__":
    main()
