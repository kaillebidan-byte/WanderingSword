#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from check_operational_docs_consistency import validate_snapshot

SHA = "a" * 40


def fixtures():
    current = {
        "operation_mode": {"execution_mode": "always_public_full_pipeline"},
        "ci_train": {"transport_status": "merged"},
    }
    state = {"transport": {"status": "merged"}}
    manifest = {"transport": {"status": "merged", "pr": 12, "merge_sha": SHA}}
    packet = {
        "release_candidate": {"status": "merged", "merge_sha": SHA},
        "do_not_do": ["mode lock前に開始しない"],
    }
    factory_markers = "translation_factory_controller.py semantic_bundle_boundary translation_quality_audit"
    texts = {
        "handoff": "PR #12: merged\ntransport: `merged`\ncycle: `target_reached / merged`\n",
        "cold": "public + `private_translation_work` + `always_public_full_pipeline`",
        "phase1": "manual public CI窓",
        "phase2": "mode-neutral release",
        "runbook": "post-merge状態専用PRは作らない",
        "public_window": "manual_visibility_cycle専用",
        "readme": factory_markers,
        "session": factory_markers,
        "factory": factory_markers,
        "private_stages": "encoding後に上書きしない",
    }
    return current, state, manifest, packet, texts


def main() -> None:
    args = fixtures()
    assert validate_snapshot(*args) == []

    current, state, manifest, packet, texts = fixtures()
    packet["release_candidate"]["status"] = "verified"
    assert any("status=merged" in error for error in validate_snapshot(current, state, manifest, packet, texts))

    current, state, manifest, packet, texts = fixtures()
    texts["handoff"] += "open / ready / mergeable"
    assert any("stale pre-merge" in error for error in validate_snapshot(current, state, manifest, packet, texts))

    current, state, manifest, packet, texts = fixtures()
    texts["cold"] = "private_translation_work + publicなら、翻訳を開始せずprivate復帰を依頼する"
    assert any("legacy public=>private" in error for error in validate_snapshot(current, state, manifest, packet, texts))

    current, state, manifest, packet, texts = fixtures()
    texts["runbook"] += "\npost-merge状態PRを作成する"
    assert any("legacy instruction" in error for error in validate_snapshot(current, state, manifest, packet, texts))

    current, state, manifest, packet, texts = fixtures()
    texts["session"] = "translation_factory_controller.py semantic_bundle_boundary"
    assert any("translation_quality_audit" in error for error in validate_snapshot(current, state, manifest, packet, texts))

    print("test_check_operational_docs_consistency: OK")


if __name__ == "__main__":
    main()
