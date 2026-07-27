#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CI_HEAD = "b0af4fe28b35a8543b6b7a38107b8c5ec55b0962"
ASSET_HEAD = "2cbbcd988e45fc995a535fb01da95e817cbea89d"
RUN_ID = 30253238587
RELATION_ARTIFACT_ID = 8647833757
RELATION_DIGEST = "sha256:0f228745eb0760b77de95bf9a27cd7be43ae78e1d6ff7d6effe6249bf0a7676a"
PR = 141
RELEASE_ID = "yuwen-mowen-train-16-r1"
EVIDENCE_REL = "_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_16.json"
APPLIED_REL = "_phase4_proofread/APPLIED_FIXES_YUWEN_MOWEN_BATCH114_2026-07-27.md"
PAIR_KEYS = 1188
PROJECT_KEYS = 1564
BATCH = 114


def load(name: str) -> dict:
    value = json.loads((P4 / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name}: top level must be object")
    return value


def write(name: str, value: dict) -> None:
    (P4 / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    evidence = {
        "schema_version": 2,
        "status": "verified",
        "release_id": RELEASE_ID,
        "train_id": "yuwen-mowen-train-16",
        "pr": PR,
        "ci_head": CI_HEAD,
        "asset_head": ASSET_HEAD,
        "applied_record": APPLIED_REL,
        "counts": {
            "batch": BATCH,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "pending_fixes": 0,
        },
        "orchestrator": {
            "id": RUN_ID,
            "workflow": "Release train orchestrator",
            "head_sha": CI_HEAD,
            "event": "pull_request",
            "conclusion": "success",
        },
        "lineage": {"mode": "branch_ancestor", "merge_sha": None},
        "notes": [
            "第113〜114束は40 reviewed keys・40 unique reviewed rows・8修正キーとして確定した",
            "40行のlive owner実測は既存owner所属34・新規owner6・複数owner0で、既存owner値更新は8件だった",
            "owner assignment v2は未変更owner bytesを保持して全owner digestを再封印し、完全preflightで検証した",
            f"orchestrator run {RUN_ID}で完全preflight、Relation、Cross、Apply、pak再生成、未適用0件、finalization入力生成を成功させた",
            f"Apply bot asset HEAD {ASSET_HEAD}で適用記録とaudit statusを第114束へ同期した",
            "次候補9150_3はminimal reservationのまま保持し、PR #141統合前にはprivate preparationを開始しない",
        ],
    }
    write("RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_16.json", evidence)

    manifest = load("CI_TRAIN_MANIFEST.json")
    manifest["status"] = "verified"
    manifest["transport"].update({"status": "awaiting_private_merge", "translation_stage": "translation_frozen", "pr": PR, "merge_sha": None})
    for bundle in manifest["bundles"]:
        bundle["apply_status"] = "verified"
    applied_result = {
        "orchestrator_run": RUN_ID,
        "asset_head": ASSET_HEAD,
        "pair_applied_keys": PAIR_KEYS,
        "project_applied_keys": PROJECT_KEYS,
        "pending_fixes": 0,
        "checkpoint_status": "verified",
    }
    verified_result = {
        "release_id": RELEASE_ID,
        "release_evidence": EVIDENCE_REL,
        "record_index_synced": True,
        "pair_applied_keys": PAIR_KEYS,
        "project_applied_keys": PROJECT_KEYS,
        "pending_fixes": 0,
    }
    manifest["applied_result"] = applied_result
    manifest["verified_result"] = verified_result
    manifest["private_stage"].update({"stage": "translation_frozen", "status": "verified", "transport_status": "awaiting_private_merge"})
    write("CI_TRAIN_MANIFEST.json", manifest)

    state = load("PRIVATE_STAGE_STATE.json")
    state["cycle_control"].update({
        "status": "target_reached",
        "continuation_required": False,
        "stop_reason": None,
        "exact_next_action": None,
        "last_safe_checkpoint": "awaiting_private_merge",
    })
    for packet in state["wave"]["packets"]:
        packet["review_record"]["apply_status"] = "verified"
    state["transport"]["status"] = "awaiting_private_merge"
    state["transport"]["history"] = [
        {"status": "not_ready", "translation_stage": "private_encoding"},
        {"status": "ready_for_public_ci", "translation_stage": "translation_frozen", "pr": PR},
        {"status": "in_public_ci", "translation_stage": "translation_frozen", "pr": PR},
        {"status": "verified", "translation_stage": "translation_frozen", "pr": PR, "release_id": RELEASE_ID},
        {"status": "awaiting_private_merge", "translation_stage": "translation_frozen", "pr": PR, "release_id": RELEASE_ID},
    ]
    state["transport"]["pr"] = PR
    state["verified_result"] = {
        "release_id": RELEASE_ID,
        "evidence": EVIDENCE_REL,
        "ci_head": CI_HEAD,
        "asset_head": ASSET_HEAD,
        "pending_fixes": 0,
    }
    write("PRIVATE_STAGE_STATE.json", state)

    work = load("CURRENT_WORK.json")
    work.update({
        "status": "verified",
        "last_completed_batch": BATCH,
        "last_reviewed_batch": BATCH,
        "pair_applied_keys": PAIR_KEYS,
        "project_applied_keys": PROJECT_KEYS,
    })
    work["checkpoint"] = {
        "status": "verified",
        "batch": BATCH,
        "pair_applied_keys": PAIR_KEYS,
        "project_applied_keys": PROJECT_KEYS,
        "applied_record": APPLIED_REL,
        "produced_by_pr": PR,
        "release_identity": {
            "kind": "pr_release_v2",
            "release_id": RELEASE_ID,
            "evidence": EVIDENCE_REL,
            "pr": PR,
            "validated_head": ASSET_HEAD,
        },
    }
    work["immediate_next"] = {
        "scene_groups": ["9150_3"],
        "task": "PR #141のphase2成功と未解決review thread 0件を確認し、private復帰後にsquash統合する。",
        "boundary": "public中は翻訳判断、fix追加、owner変更、第115束preparationを開始しない。",
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    train = work["ci_train"]
    train.update({
        "status": "verified",
        "transport_status": "awaiting_private_merge",
        "draft_pr": PR,
        "applied_result": applied_result,
        "verified_result": verified_result,
    })
    train["private_stage"].update({
        "stage": "translation_frozen",
        "status": "verified",
        "transport_status": "awaiting_private_merge",
        "cycle_status": "target_reached",
        "cycle_checkpoint": "awaiting_private_merge",
    })
    write("CURRENT_WORK.json", work)

    packet = {
        "schema_version": 6,
        "status": "ready",
        "task_id": "post-train16-minimal-wave-reservation",
        "based_on_checkpoint": {
            "batch": BATCH,
            "pair_applied_keys": PAIR_KEYS,
            "project_applied_keys": PROJECT_KEYS,
            "produced_by_pr": PR,
            "release_id": RELEASE_ID,
            "release_evidence": EVIDENCE_REL,
        },
        "current_pair": "宇文逸↔莫問",
        "scene_groups": ["9150_3"],
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
            "artifact_workflow": "Release train orchestrator",
            "artifact_name": "relation-audit-evidence",
            "artifact_file": "yuwen_mowen.json",
            "artifact_run": RUN_ID,
            "artifact_id": RELATION_ARTIFACT_ID,
            "artifact_digest": RELATION_DIGEST,
            "artifact_head": CI_HEAD,
            "freshness_rule": "train-16のsquash統合後、private preparation開始時に最新Relation artifactで9150_3と後続候補を再確認し、focus key・人物声・owner snapshot・batch planningはcandidate側で新規生成する。",
        },
        "release_candidate": {
            "train_id": "yuwen-mowen-train-16",
            "release_id": RELEASE_ID,
            "pr": PR,
            "status": "verified",
            "merge_sha": None,
        },
        "do_not_do": [
            "minimal reservationへfocus key・voice question・FACT_DOUBT・owner snapshot・batch planningを戻さない",
            "PR #141統合前に9150_3のprivate preparationを開始しない",
            "public中に翻訳判断、fix追加、owner変更、正式束追加を行わない",
            "ゲームフォルダへ配置しない",
        ],
        "ci_train": {
            "phase": "phase1_wave",
            "train_id": "yuwen-mowen-train-16",
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "planned_batch": 115,
            "post_merge_state_pr_required": False,
            "single_pr_finalization": True,
        },
    }
    write("NEXT_TASK_PACKET.json", packet)

    handoff = f"""# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: public
- PR #141: open / ready / mergeable
- train: `yuwen-mowen-train-16`
- verified checkpoint: 第114束
- last reviewed batch: 第114束
- 人物ペア適用済みowner: 1188
- プロジェクト全体適用済み: 1564
- private stage: `translation_frozen`
- train-16 transport: `awaiting_private_merge`
- cycle control: `target_reached / awaiting_private_merge`

## train-16

`6195_3 + 6198_3 + 6206_3`と`6213_1 + 6214_4 + 6229_1`を二packet・40行で連続監査し、8行を修正、32行を意図的保持とした。莫問敗北後の死の受容、宇文逸の師兄呼称と離別への恐れ、傷薬の語法、分岐別の再戦宣言を原文と関係段階へ戻した。

live owner再計測の結果、40行のうち34行は既存owner所属、6行だけが新規ownerだった。既存ownerへ8件の訳値変更を反映し、複数ownerは0件。owner生成器は未変更owner bytesを保持して全owner digestを再封印するよう修正し、回帰テストへ固定した。

orchestrator run `{RUN_ID}`で完全preflight、Relation、Cross、Apply、pak再生成、未適用0件、finalization入力生成まで成功した。asset HEADは`{ASSET_HEAD}`。

## 次の作業

最新HEADで`finalize-release`によるphase2 gateと未解決review thread 0件を確認する。完了後はrepositoryをprivateへ戻し、検証済みHEADをsquash統合する。

次waveは`9150_3`だけを最小予約している。PR #141統合前にpreparationを開始しない。

## 禁止

- public中に翻訳判断、fix追加、owner変更、正式束追加を行わない。
- private復帰前にPR #141をmergeしない。
- PR #141統合前に`9150_3`のpreparationを始めない。
- ゲームフォルダへ配置しない。
"""
    (P4 / "CURRENT_HANDOFF.md").write_text(handoff, encoding="utf-8")


if __name__ == "__main__":
    main()
