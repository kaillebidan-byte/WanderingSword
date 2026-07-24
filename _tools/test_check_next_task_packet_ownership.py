#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_next_task_packet の機械所有表を回帰検証する。"""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_next_task_packet.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_next_task_packet", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_next_task_packet.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_packet() -> dict:
    return {
        "source": {"target": "CG表", "namespace": "QuestDlgs"},
        "scene_flow": [{"focus_keys": ["Scene_Index0_Text", "Scene_Index1_Text"]}],
        "ownership_boundary": {
            "machine_ownership": {
                "existing": [
                    {
                        "path": "_phase4_proofread/fixes_relation_demo_batch1.json",
                        "keys": ["Scene_Index0_Text"],
                    }
                ],
                "unowned": [
                    {
                        "key": "Scene_Index1_Text",
                        "planned_owner": "_phase4_proofread/fixes_relation_demo_batch2.json",
                    }
                ],
            }
        },
    }


def main() -> None:
    module = load_module()
    prefix = "CG表\x1fQuestDlgs\x1f"

    with tempfile.TemporaryDirectory() as tmp:
        temp_root = Path(tmp)
        owner_path = temp_root / "_phase4_proofread" / "fixes_relation_demo_batch1.json"
        owner_path.parent.mkdir(parents=True)
        owner_path.write_text("{}\n", encoding="utf-8")

        original_root = module.ROOT
        module.ROOT = temp_root
        try:
            errors: list[str] = []
            transitions: list[str] = []
            module.validate_machine_ownership(
                sample_packet(),
                {
                    prefix + "Scene_Index0_Text": [
                        "_phase4_proofread/fixes_relation_demo_batch1.json"
                    ]
                },
                allow_consumed=False,
                errors=errors,
                transitions=transitions,
            )
            assert errors == []
            assert transitions == []

            consumed = sample_packet()
            consumed["ownership_boundary"]["machine_ownership"]["existing"] = []
            consumed["scene_flow"][0]["focus_keys"] = ["Scene_Index1_Text"]

            errors = []
            transitions = []
            module.validate_machine_ownership(
                consumed,
                {
                    prefix + "Scene_Index1_Text": [
                        "_phase4_proofread/fixes_relation_demo_batch2.json"
                    ]
                },
                allow_consumed=True,
                errors=errors,
                transitions=transitions,
            )
            assert errors == []
            assert transitions == [
                "planned owner consumed Scene_Index1_Text: "
                "_phase4_proofread/fixes_relation_demo_batch2.json"
            ]

            errors = []
            transitions = []
            module.validate_machine_ownership(
                consumed,
                {
                    prefix + "Scene_Index1_Text": [
                        "_phase4_proofread/fixes_relation_wrong.json"
                    ]
                },
                allow_consumed=True,
                errors=errors,
                transitions=transitions,
            )
            assert any("key declared unowned is already owned" in error for error in errors)
            assert transitions == []
        finally:
            module.ROOT = original_root

    # 適用後はCURRENT_WORK.checkpointが最終bundleまで進むが、次束番号は
    # manifestの出発checkpoint + 積載束数 + 1で求める。
    original_validate_manifest = module.validate_manifest
    module.validate_manifest = lambda manifest, current: []
    try:
        current = {
            "checkpoint": {"batch": 61},
            "ci_train": {"phase": "phase1_pilot", "train_id": "test-train"},
        }
        manifest = {"base_checkpoint": {"batch": 60}, "bundles": [{"batch": 61}]}
        packet = {
            "ci_train": {
                "phase": "phase1_pilot",
                "train_id": "test-train",
                "manifest": "_phase4_proofread/CI_TRAIN_MANIFEST.json",
                "bundle_status_on_completion": "reviewed_pending_ci",
                "do_not_apply_until_release": True,
                "planned_batch": 62,
            }
        }
        errors = []
        module.validate_train_packet(current, manifest, packet, errors)
        assert errors == [], errors

        packet["ci_train"]["planned_batch"] = 63
        errors = []
        module.validate_train_packet(current, manifest, packet, errors)
        assert any("planned_batch mismatch" in error for error in errors)
    finally:
        module.validate_manifest = original_validate_manifest

    print("test_check_next_task_packet_ownership: OK")


if __name__ == "__main__":
    main()
