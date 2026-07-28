#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merged cycleと予約済みRelation資料を、意味境界確定済みquality-audit stationへ初期化する。"""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from check_candidate_ownership import compute_snapshot
from select_cycle_execution_mode import selected_values

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
PAIR = "宇文逸↔莫問"
TRAIN_RE = re.compile(r"^(.+-train-)(\d+)$")
TOTAL_KEYS = ("bundle_count", "reviewed_rows", "reviewed_keys", "unique_reviewed_rows", "fix_keys", "unique_fix_rows", "new_pair_keys", "new_project_keys", "cross_register_keys", "existing_owner_updates", "keep_only_bundles")
AUDIT_PERMISSIONS = {"translation_judgment_allowed": True, "fix_writes_allowed": False, "encoding_writes_allowed": False, "throughput_metrics_visible": False, "metrics_frozen": True}


class InitializerError(ValueError):
    pass


def obj(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InitializerError(f"{label} must be an object")
    return value


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InitializerError(f"{label} must be a non-empty string")
    return value.strip()


def strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or any(not isinstance(x, str) or not x for x in value):
        raise InitializerError(f"{label} must be a string list")
    if len(value) != len(set(value)):
        raise InitializerError(f"{label} contains duplicates")
    return list(value)


def output_path(value: Any, label: str, prefix: str, suffix: str) -> str:
    path = Path(text(value, label))
    if path.is_absolute() or ".." in path.parts or path.parent.as_posix() != "_phase4_proofread":
        raise InitializerError(f"{label} must stay directly under _phase4_proofread")
    if not path.name.startswith(prefix) or not path.name.endswith(suffix):
        raise InitializerError(f"{label} filename is invalid")
    return path.as_posix()


def next_ids(old_train: str) -> tuple[str, str, str, str]:
    match = TRAIN_RE.fullmatch(old_train)
    if not match:
        raise InitializerError(f"train_id is not incrementable: {old_train!r}")
    number = int(match.group(2)) + 1
    return (f"{match.group(1)}{number}", f"agent/yuwen-mowen-train-{number}", f"yuwen-mowen-train-{number}-wave-01", f"yuwen-mowen-train{number}-packet-01")


def source_record(request: dict[str, Any]) -> dict[str, Any]:
    source = obj(request.get("source"), "request.source")
    for key in ("artifact_run", "artifact_id"):
        if not isinstance(source.get(key), int) or source[key] <= 0:
            raise InitializerError(f"request.source.{key} must be a positive integer")
    for key in ("artifact_workflow", "artifact_name", "artifact_file", "artifact_digest", "artifact_head"):
        text(source.get(key), f"request.source.{key}")
    return {"workflow": source["artifact_workflow"], "run_id": source["artifact_run"], "artifact_id": source["artifact_id"], "artifact_name": source["artifact_name"], "artifact_file": source["artifact_file"], "digest": source["artifact_digest"], "head_sha": source["artifact_head"]}


def extract_rows(artifact: dict[str, Any], scenes: list[str]) -> list[dict[str, str]]:
    groups = artifact.get("groups")
    if not isinstance(groups, list):
        raise InitializerError("relation artifact groups must be a list")
    by_family = {item.get("family"): item for item in groups if isinstance(item, dict) and isinstance(item.get("family"), str)}
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for scene in scenes:
        group = by_family.get(f"{scene}_Dlgs")
        if not isinstance(group, dict) or not isinstance(group.get("rows"), list) or not group["rows"]:
            raise InitializerError(f"relation artifact lacks non-empty scene group {scene}")
        for index, row in enumerate(group["rows"]):
            if not isinstance(row, dict):
                raise InitializerError(f"{scene}.rows[{index}] must be an object")
            key = text(row.get("key"), f"{scene}.rows[{index}].key")
            if key in seen:
                raise InitializerError(f"duplicate relation row key: {key}")
            seen.add(key)
            rows.append({"key": key, "speaker": str(row.get("speaker") or row.get("ja_speaker") or ""), "zh": str(row.get("zh") or ""), "ja": str(row.get("ja") or "")})
    return rows


def base_checkpoint(current: dict[str, Any]) -> dict[str, Any]:
    checkpoint = obj(current.get("checkpoint"), "CURRENT_WORK.checkpoint")
    result = {key: checkpoint.get(key) for key in ("batch", "pair_applied_keys", "project_applied_keys", "produced_by_pr")}
    if isinstance(checkpoint.get("release_identity"), dict):
        result["release_identity"] = copy.deepcopy(checkpoint["release_identity"])
    else:
        result.update({"translation_head": checkpoint.get("translation_head"), "verified_head": checkpoint.get("verified_head")})
    return result


def validate_start(current: dict[str, Any], state: dict[str, Any], manifest: dict[str, Any], packet: dict[str, Any]) -> None:
    transports = (current.get("ci_train", {}).get("transport_status"), state.get("transport", {}).get("status"), manifest.get("transport", {}).get("status"))
    if transports != ("merged", "merged", "merged"):
        raise InitializerError(f"initializer requires merged transport authorities: {transports!r}")
    if state.get("cycle_control", {}).get("status") != "target_reached" or current.get("checkpoint", {}).get("status") != "verified":
        raise InitializerError("initializer requires target_reached cycle and verified checkpoint")
    reservation = obj(packet.get("reservation"), "NEXT_TASK_PACKET.reservation")
    if reservation.get("status") != "reserved_only" or reservation.get("preparation_started") is not False:
        raise InitializerError("initializer requires clean reserved_only reservation")
    if current.get("current_pair") != PAIR or packet.get("current_pair") != PAIR:
        raise InitializerError("pair mismatch")


def initialize_with_semantic_boundary(current: dict[str, Any], state: dict[str, Any], manifest: dict[str, Any], packet: dict[str, Any], request: dict[str, Any], artifact: dict[str, Any], repository_visibility: str, execution_modes: dict[str, Any], *, base_commit: str | None = None, p4: Path = P4) -> dict[str, Any]:
    validate_start(current, state, manifest, packet)
    if request.get("schema_version") != 1 or request.get("contract_id") != "translation-factory-request-v1":
        raise InitializerError("factory request contract identity mismatch")
    if request.get("operation") != "initialize_with_semantic_boundary" or request.get("executor") != "fixed_cycle_initializer" or request.get("expected_controller_action") != "initialize_next_cycle_from_reservation":
        raise InitializerError("factory request operation/executor/action mismatch")

    source = source_record(request)
    reserved = obj(packet.get("source"), "NEXT_TASK_PACKET.source")
    mapping = {"artifact_workflow": "workflow", "artifact_run": "run_id", "artifact_id": "artifact_id", "artifact_name": "artifact_name", "artifact_file": "artifact_file", "artifact_digest": "digest", "artifact_head": "head_sha"}
    for packet_key, source_key in mapping.items():
        if reserved.get(packet_key) != source.get(source_key):
            raise InitializerError(f"request source mismatch for {packet_key}")

    old_train = text(current.get("ci_train", {}).get("train_id"), "CURRENT_WORK.ci_train.train_id")
    release = obj(packet.get("release_candidate"), "NEXT_TASK_PACKET.release_candidate")
    old_release = {"train_id": old_train, "release_id": text(release.get("release_id"), "release_id"), "pr": release.get("pr"), "merge_sha": text(release.get("merge_sha") or manifest.get("transport", {}).get("merge_sha"), "merge_sha")}
    train_id, branch, wave_id, packet_id = next_ids(old_train)
    if request.get("branch") not in (None, branch):
        raise InitializerError("request branch does not match deterministic next train")

    boundary = obj(request.get("semantic_boundary"), "request.semantic_boundary")
    scenes = strings(boundary.get("scene_groups"), "semantic_boundary.scene_groups")
    rows = extract_rows(artifact, scenes)
    if boundary.get("unique_reviewed_rows") != len(rows):
        raise InitializerError(f"semantic boundary row count mismatch: declared={boundary.get('unique_reviewed_rows')!r}, artifact={len(rows)}")
    if not 40 <= len(rows) <= 80:
        raise InitializerError(f"semantic boundary row count is out of range: {len(rows)}")
    extension = obj(boundary.get("semantic_extension"), "semantic_extension")
    if len(rows) > 60 and (extension.get("used") is not True or extension.get("reason") != "complete_semantic_unit"):
        raise InitializerError("rows above 60 require complete_semantic_unit extension")
    if len(rows) <= 60 and extension.get("used") is True:
        raise InitializerError("semantic extension cannot be used at 60 rows or below")

    output = obj(request.get("output"), "request.output")
    candidate_path = output_path(output.get("candidate_path"), "candidate_path", "CANDIDATE_", ".json")
    preparation_path = output_path(output.get("preparation_path"), "preparation_path", "PREPARATION_", ".md")
    timeline = text(boundary.get("timeline"), "timeline")
    branch_note = text(boundary.get("branch_note"), "branch_note")
    attestation = text(boundary.get("seal_attestation"), "seal_attestation")
    questions = strings(boundary.get("candidate_questions"), "candidate_questions")
    allusions = strings(boundary.get("allusion_candidates", []), "allusion_candidates", allow_empty=True)
    facts = strings(boundary.get("fact_doubts", []), "fact_doubts", allow_empty=True)

    candidate = {"schema_version": 2, "stage": "private_preparation", "status": "prepared_without_translation_judgment", "current_pair": PAIR, "scene_groups": scenes, "source": {"target": "CG表", "namespace": "QuestDlgs"}, "source_artifact": source, "scene_context": {"timeline": timeline, "branch_note": branch_note}, "rows": rows, "candidate_questions": questions, "unresolved_gates": {"allusion_candidates": allusions, "fact_doubts": facts}, "forbidden_outputs": ["fix_or_keep_decision", "fix_json_write", "new_owner_assignment", "formal_bundle_completion", "throughput_metrics"]}
    snapshot, errors = compute_snapshot(candidate, p4=p4)
    if errors or snapshot.get("duplicates"):
        raise InitializerError("candidate owner snapshot failed: " + "; ".join(errors or [str(snapshot.get("duplicates"))]))
    candidate["ownership_snapshot"] = snapshot

    checkpoint = copy.deepcopy(obj(current.get("checkpoint"), "CURRENT_WORK.checkpoint"))
    if not isinstance(checkpoint.get("batch"), int):
        raise InitializerError("checkpoint batch is invalid")
    planned_batch = checkpoint["batch"] + 1
    values = selected_values(obj(execution_modes, "EXECUTION_MODES"), repository_visibility)
    totals = {key: 0 for key in TOTAL_KEYS}

    new_current = copy.deepcopy(current)
    new_current["operation_mode"].update(values)
    new_current["operation_mode"]["declared_state"] = "private_translation_work"
    new_current["translation_base_commit"] = old_release["merge_sha"]
    if base_commit:
        new_current["state_base_commit"] = base_commit
    new_current["immediate_next"] = {"scene_groups": scenes, "task": f"{candidate_path}をtranslation_quality_audit stationでKEEP/FIX監査する。", "boundary": "quality auditでは翻訳判断だけを記録し、fix・owner・正式束・CI操作を行わない。", "packet": "_phase4_proofread/NEXT_TASK_PACKET.json"}
    old_ci = current.get("ci_train", {})
    new_current["ci_train"] = {"phase": old_ci.get("phase", "phase1_wave"), "policy": old_ci.get("policy", "_phase4_proofread/CI_TRAIN_PHASE2.md"), "quality_policy": old_ci.get("quality_policy", "_phase4_proofread/TRANSLATION_QUALITY_GATE.md"), "private_stage_policy": old_ci.get("private_stage_policy", "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md"), "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json", "train_id": train_id, "branch": branch, "status": "accumulating", "transport_status": "not_ready", "base_checkpoint_batch": checkpoint["batch"], "thresholds": copy.deepcopy(old_ci.get("thresholds")), "caps": copy.deepcopy(old_ci.get("caps")), "totals": totals, "private_stage": {"stage": "private_quality_audit", "status": "active", "transport_status": "not_ready", "wave_id": wave_id, "cycle_status": "running", "cycle_checkpoint": "private_quality_audit"}, "tracking_issue": None, "draft_pr": None, "finalization_phase": "phase2", "post_merge_state_pr_required": False, "single_pr_finalization": True, "previous_release": old_release}

    control = copy.deepcopy(obj(state.get("cycle_control"), "cycle_control"))
    control.update({"status": "running", "continuation_required": True, "stop_reason": None, "exact_next_action": f"{candidate_path}をtranslation_quality_audit stationで監査する", "last_safe_checkpoint": "private_quality_audit", "execution_mode": values["execution_mode"], "cycle_start_visibility": values["cycle_start_visibility"], "mode_locked_for_cycle": True, "normal_completion_target": values["normal_cycle_completion_target"]})
    packet_record = {"packet_id": packet_id, "scene_groups": scenes, "status": "prepared", "preparation_record": {"candidate_packet": candidate_path, "context_record": preparation_path}, "audit_record": None, "review_record": None, "formal_batch": None}
    new_state = {"schema_version": 2, "contract": state.get("contract", "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json"), "train_id": train_id, "stage": "private_quality_audit", "mode": state.get("mode", "wave_v2"), "cycle_control": control, "ownership_policy": copy.deepcopy(state.get("ownership_policy", {})), "wave": {"wave_id": wave_id, "queue_status": "sealed", "seal_reason": "unique_reviewed_rows_threshold", "seal_attestation": attestation, "packets": [packet_record]}, "transport": {"status": "not_ready", "history": [{"status": "not_ready", "translation_stage": "private_preparation"}], "pr": None, "merge_sha": None}, "permissions": AUDIT_PERMISSIONS, "history": [{"stage": "private_preparation", "status": "complete"}, {"stage": "private_quality_audit", "status": "active"}], "replenishment_reason": None, "source_artifact": source, "previous_release": old_release, "institutional_baseline": copy.deepcopy(state.get("institutional_baseline"))}

    new_manifest = {"schema_version": manifest.get("schema_version", 2), "phase": manifest.get("phase", "phase1_wave"), "train_id": train_id, "branch": branch, "draft_pr": None, "status": "accumulating", "transport": {"status": "not_ready", "translation_stage": "private_quality_audit", "pr": None, "merge_sha": None}, "base_checkpoint": base_checkpoint(current), "thresholds": copy.deepcopy(manifest.get("thresholds")), "caps": copy.deepcopy(manifest.get("caps")), "allowed_early_release_reasons": copy.deepcopy(manifest.get("allowed_early_release_reasons", [])), "release_trigger": None, "totals": totals, "bundles": [], "tracking_issue": None, "tracking_mode": manifest.get("tracking_mode", "quality_and_private_stage_verified_in_public_pr"), "finalization_phase": "phase2", "post_merge_state_pr_required": False, "single_pr_finalization": True, "private_stage": {"stage": "private_quality_audit", "status": "active", "transport_status": "not_ready", "wave_id": wave_id}, "next_release": {"candidate_scene": scenes, "reservation_status": "quality_audit_active", "reservation_schema": 6, "formal_batches": [], "current_private_stage": "private_quality_audit"}, "previous_release": old_release}

    new_packet = copy.deepcopy(packet)
    new_packet.update({"task_id": f"{train_id}-quality-audit", "scene_groups": scenes, "reservation": {"status": "quality_audit_active", "wave_id": wave_id, "packet_id": packet_id, "preparation_started": True, "quality_audit_started": True, "encoding_started": False, "formal_batch": None}, "do_not_do": ["quality auditではKEEP/FIX・人物性・事実・典故の判断だけを記録する", "private_encodingへ遷移するまでfix JSON・owner・正式束を書かない", "別API・別workflow・別triggerを考案しない", "ゲームフォルダへ配置しない"], "ci_train": {"phase": new_manifest["phase"], "train_id": train_id, "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json", "planned_batch": planned_batch, "post_merge_state_pr_required": False, "single_pr_finalization": True}})
    new_packet["source"].update({"artifact_workflow": source["workflow"], "artifact_run": source["run_id"], "artifact_id": source["artifact_id"], "artifact_name": source["artifact_name"], "artifact_file": source["artifact_file"], "artifact_digest": source["digest"], "artifact_head": source["head_sha"], "freshness_rule": "quality audit中は保存済みcandidateを一次資料とし、encoding前にsource stale検査を行う。"})

    preparation = f"# 宇文逸↔莫問 {train_id} wave-01 preparation\n\n- stage: `private_preparation`\n- status: `complete`\n- source: Relation artifact run `{source['run_id']}`\n- queue: 1 packet / {len(rows)} unique rows\n- semantic extension: `{'used' if extension.get('used') else 'not_used'}`\n\n## packet layout\n\n### packet-01 — {' + '.join(scenes)}\n- rows: {len(rows)}\n- candidate: `{candidate_path}`\n- context: {timeline}\n\n## boundary attestation\n\n- {attestation}\n- {branch_note}\n\n## stage boundary\n\n- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。\n- 次stationは`translation_quality_audit`。\n"
    handoff = f"# 現在の引継ぎ\n\n- active train: `{train_id}`\n- branch: `{branch}`\n- stage: `private_quality_audit`\n- transport: `not_ready`\n- wave: `{wave_id}` / 1 packet / {len(rows)} unique rows\n- candidate: `{candidate_path}`\n- previous release: `{old_release['train_id']}` / PR #{old_release['pr']} / `{old_release['merge_sha']}`\n\n## exact next action\n\n`{candidate_path}`を読み、KEEP/FIX・人物性・事実・典故だけを監査する。\nGitHub API、branch、workflow、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。\n"
    return {"current": new_current, "state": new_state, "manifest": new_manifest, "packet": new_packet, "candidate": candidate, "preparation": preparation, "handoff": handoff, "candidate_path": candidate_path, "preparation_path": preparation_path, "train_id": train_id, "branch": branch, "wave_id": wave_id, "packet_id": packet_id, "row_count": len(rows)}
