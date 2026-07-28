#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定型再開文を制度改修または翻訳factoryの一意なwork orderへ変換する。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import translation_factory_controller as translation

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
QUEUE_PATH = P4 / "INSTITUTION_WORK_QUEUE.json"
CONTRACT_PATH = P4 / "FACTORY_FLOW_CONTRACT.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
PACKET_PATH = P4 / "NEXT_TASK_PACKET.json"

EXPECTED_CONTRACT_ID = "resume-work-queue-v1"
EXPECTED_TRIGGER = "現状把握して作業の続きを"
EXPECTED_POLICY = "blocked_while_institution_tasks_pending"
EXPECTED_SELECTION = "first_pending_in_task_order"
VALID_STATUSES = {"pending", "completed"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ResumeStateError(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ResumeStateError("resume_invalid_json_shape", f"top level must be object: {path}")
    return value


def validate_queue(queue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if queue.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if queue.get("contract_id") != EXPECTED_CONTRACT_ID:
        errors.append("contract_id mismatch")
    if queue.get("standard_trigger") != EXPECTED_TRIGGER:
        errors.append("standard_trigger mismatch")
    if queue.get("required_visibility") != "public":
        errors.append("required_visibility must be public")
    if queue.get("mode_scope") != ["always_public_full_pipeline"]:
        errors.append("mode_scope must contain only always_public_full_pipeline")
    if queue.get("translation_policy") != EXPECTED_POLICY:
        errors.append("translation_policy mismatch")
    if queue.get("selection_policy") != EXPECTED_SELECTION:
        errors.append("selection_policy mismatch")

    order = queue.get("task_order")
    tasks = queue.get("tasks")
    if not isinstance(order, list) or any(not isinstance(item, str) or not item for item in order):
        errors.append("task_order must be a non-empty string list")
        order = []
    elif len(order) != len(set(order)):
        errors.append("task_order contains duplicates")
    if not isinstance(tasks, list):
        errors.append("tasks must be a list")
        tasks = []

    task_ids: list[str] = []
    pending_seen = False
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"tasks[{index}] must be an object")
            continue
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"tasks[{index}].task_id is required")
            continue
        task_ids.append(task_id)
        status = task.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"tasks[{index}].status is invalid")
        if not isinstance(task.get("priority"), int) or task.get("priority") != index + 1:
            errors.append(f"tasks[{index}].priority must equal {index + 1}")
        for field in ("title", "branch", "summary"):
            if not isinstance(task.get(field), str) or not task.get(field):
                errors.append(f"tasks[{index}].{field} is required")
        if status == "pending":
            pending_seen = True
            if "completion" in task:
                errors.append(f"pending task must not contain completion: {task_id}")
            for field in ("audit_scope", "completion_conditions", "forbidden"):
                values = task.get(field)
                if not isinstance(values, list) or not values or any(
                    not isinstance(item, str) or not item for item in values
                ):
                    errors.append(f"pending task {task_id}.{field} must be a non-empty string list")
        elif status == "completed":
            if pending_seen:
                errors.append(f"completed task appears after pending task: {task_id}")
            completion = task.get("completion")
            if not isinstance(completion, dict):
                errors.append(f"completed task requires completion object: {task_id}")
            else:
                if not isinstance(completion.get("pr"), int) or completion.get("pr") <= 0:
                    errors.append(f"completed task completion.pr is invalid: {task_id}")
                merge_sha = completion.get("merge_sha")
                if merge_sha is not None and (
                    not isinstance(merge_sha, str) or not SHA_RE.fullmatch(merge_sha)
                ):
                    errors.append(f"completed task completion.merge_sha is invalid: {task_id}")

    if task_ids != order:
        errors.append("task_order must exactly match tasks order")

    completion = queue.get("completion_contract")
    if not isinstance(completion, dict):
        errors.append("completion_contract must be an object")
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
            if completion.get(key) is not True:
                errors.append(f"completion_contract.{key} must be true")
    return errors


def first_pending_task(queue: dict[str, Any]) -> dict[str, Any] | None:
    for task in queue.get("tasks", []):
        if isinstance(task, dict) and task.get("status") == "pending":
            return task
    return None


def build_resume_work_order(
    queue: dict[str, Any],
    translation_contract: dict[str, Any],
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    repository_visibility: str,
) -> dict[str, Any]:
    errors = validate_queue(queue)
    if errors:
        raise ResumeStateError("resume_queue_invalid", "; ".join(errors))
    translation_errors = translation.validate_contract(translation_contract)
    if translation_errors:
        raise ResumeStateError("factory_contract_invalid", "; ".join(translation_errors))
    if repository_visibility not in translation.VALID_VISIBILITIES:
        raise ResumeStateError("resume_invalid_visibility", repository_visibility)

    pending = first_pending_task(queue)
    mode = current.get("operation_mode", {}).get("execution_mode")
    if pending is not None:
        if mode not in queue["mode_scope"]:
            raise ResumeStateError(
                "resume_institution_mode_mismatch",
                f"pending institution task requires mode {queue['mode_scope']!r}, got {mode!r}",
            )
        if repository_visibility != queue["required_visibility"]:
            raise ResumeStateError(
                "resume_institution_visibility_mismatch",
                f"pending institution task requires visibility {queue['required_visibility']!r}",
            )
        return {
            "schema_version": 1,
            "controller": "_tools/resume_work_controller.py",
            "route": "institution_repair",
            "action": "execute_institution_task",
            "repository_visibility": repository_visibility,
            "execution_mode": mode,
            "standard_trigger": queue["standard_trigger"],
            "queue": "_phase4_proofread/INSTITUTION_WORK_QUEUE.json",
            "task_id": pending["task_id"],
            "title": pending["title"],
            "branch": pending["branch"],
            "reason": "always-public mode prioritizes the first pending institution task before translation",
            "translation_cycle_allowed": False,
            "task": {
                "summary": pending["summary"],
                "audit_scope": pending["audit_scope"],
                "completion_conditions": pending["completion_conditions"],
                "forbidden": pending["forbidden"],
            },
            "completion_update": {
                "set_current_task_status": "completed",
                "record_pr_number_in_implementing_pr": True,
                "verify_merge_sha_from_github_after_merge": True,
                "preserve_remaining_task_order": True,
                "apply_in_same_implementing_pr": True,
                "contract": queue["completion_contract"],
            },
            "worker_rule": (
                "GitHubの最新main、open PR、Actionsを再取得し、既存実装を監査して未解消部分だけを直す。"
                "PR作成後に同じPR内でtaskをcompletedへ更新しPR番号を記録する。"
                "squash merge後はGitHub metadataでmerge SHAを検証し、main再検証まで翻訳cycleへ進まない。"
            ),
        }

    delegated = translation.build_work_order(
        translation_contract,
        current,
        state,
        manifest,
        packet,
        repository_visibility,
    )
    return {
        "schema_version": 1,
        "controller": "_tools/resume_work_controller.py",
        "route": "translation_factory",
        "action": delegated["action"],
        "repository_visibility": repository_visibility,
        "execution_mode": mode,
        "standard_trigger": queue["standard_trigger"],
        "queue": "_phase4_proofread/INSTITUTION_WORK_QUEUE.json",
        "translation_cycle_allowed": True,
        "delegated_work_order": delegated,
        "worker_rule": "制度改修キューが空なので、delegated_work_orderの一つのactionだけを実行する。",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-visibility", choices=sorted(translation.VALID_VISIBILITIES), required=True)
    parser.add_argument("--validate-contract-only", action="store_true")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        queue = load_object(QUEUE_PATH)
        translation_contract = load_object(CONTRACT_PATH)
        errors = [*validate_queue(queue), *translation.validate_contract(translation_contract)]
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        if args.validate_contract_only:
            print("OK: resume work queue and translation factory contract are valid")
            return 0
        work_order = build_resume_work_order(
            queue,
            translation_contract,
            load_object(CURRENT_PATH),
            load_object(STATE_PATH),
            load_object(MANIFEST_PATH),
            load_object(PACKET_PATH),
            args.repository_visibility,
        )
    except (OSError, json.JSONDecodeError, ResumeStateError, translation.FactoryStateError) as exc:
        code = getattr(exc, "code", "resume_input_error")
        detail = getattr(exc, "detail", str(exc))
        print(json.dumps({"status": "blocked", "error_code": code, "detail": detail}, ensure_ascii=False))
        return 1

    text = json.dumps(work_order, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
