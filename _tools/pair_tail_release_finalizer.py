#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finalize a tail release and replace the ordinary next-scene reservation with pair completion."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import fixed_release_finalizer as base
from pair_tail_common import P4, SENTINEL_SCENE, TailError, load_object, write_json, write_text


def finalize_tail(
    request: dict[str, object],
    artifact: dict[str, object],
    *,
    branch: str,
    p4: Path = P4,
) -> dict[str, object]:
    completion = request.get("pair_completion")
    if not isinstance(completion, dict) or completion.get("status") != "complete":
        raise TailError("pair_completion.status must be complete")
    if completion.get("reason") != "explicit_reference_tail_exhausted":
        raise TailError("pair_completion.reason mismatch")
    source = request.get("source")
    if not isinstance(source, dict):
        raise TailError("tail finalization source is required")
    base_request = copy.deepcopy(request)
    base_request["contract_id"] = "release-finalization-request-v1"
    base_request["operation"] = "finalize_release_state"
    base_request["executor"] = "fixed_release_finalizer"
    base_request["next_scene"] = SENTINEL_SCENE
    base_request["next_source"] = copy.deepcopy(source)
    base_request.pop("pair_completion", None)
    base_request.pop("source", None)
    result = base.finalize(base_request, artifact, branch=branch, p4=p4)

    current = load_object(p4 / "CURRENT_WORK.json")
    state = load_object(p4 / "PRIVATE_STAGE_STATE.json")
    manifest = load_object(p4 / "CI_TRAIN_MANIFEST.json")
    packet = load_object(p4 / "NEXT_TASK_PACKET.json")
    pair = current.get("current_pair")
    marker = {
        "status": "complete",
        "pair": pair,
        "reason": "explicit_reference_tail_exhausted",
        "remaining_explicit_reference_rows": 0,
        "transition": "post_merge_pair_completion_checkpoint",
    }
    packet["task_id"] = f"post-{manifest.get('train_id')}-pair-complete"
    packet["scene_groups"] = [SENTINEL_SCENE]
    packet["pair_completion"] = marker
    packet["do_not_do"] = [
        "pair completionを通常scene reservationへ戻さない",
        "同じexplicit_reference行を再監査しない",
        "phase2成功前にtranslation PRをmergeしない",
        "ゲームフォルダへ配置しない",
    ]
    current["immediate_next"] = {
        "scene_groups": [SENTINEL_SCENE],
        "task": (
            f"PR #{request.get('pr')}のfinalize-release phase2と未解決review thread 0件を確認し、"
            "検証済みHEADをsquash統合する。"
        ),
        "boundary": "統合後は宇文逸↔莫問pair completion checkpointへ遷移し、実sceneを予約しない。",
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    current["ci_train"]["pair_completion"] = marker
    manifest["next_release"].update(
        {
            "candidate_scene": [SENTINEL_SCENE],
            "reservation_status": "pair_complete_pending_merge",
        }
    )
    manifest["pair_completion"] = marker
    state["pair_completion"] = marker
    handoff = f"""# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを優先する。

## 現在地

- PR #{request.get('pr')}: open / ready / phase2待ち
- train: `{manifest.get('train_id')}`
- verified checkpoint: 第{current.get('checkpoint', {}).get('batch')}束
- transport: `awaiting_private_merge`
- explicit-reference residual: 0行
- pair completion: `pending_merge`

## 次の作業

phase2と未解決review thread 0件を確認し、検証済みHEADをsquash統合する。統合後は実sceneを予約せず、pair completion checkpointを確定する。

## 禁止

- translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない。
- 同じexplicit-reference行を再監査しない。
- ゲームフォルダへ配置しない。
"""
    write_json(p4 / "CURRENT_WORK.json", current)
    write_json(p4 / "PRIVATE_STAGE_STATE.json", state)
    write_json(p4 / "CI_TRAIN_MANIFEST.json", manifest)
    write_json(p4 / "NEXT_TASK_PACKET.json", packet)
    write_text(p4 / "CURRENT_HANDOFF.md", handoff)
    result["next_scene"] = SENTINEL_SCENE
    result["pair_completion"] = marker
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--artifact-json", type=Path, required=True)
    parser.add_argument("--branch-name", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.write:
        print("ERROR: --write is required")
        return 2
    try:
        result = finalize_tail(
            load_object(args.request),
            load_object(args.artifact_json),
            branch=args.branch_name,
        )
    except (OSError, json.JSONDecodeError, ValueError, TailError, base.FinalizerError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
