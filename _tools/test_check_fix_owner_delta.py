#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import check_fix_owner_delta as checker


def main() -> None:
    base_owners = {
        "CG表\x1fQuestDlgs\x1fA": "stale owner A",
        "CG表\x1fQuestDlgs\x1fB": "old B",
    }
    base_translation = {
        "CG表\x1fQuestDlgs\x1fA": "old A",
        "CG表\x1fQuestDlgs\x1fB": "old B",
        "CG表\x1fQuestDlgs\x1fC": "old C",
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
        base_owners, base_translation, current, owners, candidate,
        expected_new=1, expected_total=3, expected_changed=2,
    ) == []

    # 新しいownerでもrelease基準locresと同値なら、fix件数には数えない。
    keep_base_owners = {"CG表\x1fQuestDlgs\x1fA": "old A"}
    keep_base_translation = {
        "CG表\x1fQuestDlgs\x1fA": "old A",
        "CG表\x1fQuestDlgs\x1fK": "kept K",
    }
    keep_current = {
        "CG表\x1fQuestDlgs\x1fA": "old A",
        "CG表\x1fQuestDlgs\x1fK": "kept K",
    }
    assert checker.validate_integrity(
        keep_base_owners,
        keep_base_translation,
        keep_current,
        {key: ["fixes.json"] for key in keep_current},
        {"CG表\x1fQuestDlgs\x1fK"},
        expected_new=1,
        expected_total=2,
        expected_changed=0,
    ) == []

    duplicate = dict(owners)
    duplicate["CG表\x1fQuestDlgs\x1fA"] = ["one.json", "two.json"]
    errors = checker.validate_integrity(
        base_owners, base_translation, current, duplicate, candidate,
        expected_new=1, expected_total=3, expected_changed=2,
    )
    assert any("duplicate fix owners" in error for error in errors)

    outside = {"CG表\x1fQuestDlgs\x1fC"}
    errors = checker.validate_integrity(
        base_owners, base_translation, current, owners, outside,
        expected_new=1, expected_total=3, expected_changed=2,
    )
    assert any("outside current audited candidate" in error for error in errors)

    removed = {"CG表\x1fQuestDlgs\x1fA": "new A"}
    errors = checker.validate_integrity(
        base_owners,
        base_translation,
        removed,
        {key: ["fixes.json"] for key in removed},
        {"CG表\x1fQuestDlgs\x1fA"},
        expected_new=0,
        expected_total=2,
        expected_changed=1,
    )
    assert any("removed from release base" in error for error in errors)

    errors = checker.validate_integrity(
        base_owners, base_translation, current, owners, candidate,
        expected_new=1, expected_total=3, expected_changed=1,
    )
    assert any("translation fix count mismatch" in error for error in errors)

    print("test_check_fix_owner_delta: OK")


if __name__ == "__main__":
    main()
