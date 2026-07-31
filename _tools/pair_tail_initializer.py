#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize an exact, target-separated explicit-reference tail wave."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import fixed_cycle_initializer as base
from check_candidate_ownership import compute_snapshot
from pair_tail_common import (
    PAIR,
    P4,
    ROOT,
    TailError,
    load_object,
    require_strings,
    require_text,
    validate_exact_tail,
    write_json,
    write_text,
)
from select_cycle_execution_mode import selected_values


def _output_path(value: Any, label: str, prefix: str, suffix: str) -> str:
    return base.output_path(value, label, prefix, suffix)


def initialize(
    request: dict[str, Any],
    artifact: dict[str, Any],
    repository_visibility: str,
    *,
    base_commit: str | None = None,
    branch_name: str | None = None,
    p4: Path = P4,
) -> dict[str, Any]:
    current = load_object(p4 / "CURRENT_WORK.json")
    state = load_object(p4 / "PRIVATE_STAGE_STATE.json")
    manifest = load_object(p4 / "CI_TRAIN_MANIFEST.json")
    packet = load_object(p4 / "NEXT_TASK_PACKET.json")
    modes = load_object(p4 / "EXECUTION_MODES.json")
    base.validate_start(current, state, manifest, packet)

    if request.get("schema_version") != 1:
        raise TailError("request.schema_version must be 1")
    if request.get("contract_id") != "pair-tail-exhaustion-request-v1":
        raise TailError("request.contract_id mismatch")
    if request.get("operation") != "initialize_pair_tail":
        raise TailError("request.operation mismatch")
    if request.get("executor") != "pair_tail_initializer":
        raise TailError("request.executor mismatch")

    source = base.source_record(request)
    reserved = packet.get("source")
    if not isinstance(reserved, dict):
        raise TailError("NEXT_TASK_PACKET.source must be an object")
    mapping = {
        "artifact_workflow": "workflow",
        "artifact_run": "run_id",
        "artifact_id": "artifact_id",
        "artifact_name": "artifact_name",
        "artifact_file": "artifact_file",
        "artifact_digest": "digest",
        "artifact_head": "head_sha",
    }
    for packet_key, source_key in mapping.items():
        if reserved.get(packet_key) != source.get(source_key):
            raise TailError(f"request source mismatch for {packet_key}")

    candidate_paths = require_strings(
        request.get("reviewed_candidate_paths"), "reviewed_candidate_paths"
    )
    packet_groups = request.get("packet_groups")
    if not isinstance(packet_groups, list) or not packet_groups:
        raise TailError("packet_groups must be a non-empty list")
    selected = validate_exact_tail(artifact, p4.parent, candidate_paths, packet_groups)

    old_train = require_text(
        current.get("ci_train", {}).get("train_id"), "CURRENT_WORK train_id"
    )
    train_id, branch, wave_id, _ = base.next_ids(old_train)
    if request.get("branch") != branch:
        raise TailError(f"request branch must be {branch}")
    if branch_name is not None and branch_name != branch:
        raise TailError(f"workflow branch mismatch: {branch_name} != {branch}")

    release = packet.get("release_candidate")
    if not isinstance(release, dict):
        raise TailError("release_candidate must be an object")
    merge_sha = release.get("merge_sha") or manifest.get("transport", {}).get("merge_sha")
    old_release = {
        "train_id": old_train,
        "release_id": require_text(release.get("release_id"), "release_id"),
        "pr": release.get("pr"),
        "merge_sha": require_text(merge_sha, "merge_sha"),
    }
    checkpoint = copy.deepcopy(current.get("checkpoint"))
    if not isinstance(checkpoint, dict) or not isinstance(checkpoint.get("batch"), int):
        raise TailError("verified checkpoint is required")

    values = selected_values(modes, repository_visibility)
    totals = {key: 0 for key in base.TOTAL_KEYS}
    all_families: list[str] = []
    candidates: list[tuple[str, dict[str, Any]]] = []
    preparations: list[tuple[str, str]] = []
    wave_packets: list[dict[str, Any]] = []
    attestation = require_text(request.get("seal_attestation"), "seal_attestation")
    timeline = require_text(request.get("timeline"), "timeline")

    for index, (definition, rows) in enumerate(selected, start=1):
        families = require_strings(definition.get("families"), f"packet_groups[{index-1}].families")
        all_families.extend(families)
        candidate_path = _output_path(
            definition.get("candidate_path"),
            f"packet_groups[{index-1}].candidate_path",
            "CANDIDATE_",
            ".json",
        )
        preparation_path = _output_path(
            definition.get("preparation_path"),
            f"packet_groups[{index-1}].preparation_path",
            "PREPARATION_",
            ".md",
        )
        packet_id = f"yuwen-mowen-train{train_id.rsplit('-', 1)[-1]}-tail-{index:02d}"
        candidate = {
            "schema_version": 2,
            "stage": "private_preparation",
            "status": "prepared_without_translation_judgment",
            "current_pair": PAIR,
            "scene_groups": families,
            "source": {
                "target": require_text(definition.get("target"), "packet target"),
                "namespace": require_text(definition.get("namespace"), "packet namespace"),
            },
            "source_artifact": source,
            "scene_context": {
                "timeline": timeline,
                "branch_note": require_text(definition.get("branch_note"), "packet branch_note"),
            },
            "rows": [
                {
                    "key": row["key"],
                    "speaker": row["speaker"],
                    "zh": row["zh"],
                    "ja": row["ja"],
                }
                for row in rows
            ],
            "candidate_questions": require_strings(
                definition.get("candidate_questions", []),
                "candidate_questions",
                allow_empty=True,
            ),
            "unresolved_gates": {
                "allusion_candidates": require_strings(
                    definition.get("allusion_candidates", []),
                    "allusion_candidates",
                    allow_empty=True,
                ),
                "fact_doubts": require_strings(
                    definition.get("fact_doubts", []),
                    "fact_doubts",
                    allow_empty=True,
                ),
            },
            "forbidden_outputs": [
                "fix_or_keep_decision",
                "fix_json_write",
                "new_owner_assignment",
                "formal_bundle_completion",
                "throughput_metrics",
            ],
        }
        snapshot, errors = compute_snapshot(candidate, p4=p4)
        if errors or snapshot.get("duplicates"):
            raise TailError("candidate owner snapshot failed: " + "; ".join(errors or [str(snapshot.get("duplicates"))]))
        candidate["ownership_snapshot"] = snapshot
        candidates.append((candidate_path, candidate))
        preparation = (
            f"# 宇文逸↔莫問 {train_id} tail packet-{index:02d} preparation\n\n"
            f"- stage: `private_preparation`\n- status: `complete`\n"
            f"- source: Relation artifact run `{source['run_id']}`\n"
            f"- target: `{candidate['source']['target']}` / `{candidate['source']['namespace']}`\n"
            f"- rows: {len(rows)}\n- families: `{' / '.join(families)}`\n\n"
            f"## tail proof\n\n- {attestation}\n\n"
            "## stage boundary\n\n意味境界と差集合だけを記録し、KEEP/FIX・owner・正式束はまだ書かない。\n"
        )
        preparations.append((preparation_path, preparation))
        wave_packets.append(
            {
                "packet_id": packet_id,
                "scene_groups": families,
                "status": "prepared",
                "preparation_record": {
                    "candidate_packet": candidate_path,
                    "context_record": preparation_path,
                },
                "audit_record": None,
                "review_record": None,
                "formal_batch": None,
            }
        )

    new_current = copy.deepcopy(current)
    new_current["operation_mode"].update(values)
    new_current["operation_mode"]["declared_state"] = "private_translation_work"
    new_current["operation_mode"]["protocol"] = "_phase4_proofread/PUBLIC_CI_WINDOW.md"
    new_current["translation_base_commit"] = old_release["merge_sha"]
    if base_commit:
        new_current["state_base_commit"] = base_commit
    new_current["immediate_next"] = {
        "scene_groups": all_families,
        "task": "explicit-reference tailの2candidateをKEEP/FIX監査する。",
        "boundary": "quality auditでは翻訳判断だけを記録し、fix・owner・正式束・CI操作を行わない。",
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    old_ci = current.get("ci_train", {})
    new_current["ci_train"] = {
        "phase": old_ci.get("phase", "phase1_wave"),
        "policy": old_ci.get("policy", "_phase4_proofread/CI_TRAIN_PHASE2.md"),
        "quality_policy": old_ci.get("quality_policy", "_phase4_proofread/TRANSLATION_QUALITY_GATE.md"),
        "private_stage_policy": old_ci.get("private_stage_policy", "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md"),
        "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
        "train_id": train_id,
        "branch": branch,
        "status": "accumulating",
        "transport_status": "not_ready",
        "base_checkpoint_batch": checkpoint["batch"],
        "thresholds": copy.deepcopy(old_ci.get("thresholds")),
        "caps": copy.deepcopy(old_ci.get("caps")),
        "totals": totals,
        "private_stage": {
            "stage": "private_quality_audit",
            "status": "active",
            "transport_status": "not_ready",
            "wave_id": wave_id,
            "cycle_status": "running",
            "cycle_checkpoint": "private_quality_audit",
        },
        "tracking_issue": None,
        "draft_pr": None,
        "finalization_phase": "phase2",
        "post_merge_state_pr_required": False,
        "single_pr_finalization": True,
        "previous_release": old_release,
    }

    control = copy.deepcopy(state.get("cycle_control", {}))
    control.update(
        {
            "status": "running",
            "continuation_required": True,
            "stop_reason": None,
            "exact_next_action": "explicit-reference tailの2candidateをquality auditする",
            "last_safe_checkpoint": "private_quality_audit",
            "execution_mode": values["execution_mode"],
            "cycle_start_visibility": values["cycle_start_visibility"],
            "mode_locked_for_cycle": True,
            "normal_completion_target": values["normal_cycle_completion_target"],
        }
    )
    new_state = {
        "schema_version": 2,
        "contract": state.get("contract", "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json"),
        "train_id": train_id,
        "stage": "private_quality_audit",
        "mode": state.get("mode", "wave_v2"),
        "cycle_control": control,
        "ownership_policy": copy.deepcopy(state.get("ownership_policy", {})),
        "wave": {
            "wave_id": wave_id,
            "queue_status": "sealed",
            "seal_reason": "scope_exhausted",
            "seal_attestation": attestation,
            "packets": wave_packets,
        },
        "transport": {
            "status": "not_ready",
            "history": [{"status": "not_ready", "translation_stage": "private_preparation"}],
            "pr": None,
            "merge_sha": None,
        },
        "permissions": dict(base.AUDIT_PERMISSIONS),
        "history": [
            {"stage": "private_preparation", "status": "complete"},
            {"stage": "private_quality_audit", "status": "active"},
        ],
        "replenishment_reason": None,
        "source_artifact": source,
        "previous_release": old_release,
        "institutional_baseline": copy.deepcopy(state.get("institutional_baseline")),
        "tail_exhaustion": {
            "status": "verified",
            "reviewed_candidate_paths": candidate_paths,
            "residual_rows": sum(len(rows) for _, rows in selected),
            "residual_families": all_families,
        },
    }
    new_manifest = {
        "schema_version": manifest.get("schema_version", 2),
        "phase": manifest.get("phase", "phase1_wave"),
        "train_id": train_id,
        "branch": branch,
        "draft_pr": None,
        "status": "accumulating",
        "transport": {
            "status": "not_ready",
            "translation_stage": "private_quality_audit",
            "pr": None,
            "merge_sha": None,
        },
        "base_checkpoint": base.base_checkpoint(current),
        "thresholds": copy.deepcopy(manifest.get("thresholds")),
        "caps": copy.deepcopy(manifest.get("caps")),
        "allowed_early_release_reasons": copy.deepcopy(manifest.get("allowed_early_release_reasons", [])),
        "release_trigger": None,
        "totals": totals,
        "bundles": [],
        "tracking_issue": None,
        "tracking_mode": manifest.get("tracking_mode", "quality_and_private_stage_verified_in_public_pr"),
        "finalization_phase": "phase2",
        "post_merge_state_pr_required": False,
        "single_pr_finalization": True,
        "private_stage": {
            "stage": "private_quality_audit",
            "status": "active",
            "transport_status": "not_ready",
            "wave_id": wave_id,
        },
        "next_release": {
            "candidate_scene": all_families,
            "reservation_status": "quality_audit_active",
            "reservation_schema": 6,
            "formal_batches": [],
            "current_private_stage": "private_quality_audit",
        },
        "previous_release": old_release,
    }
    new_packet = copy.deepcopy(packet)
    new_packet.update(
        {
            "task_id": f"{train_id}-tail-quality-audit",
            "scene_groups": all_families,
            "reservation": {
                "status": "quality_audit_active",
                "wave_id": wave_id,
                "packet_id": f"{wave_id}-tail",
                "preparation_started": True,
                "quality_audit_started": True,
                "encoding_started": False,
                "formal_batch": None,
            },
            "do_not_do": [
                "quality auditではKEEP/FIX・人物性・事実・典故の判断だけを記録する",
                "private_encodingへ遷移するまでfix JSON・owner・正式束を書かない",
                "ゲームフォルダへ配置しない",
            ],
            "ci_train": {
                "phase": new_manifest["phase"],
                "train_id": train_id,
                "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
                "planned_batch": checkpoint["batch"] + 1,
                "post_merge_state_pr_required": False,
                "single_pr_finalization": True,
            },
            "tail_exhaustion": {
                "status": "verified",
                "residual_rows": sum(len(rows) for _, rows in selected),
                "packet_count": len(selected),
            },
        }
    )
    new_packet["source"].update(
        {
            "artifact_workflow": source["workflow"],
            "artifact_run": source["run_id"],
            "artifact_id": source["artifact_id"],
            "artifact_name": source["artifact_name"],
            "artifact_file": source["artifact_file"],
            "artifact_digest": source["digest"],
            "artifact_head": source["head_sha"],
            "freshness_rule": "quality audit中は保存済みcandidateを一次資料とし、encoding前にsource stale検査を行う。",
        }
    )
    handoff = (
        f"# 現在の引継ぎ\n\n- active train: `{train_id}`\n- branch: `{branch}`\n"
        f"- stage: `private_quality_audit`\n- transport: `not_ready`\n"
        f"- tail: {sum(len(rows) for _, rows in selected)} rows / {len(selected)} packets\n"
        f"- previous release: `{old_release['train_id']}` / PR #{old_release['pr']} / `{old_release['merge_sha']}`\n\n"
        "## exact next action\n\n2candidateを読み、KEEP/FIX・人物性・事実・典故だけを監査する。\n"
        "GitHub API、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。\n"
    )
    return {
        "current": new_current,
        "state": new_state,
        "manifest": new_manifest,
        "packet": new_packet,
        "candidates": candidates,
        "preparations": preparations,
        "handoff": handoff,
        "train_id": train_id,
        "branch": branch,
        "wave_id": wave_id,
        "row_count": sum(len(rows) for _, rows in selected),
    }


def write_result(result: dict[str, Any], p4: Path = P4) -> list[str]:
    root = p4.parent
    outputs: list[tuple[Path, str]] = [
        (p4 / "CURRENT_WORK.json", json.dumps(result["current"], ensure_ascii=False, indent=2)),
        (p4 / "PRIVATE_STAGE_STATE.json", json.dumps(result["state"], ensure_ascii=False, indent=2)),
        (p4 / "CI_TRAIN_MANIFEST.json", json.dumps(result["manifest"], ensure_ascii=False, indent=2)),
        (p4 / "NEXT_TASK_PACKET.json", json.dumps(result["packet"], ensure_ascii=False, indent=2)),
        (p4 / "CURRENT_HANDOFF.md", result["handoff"]),
    ]
    for relative, candidate in result["candidates"]:
        outputs.append((root / relative, json.dumps(candidate, ensure_ascii=False, indent=2)))
    for relative, text in result["preparations"]:
        outputs.append((root / relative, text))
    written: list[str] = []
    for path, text in outputs:
        write_text(path, text)
        written.append(path.relative_to(root).as_posix())
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--artifact-json", type=Path, required=True)
    parser.add_argument("--repository-visibility", choices=("private", "public"), required=True)
    parser.add_argument("--base-commit")
    parser.add_argument("--branch-name")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        request = load_object(args.request)
        artifact = load_object(args.artifact_json)
        result = initialize(
            request,
            artifact,
            args.repository_visibility,
            base_commit=args.base_commit,
            branch_name=args.branch_name,
        )
        summary = {
            "status": "written" if args.write else "valid",
            "train_id": result["train_id"],
            "branch": result["branch"],
            "wave_id": result["wave_id"],
            "row_count": result["row_count"],
            "candidate_paths": [path for path, _ in result["candidates"]],
        }
        if args.write:
            summary["written_paths"] = write_result(result)
    except (OSError, json.JSONDecodeError, ValueError, TailError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "pair_tail_initializer_failure", "detail": str(exc)}, ensure_ascii=False))
        return 1
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        write_text(args.output, text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
