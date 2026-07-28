#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"

STATE_PATH = P4 / "PRIVATE_STAGE_STATE.json"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"
NEXT_PATH = P4 / "NEXT_TASK_PACKET.json"
HANDOFF_PATH = P4 / "CURRENT_HANDOFF.md"
PLAN_PATH = P4 / "OWNER_ASSIGNMENT_PLAN.json"

AUDIT_MD = "_phase4_proofread/AUDIT_YUWEN_MOWEN_TRAIN26_WAVE01_2026-07-28.md"
AUDIT_JSON = "_phase4_proofread/AUDIT_DECISIONS_YUWEN_MOWEN_TRAIN26_WAVE01_2026-07-28.json"
CHALLENGE_MD = "_phase4_proofread/QUALITY_CHALLENGE_YUWEN_MOWEN_TRAIN26_WAVE01_2026-07-28.md"

SOURCE = {
    "workflow": "Release train orchestrator",
    "run_id": 30348500770,
    "artifact_id": 8683907226,
    "artifact_name": "relation-audit-evidence",
    "artifact_file": "yuwen_mowen.json",
    "digest": "sha256:a6539172c7b9c86ce7a7c89742c887f5477eefd665b2bce6b62c8e6dae901f38",
    "head_sha": "a375bb348ae2ecf90b67537dd0cf0ab7eef32beb",
}

PACKETS = [
    {
        "packet_id": "yuwen-mowen-train26-packet-01",
        "candidate": "_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5274_1_2026-07-28.json",
        "scene_groups": ["5274_1"],
        "batch": 154,
        "rows": 7,
        "review": "_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH154_2026-07-28.md",
        "new_owner_file": "_phase4_proofread/fixes_relation_yuwen_mowen_20260728_batch64.json",
        "fix_key": "5274_1_Dlgs_Index4_Text",
        "old": "5002 - 莫問 $@$待て。平康城の悪党と言ったな？　今日、丐幇幇主の左江龍殿がお見えになった。どうやらその件らしく、今は師父や清霄師伯と殿内で話し合っておられる……",
        "new": "5002 - 莫問 $@$少し待ってくれ。平康城の悪党と言ったな？　今日、丐幇幇主の左江龍殿がお見えになった。どうやらその件らしく、今は師父や清霄師伯と殿内で話し合っておられる……",
        "reason": "原文「等等」は制止ではなく会話をいったん止める呼びかけ。弟弟子への穏やかな兄弟子口調として「少し待ってくれ」とする。",
        "fact_doubts": [
            "宇文逸は平康城で危険に遭ったが、悪党の正体や事件の全貌はこの場面では確定していない",
            "丐幇幇主の来訪目的は莫問の推測を含み、宇文逸の報告前に同一事件と断定しない",
        ],
    },
    {
        "packet_id": "yuwen-mowen-train26-packet-02",
        "candidate": "_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5278_1_2026-07-28.json",
        "scene_groups": ["5278_1"],
        "batch": 155,
        "rows": 14,
        "review": "_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH155_2026-07-28.md",
        "new_owner_file": "_phase4_proofread/fixes_relation_yuwen_mowen_20260728_batch65.json",
        "fix_key": "5278_1_Dlgs_Index8_Text",
        "old": "5002 - 莫問 $@$師弟、そう慌てるな。それほどの豪商なら、平康城にも知っている者は少なくないはずだ。",
        "new": "5002 - 莫問 $@$師弟、そう慌てるな。それほどの豪商なら、平康城には知っている者も少なくないはずだ。",
        "reason": "原文「平康城内」は比較を示さない。現訳の「にも」は他地域との比較を補うため、「平康城には／者も」として城内の見込みに戻す。",
        "fact_doubts": [
            "李員外の屋敷の場所はこの場面では未確認",
            "李員外の悪事について得られる手掛かりは可能性であり、聞き込み前に事実を補わない",
        ],
    },
    {
        "packet_id": "yuwen-mowen-train26-packet-03",
        "candidate": "_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5291_1_5292_3_2026-07-28.json",
        "scene_groups": ["5291_1", "5292_3"],
        "batch": 156,
        "rows": 12,
        "review": "_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH156_2026-07-28.md",
        "new_owner_file": "_phase4_proofread/fixes_relation_yuwen_mowen_20260728_batch66.json",
        "fix_key": "5292_3_Dlgs_Index1_Text",
        "old": "5002 - 莫問 $@$（小声で）心配するな。わたしは近道を使って、すぐ助けに向かう。二人はここで李天宝を足止めしてくれ。",
        "new": "5002 - 莫問 $@$（小声で）心配するな。わたしは近道を通って、すぐ助けに向かう。二人はここで李天宝を足止めしてくれ。",
        "reason": "原文「抄近道」は近道を通ること。日本語の移動表現として「近道を通って」に直し、救出分担の意味は変えない。",
        "fact_doubts": [
            "十八人の側室が全員さらわれたという宇文逸の発言は推測",
            "柴房の泣き声の主が捕らわれた娘かどうかは、この時点では未確認",
        ],
    },
    {
        "packet_id": "yuwen-mowen-train26-packet-04",
        "candidate": "_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5293_6_5293_7_2026-07-28.json",
        "scene_groups": ["5293_6", "5293_7"],
        "batch": 157,
        "rows": 7,
        "review": "_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH157_2026-07-28.md",
        "new_owner_file": "_phase4_proofread/fixes_relation_yuwen_mowen_20260728_batch67.json",
        "fix_key": "5293_6_Dlgs_Index3_Text",
        "old": "5002 - 莫問 $@$師弟、ためらうな……",
        "new": "5002 - 莫問 $@$師弟、何も気にする必要はない……",
        "reason": "原文「无需顾虑什么」は行動を促す「ためらうな」ではなく、官憲の圧力を懸念しなくてよいという意味。",
        "fact_doubts": [
            "絶無心の脅しは官憲全体の確定した処分ではなく、本人が示す圧力",
            "莫問の発言は公道を守る原則であり、官憲一般への無差別な敵対へ広げない",
        ],
    },
]

TOTALS = {
    "bundle_count": 4,
    "reviewed_rows": 40,
    "reviewed_keys": 40,
    "unique_reviewed_rows": 40,
    "fix_keys": 4,
    "unique_fix_rows": 4,
    "new_pair_keys": 0,
    "new_project_keys": 0,
    "cross_register_keys": 0,
    "existing_owner_updates": 4,
    "keep_only_bundles": 0,
}

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"top level must be object: {path}")
    return value

def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def candidate_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    value = load(ROOT / packet["candidate"])
    rows = value.get("rows")
    if not isinstance(rows, list):
        raise SystemExit(f"candidate rows missing: {packet['candidate']}")
    if len(rows) != packet["rows"]:
        raise SystemExit(f"candidate row count changed: {packet['candidate']}")
    by_key = {row.get("key"): row for row in rows if isinstance(row, dict)}
    row = by_key.get(packet["fix_key"])
    if not isinstance(row, dict) or row.get("ja") != packet["old"]:
        raise SystemExit(f"audited source changed for {packet['fix_key']}: {row!r}")
    return rows

def write_audit_records() -> None:
    decisions = []
    md = [
        "# 宇文逸↔莫問 train-26 wave-01 品質監査",
        "",
        "- stage: `private_quality_audit`",
        "- source: train-25 Relation artifact",
        "- scope: 4 packets / 40 unique rows",
        "- judgment basis: 原文・現訳・会話前後・人物関係を一次資料として、意味、声、関係性を場面単位で再読",
        "",
        "## 修正判断",
        "",
    ]
    for packet in PACKETS:
        rows = candidate_rows(packet)
        keep_keys = [row["key"] for row in rows if row["key"] != packet["fix_key"]]
        decisions.append({
            "packet_id": packet["packet_id"],
            "candidate": packet["candidate"],
            "scene_groups": packet["scene_groups"],
            "status": "audited",
            "fixes": [{
                "key": packet["fix_key"],
                "before": packet["old"],
                "after": packet["new"],
                "reason": packet["reason"],
            }],
            "keeps": keep_keys,
            "allusion_review_candidates": [],
            "allusion_review_resolved": [],
            "fact_doubts": packet["fact_doubts"],
        })
        md.extend([
            f"### 第{packet['batch']}束 — {' + '.join(packet['scene_groups'])}",
            "",
            f"- `{packet['fix_key']}`",
            f"- before: `{packet['old']}`",
            f"- after: `{packet['new']}`",
            f"- reason: {packet['reason']}",
            "",
        ])
    md.extend([
        "## challenged keep",
        "",
        "初回keep全件を、意味の強弱、莫問の兄弟子口調、宇文逸の武当内register、推測と確定情報の境界で再監査した。",
        "追加の高確度修正は出なかった。武侠呼称の「姑娘」と宇文逸の一人称「私」は人物資料と場面に整合するため保持した。",
        "",
        "## 結論",
        "",
        "四件を実変更としてencodingへ送る。残りは好みだけの言い換えを避け、現訳を保持する。",
        "",
    ])
    (ROOT / AUDIT_MD).write_text("\n".join(md), encoding="utf-8")
    write(ROOT / AUDIT_JSON, {
        "schema_version": 1,
        "train_id": "yuwen-mowen-train-26",
        "wave_id": "yuwen-mowen-train-26-wave-01",
        "stage": "private_quality_audit",
        "status": "complete",
        "source_artifact": SOURCE,
        "decisions": decisions,
    })
    (ROOT / CHALLENGE_MD).write_text(
        "\n".join([
            "# 宇文逸↔莫問 train-26 低yield challenge",
            "",
            "- scope: `all_initial_keep_unique_rows`",
            "- initial fixes: 4",
            "- challenged initial keeps: 36",
            "- additional findings: 0",
            "- final fixes: 4",
            "",
            "四packetの初回keep全件を再読した。原文の意味、話者、相手、時系列、制御タグ、人物ペルソナを再照合した。",
            "「姑娘」は武侠世界の対外女性呼称として保持し、宇文逸の「私」も基調一人称として保持した。",
            "推測を確定事実へ強める行、別人物registerを宇文逸↔莫問へ混入する行、追加の意味誤りは見つからなかった。",
            "",
        ]),
        encoding="utf-8",
    )

def set_audit_stage() -> None:
    write_audit_records()
    state = load(STATE_PATH)
    state["stage"] = "private_quality_audit"
    state["cycle_control"].update({
        "status": "running",
        "continuation_required": True,
        "stop_reason": None,
        "exact_next_action": "監査済み四packetをprivate_encodingへ送り、owner assignmentを行う。",
        "last_safe_checkpoint": "private_quality_audit",
    })
    wave = state["wave"]
    wave.pop("preparation_summary", None)
    for packet_state, packet in zip(wave["packets"], PACKETS):
        if packet_state.get("packet_id") != packet["packet_id"]:
            raise SystemExit("packet order changed before audit")
        packet_state["status"] = "audited"
        packet_state["audit_record"] = {
            "status": "complete",
            "record": AUDIT_MD,
            "decision_record": AUDIT_JSON,
        }
    state["permissions"] = {
        "translation_judgment_allowed": True,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": False,
        "metrics_frozen": True,
    }
    state["history"] = [
        {"stage": "private_preparation", "status": "complete"},
        {"stage": "private_quality_audit", "status": "active"},
    ]
    write(STATE_PATH, state)

    current = load(CURRENT_PATH)
    current["operation_mode"]["declared_state"] = "private_translation_work"
    current["immediate_next"] = {
        "scene_groups": [scene for packet in PACKETS for scene in packet["scene_groups"]],
        "task": "監査済みtrain-26 wave-01をprivate_encodingへ送り、owner assignmentを行う。",
        "boundary": "encoding完了前にrelease-ciを開始しない。",
        "packet": "_phase4_proofread/PRIVATE_STAGE_STATE.json",
    }
    current_train = current["ci_train"]
    current_train.update({
        "status": "accumulating",
        "transport_status": "not_ready",
        "draft_pr": 162,
    })
    current_train["private_stage"] = {
        "stage": "private_quality_audit",
        "status": "complete",
        "transport_status": "not_ready",
        "wave_id": "yuwen-mowen-train-26-wave-01",
        "cycle_status": "running",
        "cycle_checkpoint": "private_quality_audit",
    }
    write(CURRENT_PATH, current)

    manifest = load(MANIFEST_PATH)
    manifest["draft_pr"] = 162
    manifest["status"] = "accumulating"
    manifest["transport"] = {
        "status": "not_ready",
        "translation_stage": "private_quality_audit",
        "pr": 162,
    }
    manifest["private_stage"] = {
        "stage": "private_quality_audit",
        "status": "complete",
        "transport_status": "not_ready",
        "wave_id": "yuwen-mowen-train-26-wave-01",
    }
    manifest["next_release"].update({
        "reservation_status": "quality_audited",
        "current_private_stage": "private_quality_audit",
    })
    write(MANIFEST_PATH, manifest)

def review_text(packet: dict[str, Any]) -> str:
    return "\n".join([
        f"# 宇文逸↔莫問 第{packet['batch']}束 review",
        "",
        f"- scenes: `{', '.join(packet['scene_groups'])}`",
        f"- candidate: `{packet['candidate']}`",
        f"- source artifact: run `{SOURCE['run_id']}` / artifact `{SOURCE['artifact_id']}`",
        "",
        "## 実変更",
        "",
        f"- key: `{packet['fix_key']}`",
        f"- before: `{packet['old']}`",
        f"- after: `{packet['new']}`",
        f"- reason: {packet['reason']}",
        "",
        "## 保持判断",
        "",
        "同一packetの残り全行は、原文の意味、話者register、時系列、制御タグを再確認し、実質的な欠陥がないため保持した。",
        "好みだけの言い換え、場面以上の事実補完、別人物の声の一括変更は行っていない。",
        "",
    ])

def set_frozen_stage() -> None:
    for packet in PACKETS:
        candidate_rows(packet)
        (ROOT / packet["review"]).write_text(review_text(packet), encoding="utf-8")

    state = load(STATE_PATH)
    state["stage"] = "translation_frozen"
    state["cycle_control"].update({
        "status": "running",
        "continuation_required": True,
        "stop_reason": None,
        "exact_next_action": "PR #162へrelease-ciを付与し、public CI・apply・finalizationを実行する。",
        "last_safe_checkpoint": "translation_frozen",
    })
    wave = state["wave"]
    for packet_state, packet in zip(wave["packets"], PACKETS):
        packet_state["status"] = "encoded"
        packet_state["formal_batch"] = packet["batch"]
        packet_state["audit_record"] = {
            "status": "complete",
            "record": AUDIT_MD,
            "decision_record": AUDIT_JSON,
        }
        packet_state["review_record"] = {
            "status": "complete",
            "record": packet["review"],
        }
    wave["encoding_summary"] = dict(TOTALS)
    state["transport"] = {
        "status": "ready_for_public_ci",
        "history": [
            {"status": "not_ready", "translation_stage": "private_preparation"},
            {"status": "ready_for_public_ci", "translation_stage": "translation_frozen"},
        ],
    }
    state["permissions"] = {
        "translation_judgment_allowed": False,
        "fix_writes_allowed": False,
        "encoding_writes_allowed": False,
        "throughput_metrics_visible": True,
        "metrics_frozen": False,
    }
    state["history"] = [
        {"stage": "private_preparation", "status": "complete"},
        {"stage": "private_quality_audit", "status": "complete"},
        {"stage": "private_encoding", "status": "complete"},
        {"stage": "translation_frozen", "status": "active"},
    ]
    write(STATE_PATH, state)

    bundles = []
    for packet in PACKETS:
        bundles.append({
            "batch": packet["batch"],
            "review_status": "complete",
            "apply_status": "pending",
            "scene_groups": packet["scene_groups"],
            "reviewed_rows": packet["rows"],
            "reviewed_keys": packet["rows"],
            "unique_rows": packet["rows"],
            "fix_keys": 1,
            "unique_fix_rows": 1,
            "new_pair_keys": 0,
            "new_project_keys": 0,
            "cross_register_keys": 0,
            "existing_owner_updates": 1,
            "keep_keys": packet["rows"] - 1,
            "fix_files": [packet["new_owner_file"]],
            "review_record": packet["review"],
            "ownership_summary": {
                "existing_keys": packet["rows"],
                "unowned_kept": 0,
                "new_keys": 0,
                "cross_register_keys": 0,
            },
            "allusion_review_candidates": [],
            "allusion_review_resolved": [],
            "fact_doubts": packet["fact_doubts"],
            "source_artifact": SOURCE,
        })

    manifest = load(MANIFEST_PATH)
    manifest.update({
        "draft_pr": 162,
        "status": "ready_for_public_ci",
        "transport": {
            "status": "ready_for_public_ci",
            "translation_stage": "translation_frozen",
            "pr": 162,
        },
        "release_trigger": None,
        "finalization_phase": "phase2",
        "totals": dict(TOTALS),
        "bundles": bundles,
        "quality_gate": {
            "schema_version": 1,
            "primary_objective": "repair_substantive_translation_defects",
            "throughput_metrics_role": "transport_only",
            "low_yield_threshold_percent": 15,
            "reviewed_keys": 40,
            "unique_reviewed_rows": 40,
            "fix_keys": 4,
            "unique_fix_rows": 4,
            "keep_only_bundles": 0,
            "pre_challenge_unique_fix_rows": 4,
            "low_yield_detected": True,
            "release_decision": "quality_passed",
            "challenge_pass": {
                "status": "complete",
                "scope": "all_initial_keep_unique_rows",
                "reviewed_candidate_keep_rows": 36,
                "findings_unique_rows": 0,
                "finding_keys": 0,
                "record": CHALLENGE_MD,
            },
        },
        "private_stage": {
            "stage": "translation_frozen",
            "status": "complete",
            "transport_status": "ready_for_public_ci",
            "wave_id": "yuwen-mowen-train-26-wave-01",
        },
        "next_release": {
            "candidate_scene": ["5296_7"],
            "reservation_status": "reserved_only",
            "reservation_schema": 6,
            "formal_batches": [154, 155, 156, 157],
            "current_private_stage": "translation_frozen",
        },
    })
    write(MANIFEST_PATH, manifest)

    current = load(CURRENT_PATH)
    current["last_reviewed_batch"] = 157
    current["operation_mode"]["declared_state"] = "translation_frozen"
    current["immediate_next"] = {
        "scene_groups": ["5296_7"],
        "task": "PR #162へrelease-ciを付与し、public CI・fix適用・release finalizationを同一PRで完了する。",
        "boundary": "verified checkpoint前にmergeしない。ゲームフォルダへ配置しない。",
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    current_train = current["ci_train"]
    current_train.update({
        "status": "ready_for_public_ci",
        "transport_status": "ready_for_public_ci",
        "draft_pr": 162,
        "policy": "_phase4_proofread/CI_TRAIN_PHASE2.md",
        "post_merge_state_pr_required": False,
        "single_pr_finalization": True,
        "totals": dict(TOTALS),
        "finalization_phase": "phase2",
    })
    current_train["private_stage"] = {
        "stage": "translation_frozen",
        "status": "complete",
        "transport_status": "ready_for_public_ci",
        "wave_id": "yuwen-mowen-train-26-wave-01",
        "cycle_status": "running",
        "cycle_checkpoint": "translation_frozen",
    }
    write(CURRENT_PATH, current)

    write(PLAN_PATH, {
        "schema_version": 1,
        "packets": [
            {
                "candidate": packet["candidate"],
                "new_owner_file": packet["new_owner_file"],
                "values": {packet["fix_key"]: packet["new"]},
                "fix_keys": [packet["fix_key"]],
            }
            for packet in PACKETS
        ],
    })

    write(NEXT_PATH, {
        "schema_version": 6,
        "status": "ready",
        "task_id": "post-train26-minimal-wave-reservation",
        "based_on_checkpoint": {
            "batch": 153,
            "pair_applied_keys": 1351,
            "project_applied_keys": 1727,
            "produced_by_pr": 154,
            "release_id": "yuwen-mowen-train-25-r1",
            "release_evidence": "_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_25.json",
        },
        "current_pair": "宇文逸↔莫問",
        "scene_groups": ["5296_7"],
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
            "artifact_run": 30348500770,
            "artifact_id": 8683907226,
            "artifact_digest": SOURCE["digest"],
            "artifact_head": SOURCE["head_sha"],
            "freshness_rule": "train-26統合後、次cycleのpreparation開始時に最新Relation artifactで5296_7と近接場面を再確認する。",
        },
        "release_candidate": {
            "train_id": "yuwen-mowen-train-26",
            "release_id": "yuwen-mowen-train-26-r1",
            "pr": 162,
            "status": "ready_for_public_ci",
            "merge_sha": None,
        },
        "do_not_do": [
            "minimal reservationへfocus key・voice question・FACT_DOUBT・owner snapshot・batch planningを戻さない",
            "次cycleのexecution modeをCURRENT_WORKとPRIVATE_STAGE_STATEへlockする前にpreparationを開始しない",
            "ゲームフォルダへ配置しない",
        ],
        "ci_train": {
            "phase": "phase1_wave",
            "train_id": "yuwen-mowen-train-26",
            "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
            "planned_batch": 158,
            "post_merge_state_pr_required": False,
            "single_pr_finalization": True,
        },
    })

    HANDOFF_PATH.write_text(
        "\n".join([
            "# 現在の申し送り",
            "",
            "> 再開指示: `現状把握して作業の続きを`",
            ">",
            "> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。",
            "",
            "## 現在地",
            "",
            "- translation PR #162: draft / active",
            "- train: `yuwen-mowen-train-26`",
            "- private stage: `translation_frozen`",
            "- transport: `ready_for_public_ci`",
            "- execution mode: `always_public_full_pipeline`",
            "- wave: 4 packets / 40 rows / 4 fixes / batches 154–157",
            "- verified checkpoint: 第153束 / pair 1351 / project 1727（train-25）",
            "- 次候補: `5296_7`（schema v6 minimal reservation）",
            "",
            "## 次の作業",
            "",
            "PR #162へ`release-ci`を付与し、preflight、relation、cross-register、apply、release finalization、verified checkpoint、squash mergeまで同一cycleで続ける。",
            "",
            "## 禁止",
            "",
            "- verified checkpoint前にmergeしない。",
            "- translation_frozen後に翻訳判断やowner手書きを再開しない。",
            "- minimal reservationへprivate preparation詳細を先書きしない。",
            "- ゲームフォルダへ配置しない。",
            "",
        ]),
        encoding="utf-8",
    )

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["audit", "freeze"])
    args = parser.parse_args()
    if args.mode == "audit":
        set_audit_stage()
    else:
        set_frozen_stage()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
