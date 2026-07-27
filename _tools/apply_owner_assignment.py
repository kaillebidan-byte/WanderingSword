#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""構造化planから既存owner更新・新規owner作成・集計・証跡を一括生成する。"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
PLAN_PATH = P4 / "OWNER_ASSIGNMENT_PLAN.json"
RESULT_PATH = P4 / "OWNER_ASSIGNMENT_RESULT.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
WORK_PATH = P4 / "CURRENT_WORK.json"
FIELD_SEPARATOR = "\x1f"
DEFAULT_TARGET = "CG表"
DEFAULT_NAMESPACE = "QuestDlgs"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def write_object(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def full_key(target: str, namespace: str, short_key: str) -> str:
    return FIELD_SEPARATOR.join((target, namespace, short_key))


def candidate_keys(candidate: dict[str, Any]) -> tuple[list[str], str, str]:
    source = candidate.get("source") if isinstance(candidate.get("source"), dict) else {}
    target = str(source.get("target") or DEFAULT_TARGET)
    namespace = str(source.get("namespace") or DEFAULT_NAMESPACE)
    rows = candidate.get("rows")
    if not isinstance(rows, list):
        raise ValueError("candidate.rows must be a list")
    keys: list[str] = []
    for index, row in enumerate(rows):
        short = row.get("key") if isinstance(row, dict) else None
        if not isinstance(short, str) or not short:
            raise ValueError(f"candidate.rows[{index}].key must be non-empty")
        if short in keys:
            raise ValueError(f"duplicate candidate key: {short}")
        keys.append(short)
    return keys, target, namespace


def classify_keys(
    keys: list[str],
    owner_map: dict[str, list[str]],
    planned_values: set[str],
    fix_keys: set[str],
    *,
    target: str = DEFAULT_TARGET,
    namespace: str = DEFAULT_NAMESPACE,
) -> dict[str, int]:
    existing = 0
    unowned = 0
    new_keys = 0
    unowned_kept = 0
    for short in keys:
        owners = owner_map.get(full_key(target, namespace, short), [])
        if len(owners) > 1:
            raise ValueError(f"multiple owners for {short}: {owners}")
        if owners:
            existing += 1
        else:
            unowned += 1
            if short in planned_values:
                new_keys += 1
            if short not in fix_keys:
                unowned_kept += 1
    return {
        "existing_keys": existing,
        "unowned_keys": unowned,
        "new_keys": new_keys,
        "unowned_kept": unowned_kept,
    }


def collect_owner_files(p4: Path, excluded: set[str]) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    files: dict[str, dict[str, str]] = {}
    owners: dict[str, list[str]] = {}
    root = p4.parent
    for path in sorted(p4.glob("fixes_*.json")):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        value = load_object(path)
        normalized: dict[str, str] = {}
        for key, text in value.items():
            if not isinstance(key, str) or key.count(FIELD_SEPARATOR) != 2:
                raise ValueError(f"invalid owner key in {rel}: {key!r}")
            if not isinstance(text, str):
                raise ValueError(f"owner value must be string in {rel}: {key!r}")
            normalized[key] = text
            owners.setdefault(key, []).append(rel)
        files[rel] = normalized
    duplicates = {key: paths for key, paths in owners.items() if len(paths) > 1}
    if duplicates:
        raise ValueError(f"existing duplicate owners: {duplicates}")
    return files, owners


def apply_plan(root: Path, plan_path: Path, result_path: Path) -> dict[str, Any]:
    p4 = root / "_phase4_proofread"
    manifest_path = p4 / "CI_TRAIN_MANIFEST.json"
    state_path = p4 / "PRIVATE_STAGE_STATE.json"
    work_path = p4 / "CURRENT_WORK.json"
    plan = load_object(plan_path)
    if plan.get("schema_version") != 1:
        raise ValueError("plan.schema_version must be 1")
    packets = plan.get("packets")
    if not isinstance(packets, list) or not packets:
        raise ValueError("plan.packets must be a non-empty list")

    state = load_object(state_path)
    wave_packets = state.get("wave", {}).get("packets", [])
    current_candidates = [
        item.get("preparation_record", {}).get("candidate_packet")
        for item in wave_packets if isinstance(item, dict)
    ]
    plan_candidates = [item.get("candidate") for item in packets if isinstance(item, dict)]
    if plan_candidates != current_candidates:
        raise ValueError(f"plan candidates must match current wave order: {current_candidates!r}")

    new_owner_paths: set[str] = set()
    for index, packet in enumerate(packets):
        if not isinstance(packet, dict):
            raise ValueError(f"plan.packets[{index}] must be object")
        new_path = packet.get("new_owner_file")
        if not isinstance(new_path, str) or not new_path.startswith("_phase4_proofread/fixes_") or not new_path.endswith(".json"):
            raise ValueError(f"invalid new_owner_file for packet {index}")
        if new_path in new_owner_paths:
            raise ValueError(f"new_owner_file reused: {new_path}")
        new_owner_paths.add(new_path)

    owner_files, owner_map = collect_owner_files(p4, new_owner_paths)
    manifest = load_object(manifest_path)
    bundles = manifest.get("bundles")
    if not isinstance(bundles, list) or len(bundles) != len(packets):
        raise ValueError("manifest bundles must align with plan packets")

    packet_results: list[dict[str, Any]] = []
    all_fix_files: set[str] = set()
    total_existing = 0
    total_new = 0
    total_fixes = 0

    for index, (packet, bundle) in enumerate(zip(packets, bundles)):
        candidate_rel = packet["candidate"]
        candidate_path = root / candidate_rel
        candidate = load_object(candidate_path)
        keys, target, namespace = candidate_keys(candidate)
        values = packet.get("values")
        fix_list = packet.get("fix_keys")
        if not isinstance(values, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in values.items()):
            raise ValueError(f"packet {index} values must be string map")
        if not isinstance(fix_list, list) or any(not isinstance(k, str) for k in fix_list):
            raise ValueError(f"packet {index} fix_keys must be string list")
        key_set = set(keys)
        value_keys = set(values)
        fix_keys = set(fix_list)
        if not value_keys <= key_set:
            raise ValueError(f"packet {index} values contain non-candidate keys: {sorted(value_keys - key_set)}")
        if not fix_keys <= value_keys:
            raise ValueError(f"packet {index} fix_keys must be included in values")

        summary = classify_keys(keys, owner_map, value_keys, fix_keys, target=target, namespace=namespace)
        new_rel = packet["new_owner_file"]
        new_values: dict[str, str] = {}
        touched_fix_files: set[str] = set()
        for short, text in values.items():
            key = full_key(target, namespace, short)
            owners = owner_map.get(key, [])
            if len(owners) > 1:
                raise ValueError(f"multiple owners for {short}: {owners}")
            if owners:
                owner_files[owners[0]][key] = text
                if short in fix_keys:
                    touched_fix_files.add(owners[0])
            else:
                new_values[key] = text
                owner_map[key] = [new_rel]
                if short in fix_keys:
                    touched_fix_files.add(new_rel)
        owner_files[new_rel] = new_values
        all_fix_files.update(touched_fix_files)

        if not isinstance(bundle, dict):
            raise ValueError(f"manifest bundle {index} must be object")
        bundle["fix_keys"] = len(fix_keys)
        bundle["unique_fix_rows"] = len(fix_keys)
        bundle["keep_keys"] = len(keys) - len(fix_keys)
        bundle["new_pair_keys"] = summary["new_keys"]
        bundle["new_project_keys"] = summary["new_keys"]
        bundle["existing_owner_updates"] = summary["existing_keys"]
        bundle["fix_files"] = sorted(touched_fix_files)
        bundle["ownership_summary"] = {
            "existing_keys": summary["existing_keys"],
            "unowned_kept": summary["unowned_kept"],
            "new_keys": summary["new_keys"],
            "cross_register_keys": 0,
        }
        packet_results.append({
            "candidate": candidate_rel,
            "new_owner_file": new_rel,
            "candidate_rows": len(keys),
            "fix_keys": len(fix_keys),
            **summary,
            "fix_files": sorted(touched_fix_files),
        })
        total_existing += summary["existing_keys"]
        total_new += summary["new_keys"]
        total_fixes += len(fix_keys)

    totals = manifest.get("totals")
    if not isinstance(totals, dict):
        raise ValueError("manifest.totals must be object")
    totals["fix_keys"] = total_fixes
    totals["unique_fix_rows"] = total_fixes
    totals["new_pair_keys"] = total_new
    totals["new_project_keys"] = total_new
    totals["existing_owner_updates"] = total_existing

    encoding_summary = state.get("wave", {}).get("encoding_summary")
    if not isinstance(encoding_summary, dict):
        raise ValueError("PRIVATE_STAGE_STATE.wave.encoding_summary must be object")
    encoding_summary["fix_keys"] = total_fixes
    encoding_summary["new_project_keys"] = total_new
    encoding_summary["existing_owner_updates"] = total_existing

    work = load_object(work_path)
    work_totals = work.get("ci_train", {}).get("totals")
    if not isinstance(work_totals, dict):
        raise ValueError("CURRENT_WORK.ci_train.totals must be object")
    work_totals.update({
        "fix_keys": total_fixes,
        "unique_fix_rows": total_fixes,
        "new_pair_keys": total_new,
        "new_project_keys": total_new,
        "existing_owner_updates": total_existing,
    })

    for rel, value in sorted(owner_files.items()):
        write_object(root / rel, dict(sorted(value.items())))
    write_object(manifest_path, manifest)
    write_object(state_path, state)
    write_object(work_path, work)

    owner_hashes = {
        path.relative_to(root).as_posix(): digest_file(path)
        for path in sorted(p4.glob("fixes_*.json"))
    }
    candidate_hashes = {rel: digest_file(root / rel) for rel in plan_candidates}
    result = {
        "schema_version": 1,
        "generated_by": "_tools/apply_owner_assignment.py",
        "plan": plan_path.relative_to(root).as_posix(),
        "plan_digest": digest_file(plan_path),
        "candidate_digests": candidate_hashes,
        "owner_file_digests": owner_hashes,
        "state_file_digests": {
            manifest_path.relative_to(root).as_posix(): digest_file(manifest_path),
            state_path.relative_to(root).as_posix(): digest_file(state_path),
            work_path.relative_to(root).as_posix(): digest_file(work_path),
        },
        "counts": {
            "existing_owner_updates": total_existing,
            "new_project_keys": total_new,
            "fix_keys": total_fixes,
        },
        "packets": packet_results,
    }
    write_object(result_path, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=PLAN_PATH)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = args.plan if args.plan.is_absolute() else ROOT / args.plan
    result = args.result if args.result.is_absolute() else ROOT / args.result
    try:
        value = apply_plan(ROOT, plan, result)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    counts = value["counts"]
    print(
        "OK: owner assignment generated; "
        f"existing={counts['existing_owner_updates']} "
        f"new={counts['new_project_keys']} fixes={counts['fix_keys']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
