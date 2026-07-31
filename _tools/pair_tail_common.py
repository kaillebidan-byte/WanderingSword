#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Explicit-reference tail exhaustion shared validation."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
PAIR = "宇文逸↔莫問"
SENTINEL_SCENE = "__PAIR_COMPLETE__"


class TailError(ValueError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TailError(f"top level must be object: {path}")
    return value


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.rstrip() + "\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_json(path: Path, value: dict[str, Any]) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2))


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TailError(f"{label} must be a non-empty string")
    return value.strip()


def require_strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise TailError(f"{label} must be a string list")
    if any(not isinstance(item, str) or not item for item in value):
        raise TailError(f"{label} must be a string list")
    if len(value) != len(set(value)):
        raise TailError(f"{label} contains duplicates")
    return list(value)


def artifact_groups(artifact: dict[str, Any]) -> dict[str, dict[str, Any]]:
    groups = artifact.get("groups")
    if not isinstance(groups, list):
        raise TailError("relation artifact groups must be a list")
    result: dict[str, dict[str, Any]] = {}
    for item in groups:
        family = item.get("family") if isinstance(item, dict) else None
        if isinstance(family, str) and family:
            if family in result:
                raise TailError(f"duplicate artifact family: {family}")
            result[family] = item
    return result


def row_record(group: dict[str, Any], row: dict[str, Any]) -> dict[str, str]:
    return {
        "key": require_text(row.get("key"), "artifact row key"),
        "speaker": str(row.get("speaker") or row.get("ja_speaker") or ""),
        "zh": str(row.get("zh") or ""),
        "ja": str(row.get("ja") or ""),
        "target": require_text(row.get("target") or group.get("target"), "artifact row target"),
        "namespace": require_text(row.get("ns") or group.get("ns"), "artifact row namespace"),
    }


def explicit_reference_rows(artifact: dict[str, Any]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for group in artifact_groups(artifact).values():
        if group.get("kind") != "explicit_reference":
            continue
        rows = group.get("rows")
        if not isinstance(rows, list) or not rows:
            raise TailError(f"explicit_reference group lacks rows: {group.get('family')}")
        for raw in rows:
            if not isinstance(raw, dict):
                raise TailError("artifact row must be an object")
            row = row_record(group, raw)
            if row["key"] in result:
                raise TailError(f"duplicate explicit_reference key: {row['key']}")
            result[row["key"]] = row
    return result


def reviewed_keys(root: Path, candidate_paths: list[str]) -> set[str]:
    result: set[str] = set()
    for relative in candidate_paths:
        path = root / relative
        candidate = load_object(path)
        rows = candidate.get("rows")
        if not isinstance(rows, list) or not rows:
            raise TailError(f"reviewed candidate lacks rows: {relative}")
        for row in rows:
            key = row.get("key") if isinstance(row, dict) else None
            key = require_text(key, f"reviewed candidate key: {relative}")
            if key in result:
                raise TailError(f"reviewed candidate coverage duplicates key: {key}")
            result.add(key)
    return result


def compute_tail(
    artifact: dict[str, Any],
    root: Path,
    candidate_paths: list[str],
) -> tuple[dict[str, dict[str, str]], set[str]]:
    explicit = explicit_reference_rows(artifact)
    reviewed = reviewed_keys(root, candidate_paths)
    unknown = reviewed - set(explicit)
    if unknown:
        raise TailError(f"reviewed candidates contain keys outside current explicit_reference artifact: {sorted(unknown)}")
    return {key: row for key, row in explicit.items() if key not in reviewed}, reviewed


def selected_packet_rows(
    artifact: dict[str, Any],
    packet_groups: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], list[dict[str, str]]]]:
    groups = artifact_groups(artifact)
    selected_keys: set[str] = set()
    result: list[tuple[dict[str, Any], list[dict[str, str]]]] = []
    for index, packet in enumerate(packet_groups):
        if not isinstance(packet, dict):
            raise TailError(f"packet_groups[{index}] must be an object")
        families = require_strings(packet.get("families"), f"packet_groups[{index}].families")
        target = require_text(packet.get("target"), f"packet_groups[{index}].target")
        namespace = require_text(packet.get("namespace"), f"packet_groups[{index}].namespace")
        rows: list[dict[str, str]] = []
        for family in families:
            group = groups.get(family)
            if not isinstance(group, dict) or group.get("kind") != "explicit_reference":
                raise TailError(f"selected tail family is missing or not explicit_reference: {family}")
            raw_rows = group.get("rows")
            if not isinstance(raw_rows, list) or not raw_rows:
                raise TailError(f"selected tail family has no rows: {family}")
            for raw in raw_rows:
                if not isinstance(raw, dict):
                    raise TailError(f"selected family row is invalid: {family}")
                row = row_record(group, raw)
                if row["target"] != target or row["namespace"] != namespace:
                    raise TailError(
                        f"packet target/namespace mismatch for {row['key']}: "
                        f"{row['target']}/{row['namespace']} != {target}/{namespace}"
                    )
                if row["key"] in selected_keys:
                    raise TailError(f"selected tail key is duplicated: {row['key']}")
                selected_keys.add(row["key"])
                rows.append(row)
        result.append((packet, rows))
    return result


def validate_exact_tail(
    artifact: dict[str, Any],
    root: Path,
    candidate_paths: list[str],
    packet_groups: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], list[dict[str, str]]]]:
    tail, reviewed = compute_tail(artifact, root, candidate_paths)
    packets = selected_packet_rows(artifact, packet_groups)
    selected = {row["key"] for _, rows in packets for row in rows}
    if selected != set(tail):
        raise TailError(
            "tail selection must equal exact explicit_reference residual: "
            f"missing={sorted(set(tail) - selected)} extra={sorted(selected - set(tail))}"
        )
    if not 0 < len(selected) < 40:
        raise TailError(f"tail exhaustion requires 1..39 residual rows, observed {len(selected)}")
    return packets
