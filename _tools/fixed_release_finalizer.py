#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orchestratorの固定artifactからrelease証跡とphase2-ready状態を一括生成する。"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TRAIN_RE = re.compile(r"^yuwen-mowen-train-(\d+)$")
RESTART_PHRASE = "現状把握して作業の続きを"


class FinalizerError(ValueError):
    """Release finalization contract violation."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FinalizerError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FinalizerError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FinalizerError(f"top level must be object: {path}")
    return value


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.rstrip() + "\n")
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_json(path: Path, value: dict[str, Any]) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2))


def require_positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise FinalizerError(f"{label} must be a positive integer")
    return value


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise FinalizerError(f"{label} must be a lowercase 40-character SHA")
    return value


def validate_inputs(
    request: dict[str, Any],
    artifact: dict[str, Any],
    branch: str,
) -> dict[str, Any]:
    if request.get("schema_version") != 1:
        raise FinalizerError("request.schema_version must be 1")
    if request.get("contract_id") != "release-finalization-request-v1":
        raise FinalizerError("request.contract_id mismatch")
    if request.get("operation") != "finalize_release_state":
        raise FinalizerError("request.operation mismatch")
    if request.get("executor") != "fixed_release_finalizer":
        raise FinalizerError("request.executor mismatch")
    if request.get("branch") != branch:
        raise FinalizerError("request.branch mismatch")

    expected = {
        "schema_version": 1,
        "pr": request.get("pr"),
        "orchestrator_run_id": request.get("orchestrator_run_id"),
        "ci_head": request.get("ci_head"),
        "asset_head": request.get("asset_head"),
        "apply_changed": request.get("apply_changed"),
    }
    if artifact != expected:
        raise FinalizerError(
            f"finalization artifact mismatch: observed={artifact!r}, expected={expected!r}"
        )

    require_positive_int(expected["pr"], "request.pr")
    require_positive_int(
        expected["orchestrator_run_id"], "request.orchestrator_run_id"
    )
    require_sha(expected["ci_head"], "request.ci_head")
    require_sha(expected["asset_head"], "request.asset_head")
    if expected["apply_changed"] is not True:
        raise FinalizerError("request.apply_changed must be true")
    return expected


def batch_number_from_path(path: str) -> int | None:
    match = re.search(r"BATCH(\d+)_", path)
    return int(match.group(1)) if match else None


def append_transport_history(
    state: dict[str, Any],
    *,
    status: str,
    pr: int,
    release_id: str | None = None,
) -> None:
    transport = state.setdefault("transport", {})
    history = transport.setdefault("history", [])
    if any(
        isinstance(item, dict)
        and item.get("status") == status
        and item.get("pr") == pr
        for item in history
    ):
        return
    item: dict[str, Any] = {
        "status": status,
        "translation_stage": "translation_frozen",
        "pr": pr,
    }
    if release_id is not None:
        item["release_id"] = release_id
    history.append(item)


def build_next_reservation(
    current: dict[str, Any],
    manifest: dict[str, Any],
    request: dict[str, Any],
    release_path: str,
) -> dict[str, Any]:
    next_scene = request.get("next_scene")
    source = request.get("next_source")
    if not isinstance(next_scene, str) or not next_scene:
        raise FinalizerError("request.next_scene is required")
    if not isinstance(source, dict):
        raise FinalizerError("request.next_source must be an object")

    string_fields = (
        "artifact_workflow",
        "artifact_name",
        "artifact_file",
        "artifact_digest",
        "artifact_head",
        "freshness_rule",
    )
    for key in string_fields:
        if not isinstance(source.get(key), str) or not source[key]:
            raise FinalizerError(f"request.next_source.{key} is required")
    require_positive_int(source.get("artifact_run"), "next_source.artifact_run")
    require_positive_int(source.get("artifact_id"), "next_source.artifact_id")

    checkpoint = current["checkpoint"]
    train_id = manifest["train_id"]
    train_number = train_id.rsplit("-", 1)[-1]
    return {
        "schema_version": 6,
        "status": "ready",
        "task_id": f"post-train{train_number}-minimal-wave-reservation",
        "based_on_checkpoint": {
            "batch": checkpoint["batch"],
            "pair_applied_keys": checkpoint["pair_applied_keys"],
            "project_applied_keys": checkpoint["project_applied_keys"],
            "produced_by_pr": checkpoint["produced_by_pr"],
            "release_id": checkpoint["release_identity"]["release_id"],
            "release_evidence": release_path,
        },
        "current_pair": current["current_pair"],
        "scene_groups": [next_scene],
        "reservation": {
            "status": "reserved_only",
            "wave_id": None,
            "packet_id": None,
            "preparation_started": False,
            "quality_audit_started": False,
            "encoding_started": False,
            "formal_batch": None,
        },
        "source": copy.deepcopy(source),
        "release_candidate": {
            "train_id": train_id,
            "release_id": checkpoint["release_identity"]["release_id"],
            "pr": checkpoint["produced_by_pr"],
            "status": "verified",
            "merge_sha": None,
        },
        "do_not_do": [
            "minimal reservationへfocus key・voice question・FACT_DOUBT・owner snapshot・batch planningを戻さない",
            f"{train_id}統合前に{next_scene}のpreparationを開始しない",
            "translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない",
            "ゲームフォルダへ配置しない",
        ],
        "ci_train": {
            "phase": manifest["phase"],
            "train_id": train_id,
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "planned_batch": checkpoint["batch"] + 1,
            "post_merge_state_pr_required": False,
            "single_pr_finalization": True,
        },
    }


def render_handoff(
    *,
    pr: int,
    train_id: str,
    batch: int,
    pair_keys: int,
    project_keys: int,
    next_scene: str,
    orchestrator_run: int,
    asset_head: str,
    totals: dict[str, Any],
) -> str:
    return f"""# 現在の申し送り

> 再開指示: `{RESTART_PHRASE}`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: public
- PR #{pr}: open / ready / mergeable
- train: `{train_id}`
- verified checkpoint: 第{batch}束 / pair {pair_keys} / project {project_keys}
- last reviewed batch: 第{batch}束
- private stage: `translation_frozen`
- transport: `awaiting_private_merge`
- queue: {totals.get("bundle_count")}packet / {totals.get("reviewed_rows")}行 / {totals.get("fix_keys")}修正 / {totals.get("reviewed_rows", 0) - totals.get("fix_keys", 0)}保持

## release

orchestrator run `{orchestrator_run}`で完全preflight、Relation、Cross、Apply、pak再生成、未適用0件、finalization入力生成まで成功した。asset HEADは`{asset_head}`。

## 次の作業

PR #{pr}の`finalize-release` phase2と未解決review thread 0件を確認し、検証済みHEADをsquash統合する。always-public cycleなのでvisibility変更は要求しない。

次候補`{next_scene}`はminimal reservationのまま保持し、{train_id}統合前にpreparationを開始しない。

## 禁止

- translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない。
- phase2成功前にPR #{pr}をmergeしない。
- {train_id}統合前に`{next_scene}`のpreparationを始めない。
- ゲームフォルダへ配置しない。
"""


def finalize(
    request: dict[str, Any],
    artifact: dict[str, Any],
    *,
    branch: str,
    p4: Path = P4,
) -> dict[str, Any]:
    info = validate_inputs(request, artifact, branch)
    current = load_object(p4 / "CURRENT_WORK.json")
    state = load_object(p4 / "PRIVATE_STAGE_STATE.json")
    manifest = load_object(p4 / "CI_TRAIN_MANIFEST.json")
    audit = load_object(p4 / "audit_status.json")

    pr = info["pr"]
    orchestrator_run = info["orchestrator_run_id"]
    ci_head = info["ci_head"]
    asset_head = info["asset_head"]

    train_id = manifest.get("train_id")
    train_match = TRAIN_RE.fullmatch(str(train_id))
    if train_match is None or manifest.get("branch") != branch:
        raise FinalizerError("active train identity mismatch")
    if current.get("ci_train", {}).get("train_id") != train_id:
        raise FinalizerError("CURRENT_WORK train mismatch")
    if state.get("train_id") != train_id:
        raise FinalizerError("PRIVATE_STAGE_STATE train mismatch")
    if (
        current.get("ci_train", {}).get("draft_pr") != pr
        or manifest.get("draft_pr") != pr
        or state.get("transport", {}).get("pr") != pr
    ):
        raise FinalizerError("active PR mismatch")
    if state.get("stage") != "translation_frozen":
        raise FinalizerError("finalizer requires translation_frozen")
    if manifest.get("status") != "ready_for_public_ci":
        raise FinalizerError("manifest must be ready_for_public_ci")
    if current.get("ci_train", {}).get("transport_status") != "ready_for_public_ci":
        raise FinalizerError("CURRENT_WORK transport must be ready_for_public_ci")

    bundles = manifest.get("bundles")
    totals = manifest.get("totals")
    if not isinstance(bundles, list) or not bundles:
        raise FinalizerError("formal bundles are missing")
    if not isinstance(totals, dict):
        raise FinalizerError("manifest totals are missing")
    batch = max(
        require_positive_int(bundle.get("batch"), "bundle.batch")
        for bundle in bundles
        if isinstance(bundle, dict)
    )

    pair = current.get("current_pair")
    pair_status = audit.get("pair_status", {}).get(pair, {})
    latest_build = audit.get("project", {}).get("latest_build", {})
    pair_keys = require_positive_int(pair_status.get("applied_keys"), "pair applied_keys")
    project_keys = require_positive_int(
        latest_build.get("applied_keys"), "project applied_keys"
    )
    record_index = latest_build.get("record_index", [])
    if not isinstance(record_index, list):
        raise FinalizerError("audit_status.record_index must be a list")
    applied_records = [
        path
        for path in record_index
        if isinstance(path, str) and batch_number_from_path(path) == batch
    ]
    if len(applied_records) != 1:
        raise FinalizerError(
            f"exactly one applied record is required for batch {batch}: {applied_records}"
        )
    applied_record = applied_records[0]
    if not (p4.parent / applied_record).is_file():
        raise FinalizerError(f"applied record is missing: {applied_record}")

    notes = request.get("notes", [])
    if not isinstance(notes, list) or any(
        not isinstance(item, str) or not item for item in notes
    ):
        raise FinalizerError("request.notes must be a list of non-empty strings")
    date = request.get("date")
    if not isinstance(date, str) or not date:
        raise FinalizerError("request.date is required")
    next_scene = request.get("next_scene")
    if not isinstance(next_scene, str) or not next_scene:
        raise FinalizerError("request.next_scene is required")

    release_id = f"{train_id}-r1"
    release_path = (
        f"_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_{train_match.group(1)}.json"
    )
    evidence = {
        "schema_version": 2,
        "status": "verified",
        "release_id": release_id,
        "train_id": train_id,
        "pr": pr,
        "ci_head": ci_head,
        "asset_head": asset_head,
        "applied_record": applied_record,
        "counts": {
            "batch": batch,
            "pair_applied_keys": pair_keys,
            "project_applied_keys": project_keys,
            "pending_fixes": 0,
        },
        "orchestrator": {
            "id": orchestrator_run,
            "workflow": "Release train orchestrator",
            "head_sha": ci_head,
            "event": "pull_request",
            "conclusion": "success",
        },
        "lineage": {"mode": "branch_ancestor", "merge_sha": None},
        "notes": notes,
    }

    current = copy.deepcopy(current)
    state = copy.deepcopy(state)
    manifest = copy.deepcopy(manifest)

    current.update(
        {
            "updated_at": date,
            "state_base_commit": asset_head,
            "last_completed_batch": batch,
            "last_reviewed_batch": batch,
            "pair_applied_keys": pair_keys,
            "project_applied_keys": project_keys,
        }
    )
    current["checkpoint"] = {
        "status": "verified",
        "batch": batch,
        "pair_applied_keys": pair_keys,
        "project_applied_keys": project_keys,
        "produced_by_pr": pr,
        "release_identity": {
            "kind": "pr_release_v2",
            "release_id": release_id,
            "evidence": release_path,
            "pr": pr,
            "validated_head": asset_head,
        },
        "applied_record": applied_record,
    }
    current["immediate_next"] = {
        "scene_groups": [next_scene],
        "task": (
            f"PR #{pr}のfinalize-release phase2と未解決review thread 0件を確認し、"
            "検証済みHEADをsquash統合する。"
        ),
        "boundary": (
            "translation_frozen後は翻訳判断、fix追加、owner変更、正式束追加を行わない。"
        ),
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    ci_train = current["ci_train"]
    ci_train.update(
        {
            "status": "verified",
            "transport_status": "awaiting_private_merge",
            "applied_result": {
                "orchestrator_run": orchestrator_run,
                "asset_head": asset_head,
                "pair_applied_keys": pair_keys,
                "project_applied_keys": project_keys,
                "pending_fixes": 0,
                "checkpoint_status": "verified",
            },
            "verified_result": {
                "release_id": release_id,
                "release_evidence": release_path,
                "record_index_synced": True,
                "pair_applied_keys": pair_keys,
                "project_applied_keys": project_keys,
                "pending_fixes": 0,
            },
            "release_evidence": release_path,
        }
    )
    private_stage = ci_train["private_stage"]
    private_stage.update(
        {
            "status": "verified",
            "transport_status": "awaiting_private_merge",
            "cycle_status": "running",
            "cycle_checkpoint": "awaiting_private_merge",
        }
    )
    current["release_evidence"] = release_path

    for bundle in manifest["bundles"]:
        if isinstance(bundle, dict):
            bundle["apply_status"] = "verified"
    manifest["status"] = "verified"
    manifest["release_evidence"] = release_path
    manifest["transport"].update(
        {
            "status": "awaiting_private_merge",
            "translation_stage": "translation_frozen",
            "pr": pr,
            "merge_sha": None,
        }
    )
    manifest["private_stage"].update(
        {"status": "verified", "transport_status": "awaiting_private_merge"}
    )
    manifest["next_release"].update(
        {
            "candidate_scene": [next_scene],
            "reservation_status": "reserved_only",
            "reservation_schema": 6,
            "formal_batches": [
                bundle["batch"]
                for bundle in manifest["bundles"]
                if isinstance(bundle, dict)
            ],
            "current_private_stage": "translation_frozen",
        }
    )

    state["transport"].update(
        {"status": "awaiting_private_merge", "pr": pr, "merge_sha": None}
    )
    append_transport_history(state, status="in_public_ci", pr=pr)
    append_transport_history(state, status="verified", pr=pr, release_id=release_id)
    append_transport_history(
        state, status="awaiting_private_merge", pr=pr, release_id=release_id
    )
    state["cycle_control"].update(
        {
            "status": "running",
            "continuation_required": True,
            "stop_reason": None,
            "exact_next_action": (
                f"PR #{pr}のfinalize-release phase2とreview thread 0件を確認し、"
                "検証済みHEADをsquash mergeする"
            ),
            "last_safe_checkpoint": "awaiting_private_merge",
        }
    )
    state["verified_result"] = {
        "release_id": release_id,
        "evidence": release_path,
        "ci_head": ci_head,
        "asset_head": asset_head,
        "pending_fixes": 0,
    }
    for packet_entry in state.get("wave", {}).get("packets", []):
        if isinstance(packet_entry, dict) and isinstance(
            packet_entry.get("review_record"), dict
        ):
            packet_entry["review_record"]["apply_status"] = "verified"

    next_packet = build_next_reservation(current, manifest, request, release_path)
    handoff = render_handoff(
        pr=pr,
        train_id=train_id,
        batch=batch,
        pair_keys=pair_keys,
        project_keys=project_keys,
        next_scene=next_scene,
        orchestrator_run=orchestrator_run,
        asset_head=asset_head,
        totals=totals,
    )

    write_json(p4.parent / release_path, evidence)
    write_json(p4 / "CURRENT_WORK.json", current)
    write_json(p4 / "PRIVATE_STAGE_STATE.json", state)
    write_json(p4 / "CI_TRAIN_MANIFEST.json", manifest)
    write_json(p4 / "NEXT_TASK_PACKET.json", next_packet)
    write_text(p4 / "CURRENT_HANDOFF.md", handoff)

    return {
        "status": "finalized",
        "train_id": train_id,
        "pr": pr,
        "batch": batch,
        "release_id": release_id,
        "release_evidence": release_path,
        "ci_head": ci_head,
        "asset_head": asset_head,
        "next_scene": next_scene,
        "transport_status": "awaiting_private_merge",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--artifact-json", type=Path, required=True)
    parser.add_argument("--branch-name", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.write:
        print("ERROR: --write is required")
        return 2
    try:
        result = finalize(
            load_object(args.request),
            load_object(args.artifact_json),
            branch=args.branch_name,
        )
    except (FinalizerError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.output is not None:
        write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
