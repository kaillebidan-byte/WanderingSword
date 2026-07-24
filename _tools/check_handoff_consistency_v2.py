#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase2のrelease証跡、冷間再開、監査件数を一つのPR内で整合検査する。"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from check_release_evidence import evidence_path_from_current, validate_evidence

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
HANDOFF_PATH = P4 / "CURRENT_HANDOFF.md"
SESSION_PATH = P4 / "SESSION_BOOTSTRAP.md"
AUDIT_PATH = P4 / "audit_status.json"
README_PATH = ROOT / "README.md"
AGENTS_PATH = ROOT / "AGENTS.md"
EXPECTED_TRIGGER = "現状把握して作業の続きを"
EXPECTED_PROTOCOL = "_phase4_proofread/SESSION_BOOTSTRAP.md"
VALID_CHECKPOINT_STATES = {"verified", "pending_audit_sync"}
VALID_PR_TRIAGE_STATES = {"active", "superseded", "abandoned", "unrelated"}


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


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"required onboarding file missing: {path.relative_to(ROOT)}")
        return ""


def batch_number(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"batch(\d+)", value)
    return int(match.group(1)) if match else None


def check_git_ancestor(label: str, commit: str, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        errors.append(f"{label} must be a 40-character lowercase SHA")
        return
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode == 1:
        errors.append(f"{label} is not an ancestor of HEAD: {commit}")
    elif result.returncode not in (0, 1):
        warnings.append(f"git ancestor check failed for {label}: {result.stderr.strip()}")


def require_bool(mapping: dict[str, Any], key: str, expected: bool, errors: list[str]) -> None:
    if mapping.get(key) is not expected:
        errors.append(f"session_bootstrap.{key} must be {expected!r}")


def validate_checkpoint_and_evidence(
    current: dict[str, Any], evidence: dict[str, Any], *, require_verified: bool
) -> list[str]:
    errors: list[str] = []
    schema = current.get("schema_version")
    if not isinstance(schema, int) or schema < 7:
        errors.append(f"CURRENT_WORK.schema_version must be >= 7 for phase2, got {schema!r}")

    checkpoint = current.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return errors + ["CURRENT_WORK.checkpoint must be an object"]
    status = checkpoint.get("status")
    if status not in VALID_CHECKPOINT_STATES:
        errors.append(f"checkpoint.status must be one of {sorted(VALID_CHECKPOINT_STATES)!r}")
    if require_verified and status != "verified":
        errors.append("verified checkpoint required before merge")

    for key, expected in (
        ("batch", current.get("last_completed_batch")),
        ("pair_applied_keys", current.get("pair_applied_keys")),
        ("project_applied_keys", current.get("project_applied_keys")),
    ):
        if checkpoint.get(key) != expected:
            errors.append(f"checkpoint.{key} mismatch: {checkpoint.get(key)!r} != {expected!r}")

    if "translation_head" in checkpoint or "verified_head" in checkpoint:
        errors.append("phase2 checkpoint must not depend on translation_head/verified_head")

    applied_record = checkpoint.get("applied_record")
    if not isinstance(applied_record, str) or not applied_record:
        errors.append("checkpoint.applied_record must be a repository path")
    if not isinstance(checkpoint.get("produced_by_pr"), int) or checkpoint.get("produced_by_pr") <= 0:
        errors.append("checkpoint.produced_by_pr must be a positive integer")

    errors.extend(validate_evidence(evidence, current))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-verified", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_object(CURRENT_PATH)
    audit = load_object(AUDIT_PATH)
    evidence = load_object(evidence_path_from_current(current))
    errors = validate_checkpoint_and_evidence(current, evidence, require_verified=args.require_verified)
    warnings: list[str] = []

    texts = {
        "README.md": read_text(README_PATH, errors),
        "AGENTS.md": read_text(AGENTS_PATH, errors),
        "CURRENT_HANDOFF.md": read_text(HANDOFF_PATH, errors),
        "SESSION_BOOTSTRAP.md": read_text(SESSION_PATH, errors),
    }

    checkpoint = current.get("checkpoint", {})
    checkpoint_verified = checkpoint.get("status") == "verified"
    applied_record = checkpoint.get("applied_record")
    if isinstance(applied_record, str) and not (ROOT / applied_record).is_file():
        errors.append(f"checkpoint.applied_record does not exist: {applied_record}")

    continuity = current.get("pr_continuity")
    if not isinstance(continuity, dict):
        errors.append("CURRENT_WORK.pr_continuity must be an object")
    else:
        if continuity.get("open_prs_require_triage") is not True:
            errors.append("pr_continuity.open_prs_require_triage must be true")
        states = continuity.get("triage_states")
        if not isinstance(states, list) or set(states) != VALID_PR_TRIAGE_STATES:
            errors.append("pr_continuity.triage_states are incomplete")

    bootstrap = current.get("session_bootstrap")
    if not isinstance(bootstrap, dict):
        errors.append("CURRENT_WORK.session_bootstrap must be an object")
        bootstrap = {}
    if bootstrap.get("protocol") != EXPECTED_PROTOCOL:
        errors.append("session_bootstrap.protocol mismatch")
    if bootstrap.get("trigger_phrase") != EXPECTED_TRIGGER:
        errors.append("session_bootstrap.trigger_phrase mismatch")
    for key, expected in (
        ("same_project_repository_known", True),
        ("ask_repository_again", False),
        ("resume_work_in_same_response", True),
        ("status_only_when_explicitly_requested", True),
        ("open_pr_triage_required", True),
        ("bot_action_required_is_not_failure", True),
        ("merge_requires_verified_checkpoint", True),
        ("next_task_packet_required", True),
    ):
        require_bool(bootstrap, key, expected, errors)

    for label in ("README.md", "CURRENT_HANDOFF.md", "SESSION_BOOTSTRAP.md"):
        text = texts.get(label, "")
        if text and EXPECTED_TRIGGER not in text:
            errors.append(f"{label} does not contain bootstrap trigger phrase")

    session_text = texts.get("SESSION_BOOTSTRAP.md", "")
    for phrase in (
        "未統合PR",
        "GitHub Actions",
        "同じ応答内で実作業",
        "URLや前回作業を聞き直さず",
        "開いているだけで現行作業と決めない",
        "action_required",
        "release evidence",
        "post-merge状態PR",
        "verified",
    ):
        if session_text and phrase not in session_text:
            errors.append(f"SESSION_BOOTSTRAP.md lacks required phrase: {phrase}")

    read_order = current.get("mandatory_read_order")
    required_paths = {
        "README.md",
        "AGENTS.md",
        EXPECTED_PROTOCOL,
        "_phase4_proofread/CI_TRAIN_PHASE2.md",
        "_phase4_proofread/CURRENT_WORK.json",
        "_phase4_proofread/audit_status.json",
    }
    if not isinstance(read_order, list):
        errors.append("CURRENT_WORK.mandatory_read_order must be a list")
    else:
        for path in sorted(required_paths - set(read_order)):
            errors.append(f"mandatory_read_order is missing: {path}")

    current_pair = current.get("current_pair")
    current_cluster = current.get("current_cluster")
    pair_keys = current.get("pair_applied_keys")
    project_keys = current.get("project_applied_keys")
    last_batch = current.get("last_completed_batch")
    audit_current = audit.get("current", {})
    latest_build = audit.get("project", {}).get("latest_build", {})
    pair_status = audit.get("pair_status", {}).get(current_pair, {})

    for message, left, right in (
        ("current pair mismatch", current_pair, audit_current.get("pair")),
        ("current cluster mismatch", current_cluster, audit_current.get("cluster")),
        ("project applied key mismatch", project_keys, latest_build.get("applied_keys")),
        ("pair applied key mismatch", pair_keys, pair_status.get("applied_keys")),
        ("build status mismatch", current.get("build_status"), latest_build.get("status")),
        ("game verification mismatch", current.get("game_verified"), latest_build.get("game_verified")),
    ):
        if left != right:
            target = errors if checkpoint_verified else warnings
            target.append(f"{message}: CURRENT_WORK={left!r}, audit_status={right!r}")

    for label, observed in (
        ("translation_reaudited", batch_number(pair_status.get("translation_reaudited"))),
        ("build_verified", batch_number(pair_status.get("build_verified"))),
    ):
        if observed != last_batch:
            target = errors if checkpoint_verified else warnings
            target.append(f"completed batch mismatch for {label}: {observed!r} != {last_batch!r}")

    record_index = latest_build.get("record_index", [])
    if isinstance(applied_record, str) and applied_record not in record_index:
        target = errors if checkpoint_verified else warnings
        target.append(f"applied record is absent from audit_status.record_index: {applied_record}")

    immediate = current.get("immediate_next")
    if not isinstance(immediate, dict) or not immediate.get("scene_groups") or not immediate.get("task"):
        errors.append("CURRENT_WORK.immediate_next must include scene_groups and task")

    check_git_ancestor("translation_base_commit", current.get("translation_base_commit"), errors, warnings)
    check_git_ancestor("state_base_commit", current.get("state_base_commit"), errors, warnings)

    print("=== Handoff consistency phase2 ===")
    print(f"checkpoint: {checkpoint.get('status')}")
    print(f"release: {checkpoint.get('release_identity', {}).get('release_id')}")
    print(f"checkpoint PR: {checkpoint.get('produced_by_pr')}")
    print(f"pair: {current_pair}")
    print(f"completed batch: {last_batch}")
    print(f"pair keys: {pair_keys}")
    print(f"project keys: {project_keys}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK {'VERIFIED' if checkpoint_verified else 'TRANSITIONAL'}: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
