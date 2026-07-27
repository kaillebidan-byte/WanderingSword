#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""owner assignment生成証跡と現在のowner・候補・状態正本digestを照合する。"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_PATH = P4 / "PRIVATE_TRANSLATION_STAGES.json"
RESULT_PATH = P4 / "OWNER_ASSIGNMENT_RESULT.json"
FIELD_SEPARATOR = "\x1f"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT)}")
    return value


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def required() -> bool:
    contract = load_object(CONTRACT_PATH)
    policy = contract.get("wave_policy", {}).get("owner_assignment")
    return isinstance(policy, dict) and policy.get("result_required_before_translation_frozen") is True


def compare_digest_map(label: str, stored: Any, current: dict[str, str]) -> list[str]:
    if not isinstance(stored, dict):
        return [f"{label} must be object"]
    errors: list[str] = []
    if stored != current:
        missing = sorted(set(current) - set(stored))
        extra = sorted(set(stored) - set(current))
        changed = sorted(key for key in set(current) & set(stored) if current[key] != stored[key])
        errors.append(f"{label} mismatch: missing={missing} extra={extra} changed={changed}")
    return errors


def main() -> int:
    try:
        if not required():
            print("SKIP: owner assignment result is not required by contract")
            return 0
        result = load_object(RESULT_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    errors: list[str] = []
    if result.get("schema_version") != 1:
        errors.append("OWNER_ASSIGNMENT_RESULT.schema_version must be 1")
    if result.get("generated_by") != "_tools/apply_owner_assignment.py":
        errors.append("OWNER_ASSIGNMENT_RESULT.generated_by is invalid")

    plan_rel = result.get("plan")
    if not isinstance(plan_rel, str) or not plan_rel:
        errors.append("OWNER_ASSIGNMENT_RESULT.plan is required")
    else:
        plan_path = ROOT / plan_rel
        if not plan_path.is_file():
            errors.append(f"missing plan: {plan_rel}")
        elif result.get("plan_digest") != digest_file(plan_path):
            errors.append("owner assignment plan digest mismatch")

    candidate_digests = result.get("candidate_digests")
    current_candidates: dict[str, str] = {}
    if isinstance(candidate_digests, dict):
        for rel in candidate_digests:
            if isinstance(rel, str) and (ROOT / rel).is_file():
                current_candidates[rel] = digest_file(ROOT / rel)
            else:
                errors.append(f"missing candidate recorded by owner assignment: {rel!r}")
    errors.extend(compare_digest_map("candidate_digests", candidate_digests, current_candidates))

    current_owners: dict[str, str] = {}
    owner_map: dict[str, list[str]] = {}
    try:
        for path in sorted(P4.glob("fixes_*.json")):
            rel = path.relative_to(ROOT).as_posix()
            current_owners[rel] = digest_file(path)
            value = load_object(path)
            for key in value:
                if isinstance(key, str) and key.count(FIELD_SEPARATOR) == 2:
                    owner_map.setdefault(key, []).append(rel)
                else:
                    errors.append(f"invalid owner key in {rel}: {key!r}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    duplicates = {key: paths for key, paths in owner_map.items() if len(paths) > 1}
    if duplicates:
        errors.append(f"duplicate owner keys after assignment: {duplicates}")
    errors.extend(compare_digest_map("owner_file_digests", result.get("owner_file_digests"), current_owners))

    state_paths = [
        P4 / "CI_TRAIN_MANIFEST.json",
        P4 / "PRIVATE_STAGE_STATE.json",
        P4 / "CURRENT_WORK.json",
    ]
    current_state = {path.relative_to(ROOT).as_posix(): digest_file(path) for path in state_paths}
    errors.extend(compare_digest_map("state_file_digests", result.get("state_file_digests"), current_state))

    counts = result.get("counts")
    if not isinstance(counts, dict):
        errors.append("OWNER_ASSIGNMENT_RESULT.counts must be object")
        counts = {}
    try:
        manifest = load_object(P4 / "CI_TRAIN_MANIFEST.json")
        state = load_object(P4 / "PRIVATE_STAGE_STATE.json")
        work = load_object(P4 / "CURRENT_WORK.json")
        expected = manifest.get("totals", {})
        mirrors = [
            state.get("wave", {}).get("encoding_summary", {}),
            work.get("ci_train", {}).get("totals", {}),
        ]
        for key in ("existing_owner_updates", "new_project_keys", "fix_keys"):
            if counts.get(key) != expected.get(key):
                errors.append(f"result count mismatch for {key}")
            for index, mirror in enumerate(mirrors):
                if mirror.get(key) != expected.get(key):
                    errors.append(f"state mirror {index} mismatch for {key}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED owner assignment attestation: {len(errors)} error(s)")
        return 1
    print("OK: owner assignment plan, owner files, candidate inputs, and state counts are sealed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
