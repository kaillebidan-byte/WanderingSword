#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quality-audit encodingを初回実行または安全再開し、release transport契約を補完する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import fixed_encoding_pipeline as encoding

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
RESTART_PHRASE = "現状把握して作業の続きを"


class ExecutorError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    return encoding.load(path)


def apply_transport_contract(*, p4: Path, pr_number: int) -> dict[str, Any]:
    current = load(p4 / "CURRENT_WORK.json")
    state = load(p4 / "PRIVATE_STAGE_STATE.json")
    manifest = load(p4 / "CI_TRAIN_MANIFEST.json")
    packet = load(p4 / "NEXT_TASK_PACKET.json")

    train_id = manifest.get("train_id")
    branch = manifest.get("branch")
    bundles = manifest.get("bundles")
    totals = manifest.get("totals")
    reservation = packet.get("reservation")
    private_stage = current.get("ci_train", {}).get("private_stage", {})
    if not isinstance(train_id, str) or not isinstance(branch, str):
        raise ExecutorError("manifest train identity is incomplete")
    if state.get("stage") != "translation_frozen" or private_stage.get("stage") != "translation_frozen":
        raise ExecutorError("transport completion requires translation_frozen authorities")
    if manifest.get("status") != "ready_for_public_ci" or state.get("transport", {}).get("status") != "ready_for_public_ci":
        raise ExecutorError("transport completion requires ready_for_public_ci")
    if not isinstance(reservation, dict) or reservation.get("status") != "encoded":
        raise ExecutorError("transport completion requires encoded reservation")
    if not isinstance(bundles, list) or not bundles or not isinstance(totals, dict):
        raise ExecutorError("formal bundles and totals are required")

    formal_batches = [bundle.get("batch") for bundle in bundles if isinstance(bundle, dict)]
    if len(formal_batches) != len(bundles) or any(not isinstance(batch, int) or batch <= 0 for batch in formal_batches):
        raise ExecutorError("formal batch identities are invalid")
    planned = packet.get("ci_train")
    if not isinstance(planned, dict):
        raise ExecutorError("NEXT_TASK_PACKET.ci_train must be an object")
    planned["planned_batch"] = formal_batches[-1]
    packet["release_candidate"] = {
        "train_id": train_id,
        "release_id": f"{train_id}-r1",
        "pr": pr_number,
        "status": "ready_for_public_ci",
    }

    handoff = "\n".join([
        "# 現在の引継ぎ",
        "",
        f"- active train: `{train_id}`",
        f"- branch: `{branch}`",
        "- stage: `translation_frozen`",
        "- transport: `ready_for_public_ci`",
        f"- formal batches: `{', '.join(map(str, formal_batches))}`",
        f"- reviewed rows: `{totals.get('reviewed_rows')}` / fixes: `{totals.get('fix_keys')}` / keeps: `{sum(int(bundle.get('keep_keys', 0)) for bundle in bundles)}`",
        f"- pull request: `#{pr_number}`",
        "",
        "## exact next action",
        "",
        "`release-ci` labelから固定`Release train orchestrator`を起動し、Relation・Cross・Apply・phase2を実行する。",
        "",
        f"再開句: `{RESTART_PHRASE}`",
        "",
        "翻訳判断は凍結済み。KEEP/FIX、owner、正式束を手作業で変更しない。",
        "",
    ])
    encoding.write_json(p4 / "NEXT_TASK_PACKET.json", packet)
    encoding.write_text(p4 / "CURRENT_HANDOFF.md", handoff)
    return {
        "train_id": train_id,
        "formal_batches": formal_batches,
        "reviewed_rows": totals.get("reviewed_rows"),
        "fix_keys": totals.get("fix_keys"),
        "transport": "ready_for_public_ci",
    }


def execute(
    *,
    audit_path: Path,
    pr_number: int,
    new_owner_file: str,
    challenge_record: str,
    p4: Path = P4,
) -> dict[str, Any]:
    state = load(p4 / "PRIVATE_STAGE_STATE.json")
    packet = load(p4 / "NEXT_TASK_PACKET.json")
    reservation = packet.get("reservation", {})
    if state.get("stage") == "private_quality_audit":
        result = encoding.run_pipeline(audit_path, pr_number, new_owner_file, challenge_record, p4)
        resumed = False
    elif state.get("stage") == "translation_frozen" and isinstance(reservation, dict) and reservation.get("status") == "encoded":
        result = {"status": "already_encoded"}
        resumed = True
    else:
        raise ExecutorError(
            f"unsupported encoding checkpoint: stage={state.get('stage')!r} reservation={reservation.get('status')!r}"
        )
    transport = apply_transport_contract(p4=p4, pr_number=pr_number)
    return {**result, **transport, "resumed": resumed}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--new-owner-file", required=True)
    parser.add_argument("--challenge-record", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = args.audit if args.audit.is_absolute() else ROOT / args.audit
    if not args.write:
        print(json.dumps({"status": "dry_run", "audit": str(args.audit)}, ensure_ascii=False))
        return 0
    try:
        result = execute(
            audit_path=audit,
            pr_number=args.pr_number,
            new_owner_file=args.new_owner_file,
            challenge_record=args.challenge_record,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "factory_encoding_executor_failure", "detail": str(exc)}, ensure_ascii=False))
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        encoding.write_text(args.output, text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
