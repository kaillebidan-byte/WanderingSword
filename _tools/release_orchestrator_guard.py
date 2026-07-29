#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release train開始前にlive PR HEAD・station・release lineageを照合する。"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
READY = "ready_for_public_ci"
ACTIVE_LABELS = {"release-ci", "ci-heavy-rerun"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def append_mismatch(reasons: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        reasons.append(f"{label}: expected {expected!r}, got {actual!r}")


def evaluate(
    current: dict[str, Any],
    manifest: dict[str, Any],
    stage: dict[str, Any],
    packet: dict[str, Any],
    *,
    event_action: str,
    event_label: str,
    event_head: str,
    current_pr_head: str,
    head_ref: str,
    pr_number: int,
) -> dict[str, Any]:
    reasons: list[str] = []

    if event_action == "synchronize":
        reasons.append("synchronize_requires_explicit_relabel")
    elif event_action != "labeled":
        reasons.append(f"unsupported_event_action:{event_action}")
    elif event_label not in ACTIVE_LABELS:
        reasons.append(f"inactive_release_label:{event_label}")

    if not SHA_RE.fullmatch(event_head):
        reasons.append("event_head_is_invalid")
    if not SHA_RE.fullmatch(current_pr_head):
        reasons.append("current_pr_head_is_invalid")
    if event_head != current_pr_head:
        reasons.append("event_head_is_stale")

    train = current.get("ci_train") if isinstance(current.get("ci_train"), dict) else {}
    manifest_transport = manifest.get("transport") if isinstance(manifest.get("transport"), dict) else {}
    manifest_stage = manifest.get("private_stage") if isinstance(manifest.get("private_stage"), dict) else {}
    stage_transport = stage.get("transport") if isinstance(stage.get("transport"), dict) else {}
    stage_cycle = stage.get("cycle_control") if isinstance(stage.get("cycle_control"), dict) else {}
    train_stage = train.get("private_stage") if isinstance(train.get("private_stage"), dict) else {}
    release_candidate = packet.get("release_candidate") if isinstance(packet.get("release_candidate"), dict) else {}
    reservation = packet.get("reservation") if isinstance(packet.get("reservation"), dict) else {}
    packet_train = packet.get("ci_train") if isinstance(packet.get("ci_train"), dict) else {}

    append_mismatch(reasons, "CURRENT_WORK.operation_mode.declared_state", current.get("operation_mode", {}).get("declared_state"), "translation_frozen")
    append_mismatch(reasons, "CURRENT_WORK.ci_train.status", train.get("status"), READY)
    append_mismatch(reasons, "CURRENT_WORK.ci_train.transport_status", train.get("transport_status"), READY)
    append_mismatch(reasons, "CURRENT_WORK.ci_train.private_stage.stage", train_stage.get("stage"), "translation_frozen")
    append_mismatch(reasons, "CURRENT_WORK.ci_train.private_stage.status", train_stage.get("status"), "complete")
    append_mismatch(reasons, "CURRENT_WORK.ci_train.private_stage.transport_status", train_stage.get("transport_status"), READY)
    append_mismatch(reasons, "CURRENT_WORK.ci_train.branch", train.get("branch"), head_ref)
    append_mismatch(reasons, "CURRENT_WORK.ci_train.draft_pr", train.get("draft_pr"), pr_number)

    append_mismatch(reasons, "CI_TRAIN_MANIFEST.status", manifest.get("status"), READY)
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.transport.status", manifest_transport.get("status"), READY)
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.transport.translation_stage", manifest_transport.get("translation_stage"), "translation_frozen")
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.transport.pr", manifest_transport.get("pr"), pr_number)
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.private_stage.stage", manifest_stage.get("stage"), "translation_frozen")
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.private_stage.status", manifest_stage.get("status"), "complete")
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.private_stage.transport_status", manifest_stage.get("transport_status"), READY)
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.branch", manifest.get("branch"), head_ref)
    append_mismatch(reasons, "CI_TRAIN_MANIFEST.draft_pr", manifest.get("draft_pr"), pr_number)

    append_mismatch(reasons, "PRIVATE_STAGE_STATE.stage", stage.get("stage"), "translation_frozen")
    append_mismatch(reasons, "PRIVATE_STAGE_STATE.transport.status", stage_transport.get("status"), READY)
    append_mismatch(reasons, "PRIVATE_STAGE_STATE.transport.pr", stage_transport.get("pr"), pr_number)
    append_mismatch(reasons, "PRIVATE_STAGE_STATE.cycle_control.last_safe_checkpoint", stage_cycle.get("last_safe_checkpoint"), READY)

    train_id = train.get("train_id")
    append_mismatch(reasons, "manifest train lineage", manifest.get("train_id"), train_id)
    append_mismatch(reasons, "stage train lineage", stage.get("train_id"), train_id)
    append_mismatch(reasons, "packet train lineage", packet_train.get("train_id"), train_id)
    append_mismatch(reasons, "release candidate train lineage", release_candidate.get("train_id"), train_id)
    append_mismatch(reasons, "release candidate PR lineage", release_candidate.get("pr"), pr_number)
    append_mismatch(reasons, "release candidate status", release_candidate.get("status"), READY)
    append_mismatch(reasons, "packet reservation status", reservation.get("status"), "encoded")

    immediate = current.get("immediate_next") if isinstance(current.get("immediate_next"), dict) else {}
    if "release-ci" not in str(immediate.get("task", "")):
        reasons.append("CURRENT_WORK.immediate_next is not release-ci")

    proceed = not reasons
    return {
        "schema_version": 1,
        "status": "proceed" if proceed else "stale_noop",
        "proceed": proceed,
        "remove_release_labels": not proceed,
        "event": {
            "action": event_action,
            "label": event_label,
            "event_head": event_head,
            "current_pr_head": current_pr_head,
            "head_ref": head_ref,
            "pr": pr_number,
        },
        "train_id": train_id,
        "reasons": reasons,
    }


def write_github_output(path: Path, result: dict[str, Any]) -> None:
    reason = result["reasons"][0] if result["reasons"] else "release_inputs_current"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"proceed={'true' if result['proceed'] else 'false'}\n")
        handle.write(f"status={result['status']}\n")
        handle.write(f"remove_release_labels={'true' if result['remove_release_labels'] else 'false'}\n")
        handle.write(f"reason={reason}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-action", required=True)
    parser.add_argument("--event-label", default="")
    parser.add_argument("--event-head", required=True)
    parser.add_argument("--current-pr-head", required=True)
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = evaluate(
        load_object(P4 / "CURRENT_WORK.json"),
        load_object(P4 / "CI_TRAIN_MANIFEST.json"),
        load_object(P4 / "PRIVATE_STAGE_STATE.json"),
        load_object(P4 / "NEXT_TASK_PACKET.json"),
        event_action=args.event_action,
        event_label=args.event_label,
        event_head=args.event_head,
        current_pr_head=args.current_pr_head,
        head_ref=args.head_ref,
        pr_number=args.pr_number,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    if args.github_output:
        write_github_output(args.github_output, result)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
