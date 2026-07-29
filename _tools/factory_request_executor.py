#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""translation factory requestを、controllerが許可した固定adapterだけで実行する。"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from fixed_cycle_initializer import InitializerError, initialize_with_semantic_boundary
from translation_factory_controller import FactoryStateError, build_work_order, validate_contract

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
PACKET_PATH = P4 / "NEXT_TASK_PACKET.json"
HANDOFF_PATH = P4 / "CURRENT_HANDOFF.md"
FLOW_CONTRACT_PATH = P4 / "FACTORY_FLOW_CONTRACT.json"
EXECUTION_MODES_PATH = P4 / "EXECUTION_MODES.json"
REQUEST_CONTRACT_PATH = P4 / "FACTORY_REQUEST_CONTRACT.json"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return value


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def _relative_repo_path(path: Path, root: Path) -> str:
    candidate = path
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"path is outside repository: {path}") from exc
    if ".." in candidate.parts:
        raise ValueError(f"path escapes repository: {path}")
    return candidate.as_posix()


def execution_written_paths(path: Path) -> list[str]:
    value = load_object(path)
    paths = value.get("written_paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("execution result must contain non-empty written_paths")
    if any(not isinstance(item, str) or not item or Path(item).is_absolute() or ".." in Path(item).parts for item in paths):
        raise ValueError("execution result written_paths contains invalid repository path")
    return sorted(set(paths))


def classify_branch_update(local_parent: str, remote_head: str, differing_paths: list[str]) -> str:
    if remote_head == local_parent:
        return "ready_to_push"
    if not differing_paths:
        return "already_applied"
    return "conflict"


def reconcile_remote_branch(
    remote_ref: str,
    request_path: Path,
    execution_result: Path,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    local_head = _git(root, "rev-parse", "HEAD")
    local_parent = _git(root, "rev-parse", "HEAD^")
    remote_head = _git(root, "rev-parse", remote_ref)
    scope = sorted(
        set(
            [
                *execution_written_paths(execution_result),
                _relative_repo_path(request_path, root),
            ]
        )
    )
    differing_output = _git(root, "diff", "--name-only", "HEAD", remote_ref, "--", *scope)
    differing_paths = [line for line in differing_output.splitlines() if line]
    status = classify_branch_update(local_parent, remote_head, differing_paths)
    return {
        "status": status,
        "local_head": local_head,
        "local_parent": local_parent,
        "remote_head": remote_head,
        "scope": scope,
        "differing_paths": differing_paths,
    }


def execute(
    request: dict[str, Any],
    artifact: dict[str, Any],
    repository_visibility: str,
    *,
    base_commit: str | None = None,
    branch_name: str | None = None,
    p4: Path = P4,
) -> dict[str, Any]:
    current = load_object(CURRENT_PATH if p4 == P4 else p4 / "CURRENT_WORK.json")
    state = load_object(STATE_PATH if p4 == P4 else p4 / "PRIVATE_STAGE_STATE.json")
    manifest = load_object(MANIFEST_PATH if p4 == P4 else p4 / "CI_TRAIN_MANIFEST.json")
    packet = load_object(PACKET_PATH if p4 == P4 else p4 / "NEXT_TASK_PACKET.json")
    flow = load_object(FLOW_CONTRACT_PATH if p4 == P4 else p4 / "FACTORY_FLOW_CONTRACT.json")
    execution_modes = load_object(EXECUTION_MODES_PATH if p4 == P4 else p4 / "EXECUTION_MODES.json")
    request_contract = load_object(REQUEST_CONTRACT_PATH if p4 == P4 else p4 / "FACTORY_REQUEST_CONTRACT.json")

    contract_errors = validate_contract(flow)
    if contract_errors:
        raise ValueError("factory contract invalid: " + "; ".join(contract_errors))
    if request.get("contract_id") != request_contract.get("contract_id"):
        raise FactoryStateError("factory_unmapped_action", "request contract identity mismatch")
    operation = request.get("operation")
    operation_definition = request_contract.get("allowed_operations", {}).get(operation)
    if not isinstance(operation_definition, dict):
        raise FactoryStateError("factory_unmapped_action", f"unsupported request operation: {operation!r}")
    if request.get("executor") != "fixed_cycle_initializer" or operation_definition.get("adapter") != "_tools/fixed_cycle_initializer.py":
        raise FactoryStateError("factory_adapter_missing", "fixed_cycle_initializer adapter is not registered")

    work_order = build_work_order(flow, current, state, manifest, packet, repository_visibility)
    expected_action = request.get("expected_controller_action")
    if work_order.get("action") != expected_action:
        raise ValueError(
            f"factory request action mismatch: request={expected_action!r}, controller={work_order.get('action')!r}"
        )
    if work_order.get("executor") != "fixed_cycle_initializer":
        raise FactoryStateError("factory_adapter_missing", f"unexpected executor: {work_order.get('executor')!r}")
    expected_fingerprint = request.get("expected_state_fingerprint")
    if expected_fingerprint is not None and expected_fingerprint != work_order.get("state_fingerprint"):
        raise ValueError("factory request state fingerprint is stale")

    result = initialize_with_semantic_boundary(
        current,
        state,
        manifest,
        packet,
        request,
        artifact,
        repository_visibility,
        execution_modes,
        base_commit=base_commit,
        p4=p4,
    )
    if result["current"].get("operation_mode", {}).get("declared_state") == "private_translation_work":
        result["current"]["operation_mode"]["protocol"] = "_phase4_proofread/PUBLIC_CI_WINDOW.md"
    if branch_name is not None and result["branch"] != branch_name:
        raise ValueError(f"factory branch mismatch: request branch {branch_name!r}, adapter {result['branch']!r}")
    result["work_order"] = work_order
    return result


def write_result(result: dict[str, Any], *, p4: Path = P4) -> list[str]:
    root = p4.parent
    outputs = {
        p4 / "CURRENT_WORK.json": json_text(result["current"]),
        p4 / "PRIVATE_STAGE_STATE.json": json_text(result["state"]),
        p4 / "CI_TRAIN_MANIFEST.json": json_text(result["manifest"]),
        p4 / "NEXT_TASK_PACKET.json": json_text(result["packet"]),
        p4 / "CURRENT_HANDOFF.md": result["handoff"],
        root / result["candidate_path"]: json_text(result["candidate"]),
        root / result["preparation_path"]: result["preparation"],
    }
    written: list[str] = []
    for path, text in outputs.items():
        atomic_write(path, text)
        written.append(path.relative_to(root).as_posix())
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--artifact-json", type=Path)
    parser.add_argument("--repository-visibility", choices=("private", "public"))
    parser.add_argument("--base-commit")
    parser.add_argument("--branch-name")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--reconcile-remote-ref")
    parser.add_argument("--execution-result", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.reconcile_remote_ref:
            if args.execution_result is None:
                raise ValueError("--execution-result is required with --reconcile-remote-ref")
            summary = reconcile_remote_branch(
                args.reconcile_remote_ref,
                args.request,
                args.execution_result,
            )
            text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                atomic_write(args.output, text)
            print(text, end="")
            return 2 if summary["status"] == "conflict" else 0

        if args.artifact_json is None or args.repository_visibility is None:
            raise ValueError("--artifact-json and --repository-visibility are required for execution")
        request = load_object(args.request)
        artifact = load_object(args.artifact_json)
        result = execute(
            request,
            artifact,
            args.repository_visibility,
            base_commit=args.base_commit,
            branch_name=args.branch_name,
        )
        summary = {
            "status": "ready_to_write" if not args.write else "written",
            "action": result["work_order"]["action"],
            "executor": result["work_order"]["executor"],
            "train_id": result["train_id"],
            "branch": result["branch"],
            "stage": result["state"]["stage"],
            "candidate_path": result["candidate_path"],
            "row_count": result["row_count"],
        }
        if args.write:
            summary["written_paths"] = write_result(result)
        text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            atomic_write(args.output, text)
        print(text, end="")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, FactoryStateError, InitializerError) as exc:
        code = exc.code if isinstance(exc, FactoryStateError) else "factory_adapter_failure"
        print(json.dumps({"status": "blocked", "error_code": code, "detail": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
