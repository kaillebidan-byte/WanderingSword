#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge済み翻訳PRを検証し、状態正本のtransportをmergedへ冪等に確定する。"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_NAME = "CURRENT_WORK.json"
STATE_NAME = "PRIVATE_STAGE_STATE.json"
MANIFEST_NAME = "CI_TRAIN_MANIFEST.json"
PACKET_NAME = "NEXT_TASK_PACKET.json"
HANDOFF_NAME = "CURRENT_HANDOFF.md"
QUEUE_NAME = "INSTITUTION_WORK_QUEUE.json"
VALID_PREMERGE_STATUSES = {"awaiting_private_merge", "merged"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: dict[str, Any]) -> None:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"
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


def aligned_pr_number(current: dict[str, Any], state: dict[str, Any], manifest: dict[str, Any]) -> int:
    values = [
        current.get("ci_train", {}).get("draft_pr"),
        state.get("transport", {}).get("pr"),
        manifest.get("transport", {}).get("pr"),
    ]
    if any(not isinstance(value, int) or value <= 0 for value in values):
        raise ValueError(f"state authorities do not contain a valid PR number: {values!r}")
    if len(set(values)) != 1:
        raise ValueError(f"state authority PR mismatch: {values!r}")
    return values[0]


def validate_merge_sha(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 40 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError(f"invalid merge SHA: {value!r}")
    return normalized


def fetch_pr(repository: str, pr_number: int, token: str | None) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "wandering-sword-merge-reconciler",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError(f"failed to read PR #{pr_number}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("GitHub PR response must be an object")
    return value


def insert_after(items: list[Any], anchor: str, value: str) -> None:
    if value in items:
        return
    try:
        index = items.index(anchor) + 1
    except ValueError:
        items.append(value)
    else:
        items.insert(index, value)


def has_pending_institution_task(queue: dict[str, Any] | None) -> bool:
    if not isinstance(queue, dict):
        return False
    tasks = queue.get("tasks")
    return isinstance(tasks, list) and any(
        isinstance(task, dict) and task.get("status") == "pending" for task in tasks
    )


def reconcile_values(
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    *,
    pr_number: int,
    merge_sha: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bool]:
    merge_sha = validate_merge_sha(merge_sha)
    actual_pr = aligned_pr_number(current, state, manifest)
    if actual_pr != pr_number:
        raise ValueError(f"requested PR #{pr_number} does not match active state PR #{actual_pr}")

    checkpoint = current.get("checkpoint")
    if not isinstance(checkpoint, dict) or checkpoint.get("status") != "verified":
        raise ValueError("CURRENT_WORK checkpoint must be verified before merge reconciliation")
    if checkpoint.get("produced_by_pr") != pr_number:
        raise ValueError("CURRENT_WORK checkpoint produced_by_pr mismatch")

    statuses = {
        "CURRENT_WORK": current.get("ci_train", {}).get("transport_status"),
        "PRIVATE_STAGE_STATE": state.get("transport", {}).get("status"),
        "CI_TRAIN_MANIFEST": manifest.get("transport", {}).get("status"),
    }
    invalid = {name: status for name, status in statuses.items() if status not in VALID_PREMERGE_STATUSES}
    if invalid:
        raise ValueError(f"transport state is not reconcilable: {invalid!r}")

    existing_shas = {
        manifest.get("transport", {}).get("merge_sha"),
        current.get("ci_train", {}).get("merge_result", {}).get("merge_sha"),
        state.get("transport", {}).get("merge_sha"),
    }
    existing_shas.discard(None)
    if all(status == "merged" for status in statuses.values()):
        if existing_shas and existing_shas != {merge_sha}:
            raise ValueError(f"already-merged state uses a different SHA: {existing_shas!r}")
        return current, state, manifest, False

    current = copy.deepcopy(current)
    state = copy.deepcopy(state)
    manifest = copy.deepcopy(manifest)

    current["translation_base_commit"] = merge_sha
    current["state_base_commit"] = merge_sha
    current["last_merged_translation_pr"] = pr_number
    ci_train = current.setdefault("ci_train", {})
    ci_train["transport_status"] = "merged"
    ci_train["merge_result"] = {"pr": pr_number, "merge_sha": merge_sha}
    private_stage = ci_train.setdefault("private_stage", {})
    private_stage["transport_status"] = "merged"
    private_stage["cycle_status"] = "target_reached"
    private_stage["cycle_checkpoint"] = "merged"

    immediate_next = current.get("immediate_next")
    if isinstance(immediate_next, dict):
        immediate_next["task"] = (
            f"PR #{pr_number}のmerge確定済み。次cycle開始時visibilityからexecution modeを選び、"
            "予約候補のpreparationを開始する。"
        )
        immediate_next["boundary"] = (
            "新cycleのexecution modeをCURRENT_WORKとPRIVATE_STAGE_STATEへlockするまで、"
            "翻訳準備・判断・owner書込みを開始しない。"
        )

    read_order = current.get("mandatory_read_order")
    if isinstance(read_order, list):
        insert_after(read_order, "AGENTS.md", "_phase4_proofread/PROJECT_SCOPE_LOCK.json")
        insert_after(
            read_order,
            "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
            "_phase4_proofread/REGULATED_PHASE_STATE.json",
        )

    state_transport = state.setdefault("transport", {})
    state_transport["status"] = "merged"
    state_transport["merge_sha"] = merge_sha
    history = state_transport.setdefault("history", [])
    if not any(
        isinstance(item, dict) and item.get("status") == "merged" and item.get("merge_sha") == merge_sha
        for item in history
    ):
        history.append({
            "status": "merged",
            "translation_stage": state.get("stage"),
            "pr": pr_number,
            "merge_sha": merge_sha,
        })
    control = state.setdefault("cycle_control", {})
    control.update({
        "status": "target_reached",
        "continuation_required": False,
        "stop_reason": None,
        "exact_next_action": None,
        "last_safe_checkpoint": "merged",
    })

    manifest_transport = manifest.setdefault("transport", {})
    manifest_transport["status"] = "merged"
    manifest_transport["merge_sha"] = merge_sha
    manifest["merge_result"] = {"pr": pr_number, "merge_sha": merge_sha}
    manifest_private = manifest.setdefault("private_stage", {})
    manifest_private["transport_status"] = "merged"

    return current, state, manifest, True


def render_handoff(current: dict[str, Any], manifest: dict[str, Any], packet: dict[str, Any]) -> str:
    checkpoint = current.get("checkpoint", {})
    scenes = " / ".join(map(str, packet.get("scene_groups", [])))
    pr = manifest.get("transport", {}).get("pr")
    return f"""# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- translation PR #{pr}: merged
- train: `{manifest.get('train_id')}`
- verified checkpoint: 第{checkpoint.get('batch')}束 / pair {checkpoint.get('pair_applied_keys')} / project {checkpoint.get('project_applied_keys')}
- transport: `merged`
- cycle: `target_reached / merged`
- 次候補: `{scenes}`（schema v6 minimal reservation）

## 次の作業

cycle開始時visibilityからmodeを選び、CURRENT_WORKとPRIVATE_STAGE_STATEへlockした後、予約候補のpreparationを開始する。

## 禁止

- merged済みPRのphase2やmergeを再実行しない。
- mode lock前に翻訳準備、判断、owner書込みを開始しない。
- minimal reservationへprivate preparation詳細を先書きしない。
- ゲームフォルダへ配置しない。
"""


def reconcile_companions(
    current: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    handoff: str,
    *,
    pr_number: int,
    merge_sha: str,
    institution_queue: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str, bool]:
    updated = copy.deepcopy(packet)
    release = updated.get("release_candidate")
    if not isinstance(release, dict) or release.get("pr") != pr_number:
        raise ValueError("NEXT_TASK_PACKET release_candidate PR mismatch")
    release["status"] = "merged"
    release["merge_sha"] = merge_sha
    updated["do_not_do"] = [
        "minimal reservationへfocus key・voice question・FACT_DOUBT・owner snapshot・batch planningを戻さない",
        "新cycleのexecution modeをCURRENT_WORKとPRIVATE_STAGE_STATEへlockする前にpreparationを開始しない",
        "ゲームフォルダへ配置しない",
    ]
    rendered = (
        handoff
        if has_pending_institution_task(institution_queue)
        else render_handoff(current, manifest, updated)
    )
    return updated, rendered, updated != packet or rendered != handoff


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--event-pr", type=int)
    parser.add_argument("--merge-sha")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p4 = args.root / "_phase4_proofread"
    paths = {
        "current": p4 / CURRENT_NAME,
        "state": p4 / STATE_NAME,
        "manifest": p4 / MANIFEST_NAME,
        "packet": p4 / PACKET_NAME,
        "handoff": p4 / HANDOFF_NAME,
        "queue": p4 / QUEUE_NAME,
    }
    try:
        current = load(paths["current"])
        state = load(paths["state"])
        manifest = load(paths["manifest"])
        packet = load(paths["packet"])
        handoff = paths["handoff"].read_text(encoding="utf-8")
        queue = load(paths["queue"]) if paths["queue"].is_file() else None
        pr_number = aligned_pr_number(current, state, manifest)
        if args.event_pr is not None and args.event_pr != pr_number:
            print(f"NOOP: closed PR #{args.event_pr} is not the active translation PR #{pr_number}")
            return 0

        merge_sha = args.merge_sha
        if merge_sha is None:
            if not args.repository:
                raise ValueError("--repository or GITHUB_REPOSITORY is required to discover merge state")
            pr = fetch_pr(args.repository, pr_number, args.token)
            if pr.get("merged") is not True:
                print(f"NOOP: active PR #{pr_number} is not merged")
                return 0
            merge_sha = pr.get("merge_commit_sha")
            if not isinstance(merge_sha, str):
                raise ValueError(f"merged PR #{pr_number} has no merge_commit_sha")

        current, state, manifest, changed = reconcile_values(
            current, state, manifest, pr_number=pr_number, merge_sha=merge_sha
        )
        packet, handoff, companion_changed = reconcile_companions(
            current,
            manifest,
            packet,
            handoff,
            pr_number=pr_number,
            merge_sha=merge_sha,
            institution_queue=queue,
        )
        changed = changed or companion_changed
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"active PR: {pr_number}")
    print(f"merge SHA: {merge_sha}")
    if not changed:
        print("NOOP: merged transport state is already reconciled")
        return 0
    if not args.write:
        print("DRY RUN: pass --write to update the state authorities")
        return 0
    try:
        write_json(paths["current"], current)
        write_json(paths["state"], state)
        write_json(paths["manifest"], manifest)
        write_json(paths["packet"], packet)
        write_text(paths["handoff"], handoff)
    except OSError as exc:
        print(f"ERROR: failed to write reconciled state: {exc}")
        return 1
    print("OK: state authorities, NEXT_TASK_PACKET and CURRENT_HANDOFF are merged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
