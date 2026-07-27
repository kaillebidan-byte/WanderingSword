#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""owner assignment v2: 既存owner所属行と実際の既存owner値更新を分離する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import apply_owner_assignment as legacy

ROOT = legacy.ROOT
P4 = legacy.P4
PLAN_PATH = legacy.PLAN_PATH
RESULT_PATH = legacy.RESULT_PATH


def existing_update_count(
    owner_map: dict[str, list[str]],
    values: set[str],
    fix_keys: set[str],
    *,
    target: str = legacy.DEFAULT_TARGET,
    namespace: str = legacy.DEFAULT_NAMESPACE,
) -> int:
    """planで値を書き込む既存owner keyだけを更新件数として数える。"""
    count = 0
    for short in values:
        owners = owner_map.get(legacy.full_key(target, namespace, short), [])
        if len(owners) > 1:
            raise ValueError(f"multiple owners for {short}: {owners}")
        if owners:
            if short not in fix_keys:
                raise ValueError(
                    f"existing owner value may be written only for a recorded fix: {short}"
                )
            count += 1
    return count


def planned_existing_updates(root: Path, plan: dict[str, Any]) -> list[int]:
    p4 = root / "_phase4_proofread"
    packets = plan.get("packets")
    if not isinstance(packets, list) or not packets:
        raise ValueError("plan.packets must be a non-empty list")
    new_paths: set[str] = set()
    for index, packet in enumerate(packets):
        if not isinstance(packet, dict):
            raise ValueError(f"plan.packets[{index}] must be object")
        new_path = packet.get("new_owner_file")
        if not isinstance(new_path, str):
            raise ValueError(f"plan.packets[{index}].new_owner_file is required")
        new_paths.add(new_path)
    _, owner_map = legacy.collect_owner_files(p4, new_paths)

    result: list[int] = []
    for index, packet in enumerate(packets):
        candidate_rel = packet.get("candidate")
        if not isinstance(candidate_rel, str):
            raise ValueError(f"plan.packets[{index}].candidate is required")
        candidate = legacy.load_object(root / candidate_rel)
        _, target, namespace = legacy.candidate_keys(candidate)
        values = packet.get("values")
        fixes = packet.get("fix_keys")
        if not isinstance(values, dict):
            raise ValueError(f"plan.packets[{index}].values must be object")
        if not isinstance(fixes, list):
            raise ValueError(f"plan.packets[{index}].fix_keys must be list")
        result.append(
            existing_update_count(
                owner_map,
                set(values),
                set(fixes),
                target=target,
                namespace=namespace,
            )
        )
    return result


def apply_plan(root: Path, plan_path: Path, result_path: Path) -> dict[str, Any]:
    plan = legacy.load_object(plan_path)
    update_counts = planned_existing_updates(root, plan)

    legacy.apply_plan(root, plan_path, result_path)
    p4 = root / "_phase4_proofread"
    manifest_path = p4 / "CI_TRAIN_MANIFEST.json"
    state_path = p4 / "PRIVATE_STAGE_STATE.json"
    work_path = p4 / "CURRENT_WORK.json"
    manifest = legacy.load_object(manifest_path)
    state = legacy.load_object(state_path)
    work = legacy.load_object(work_path)

    bundles = manifest.get("bundles")
    if not isinstance(bundles, list) or len(bundles) != len(update_counts):
        raise ValueError("manifest bundles must align with owner assignment plan")
    for bundle, count in zip(bundles, update_counts):
        if not isinstance(bundle, dict):
            raise ValueError("manifest bundle must be object")
        bundle["existing_owner_updates"] = count
    total_updates = sum(update_counts)
    totals = manifest.get("totals")
    encoding_summary = state.get("wave", {}).get("encoding_summary")
    work_totals = work.get("ci_train", {}).get("totals")
    for label, value in (
        ("manifest.totals", totals),
        ("PRIVATE_STAGE_STATE.wave.encoding_summary", encoding_summary),
        ("CURRENT_WORK.ci_train.totals", work_totals),
    ):
        if not isinstance(value, dict):
            raise ValueError(f"{label} must be object")
        value["existing_owner_updates"] = total_updates

    legacy.write_object(manifest_path, manifest)
    legacy.write_object(state_path, state)
    legacy.write_object(work_path, work)

    result = legacy.load_object(result_path)
    result["generated_by"] = "_tools/apply_owner_assignment_v2.py"
    counts = result.get("counts")
    if not isinstance(counts, dict):
        raise ValueError("OWNER_ASSIGNMENT_RESULT.counts must be object")
    counts["existing_owner_updates"] = total_updates
    packet_results = result.get("packets")
    if not isinstance(packet_results, list) or len(packet_results) != len(update_counts):
        raise ValueError("OWNER_ASSIGNMENT_RESULT.packets must align with plan")
    for packet_result, count in zip(packet_results, update_counts):
        if not isinstance(packet_result, dict):
            raise ValueError("OWNER_ASSIGNMENT_RESULT packet must be object")
        packet_result["existing_owner_updates"] = count
    result["state_file_digests"] = {
        manifest_path.relative_to(root).as_posix(): legacy.digest_file(manifest_path),
        state_path.relative_to(root).as_posix(): legacy.digest_file(state_path),
        work_path.relative_to(root).as_posix(): legacy.digest_file(work_path),
    }
    legacy.write_object(result_path, result)
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
        f"existing_updates={counts['existing_owner_updates']} "
        f"new={counts['new_project_keys']} fixes={counts['fix_keys']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
