#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seal a merged tail release as a paused pair-completion checkpoint."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pair_tail_common import P4, SENTINEL_SCENE, TailError, load_object, write_json, write_text

EXACT_NEXT = "宇文逸↔莫問の完了checkpointを確認し、次人物ペアの証拠inventoryをbootstrapする"


def seal(p4: Path = P4) -> bool:
    current = load_object(p4 / "CURRENT_WORK.json")
    state = load_object(p4 / "PRIVATE_STAGE_STATE.json")
    manifest = load_object(p4 / "CI_TRAIN_MANIFEST.json")
    packet = load_object(p4 / "NEXT_TASK_PACKET.json")
    audit = load_object(p4 / "audit_status.json")
    completion = packet.get("pair_completion")
    if not isinstance(completion, dict) or completion.get("status") != "complete":
        return False
    if packet.get("release_candidate", {}).get("status") != "merged":
        return False
    statuses = (
        current.get("ci_train", {}).get("transport_status"),
        state.get("transport", {}).get("status"),
        manifest.get("transport", {}).get("status"),
    )
    if statuses != ("merged", "merged", "merged"):
        return False
    already = (
        state.get("cycle_control", {}).get("status") == "paused"
        and state.get("cycle_control", {}).get("exact_next_action") == EXACT_NEXT
        and manifest.get("next_release", {}).get("reservation_status") == "pair_complete"
    )
    if already:
        return False

    control = state.setdefault("cycle_control", {})
    control.update(
        {
            "status": "paused",
            "continuation_required": True,
            "stop_reason": "pair_scope_exhausted",
            "exact_next_action": EXACT_NEXT,
            "last_safe_checkpoint": "merged_pair_complete",
        }
    )
    state["pair_completion"] = completion
    current.setdefault("ci_train", {}).setdefault("private_stage", {}).update(
        {
            "cycle_status": "pair_complete",
            "cycle_checkpoint": "merged_pair_complete",
        }
    )
    current["ci_train"]["pair_completion"] = completion
    current["immediate_next"] = {
        "scene_groups": [SENTINEL_SCENE],
        "task": EXACT_NEXT + "。",
        "boundary": "次人物ペアの正本とRelation evidenceを確定するまで、翻訳準備・判断・owner書込みを開始しない。",
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    manifest.setdefault("next_release", {}).update(
        {
            "candidate_scene": [SENTINEL_SCENE],
            "reservation_status": "pair_complete",
            "current_private_stage": "translation_frozen",
        }
    )
    manifest["pair_completion"] = completion
    packet["scene_groups"] = [SENTINEL_SCENE]
    packet["pair_completion"] = completion
    packet["do_not_do"] = [
        "pair completionを通常scene reservationへ戻さない",
        "同じexplicit_reference行を再監査しない",
        "次人物ペアの正本確定前にpreparationを開始しない",
        "ゲームフォルダへ配置しない",
    ]
    pair = current.get("current_pair")
    pair_status = audit.setdefault("pair_status", {}).setdefault(pair, {})
    pair_status["translation_reaudited"] = "high_confidence_pass_complete"
    pair_status["build_verified"] = "high_confidence_pass_complete"
    pair_status["residual_candidates"] = "none_in_explicit_reference_artifact"
    pair_status["pair_completion_checkpoint"] = {
        "batch": current.get("checkpoint", {}).get("batch"),
        "release_id": current.get("checkpoint", {}).get("release_identity", {}).get("release_id"),
        "reason": "explicit_reference_tail_exhausted",
    }
    handoff = f"""# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得する。

## 現在地

- translation PR #{manifest.get('transport', {}).get('pr')}: merged
- train: `{manifest.get('train_id')}`
- verified checkpoint: 第{current.get('checkpoint', {}).get('batch')}束 / pair {current.get('checkpoint', {}).get('pair_applied_keys')} / project {current.get('checkpoint', {}).get('project_applied_keys')}
- transport: `merged`
- cycle: `paused / merged_pair_complete`
- 宇文逸↔莫問 explicit-reference residual: 0行
- pair completion: `complete`

## exact next action

{EXACT_NEXT}。

## 禁止

- pair completionを通常scene reservationへ戻さない。
- 同じexplicit-reference行を再監査しない。
- 次人物ペアの正本確定前に翻訳準備、判断、owner書込みを開始しない。
- ゲームフォルダへ配置しない。
"""
    write_json(p4 / "CURRENT_WORK.json", current)
    write_json(p4 / "PRIVATE_STAGE_STATE.json", state)
    write_json(p4 / "CI_TRAIN_MANIFEST.json", manifest)
    write_json(p4 / "NEXT_TASK_PACKET.json", packet)
    write_json(p4 / "audit_status.json", audit)
    write_text(p4 / "CURRENT_HANDOFF.md", handoff)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=P4.parent)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        p4 = args.root / "_phase4_proofread"
        if not args.write:
            current = load_object(p4 / "CURRENT_WORK.json")
            packet = load_object(p4 / "NEXT_TASK_PACKET.json")
            ready = (
                packet.get("pair_completion", {}).get("status") == "complete"
                and current.get("ci_train", {}).get("transport_status") == "merged"
            )
            print(json.dumps({"status": "ready" if ready else "noop"}, ensure_ascii=False))
            return 0
        changed = seal(p4)
    except (OSError, json.JSONDecodeError, ValueError, TailError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print("OK: pair completion checkpoint sealed" if changed else "NOOP: pair completion is not ready or already sealed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
