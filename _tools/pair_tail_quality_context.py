#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inject quality-audit context into every target-separated tail candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import quality_audit_context as base
from pair_tail_common import P4, ROOT, TailError, load_object, write_json, write_text


def inject_many(candidate_paths: list[str], root: Path = ROOT) -> dict[str, object]:
    if not candidate_paths or len(candidate_paths) != len(set(candidate_paths)):
        raise TailError("candidate_paths must be a non-empty unique list")
    summaries: list[dict[str, object]] = []
    digests: dict[str, str] = {}
    target_counts: dict[str, int] = {}
    unresolved: dict[str, list[str]] = {}
    for relative in candidate_paths:
        path = root / relative
        candidate = load_object(path)
        if candidate.get("schema_version") not in {2, 3}:
            raise TailError(f"candidate schema must be 2 or 3: {relative}")
        context = base.build_context(candidate, root)
        candidate["schema_version"] = 3
        candidate["quality_audit_context"] = context
        forbidden = candidate.get("forbidden_outputs")
        if isinstance(forbidden, list):
            for marker in ("source_document_decision", "source_document_write"):
                if marker not in forbidden:
                    forbidden.append(marker)
        write_json(path, candidate)
        digests[relative] = context["manifest_digest"]
        target_counts[relative] = len(context["source_document_targets"])
        unresolved[relative] = list(context["unresolved_speakers"])
        summaries.append(
            {
                "candidate": relative,
                "manifest_digest": context["manifest_digest"],
                "required_document_count": len(context["required_documents"]),
                "source_document_target_count": len(context["source_document_targets"]),
                "unresolved_speakers": context["unresolved_speakers"],
            }
        )

    current = load_object(root / "_phase4_proofread/CURRENT_WORK.json")
    immediate = current.setdefault("immediate_next", {})
    immediate["source_feedback_contract"] = base.CONTRACT_REL
    immediate["quality_audit_context_digests"] = digests
    write_json(root / "_phase4_proofread/CURRENT_WORK.json", current)

    state = load_object(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json")
    packets = state.get("wave", {}).get("packets")
    if not isinstance(packets, list) or len(packets) != len(candidate_paths):
        raise TailError("tail context injection packet count mismatch")
    by_path = {
        packet.get("preparation_record", {}).get("candidate_packet"): packet
        for packet in packets
        if isinstance(packet, dict)
    }
    if set(by_path) != set(candidate_paths):
        raise TailError("tail context injection candidate/packet mismatch")
    for relative in candidate_paths:
        packet = by_path[relative]
        packet.setdefault("preparation_record", {})["quality_audit_context_digest"] = digests[relative]
        packet["source_document_target_count"] = target_counts[relative]
    write_json(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json", state)

    packet = load_object(root / "_phase4_proofread/NEXT_TASK_PACKET.json")
    packet["quality_audit_source_feedback"] = {
        "contract": base.CONTRACT_REL,
        "candidate_schema": 3,
        "audit_decision_schema": 2,
        "candidate_manifests": [
            {"candidate": relative, "manifest_digest": digests[relative]}
            for relative in candidate_paths
        ],
    }
    write_json(root / "_phase4_proofread/NEXT_TASK_PACKET.json", packet)

    handoff_path = root / "_phase4_proofread/CURRENT_HANDOFF.md"
    handoff = handoff_path.read_text(encoding="utf-8")
    addition = (
        "\n## quality audit資料還流\n\n"
        "2candidateをtarget/namespace別に保ち、各candidateの一次資料から典故・事実疑義を先に立てる。"
        "その後、各`quality_audit_context.required_documents`を照合し、全人物資料targetへ"
        "`keep/revise/create/unresolved`を記録する。人物資料は直接編集しない。\n"
    )
    if "## quality audit資料還流" not in handoff:
        write_text(handoff_path, handoff.rstrip() + "\n" + addition)
    return {"status": "written", "candidates": summaries, "unresolved": unresolved}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution-result", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = load_object(args.execution_result)
        paths = result.get("candidate_paths")
        if not isinstance(paths, list) or any(not isinstance(path, str) or not path for path in paths):
            raise TailError("execution result lacks candidate_paths")
        if not args.write:
            summary = {"status": "valid", "candidate_paths": paths}
        else:
            summary = inject_many(paths)
    except (OSError, json.JSONDecodeError, ValueError, TailError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "pair_tail_context_failure", "detail": str(exc)}, ensure_ascii=False))
        return 1
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        write_text(args.output, text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
