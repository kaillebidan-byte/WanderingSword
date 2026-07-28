#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""実作業の状態正本、人間向け文書、mode別手順、制度再開キューの陳腐化を検査する。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

TEXT_PATHS = {
    "handoff": P4 / "CURRENT_HANDOFF.md",
    "cold": P4 / "COLD_START_ACCEPTANCE.md",
    "phase1": P4 / "CI_TRAIN_PHASE1.md",
    "phase2": P4 / "CI_TRAIN_PHASE2.md",
    "runbook": P4 / "RUNBOOK_人物ペア再監査.md",
    "public_window": P4 / "PUBLIC_CI_WINDOW.md",
    "readme": ROOT / "README.md",
    "session": P4 / "SESSION_BOOTSTRAP.md",
    "factory": P4 / "FACTORY_FLOW.md",
    "private_stages": P4 / "PRIVATE_TRANSLATION_STAGES.md",
    "always_public": P4 / "ALWAYS_PUBLIC_FULL_PIPELINE.md",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def pending_task(queue: dict[str, Any]) -> dict[str, Any] | None:
    for task in queue.get("tasks", []):
        if isinstance(task, dict) and task.get("status") == "pending":
            return task
    return None


def validate_institution_queue(queue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if queue.get("schema_version") != 1 or queue.get("contract_id") != "resume-work-queue-v1":
        errors.append("institution work queue identity mismatch")
    if queue.get("standard_trigger") != "現状把握して作業の続きを":
        errors.append("institution work queue trigger mismatch")
    if queue.get("required_visibility") != "public":
        errors.append("institution work queue visibility must be public")
    if queue.get("mode_scope") != ["always_public_full_pipeline"]:
        errors.append("institution work queue mode scope mismatch")
    if queue.get("translation_policy") != "blocked_while_institution_tasks_pending":
        errors.append("institution work queue translation policy mismatch")
    order = queue.get("task_order")
    tasks = queue.get("tasks")
    if not isinstance(order, list) or not isinstance(tasks, list):
        return errors + ["institution work queue task order/tasks invalid"]
    ids = [task.get("task_id") for task in tasks if isinstance(task, dict)]
    if ids != order or len(ids) != len(tasks):
        errors.append("institution work queue task order mismatch")
    pending_seen = False
    for task in tasks:
        if not isinstance(task, dict):
            continue
        status = task.get("status")
        if status == "pending":
            pending_seen = True
        elif status == "completed":
            if pending_seen:
                errors.append("institution work queue completed task appears after pending")
            completion = task.get("completion")
            if not isinstance(completion, dict) or not isinstance(completion.get("pr"), int) or completion.get("pr") <= 0:
                errors.append(f"institution completed task lacks PR evidence: {task.get('task_id')}")
            elif completion.get("merge_sha") is not None and (
                not isinstance(completion.get("merge_sha"), str)
                or not SHA_RE.fullmatch(completion["merge_sha"])
            ):
                errors.append(f"institution completed task has invalid optional merge SHA: {task.get('task_id')}")
        else:
            errors.append(f"institution task status invalid: {task.get('task_id')}")

    completion_contract = queue.get("completion_contract")
    if not isinstance(completion_contract, dict):
        errors.append("institution completion contract missing")
    else:
        for key in (
            "task_is_completed_only_in_implementing_pr",
            "completed_entry_requires_pr_number",
            "merge_sha_is_verified_from_github_after_merge",
            "requires_root_cause",
            "requires_permanent_fix",
            "requires_normal_and_failure_regressions",
            "requires_institution_ci",
            "requires_live_checker_success",
            "requires_zero_unresolved_review_threads",
            "requires_squash_merge",
            "requires_main_revalidation",
            "requires_open_pr_triage",
        ):
            if completion_contract.get(key) is not True:
                errors.append(f"institution completion contract flag is not true: {key}")
    return errors


def validate_snapshot(
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    queue: dict[str, Any],
    texts: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    current_transport = current.get("ci_train", {}).get("transport_status")
    state_transport = state.get("transport", {}).get("status")
    manifest_transport = manifest.get("transport", {}).get("status")
    if len({current_transport, state_transport, manifest_transport}) != 1:
        errors.append("transport mismatch across CURRENT_WORK, PRIVATE_STAGE_STATE and manifest")

    pr = manifest.get("transport", {}).get("pr")
    merge_sha = manifest.get("transport", {}).get("merge_sha")
    release = packet.get("release_candidate", {})
    if manifest_transport == "merged":
        if release.get("status") != "merged":
            errors.append("merged transport requires NEXT_TASK_PACKET.release_candidate.status=merged")
        if release.get("merge_sha") != merge_sha:
            errors.append("NEXT_TASK_PACKET merge_sha must match manifest")
        handoff = texts.get("handoff", "")
        for required in (f"PR #{pr}: merged", "transport: `merged`", "cycle: `target_reached / merged`"):
            if required not in handoff:
                errors.append(f"CURRENT_HANDOFF lacks merged fact: {required}")
        for stale in ("open / ready / mergeable", "awaiting_private_merge", "finalize-release phase2"):
            if stale in handoff:
                errors.append(f"CURRENT_HANDOFF contains stale pre-merge text: {stale}")
        for item in packet.get("do_not_do", []):
            if isinstance(item, str) and "統合前" in item:
                errors.append("NEXT_TASK_PACKET retains a pre-merge prohibition after merge")

    errors.extend(validate_institution_queue(queue))
    handoff = texts.get("handoff", "")
    if any(line.startswith("- main:") for line in handoff.splitlines()):
        errors.append("CURRENT_HANDOFF must not pin a stale main commit or PR number")

    mode = current.get("operation_mode", {}).get("execution_mode")
    if mode == "always_public_full_pipeline":
        cold = texts.get("cold", "")
        if "public + `private_translation_work` + `always_public_full_pipeline`" not in cold:
            errors.append("cold-start contract does not allow locked always-public translation stages")
        if "private_translation_work + publicなら、翻訳を開始せずprivate復帰を依頼する" in cold:
            errors.append("cold-start contract retains legacy public=>private rule")
        active = pending_task(queue)
        if active is not None:
            if active.get("task_id") not in handoff:
                errors.append("CURRENT_HANDOFF lacks current institution task")
            if "翻訳cycleを開始しない" not in handoff:
                errors.append("CURRENT_HANDOFF lacks institution-before-translation prohibition")

    required_text = {
        "phase1": "manual public CI窓",
        "phase2": "mode-neutral release",
        "runbook": "post-merge状態専用PRは作らない",
        "public_window": "manual_visibility_cycle専用",
        "readme": "resume_work_controller.py",
        "session": "resume_work_controller.py",
        "factory": "semantic_bundle_boundary",
        "private_stages": "encoding後に上書きしない",
        "always_public": "INSTITUTION_WORK_QUEUE.json",
    }
    for label, needle in required_text.items():
        if needle not in texts.get(label, ""):
            errors.append(f"{label} lacks current contract marker: {needle}")

    for label in ("readme", "session"):
        text = texts.get(label, "")
        for needle in ("INSTITUTION_WORK_QUEUE.json", "translation_factory_controller.py"):
            if needle not in text:
                errors.append(f"{label} lacks resume delegation marker: {needle}")

    for label in ("readme", "session", "factory"):
        text = texts.get(label, "")
        for station in ("semantic_bundle_boundary", "translation_quality_audit"):
            if station not in text:
                errors.append(f"{label} lacks human station marker: {station}")

    for label in ("readme", "session", "always_public"):
        text = texts.get(label, "")
        for needle in ("PR番号", "merge SHA", "GitHub metadata"):
            if needle not in text:
                errors.append(f"{label} lacks feasible institution completion evidence marker: {needle}")

    forbidden = {
        "phase2": ("encoding後にowner snapshotを再生成する", "repository metadataでprivate復帰確認"),
        "runbook": ("post-merge状態PRを作成する", "NEXT_TASK_PACKET.batch_planning"),
        "readme": ("check_handoff_consistency.py --require-verified",),
    }
    for label, needles in forbidden.items():
        for needle in needles:
            if needle in texts.get(label, ""):
                errors.append(f"{label} retains legacy instruction: {needle}")
    return errors


def main() -> int:
    try:
        current = load(P4 / "CURRENT_WORK.json")
        state = load(P4 / "PRIVATE_STAGE_STATE.json")
        manifest = load(P4 / "CI_TRAIN_MANIFEST.json")
        packet = load(P4 / "NEXT_TASK_PACKET.json")
        queue = load(P4 / "INSTITUTION_WORK_QUEUE.json")
        texts = {name: path.read_text(encoding="utf-8") for name, path in TEXT_PATHS.items()}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate_snapshot(current, state, manifest, packet, queue, texts)
    print("=== Operational contract consistency ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: state, handoff, institution queue, reservation, factory flow and mode-specific documents are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
