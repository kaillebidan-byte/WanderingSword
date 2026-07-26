#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import check_candidate_ownership as checker


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def test_snapshot_and_staleness() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        p4 = root / "_phase4_proofread"
        key_a = checker.full_key("CG表", "QuestDlgs", "A")
        key_b = checker.full_key("CG表", "QuestDlgs", "B")
        write_json(p4 / "fixes_relation_a.json", {key_a: "訳A"})
        candidate = {"schema_version": 2, "rows": [{"key": "A"}, {"key": "B"}]}
        snapshot, errors = checker.compute_snapshot(candidate, p4=p4)
        assert not errors
        assert snapshot["existing"] == [{"path": "_phase4_proofread/fixes_relation_a.json", "keys": ["A"]}]
        assert snapshot["unowned"] == ["B"]
        candidate["ownership_snapshot"] = snapshot
        assert checker.validate_candidate(candidate, p4=p4, require_snapshot=True) == []

        write_json(p4 / "fixes_cross_register_b.json", {key_b: "訳B"})
        stale = checker.validate_candidate(candidate, p4=p4, require_snapshot=True)
        assert any("stale or incomplete" in item for item in stale)

        live, live_errors, drift = checker.validate_candidate_live(candidate, p4=p4)
        assert live_errors == []
        assert drift is True
        assert live["unowned"] == []
        assert sum(len(item["keys"]) for item in live["existing"]) == 2


def test_release_live_rejects_corrupt_partition() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        p4 = root / "_phase4_proofread"
        key = checker.full_key("CG表", "QuestDlgs", "A")
        write_json(p4 / "fixes_relation_a.json", {key: "訳A"})
        candidate = {"schema_version": 2, "rows": [{"key": "A"}]}
        snapshot, errors = checker.compute_snapshot(candidate, p4=p4)
        assert not errors
        snapshot["unowned"] = ["B"]
        candidate["ownership_snapshot"] = snapshot
        _, result, _ = checker.validate_candidate_live(candidate, p4=p4)
        assert any("row partition" in item for item in result)


def test_duplicate_owner_fails() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        p4 = root / "_phase4_proofread"
        key = checker.full_key("CG表", "QuestDlgs", "A")
        write_json(p4 / "fixes_relation_a.json", {key: "訳A"})
        write_json(p4 / "fixes_relation_b.json", {key: "訳A"})
        candidate = {"schema_version": 2, "rows": [{"key": "A"}]}
        snapshot, errors = checker.compute_snapshot(candidate, p4=p4)
        assert not errors
        candidate["ownership_snapshot"] = snapshot
        result = checker.validate_candidate(candidate, p4=p4, require_snapshot=True)
        assert any("multiple fix owners" in item for item in result)
        _, live_result, _ = checker.validate_candidate_live(candidate, p4=p4)
        assert any("multiple live fix owners" in item for item in live_result)


def main() -> None:
    test_snapshot_and_staleness()
    test_release_live_rejects_corrupt_partition()
    test_duplicate_owner_fails()
    print("OK: candidate ownership tests")


if __name__ == "__main__":
    main()
