#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import check_fix_owner_delta as checker


def main() -> None:
    base = {
        "CG表\x1fQuestDlgs\x1fA": "old A",
        "CG表\x1fQuestDlgs\x1fB": "old B",
    }
    current = {
        "CG表\x1fQuestDlgs\x1fA": "new A",
        "CG表\x1fQuestDlgs\x1fB": "old B",
        "CG表\x1fQuestDlgs\x1fC": "new C",
    }
    owners = {key: ["fixes.json"] for key in current}
    candidate = {
        "CG表\x1fQuestDlgs\x1fA",
        "CG表\x1fQuestDlgs\x1fC",
    }
    assert checker.validate_integrity(
        base, current, owners, candidate,
        expected_new=1, expected_total=3, expected_changed=2,
    ) == []

    duplicate = dict(owners)
    duplicate["CG表\x1fQuestDlgs\x1fA"] = ["one.json", "two.json"]
    errors = checker.validate_integrity(
        base, current, duplicate, candidate,
        expected_new=1, expected_total=3, expected_changed=2,
    )
    assert any("duplicate fix owners" in error for error in errors)

    outside = {"CG表\x1fQuestDlgs\x1fC"}
    errors = checker.validate_integrity(
        base, current, owners, outside,
        expected_new=1, expected_total=3, expected_changed=2,
    )
    assert any("outside current audited candidate" in error for error in errors)

    removed = {"CG表\x1fQuestDlgs\x1fA": "new A"}
    errors = checker.validate_integrity(
        base, removed, {key: ["fixes.json"] for key in removed},
        {"CG表\x1fQuestDlgs\x1fA"},
        expected_new=0, expected_total=2, expected_changed=1,
    )
    assert any("removed from release base" in error for error in errors)

    errors = checker.validate_integrity(
        base, current, owners, candidate,
        expected_new=1, expected_total=3, expected_changed=1,
    )
    assert any("changed fix value count mismatch" in error for error in errors)

    print("test_check_fix_owner_delta: OK")


if __name__ == "__main__":
    main()
