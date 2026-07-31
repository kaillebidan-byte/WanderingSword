#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encode an exact under-40 pair tail using the ordinary owner/freeze machinery."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import apply_owner_assignment_v2 as owner_v2
import fixed_encoding_pipeline as base
from pair_tail_common import P4, ROOT, TailError

AUDIT_RE = re.compile(
    r"^TAIL_AUDIT_DECISIONS_YUWEN_MOWEN_TRAIN(?P<train>\d+)_WAVE(?P<wave>\d+)_(?P<date>\d{4}-\d{2}-\d{2})\.json$"
)


def identity(path: Path) -> tuple[int, int, str]:
    match = AUDIT_RE.fullmatch(path.name)
    if not match:
        raise TailError(f"invalid tail audit filename: {path.name}")
    return int(match["train"]), int(match["wave"]), match["date"]


def prepare(audit_path: Path, pr: int, new_owner: str, p4: Path) -> dict[str, object]:
    current = base.load(p4 / "CURRENT_WORK.json")
    state = base.load(p4 / "PRIVATE_STAGE_STATE.json")
    manifest = base.load(p4 / "CI_TRAIN_MANIFEST.json")
    packet = base.load(p4 / "NEXT_TASK_PACKET.json")
    audit = base.load(audit_path)
    new_owner = base.direct_path(new_owner, p4, "fixes_", ".json")
    train_no, wave_no, date = identity(audit_path)
    train = f"yuwen-mowen-train-{train_no}"
    wave = f"{train}-wave-{wave_no:02d}"
    if (
        audit.get("train_id") != train
        or audit.get("wave_id") != wave
        or audit.get("status") != "complete"
        or audit.get("stage") != "private_quality_audit"
    ):
        raise TailError("tail audit identity/state mismatch")
    if (
        state.get("stage") != "private_quality_audit"
        or state.get("train_id") != train
        or manifest.get("train_id") != train
        or current.get("ci_train", {}).get("train_id") != train
    ):
        raise TailError("tail train authorities mismatch")
    tail = state.get("tail_exhaustion")
    if not isinstance(tail, dict) or tail.get("status") != "verified":
        raise TailError("verified tail_exhaustion proof is required")
    if state.get("wave", {}).get("seal_reason") != "scope_exhausted":
        raise TailError("tail wave must use scope_exhausted seal")

    decisions = audit.get("decisions")
    packets = state.get("wave", {}).get("packets")
    base_batch = manifest.get("base_checkpoint", {}).get("batch")
    source = audit.get("source_artifact")
    if (
        not isinstance(decisions, list)
        or not decisions
        or not isinstance(packets, list)
        or len(decisions) != len(packets)
        or not isinstance(base_batch, int)
        or not isinstance(source, dict)
    ):
        raise TailError("tail audit/wave/base/source shape mismatch")

    bundles: list[dict[str, object]] = []
    plans: list[dict[str, object]] = []
    reviews: list[str] = []
    focus: list[dict[str, object]] = []
    total_rows = total_fixes = total_keeps = 0
    for index, (decision, wave_packet) in enumerate(zip(decisions, packets)):
        if (
            not isinstance(decision, dict)
            or not isinstance(wave_packet, dict)
            or decision.get("packet_id") != wave_packet.get("packet_id")
        ):
            raise TailError("tail packet alignment mismatch")
        candidate_rel = decision.get("candidate")
        if (
            not isinstance(candidate_rel, str)
            or wave_packet.get("preparation_record", {}).get("candidate_packet") != candidate_rel
        ):
            raise TailError("tail candidate path mismatch")
        candidate = base.load(p4.parent / candidate_rel)
        if candidate.get("source_artifact") != source:
            raise TailError("tail candidate source artifact mismatch")
        data = base.validate_decision(decision, candidate)
        batch = base_batch + index + 1
        review = f"_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH{batch}_{date}.md"
        base.write_text(
            p4.parent / review,
            base.review_text(batch, candidate_rel, candidate, source, data),
        )
        reviews.append(review)
        rows = len(data["rows"])
        fixes = len(data["fixes"])
        total_rows += rows
        total_fixes += fixes
        total_keeps += len(data["keeps"])
        owner_path = new_owner if index == 0 else new_owner.replace(".json", f"_{index + 1}.json")
        plans.append(
            {
                "candidate": candidate_rel,
                "new_owner_file": owner_path,
                "values": data["fix_map"],
                "fix_keys": list(data["fix_map"]),
            }
        )
        bundles.append(
            {
                "batch": batch,
                "review_status": "complete",
                "apply_status": "pending",
                "scene_groups": list(candidate.get("scene_groups", [])),
                "reviewed_rows": rows,
                "reviewed_keys": rows,
                "unique_rows": rows,
                "fix_keys": fixes,
                "unique_fix_rows": fixes,
                "new_pair_keys": 0,
                "new_project_keys": 0,
                "cross_register_keys": 0,
                "existing_owner_updates": 0,
                "keep_keys": len(data["keeps"]),
                "fix_files": [],
                "review_record": review,
                "ownership_summary": {
                    "existing_keys": 0,
                    "unowned_kept": 0,
                    "new_keys": 0,
                    "cross_register_keys": 0,
                },
                "allusion_review_candidates": data["allusion_review_candidates"],
                "allusion_review_resolved": data["allusion_review_resolved"],
                "fact_doubts": data["fact_doubts"],
                "source_artifact": source,
            }
        )
        focus.append(
            {
                "scene": " / ".join(candidate.get("scene_groups", [])),
                "focus_keys": [row["key"] for row in data["rows"]],
            }
        )
        wave_packet.update(
            {
                "status": "audited",
                "audit_record": {
                    "status": "complete",
                    "record": f"_phase4_proofread/AUDIT_YUWEN_MOWEN_TRAIN{train_no}_WAVE{wave_no:02d}_{date}.md",
                    "decision_record": audit_path.relative_to(p4.parent).as_posix(),
                },
                "formal_batch": None,
                "review_record": None,
            }
        )

    if not 0 < total_rows < 40 or total_rows != tail.get("residual_rows"):
        raise TailError(
            f"tail row count must match verified 1..39 residual: rows={total_rows} proof={tail.get('residual_rows')}"
        )
    base.transition(state, "private_encoding")
    state["stage"] = "private_encoding"
    state["permissions"] = dict(base.ENCODING_PERMS)
    state["cycle_control"].update(
        {
            "continuation_required": True,
            "stop_reason": None,
            "exact_next_action": "記録済みtail監査をowner・正式束・release stateへ機械収録する",
            "last_safe_checkpoint": "private_encoding",
        }
    )
    summary = {
        "bundle_count": len(bundles),
        "reviewed_rows": total_rows,
        "reviewed_keys": total_rows,
        "unique_reviewed_rows": total_rows,
        "fix_keys": total_fixes,
        "unique_fix_rows": total_fixes,
        "new_pair_keys": 0,
        "new_project_keys": 0,
        "cross_register_keys": 0,
        "existing_owner_updates": 0,
        "keep_only_bundles": sum(bundle["fix_keys"] == 0 for bundle in bundles),
    }
    state["wave"]["encoding_summary"] = dict(summary)
    manifest["bundles"] = bundles
    manifest["totals"] = dict(summary)
    manifest["release_trigger"] = {
        "reason": "schema_change",
        "detail": "explicit_reference tail exhaustion replaces an ordinary next-scene reservation with a pair-completion checkpoint",
    }
    manifest["private_stage"] = {
        "stage": "private_encoding",
        "status": "active",
        "transport_status": "not_ready",
        "wave_id": wave,
    }
    manifest["next_release"].update(
        {
            "reservation_status": "encoding_active",
            "formal_batches": [bundle["batch"] for bundle in bundles],
            "current_private_stage": "private_encoding",
        }
    )
    current["ci_train"]["totals"] = dict(summary)
    current["ci_train"]["private_stage"].update(
        {
            "stage": "private_encoding",
            "status": "active",
            "cycle_checkpoint": "private_encoding",
        }
    )
    current["immediate_next"] = {
        "scene_groups": list(packet.get("scene_groups", [])),
        "task": "記録済みtail監査をprivate encoding pipelineで収録する。",
        "boundary": "翻訳判断を再開せず、decision recordだけをowner・正式束へ写像する。",
        "packet": "_phase4_proofread/NEXT_TASK_PACKET.json",
    }
    packet["reservation"].update(
        {
            "status": "encoding_active",
            "encoding_started": True,
            "formal_batch": [bundle["batch"] for bundle in bundles],
        }
    )
    attestation = state.get("wave", {}).get("seal_attestation")
    packet["scene_flow"] = focus
    packet["batch_planning"] = {
        "mode": "detail_packet",
        "reviewed_rows": total_rows,
        "target_rows": {"min": 15, "max": 30},
        "adjacent_candidates_checked": list(packet.get("scene_groups", [])),
        "grouping_decision": attestation,
        "exception": {
            "reason_code": "no_adjacent_in_scope_scene",
            "detail": attestation,
        },
    }
    for name, value in (
        ("CURRENT_WORK.json", current),
        ("PRIVATE_STAGE_STATE.json", state),
        ("CI_TRAIN_MANIFEST.json", manifest),
        ("NEXT_TASK_PACKET.json", packet),
    ):
        base.write_json(p4 / name, value)
    base.write_json(p4 / "OWNER_ASSIGNMENT_PLAN.json", {"schema_version": 1, "packets": plans})
    return {
        "train_id": train,
        "wave_id": wave,
        "date": date,
        "review_paths": reviews,
        "batch_numbers": [bundle["batch"] for bundle in bundles],
        "reviewed_rows": total_rows,
        "fix_keys": total_fixes,
        "keep_keys": total_keeps,
    }


def run_pipeline(
    audit_path: Path,
    pr_number: int,
    new_owner_file: str,
    challenge_record: str,
    p4: Path = P4,
) -> dict[str, object]:
    prepared = prepare(audit_path, pr_number, new_owner_file, p4)
    owner_v2.apply_plan(p4.parent, p4 / "OWNER_ASSIGNMENT_PLAN.json", p4 / "OWNER_ASSIGNMENT_RESULT.json")
    return base.finalize(prepared, pr_number, challenge_record, p4)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--new-owner-file", required=True)
    parser.add_argument("--challenge-record", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit = args.audit if args.audit.is_absolute() else ROOT / args.audit
    if not args.write:
        print(json.dumps({"status": "dry_run_requires_isolated_fixture", "audit": str(args.audit)}, ensure_ascii=False))
        return 0
    try:
        result = run_pipeline(
            audit,
            args.pr_number,
            args.new_owner_file,
            args.challenge_record,
        )
    except (OSError, json.JSONDecodeError, ValueError, TailError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "pair_tail_encoding_failure", "detail": str(exc)}, ensure_ascii=False))
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        base.write_text(args.output, text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
