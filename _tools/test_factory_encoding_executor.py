#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import factory_encoding_executor as executor


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        p4 = Path(temp) / "_phase4_proofread"
        p4.mkdir()
        write(p4 / "CURRENT_WORK.json", {
            "ci_train": {"private_stage": {"stage": "translation_frozen"}},
        })
        write(p4 / "PRIVATE_STAGE_STATE.json", {
            "stage": "translation_frozen",
            "transport": {"status": "ready_for_public_ci"},
        })
        write(p4 / "CI_TRAIN_MANIFEST.json", {
            "train_id": "yuwen-mowen-train-27",
            "branch": "agent/yuwen-mowen-train-27",
            "status": "ready_for_public_ci",
            "bundles": [{"batch": 158, "keep_keys": 59}],
            "totals": {"reviewed_rows": 62, "fix_keys": 3},
        })
        write(p4 / "NEXT_TASK_PACKET.json", {
            "reservation": {"status": "encoded"},
            "ci_train": {"planned_batch": 159},
        })
        result = executor.apply_transport_contract(p4=p4, pr_number=166)
        assert result["formal_batches"] == [158]
        packet = json.loads((p4 / "NEXT_TASK_PACKET.json").read_text(encoding="utf-8"))
        assert packet["ci_train"]["planned_batch"] == 158
        assert packet["release_candidate"] == {
            "train_id": "yuwen-mowen-train-27",
            "release_id": "yuwen-mowen-train-27-r1",
            "pr": 166,
            "status": "ready_for_public_ci",
        }
        handoff = (p4 / "CURRENT_HANDOFF.md").read_text(encoding="utf-8")
        assert executor.RESTART_PHRASE in handoff
        assert "translation_frozen" in handoff
    print("test_factory_encoding_executor: OK")


if __name__ == "__main__":
    main()
