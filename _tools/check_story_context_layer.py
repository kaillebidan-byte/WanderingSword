#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail-closed validator for the independent story-context preparation layer."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
P4 = Path("_phase4_proofread")
SOURCE = P4 / "source_zh.json"
CONTRACT = Path("_story_context/STORY_CONTEXT_PREPARATION_CONTRACT.json")
STATE = Path("_story_context/STATE.json")
BASELINE = Path("_story_context/PHASE_BASELINE.json")
GATE = Path("_story_context/REFERENCE_GATE.json")
EXPECTED_STAGES = [
    "investigated",
    "contract_ready",
    "candidate_inventory_ready",
    "event_manifest_ready",
    "scene_context_ready",
    "spoiler_context_ready",
    "crosschecked",
    "reference_ready",
]


class StoryContextError(ValueError):
    pass


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StoryContextError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StoryContextError(f"invalid JSON: {path}: {exc}") from exc


def obj(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StoryContextError(f"{label} must be an object")
    return value


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StoryContextError(f"{label} must be a non-empty string")
    return value


def slist(value: Any, label: str, empty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (not empty and not value)
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise StoryContextError(f"{label} must be a string array")
    if len(value) != len(set(value)):
        raise StoryContextError(f"{label} contains duplicates")
    return list(value)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def natural_id(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split("_"))
    except ValueError as exc:
        raise StoryContextError(f"invalid numeric identifier: {value}") from exc


def contract(root: Path) -> dict[str, Any]:
    value = obj(load(root / CONTRACT), "contract")
    if value.get("schema_version") != 1 or value.get("contract_id") != "story-context-preparation-v1":
        raise StoryContextError("contract identity mismatch")
    if value.get("stage_order") != EXPECTED_STAGES:
        raise StoryContextError("stage_order mismatch")
    expected = {
        "root": "_story_context",
        "state": STATE.as_posix(),
        "phase_baseline": BASELINE.as_posix(),
        "reference_gate": GATE.as_posix(),
        "checker": "_tools/check_story_context_layer.py",
        "regression_test": "_tools/test_check_story_context_layer.py",
        "candidate_extractor": "_tools/build_story_context_candidates.py",
        "candidate_regression_test": "_tools/test_build_story_context_candidates.py",
        "contract_workflow": ".github/workflows/story-context-bootstrap.yml",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise StoryContextError(f"contract path mismatch: {key}")
    for key in ("read_only_inputs", "owned_paths", "forbidden_write_prefixes"):
        slist(value.get(key), key)
    slist(value.get("temporary_bootstrap_paths"), "temporary_bootstrap_paths", empty=True)
    schema_map = obj(value.get("schemas"), "schemas")
    if set(schema_map) != {
        "candidate_inventory",
        "event_manifest",
        "scene_context",
        "spoiler_context",
    }:
        raise StoryContextError("schema map mismatch")
    candidate_policy = obj(value.get("candidate_policy"), "candidate_policy")
    if (
        candidate_policy.get("status") != "candidate_only"
        or candidate_policy.get("ordering_declared") is not False
        or candidate_policy.get("formal_reference_allowed") is not False
        or candidate_policy.get("active_event_selected") is not False
        or candidate_policy.get("numeric_proximity_is_not_evidence") is not True
        or candidate_policy.get("manual_event_review_required") is not True
    ):
        raise StoryContextError("candidate policy must remain non-authoritative")
    slist(candidate_policy.get("allowed_link_reasons"), "candidate allowed_link_reasons")
    reference_policy = obj(value.get("reference_policy"), "reference_policy")
    if (
        reference_policy.get("default") != "deny"
        or reference_policy.get("formal_reference_requires_stage") != "reference_ready"
    ):
        raise StoryContextError("reference policy must default deny")
    slist(reference_policy.get("scene_context_forbidden_fields"), "scene spoiler denylist")
    return value


def schemas(root: Path, contract_value: dict[str, Any]) -> None:
    loaded: dict[str, dict[str, Any]] = {}
    for name, relative in contract_value["schemas"].items():
        schema = obj(load(root / relative), name)
        loaded[name] = schema
        if (
            schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("type") != "object"
            or schema.get("additionalProperties") is not False
        ):
            raise StoryContextError(f"invalid closed schema: {name}")
        slist(schema.get("required"), f"{name}.required")
        obj(schema.get("properties"), f"{name}.properties")
    candidate_properties = loaded["candidate_inventory"]["properties"]
    if candidate_properties.get("status", {}).get("const") != "candidate_only":
        raise StoryContextError("candidate schema status mismatch")
    policy_properties = candidate_properties.get("policy", {}).get("properties", {})
    for field in ("ordering_declared", "formal_reference_allowed", "active_event_selected"):
        if policy_properties.get(field, {}).get("const") is not False:
            raise StoryContextError(f"candidate schema must deny {field}")
    if loaded["scene_context"]["properties"].get("layer", {}).get("const") != "scene_time":
        raise StoryContextError("scene layer const mismatch")
    if loaded["spoiler_context"]["properties"].get("layer", {}).get("const") != "full_spoiler":
        raise StoryContextError("spoiler layer const mismatch")
    scene_schema = json.dumps(loaded["scene_context"], ensure_ascii=False)
    for field in contract_value["reference_policy"]["scene_context_forbidden_fields"]:
        if f'"{field}"' in scene_schema:
            raise StoryContextError(f"scene schema contains forbidden spoiler field: {field}")


def baseline(root: Path) -> dict[str, Any]:
    value = obj(load(root / BASELINE), "baseline")
    if value.get("schema_version") != 1:
        raise StoryContextError("baseline schema mismatch")
    authorities = obj(value.get("authority_blobs"), "authority_blobs")
    if len(authorities) < 5:
        raise StoryContextError("authority baseline incomplete")
    for relative, expected_sha in authorities.items():
        if not re.fullmatch(r"[0-9a-f]{40}", str(expected_sha)):
            raise StoryContextError(f"invalid authority blob: {relative}")
        path = root / relative
        if not path.is_file():
            raise StoryContextError(f"authority missing: {relative}")
        actual = git_blob_sha(path)
        if actual != expected_sha:
            raise StoryContextError(f"phase authority changed: {relative}: {actual} != {expected_sha}")
    source = obj(value.get("source_index"), "source_index")
    if source.get("path") != SOURCE.as_posix() or not (root / SOURCE).is_file():
        raise StoryContextError("source index mismatch")
    return value


def state(root: Path, contract_value: dict[str, Any]) -> dict[str, Any]:
    value = obj(load(root / STATE), "state")
    if value.get("schema_version") != 1 or value.get("contract_id") != contract_value["contract_id"]:
        raise StoryContextError("state identity mismatch")
    stage = value.get("current_stage")
    if stage not in EXPECTED_STAGES:
        raise StoryContextError("unknown current stage")
    history = value.get("history")
    if not isinstance(history, list) or not history:
        raise StoryContextError("state history missing")
    indices: list[int] = []
    for index, item in enumerate(history):
        item = obj(item, f"history[{index}]")
        name = item.get("stage")
        if name not in EXPECTED_STAGES:
            raise StoryContextError("unknown history stage")
        text(item.get("date"), "history date")
        text(item.get("evidence"), "history evidence")
        indices.append(EXPECTED_STAGES.index(name))
    if indices[0] != 0 or any(right != left + 1 for left, right in zip(indices, indices[1:])):
        raise StoryContextError("state history must advance one adjacent stage at a time")
    if EXPECTED_STAGES[indices[-1]] != stage:
        raise StoryContextError("current stage/history mismatch")
    ready = stage == "reference_ready"
    if value.get("formal_reference") is not ready:
        raise StoryContextError("formal_reference must be true only at reference_ready")
    event_stage = EXPECTED_STAGES.index(stage) >= EXPECTED_STAGES.index("event_manifest_ready")
    active_event = value.get("active_event")
    if event_stage:
        text(active_event, "active_event")
    elif active_event is not None:
        raise StoryContextError("active_event must remain null before event_manifest_ready")
    for key, mutation in obj(value.get("non_interference"), "non_interference").items():
        if mutation != "none":
            raise StoryContextError(f"non-interference mutation recorded: {key}")
    obj(value.get("artifacts"), "artifacts")
    return value


def changed(root: Path, base: str) -> list[str]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", f"{base}...HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise StoryContextError(
            f"cannot inspect changed files: {getattr(exc, 'output', exc)}"
        ) from exc
    return [line for line in output.splitlines() if line]


def allowed(path: str, contract_value: dict[str, Any]) -> bool:
    return any(
        path.startswith(prefix) if prefix.endswith("/") else path == prefix
        for prefix in contract_value["owned_paths"]
    )


def changed_paths(root: Path, contract_value: dict[str, Any], base: str | None) -> None:
    if not base:
        return
    for path in changed(root, base):
        if any(path.startswith(prefix) for prefix in contract_value["forbidden_write_prefixes"]):
            raise StoryContextError(f"forbidden changed path: {path}")
        if not allowed(path, contract_value):
            raise StoryContextError(f"changed path is outside story-context ownership: {path}")


def stage_at(stage: str, minimum: str) -> bool:
    return EXPECTED_STAGES.index(stage) >= EXPECTED_STAGES.index(minimum)


def artifact(
    root: Path,
    state_value: dict[str, Any],
    name: str,
    minimum: str,
) -> Path | None:
    value = state_value["artifacts"].get(name)
    if stage_at(state_value["current_stage"], minimum):
        if not isinstance(value, str) or not value:
            raise StoryContextError(f"artifact required at {minimum}: {name}")
        path = root / value
        if not path.is_file():
            raise StoryContextError(f"artifact missing: {value}")
        return path
    if value is not None:
        raise StoryContextError(f"artifact recorded before stage: {name}")
    return None


def validate_candidate(
    path: Path,
    root: Path,
    contract_value: dict[str, Any],
    state_value: dict[str, Any],
) -> dict[str, Any]:
    value = obj(load(path), "candidate inventory")
    if (
        value.get("schema_version") != 1
        or value.get("contract_id") != contract_value["contract_id"]
        or value.get("generator_version") != 1
        or value.get("status") != "candidate_only"
    ):
        raise StoryContextError("candidate inventory identity/status mismatch")
    source = obj(value.get("source"), "candidate source")
    source_path = text(source.get("path"), "candidate source.path")
    if source_path != SOURCE.as_posix():
        raise StoryContextError("candidate source path mismatch")
    expected_digest = text(source.get("sha256"), "candidate source.sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        raise StoryContextError("candidate source digest is invalid")
    actual_digest = sha256_file(root / SOURCE)
    if actual_digest != expected_digest:
        raise StoryContextError(
            f"candidate source digest mismatch: {actual_digest} != {expected_digest}"
        )
    source_entries = source.get("entries")
    source_index = obj(load(root / SOURCE), "source index")
    if source_entries != len(source_index):
        raise StoryContextError("candidate source entry count mismatch")

    policy = obj(value.get("policy"), "candidate policy")
    if (
        policy.get("read_only") is not True
        or policy.get("ordering_declared") is not False
        or policy.get("formal_reference_allowed") is not False
        or policy.get("active_event_selected") is not False
        or policy.get("numeric_proximity_is_not_evidence") is not True
        or policy.get("candidate_links_require_manual_event_review") is not True
    ):
        raise StoryContextError("candidate inventory became authoritative")
    allowed_reasons = set(slist(policy.get("allowed_link_reasons"), "candidate link reasons"))
    contract_reasons = set(contract_value["candidate_policy"]["allowed_link_reasons"])
    if allowed_reasons != contract_reasons:
        raise StoryContextError("candidate link reason contract mismatch")

    quests = value.get("quest_groups")
    scenes = value.get("scene_families")
    links = value.get("candidate_links")
    clusters = value.get("duplicate_title_clusters")
    if not isinstance(quests, list) or not quests:
        raise StoryContextError("candidate quest_groups must be non-empty")
    if not isinstance(scenes, list) or not scenes:
        raise StoryContextError("candidate scene_families must be non-empty")
    if not isinstance(links, list):
        raise StoryContextError("candidate_links must be an array")
    if not isinstance(clusters, list):
        raise StoryContextError("duplicate_title_clusters must be an array")

    quest_ids: list[str] = []
    for index, row in enumerate(quests):
        row = obj(row, f"quest_groups[{index}]")
        quest_id = text(row.get("quest_id"), "quest_id")
        natural_id(quest_id)
        if row.get("record_count") is None or not isinstance(row.get("record_count"), int) or row["record_count"] < 1:
            raise StoryContextError("quest record_count must be positive")
        obj(row.get("lifecycle_counts"), "lifecycle_counts")
        text(row.get("first_source_key"), "quest first_source_key")
        text(row.get("last_source_key"), "quest last_source_key")
        text(row.get("record_digest"), "quest record_digest")
        quest_ids.append(quest_id)
    if len(quest_ids) != len(set(quest_ids)):
        raise StoryContextError("duplicate quest_id in candidate inventory")
    if quest_ids != sorted(quest_ids, key=lambda item: int(item)):
        raise StoryContextError("candidate quest_groups are not deterministically sorted")

    scene_ids: list[str] = []
    for index, row in enumerate(scenes):
        row = obj(row, f"scene_families[{index}]")
        family_id = text(row.get("family_id"), "family_id")
        root_id = text(row.get("root_id"), "scene root_id")
        natural_id(family_id)
        natural_id(root_id)
        if family_id.split("_", 1)[0] != root_id:
            raise StoryContextError("scene family/root mismatch")
        if row.get("line_count") is None or not isinstance(row.get("line_count"), int) or row["line_count"] < 1:
            raise StoryContextError("scene line_count must be positive")
        text(row.get("first_source_key"), "scene first_source_key")
        text(row.get("last_source_key"), "scene last_source_key")
        text(row.get("record_digest"), "scene record_digest")
        scene_ids.append(family_id)
    if len(scene_ids) != len(set(scene_ids)):
        raise StoryContextError("duplicate family_id in candidate inventory")
    if scene_ids != sorted(scene_ids, key=natural_id):
        raise StoryContextError("candidate scene_families are not deterministically sorted")

    quest_set = set(quest_ids)
    scene_set = set(scene_ids)
    edge_ids: set[tuple[str, str]] = set()
    forbidden_candidate_fields = {"order", "event_id", "placement_basis", "verified", "status"}
    for index, row in enumerate(links):
        row = obj(row, f"candidate_links[{index}]")
        forbidden = forbidden_candidate_fields.intersection(row)
        if forbidden:
            raise StoryContextError(
                f"candidate link contains authoritative field: {sorted(forbidden)[0]}"
            )
        quest_id = text(row.get("quest_id"), "candidate link quest_id")
        scene_id = text(row.get("scene_family_id"), "candidate link scene_family_id")
        if quest_id not in quest_set or scene_id not in scene_set:
            raise StoryContextError("candidate link references unknown group")
        reasons = set(slist(row.get("reasons"), "candidate link reasons"))
        if not reasons.issubset(allowed_reasons):
            raise StoryContextError("candidate link contains unsupported reason")
        if row.get("candidate_only") is not True or row.get("order_inference_allowed") is not False:
            raise StoryContextError("candidate link permits unsupported order inference")
        edge = (quest_id, scene_id)
        if edge in edge_ids:
            raise StoryContextError("duplicate candidate link")
        edge_ids.add(edge)

    for index, row in enumerate(clusters):
        row = obj(row, f"duplicate_title_clusters[{index}]")
        text(row.get("title"), "duplicate title")
        ids = slist(row.get("quest_ids"), "duplicate title quest_ids")
        if len(ids) < 2 or any(item not in quest_set for item in ids):
            raise StoryContextError("invalid duplicate title cluster")

    summary = obj(value.get("summary"), "candidate summary")
    expected_counts = {
        "quest_group_count": len(quests),
        "scene_family_count": len(scenes),
        "candidate_link_count": len(links),
        "duplicate_title_cluster_count": len(clusters),
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            raise StoryContextError(f"candidate summary mismatch: {key}")
    text(value.get("next_action"), "candidate next_action")
    return value


def source_keys(root: Path) -> set[str]:
    return set(obj(load(root / SOURCE), "source index"))


def existing(value: Any, known: set[str], label: str) -> list[str]:
    keys = slist(value, label)
    missing = [key for key in keys if key not in known]
    if missing:
        raise StoryContextError(f"unknown source key in {label}: {missing[0]}")
    return keys


def order(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise StoryContextError(f"{label} must be non-empty")
    rows = [obj(item, label) for item in value]
    if [row.get("order") for row in rows] != list(range(1, len(rows) + 1)):
        raise StoryContextError(f"{label} order must be contiguous")
    return rows


def validate_manifest(path: Path, state_value: dict[str, Any], known: set[str]) -> dict[str, Any]:
    value = obj(load(path), "manifest")
    if (
        value.get("schema_version") != 1
        or value.get("status") != "verified"
        or value.get("event_id") != state_value.get("active_event")
    ):
        raise StoryContextError("manifest identity/status mismatch")
    all_keys = set(existing(value.get("source_keys"), known, "manifest source_keys"))
    collected: set[str] = set()
    for row in order(value.get("quest_lifecycle"), "quest lifecycle"):
        if row.get("phase") not in {"request", "processed", "option", "finishing", "other"}:
            raise StoryContextError("invalid quest phase")
        collected.update(existing(row.get("source_keys"), known, "quest lifecycle source_keys"))
    seen: set[str] = set()
    for row in order(value.get("scenes"), "manifest scenes"):
        scene_id = text(row.get("scene_id"), "scene_id")
        if scene_id in seen:
            raise StoryContextError(f"duplicate scene_id: {scene_id}")
        seen.add(scene_id)
        text(row.get("family"), "family")
        slist(row.get("placement_basis"), "placement_basis")
        collected.update(existing(row.get("source_keys"), known, "scene source_keys"))
    if not collected.issubset(all_keys):
        raise StoryContextError("manifest aggregate source_keys omits child keys")
    return value


def forbidden(value: Any, names: set[str], path: str = "") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{path}.{key}" if path else key
            if key in names:
                return here
            hit = forbidden(child, names, here)
            if hit:
                return hit
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hit = forbidden(child, names, f"{path}[{index}]")
            if hit:
                return hit
    return None


def validate_scene(
    path: Path,
    manifest: dict[str, Any],
    contract_value: dict[str, Any],
    known: set[str],
) -> dict[str, Any]:
    value = obj(load(path), "scene context")
    if (
        value.get("schema_version") != 1
        or value.get("layer") != "scene_time"
        or value.get("event_id") != manifest["event_id"]
    ):
        raise StoryContextError("scene context identity mismatch")
    hit = forbidden(value, set(contract_value["reference_policy"]["scene_context_forbidden_fields"]))
    if hit:
        raise StoryContextError(f"scene context contains spoiler field: {hit}")
    rows = order(value.get("scenes"), "scene context scenes")
    if [row.get("scene_id") for row in rows] != [
        row.get("scene_id") for row in manifest["scenes"]
    ]:
        raise StoryContextError("scene context order does not match manifest")
    collected: set[str] = set()
    for row in rows:
        for key in (
            "player_knowledge_before",
            "player_knowledge_after",
            "beliefs_and_misunderstandings",
            "uncertainties",
        ):
            slist(row.get(key), key, empty=True)
        obj(row.get("character_knowledge"), "character_knowledge")
        collected.update(existing(row.get("source_keys"), known, "scene context source_keys"))
    aggregate = set(existing(value.get("source_keys"), known, "scene context aggregate keys"))
    if not collected.issubset(aggregate):
        raise StoryContextError("scene context aggregate source_keys omits child keys")
    return value


def validate_spoiler(
    path: Path,
    manifest: dict[str, Any],
    known: set[str],
) -> dict[str, Any]:
    value = obj(load(path), "spoiler context")
    if (
        value.get("schema_version") != 1
        or value.get("layer") != "full_spoiler"
        or value.get("event_id") != manifest["event_id"]
    ):
        raise StoryContextError("spoiler context identity mismatch")
    truths = value.get("truths")
    if not isinstance(truths, list) or not truths:
        raise StoryContextError("spoiler truths must be non-empty")
    truth_ids: set[str] = set()
    collected: set[str] = set()
    for row in truths:
        row = obj(row, "truth")
        truth_id = text(row.get("truth_id"), "truth_id")
        if truth_id in truth_ids:
            raise StoryContextError(f"duplicate truth_id: {truth_id}")
        truth_ids.add(truth_id)
        text(row.get("statement"), "statement")
        collected.update(existing(row.get("source_keys"), known, "truth source_keys"))
    scenes = {row["scene_id"] for row in manifest["scenes"]}
    for row in order(value.get("reveal_order"), "reveal_order"):
        if row.get("truth_id") not in truth_ids or row.get("scene_id") not in scenes:
            raise StoryContextError("reveal_order reference mismatch")
        if row.get("reveal_kind") not in {
            "hint",
            "partial",
            "apparent",
            "confirmed",
            "recontextualized",
        }:
            raise StoryContextError("invalid reveal_kind")
        collected.update(existing(row.get("source_keys"), known, "reveal source_keys"))
    aggregate = set(existing(value.get("source_keys"), known, "spoiler aggregate keys"))
    if not collected.issubset(aggregate):
        raise StoryContextError("spoiler aggregate source_keys omits child keys")
    return value


def validate_cross(path: Path, event: str) -> dict[str, Any]:
    value = obj(load(path), "crosscheck")
    if (
        value.get("schema_version") != 1
        or value.get("event_id") != event
        or value.get("later_development_checked") is not True
    ):
        raise StoryContextError("later development check is incomplete")
    if value.get("unresolved_conflicts") != []:
        raise StoryContextError("unresolved crosscheck conflicts remain")
    checks = obj(value.get("checks"), "checks")
    for key in (
        "source_keys_verified",
        "scene_spoiler_separation_verified",
        "event_order_verified",
    ):
        if checks.get(key) is not True:
            raise StoryContextError(f"crosscheck failed: {key}")
    return value


def gate(
    root: Path,
    contract_value: dict[str, Any],
    state_value: dict[str, Any],
    crosscheck: dict[str, Any] | None,
) -> None:
    value = obj(load(root / GATE), "gate")
    ready = state_value["current_stage"] == "reference_ready"
    if value.get("schema_version") != 1 or value.get("contract_id") != contract_value["contract_id"]:
        raise StoryContextError("reference gate identity mismatch")
    expected_status = "open" if ready else "closed"
    if value.get("status") != expected_status:
        raise StoryContextError(f"reference gate must be {expected_status}")
    if value.get("formal_reference_allowed") is not ready:
        raise StoryContextError("reference gate flag mismatch")
    consumers = obj(value.get("consumer_policy"), "consumer_policy")
    for key in (
        "proofreading_may_reference",
        "translation_factory_may_reference",
        "chapter_readthrough_may_reference",
    ):
        if consumers.get(key) is not ready:
            raise StoryContextError(f"consumer gate mismatch: {key}")
    if ready and crosscheck is None:
        raise StoryContextError("reference gate cannot open without crosscheck")


def validate_root(root: Path, base_ref: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    contract_value = contract(root)
    schemas(root, contract_value)
    baseline_value = baseline(root)
    state_value = state(root, contract_value)
    changed_paths(root, contract_value, base_ref)

    candidate_path = artifact(root, state_value, "candidate_inventory", "candidate_inventory_ready")
    manifest_path = artifact(root, state_value, "event_manifest", "event_manifest_ready")
    scene_path = artifact(root, state_value, "scene_context", "scene_context_ready")
    spoiler_path = artifact(root, state_value, "spoiler_context", "spoiler_context_ready")
    cross_path = artifact(root, state_value, "crosscheck", "crosschecked")

    candidate = manifest = scene = spoiler = crosscheck = None
    known: set[str] | None = None
    if candidate_path:
        candidate = validate_candidate(candidate_path, root, contract_value, state_value)
    if manifest_path:
        known = source_keys(root)
        manifest = validate_manifest(manifest_path, state_value, known)
    if scene_path:
        scene = validate_scene(scene_path, manifest, contract_value, known)
    if spoiler_path:
        spoiler = validate_spoiler(spoiler_path, manifest, known)
    if cross_path:
        crosscheck = validate_cross(cross_path, manifest["event_id"])

    gate(root, contract_value, state_value, crosscheck)
    result = {
        "status": "ok",
        "contract_id": contract_value["contract_id"],
        "current_stage": state_value["current_stage"],
        "formal_reference": state_value["formal_reference"],
        "phase_authorities": len(baseline_value["authority_blobs"]),
        "active_event": state_value.get("active_event"),
    }
    if candidate:
        result["candidate_summary"] = candidate["summary"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base-ref")
    args = parser.parse_args()
    try:
        result = validate_root(args.root, args.base_ref)
    except (OSError, StoryContextError) as exc:
        print(json.dumps({"status": "blocked", "detail": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
