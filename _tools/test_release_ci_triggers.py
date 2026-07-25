#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def assert_heavy(name: str) -> None:
    text = read(name)
    assert "types:\n      - labeled" in text, name
    for forbidden in ("      - opened\n", "      - reopened\n", "      - ready_for_review\n", "      - synchronize\n"):
        assert forbidden not in text, f"{name}: unexpected automatic trigger {forbidden.strip()}"
    assert "github.event.label.name == 'release-ci'" in text, name
    assert "github.event.label.name == 'ci-heavy-rerun'" in text, name
    assert "github.event.repository.visibility == 'public'" in text, name


def main() -> None:
    for name in ("relation-audit.yml", "cross-register-qa.yml", "apply-curated-fixes.yml"):
        assert_heavy(name)
    phase2 = read("ci-train-phase2.yml")
    assert "types:\n      - labeled" in phase2
    assert "github.event.label.name == 'finalize-release'" in phase2
    assert "      - synchronize\n" not in phase2
    assert "      - opened\n" not in phase2
    print("OK: release CI triggers are explicit and two-stage")


if __name__ == "__main__":
    main()
