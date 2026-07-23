#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新チャット再開プロトコルと監査状態の整合を検査する。"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
HANDOFF_PATH = P4 / "CURRENT_HANDOFF.md"
SESSION_PATH = P4 / "SESSION_BOOTSTRAP.md"
AUDIT_PATH = P4 / "audit_status.json"
TODO_PATH = P4 / "_TODO.md"
README_PATH = ROOT / "README.md"
AGENTS_PATH = ROOT / "AGENTS.md"
EXPECTED_TRIGGER = "現状把握して作業の続きを"
EXPECTED_PROTOCOL = "_phase4_proofread/SESSION_BOOTSTRAP.md"


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as fp:
            value = json.load(fp)
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: required file not found: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top-level JSON must be an object: {path.relative_to(ROOT)}")
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
    if not commit:
        errors.append(f"CURRENT_WORK.{label} is empty")
        return
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except OSError as exc:
        warnings.append(f"git ancestor check skipped for {label}: {exc}")
        return
    if result.returncode == 1:
        errors.append(f"{label} is not an ancestor of HEAD: {commit}")
    elif result.returncode not in (0, 1):
        warnings.append(f"git ancestor check failed for {label}: {result.stderr.strip()}")


def require_bool(
    mapping: dict[str, Any], key: str, expected: bool, errors: list[str]
) -> None:
    observed = mapping.get(key)
    if observed is not expected:
        errors.append(f"session_bootstrap.{key} must be {expected!r}, got {observed!r}")


def main() -> int:
    current = load_json(CURRENT_PATH)
    audit = load_json(AUDIT_PATH)
    errors: list[str] = []
    warnings: list[str] = []

    texts = {
        "README.md": read_text(README_PATH, errors),
        "AGENTS.md": read_text(AGENTS_PATH, errors),
        "CURRENT_HANDOFF.md": read_text(HANDOFF_PATH, errors),
        "SESSION_BOOTSTRAP.md": read_text(SESSION_PATH, errors),
    }

    schema_version = current.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 2:
        errors.append(f"CURRENT_WORK.schema_version must be >= 2, got {schema_version!r}")

    bootstrap = current.get("session_bootstrap")
    if not isinstance(bootstrap, dict):
        errors.append("CURRENT_WORK.session_bootstrap must be an object")
        bootstrap = {}

    if bootstrap.get("protocol") != EXPECTED_PROTOCOL:
        errors.append(
            f"session_bootstrap.protocol mismatch: {bootstrap.get('protocol')!r} != {EXPECTED_PROTOCOL!r}"
        )
    if bootstrap.get("trigger_phrase") != EXPECTED_TRIGGER:
        errors.append(
            f"session_bootstrap.trigger_phrase mismatch: {bootstrap.get('trigger_phrase')!r} != {EXPECTED_TRIGGER!r}"
        )

    require_bool(bootstrap, "same_project_repository_known", True, errors)
    require_bool(bootstrap, "ask_repository_again", False, errors)
    require_bool(bootstrap, "resume_work_in_same_response", True, errors)
    require_bool(bootstrap, "status_only_when_explicitly_requested", True, errors)

    for label in ("README.md", "CURRENT_HANDOFF.md", "SESSION_BOOTSTRAP.md"):
        text = texts.get(label, "")
        if text and EXPECTED_TRIGGER not in text:
            errors.append(f"{label} does not contain the bootstrap trigger phrase")

    session_text = texts.get("SESSION_BOOTSTRAP.md", "")
    for required_phrase in (
        "未統合PR",
        "GitHub Actions",
        "同じ応答内で実作業",
        "URLや前回作業を聞き直さず",
    ):
        if session_text and required_phrase not in session_text:
            errors.append(f"SESSION_BOOTSTRAP.md lacks required contract phrase: {required_phrase}")

    read_order = current.get("mandatory_read_order")
    if not isinstance(read_order, list):
        errors.append("CURRENT_WORK.mandatory_read_order must be a list")
    else:
        for required_path in (
            "README.md",
            "AGENTS.md",
            EXPECTED_PROTOCOL,
            "_phase4_proofread/CURRENT_WORK.json",
            "_phase4_proofread/audit_status.json",
        ):
            if required_path not in read_order:
                errors.append(f"mandatory_read_order is missing: {required_path}")

    current_pair = current.get("current_pair")
    audit_current = audit.get("current", {})
    if current_pair != audit_current.get("pair"):
        errors.append(
            f"current pair mismatch: CURRENT_WORK={current_pair!r}, "
            f"audit_status={audit_current.get('pair')!r}"
        )

    current_cluster = current.get("current_cluster")
    if current_cluster != audit_current.get("cluster"):
        errors.append(
            f"current cluster mismatch: CURRENT_WORK={current_cluster!r}, "
            f"audit_status={audit_current.get('cluster')!r}"
        )

    latest_build = audit.get("project", {}).get("latest_build", {})
    project_keys = current.get("project_applied_keys")
    if project_keys != latest_build.get("applied_keys"):
        errors.append(
            f"project applied key mismatch: CURRENT_WORK={project_keys!r}, "
            f"audit_status={latest_build.get('applied_keys')!r}"
        )

    pair_status = audit.get("pair_status", {}).get(current_pair, {})
    pair_keys = current.get("pair_applied_keys")
    if pair_keys != pair_status.get("applied_keys"):
        errors.append(
            f"pair applied key mismatch: CURRENT_WORK={pair_keys!r}, "
            f"audit_status={pair_status.get('applied_keys')!r}"
        )

    last_batch = current.get("last_completed_batch")
    translation_batch = batch_number(pair_status.get("translation_reaudited"))
    build_batch = batch_number(pair_status.get("build_verified"))
    for label, observed in (
        ("translation_reaudited", translation_batch),
        ("build_verified", build_batch),
    ):
        if observed is None:
            errors.append(f"audit_status pair field has no batch number: {label}")
        elif observed != last_batch:
            errors.append(
                f"completed batch mismatch for {label}: CURRENT_WORK={last_batch!r}, "
                f"audit_status={observed!r}"
            )

    record_token = current.get("applied_record_batch_token")
    if not isinstance(record_token, str) or not record_token:
        errors.append("CURRENT_WORK.applied_record_batch_token must be a non-empty string")
    else:
        record_index = latest_build.get("record_index", [])
        expected_record = f"{record_token}{last_batch}_"
        if not any(expected_record in str(path) for path in record_index):
            errors.append(
                "latest applied record is absent from audit_status.record_index: "
                f"{expected_record}"
            )

    immediate = current.get("immediate_next", {})
    if not isinstance(immediate, dict) or not immediate.get("scene_groups") or not immediate.get("task"):
        errors.append("CURRENT_WORK.immediate_next must include scene_groups and task")

    if current.get("build_status") != latest_build.get("status"):
        errors.append(
            f"build status mismatch: CURRENT_WORK={current.get('build_status')!r}, "
            f"audit_status={latest_build.get('status')!r}"
        )
    if current.get("game_verified") != latest_build.get("game_verified"):
        errors.append(
            f"game verification mismatch: CURRENT_WORK={current.get('game_verified')!r}, "
            f"audit_status={latest_build.get('game_verified')!r}"
        )

    check_git_ancestor(
        "translation_base_commit",
        str(current.get("translation_base_commit", "")),
        errors,
        warnings,
    )
    check_git_ancestor(
        "state_base_commit",
        str(current.get("state_base_commit", "")),
        errors,
        warnings,
    )

    audit_next = audit_current.get("next_action")
    current_next = immediate.get("task") if isinstance(immediate, dict) else None
    if audit_next and current_next and audit_next != current_next:
        warnings.append(
            "audit_status.current.next_action differs from CURRENT_WORK.immediate_next.task; "
            "README defines CURRENT_WORK as the immediate-work source"
        )

    try:
        todo_text = TODO_PATH.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        warnings.append("_TODO.md not found")
    else:
        pair_line = next(
            (line for line in todo_text.splitlines() if line.startswith(f"- [ ] **{current_pair}**")),
            "",
        )
        match = re.search(r"計(\d+)キー", pair_line)
        if match and int(match.group(1)) != pair_keys:
            warnings.append(
                f"_TODO.md has stale {current_pair} count: {match.group(1)} != {pair_keys}; "
                "use CURRENT_WORK/audit_status for current counts"
            )

    print("=== Handoff consistency ===")
    print(f"trigger: {bootstrap.get('trigger_phrase')}")
    print(f"protocol: {bootstrap.get('protocol')}")
    print(f"resume in same response: {bootstrap.get('resume_work_in_same_response')}")
    print(f"pair: {current_pair}")
    print(f"completed batch: {last_batch}")
    print(f"pair keys: {pair_keys}")
    print(f"project keys: {project_keys}")
    scenes = immediate.get("scene_groups", []) if isinstance(immediate, dict) else []
    print(f"next scenes: {', '.join(map(str, scenes))}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
