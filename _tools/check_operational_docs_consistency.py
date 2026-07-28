#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""実作業の状態正本、人間向け文書、mode別手順の陳腐化を検査する。"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"

TEXT_PATHS = {
    "handoff": P4 / "CURRENT_HANDOFF.md",
    "cold": P4 / "COLD_START_ACCEPTANCE.md",
    "phase1": P4 / "CI_TRAIN_PHASE1.md",
    "phase2": P4 / "CI_TRAIN_PHASE2.md",
    "runbook": P4 / "RUNBOOK_人物ペア再監査.md",
    "public_window": P4 / "PUBLIC_CI_WINDOW.md",
    "readme": ROOT / "README.md",
    "session": P4 / "SESSION_BOOTSTRAP.md",
    "factory": P4 / "FACTORY_FLOW.md",
    "private_stages": P4 / "PRIVATE_TRANSLATION_STAGES.md",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"top level must be object: {path}")
    return value


def validate_snapshot(
    current: dict[str, Any],
    state: dict[str, Any],
    manifest: dict[str, Any],
    packet: dict[str, Any],
    texts: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    current_transport = current.get("ci_train", {}).get("transport_status")
    state_transport = state.get("transport", {}).get("status")
    manifest_transport = manifest.get("transport", {}).get("status")
    if len({current_transport, state_transport, manifest_transport}) != 1:
        errors.append("transport mismatch across CURRENT_WORK, PRIVATE_STAGE_STATE and manifest")

    pr = manifest.get("transport", {}).get("pr")
    merge_sha = manifest.get("transport", {}).get("merge_sha")
    release = packet.get("release_candidate", {})
    if manifest_transport == "merged":
        if release.get("status") != "merged":
            errors.append("merged transport requires NEXT_TASK_PACKET.release_candidate.status=merged")
        if release.get("merge_sha") != merge_sha:
            errors.append("NEXT_TASK_PACKET merge_sha must match manifest")
        handoff = texts.get("handoff", "")
        for required in (f"PR #{pr}: merged", "transport: `merged`", "cycle: `target_reached / merged`"):
            if required not in handoff:
                errors.append(f"CURRENT_HANDOFF lacks merged fact: {required}")
        for stale in ("open / ready / mergeable", "awaiting_private_merge", "finalize-release phase2"):
            if stale in handoff:
                errors.append(f"CURRENT_HANDOFF contains stale pre-merge text: {stale}")
        for item in packet.get("do_not_do", []):
            if isinstance(item, str) and "統合前" in item:
                errors.append("NEXT_TASK_PACKET retains a pre-merge prohibition after merge")

    mode = current.get("operation_mode", {}).get("execution_mode")
    if mode == "always_public_full_pipeline":
        cold = texts.get("cold", "")
        if "public + `private_translation_work` + `always_public_full_pipeline`" not in cold:
            errors.append("cold-start contract does not allow locked always-public translation stages")
        if "private_translation_work + publicなら、翻訳を開始せずprivate復帰を依頼する" in cold:
            errors.append("cold-start contract retains legacy public=>private rule")

    required_text = {
        "phase1": "manual public CI窓",
        "phase2": "mode-neutral release",
        "runbook": "post-merge状態専用PRは作らない",
        "public_window": "manual_visibility_cycle専用",
        "readme": "translation_factory_controller.py",
        "session": "translation_factory_controller.py",
        "factory": "semantic_bundle_boundary",
        "private_stages": "encoding後に上書きしない",
    }
    for label, needle in required_text.items():
        if needle not in texts.get(label, ""):
            errors.append(f"{label} lacks current contract marker: {needle}")

    for label in ("readme", "session", "factory"):
        text = texts.get(label, "")
        for station in ("semantic_bundle_boundary", "translation_quality_audit"):
            if station not in text:
                errors.append(f"{label} lacks human station marker: {station}")

    forbidden = {
        "phase2": ("encoding後にowner snapshotを再生成する", "repository metadataでprivate復帰確認"),
        "runbook": ("post-merge状態PRを作成する", "NEXT_TASK_PACKET.batch_planning"),
        "readme": ("check_handoff_consistency.py --require-verified",),
    }
    for label, needles in forbidden.items():
        for needle in needles:
            if needle in texts.get(label, ""):
                errors.append(f"{label} retains legacy instruction: {needle}")
    return errors


def main() -> int:
    try:
        current = load(P4 / "CURRENT_WORK.json")
        state = load(P4 / "PRIVATE_STAGE_STATE.json")
        manifest = load(P4 / "CI_TRAIN_MANIFEST.json")
        packet = load(P4 / "NEXT_TASK_PACKET.json")
        texts = {name: path.read_text(encoding="utf-8") for name, path in TEXT_PATHS.items()}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate_snapshot(current, state, manifest, packet, texts)
    print("=== Operational contract consistency ===")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: state, handoff, reservation, factory flow and mode-specific documents are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
