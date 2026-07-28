#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"

PR = 162
TRAIN = "yuwen-mowen-train-26"
RELEASE = "yuwen-mowen-train-26-r1"
CI_HEAD = "e75dcf356b8aed33066dff77ac04468cab5cb4a4"
ASSET_HEAD = "b8e1a735b7518e4472d514d12a6aac3cd56ddd94"
ORCHESTRATOR_RUN = 30360391808
BATCH = 157
PAIR_KEYS = 1351
PROJECT_KEYS = 1727
APPLIED = "_phase4_proofread/APPLIED_FIXES_YUWEN_MOWEN_BATCH157_2026-07-28.md"
EVIDENCE = "_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_26.json"
NEXT_SCENES = ["5296_7"]
RELATION_ARTIFACT = {
    "artifact_workflow": "Release train orchestrator",
    "artifact_name": "relation-audit-evidence",
    "artifact_file": "yuwen_mowen.json",
    "artifact_run": ORCHESTRATOR_RUN,
    "artifact_id": 8688546867,
    "artifact_digest": "sha256:811e4e8fa0930d636e736c7371effbfa963e8445262ca5f9adca2e7e702a0ef1",
    "artifact_head": CI_HEAD,
}


def load(name: str) -> dict[str, Any]:
    value = json.loads((P4 / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{name}: top level must be object")
    return value


def write(name: str, value: dict[str, Any]) -> None:
    (P4 / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalize_current() -> None:
    current = load("CURRENT_WORK.json")
    current.update({
        "status": "verified",
        "last_completed_batch": BATCH,
        "last_reviewed_batch": BATCH,
        "pair_applied_keys": PAIR_KEYS,
        "project_applied_keys": PROJECT_KEYS,
        "build_status": "verified_not_deployed",
        "game_verified": "not_started",
        "checkpoint": {
            "status": "verified",
            "batch": BATCH,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "produced_by_pr": PR,
            "release_identity": {
                "kind": "pr_release_v2",
                "release_id": RELEASE,
                "evidence": EVIDENCE,
                "pr": PR,
                "validated_head": ASSET_HEAD,
            },
            "applied_record": APPLIED,
        },
        "immediate_next": {
            "scene_groups": NEXT_SCENES,
            "task": "PR #162のfinalize-release phase2と未解決review thread 0件を確認し、検証済みHEADをsquash統合する。",
            "boundary": "translation_frozen後は翻訳判断、fix追加、owner変更、正式束追加を行わない。",
            "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
        },
        "release_evidence": EVIDENCE,
    })
    train = current["ci_train"]
    train.update({
        "status": "verified",
        "transport_status": "awaiting_private_merge",
        "caps": {"bundle_count": 6, "reviewed_rows": 80},
        "finalization_phase": "phase2",
        "post_merge_state_pr_required": False,
        "single_pr_finalization": True,
        "applied_result": {
            "orchestrator_run": ORCHESTRATOR_RUN,
            "asset_head": ASSET_HEAD,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "pending_fixes": 0,
            "checkpoint_status": "verified",
        },
        "verified_result": {
            "release_id": RELEASE,
            "release_evidence": EVIDENCE,
            "record_index_synced": True,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "pending_fixes": 0,
        },
        "release_evidence": EVIDENCE,
    })
    train["private_stage"].update({
        "stage": "translation_frozen",
        "status": "verified",
        "transport_status": "awaiting_private_merge",
        "cycle_status": "running",
        "cycle_checkpoint": "awaiting_private_merge",
    })
    write("CURRENT_WORK.json", current)


def finalize_manifest() -> None:
    manifest = load("CI_TRAIN_MANIFEST.json")
    manifest.update({
        "status": "verified",
        "caps": {"bundle_count": 6, "reviewed_rows": 80},
        "transport": {
            "status": "awaiting_private_merge",
            "translation_stage": "translation_frozen",
            "pr": PR,
            "merge_sha": None,
        },
        "release_evidence": EVIDENCE,
        "finalization_phase": "phase2",
        "post_merge_state_pr_required": False,
        "single_pr_finalization": True,
    })
    for bundle in manifest.get("bundles", []):
        if isinstance(bundle, dict):
            bundle["apply_status"] = "verified"
    manifest["private_stage"].update({
        "stage": "translation_frozen",
        "status": "verified",
        "transport_status": "awaiting_private_merge",
    })
    manifest["next_release"].update({
        "candidate_scene": NEXT_SCENES,
        "reservation_status": "reserved_only",
        "reservation_schema": 6,
        "formal_batches": [154, 155, 156, 157],
        "current_private_stage": "translation_frozen",
    })
    write("CI_TRAIN_MANIFEST.json", manifest)


def finalize_private_state() -> None:
    state = load("PRIVATE_STAGE_STATE.json")
    state["cycle_control"].update({
        "status": "running",
        "continuation_required": True,
        "stop_reason": None,
        "exact_next_action": "PR #162のfinalize-release phase2とreview thread 0件を確認し、検証済みHEADをsquash mergeする",
        "last_safe_checkpoint": "awaiting_private_merge",
    })
    for packet in state.get("wave", {}).get("packets", []):
        if isinstance(packet, dict):
            packet.setdefault("review_record", {})["apply_status"] = "verified"
    state["transport"] = {
        "status": "awaiting_private_merge",
        "history": [
            {"status": "not_ready", "translation_stage": "private_preparation"},
            {"status": "ready_for_public_ci", "translation_stage": "translation_frozen", "pr": PR},
            {"status": "in_public_ci", "translation_stage": "translation_frozen", "pr": PR},
            {"status": "verified", "translation_stage": "translation_frozen", "pr": PR, "release_id": RELEASE},
            {"status": "awaiting_private_merge", "translation_stage": "translation_frozen", "pr": PR, "release_id": RELEASE},
        ],
        "pr": PR,
        "merge_sha": None,
    }
    state["verified_result"] = {
        "release_id": RELEASE,
        "evidence": EVIDENCE,
        "ci_head": CI_HEAD,
        "asset_head": ASSET_HEAD,
        "pending_fixes": 0,
    }
    write("PRIVATE_STAGE_STATE.json", state)


def finalize_next_packet() -> None:
    packet = load("NEXT_TASK_PACKET.json")
    packet.update({
        "status": "ready",
        "task_id": "post-train26-minimal-wave-reservation",
        "based_on_checkpoint": {
            "batch": BATCH,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "produced_by_pr": PR,
            "release_id": RELEASE,
            "release_evidence": EVIDENCE,
        },
        "current_pair": "宇文逸↔莫問",
        "scene_groups": NEXT_SCENES,
        "reservation": {
            "status": "reserved_only",
            "wave_id": None,
            "packet_id": None,
            "preparation_started": False,
            "quality_audit_started": False,
            "encoding_started": False,
            "formal_batch": None,
        },
        "source": {
            **RELATION_ARTIFACT,
            "freshness_rule": "train-26統合後、次cycleのpreparation開始時に最新Relation artifactで5296_7と近接場面を再確認する。",
        },
        "release_candidate": {
            "train_id": TRAIN,
            "release_id": RELEASE,
            "pr": PR,
            "status": "verified",
            "merge_sha": None,
        },
        "do_not_do": [
            "minimal reservationへfocus key・voice question・FACT_DOUBT・owner snapshot・batch planningを戻さない",
            "train-26統合前に5296_7のpreparationを開始しない",
            "translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない",
            "ゲームフォルダへ配置しない",
        ],
        "ci_train": {
            "phase": "phase1_wave",
            "train_id": TRAIN,
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "planned_batch": 158,
            "post_merge_state_pr_required": False,
            "single_pr_finalization": True,
        },
    })
    write("NEXT_TASK_PACKET.json", packet)


def write_evidence() -> None:
    write("RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_26.json", {
        "schema_version": 2,
        "status": "verified",
        "release_id": RELEASE,
        "train_id": TRAIN,
        "pr": PR,
        "ci_head": CI_HEAD,
        "asset_head": ASSET_HEAD,
        "applied_record": APPLIED,
        "counts": {
            "batch": BATCH,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "pending_fixes": 0,
        },
        "orchestrator": {
            "id": ORCHESTRATOR_RUN,
            "workflow": "Release train orchestrator",
            "head_sha": CI_HEAD,
            "event": "pull_request",
            "conclusion": "success",
        },
        "lineage": {"mode": "branch_ancestor", "merge_sha": None},
        "notes": [
            "第154〜157束は40 reviewed keys・40 unique reviewed rows・4修正キーとして確定した",
            "live owner実測は新規owner0・既存owner値更新4・複数owner0だった",
            "莫問の兄弟子口調、平康城内の情報範囲、近道表現、官憲への懸念の意味を修正した",
            "初回keep36行を再監査し、武侠呼称の姑娘と宇文逸の一人称は人物資料に従って保持した",
            "orchestrator run 30360391808で完全preflight、Relation、Cross、Apply、pak再生成、未適用0件、finalization入力生成を成功させた",
            "Apply bot asset HEAD b8e1a735b7518e4472d514d12a6aac3cd56ddd94で適用記録とaudit statusを第157束へ同期した",
            "次候補5296_7はminimal reservationのまま保持し、PR #162統合前にはpreparationを開始しない",
        ],
    })


def write_handoff() -> None:
    (P4 / "CURRENT_HANDOFF.md").write_text("\n".join([
        "# 現在の申し送り",
        "",
        "> 再開指示: `現状把握して作業の続きを`",
        ">",
        "> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。",
        "",
        "## 現在地",
        "",
        "- 実visibility: public",
        "- PR #162: open / ready / mergeable",
        f"- train: `{TRAIN}`",
        f"- verified checkpoint: 第{BATCH}束 / pair {PAIR_KEYS} / project {PROJECT_KEYS}",
        f"- last reviewed batch: 第{BATCH}束",
        "- private stage: `translation_frozen`",
        "- train-26 transport: `awaiting_private_merge`",
        "- queue: 4packet / 40行 / 4修正 / 36保持",
        "",
        "## train-26",
        "",
        "平康城への帰還報告、李員外の聞き込み、李府の救出分担、官憲をめぐる対立までを監査した。live owner実測は新規owner 0、既存owner更新4、複数owner0。",
        "",
        f"orchestrator run `{ORCHESTRATOR_RUN}`で完全preflight、Relation、Cross、Apply、pak再生成、未適用0件、finalization入力生成まで成功した。asset HEADは`{ASSET_HEAD}`。",
        "",
        "## 次の作業",
        "",
        "PR #162の`finalize-release` phase2と未解決review thread 0件を確認し、検証済みHEADをsquash統合する。always-public cycleなのでvisibility変更は要求しない。",
        "",
        "次候補`5296_7`はminimal reservationのまま保持し、train-26統合前にpreparationを開始しない。",
        "",
        "## 禁止",
        "",
        "- translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない。",
        "- phase2成功前にPR #162をmergeしない。",
        "- train-26統合前に`5296_7`のpreparationを始めない。",
        "- ゲームフォルダへ配置しない。",
        "",
    ]), encoding="utf-8")


def main() -> int:
    finalize_current()
    finalize_manifest()
    finalize_private_state()
    finalize_next_packet()
    write_evidence()
    write_handoff()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
