#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def assert_label_only(name: str) -> str:
    text = read(name)
    assert "types:\n      - labeled" in text, name
    for forbidden in ("      - opened\n", "      - reopened\n", "      - ready_for_review\n", "      - synchronize\n"):
        assert forbidden not in text, f"{name}: unexpected automatic trigger {forbidden.strip()}"
    assert "github.event.repository.visibility == 'public'" in text, name
    return text


def main() -> None:
    orchestrator = assert_label_only("release-train-orchestrator.yml")
    assert "github.event.label.name == 'release-ci'" in orchestrator
    assert "github.event.label.name == 'ci-heavy-rerun'" in orchestrator
    assert "check_private_release_preflight.py" in orchestrator
    assert "orchestrate_release_ci.py" in orchestrator

    relation = assert_label_only("relation-audit.yml")
    cross = assert_label_only("cross-register-qa.yml")
    apply = assert_label_only("apply-curated-fixes.yml")
    for name, text in (("relation", relation), ("cross", cross)):
        assert "github.event.label.name == 'release-qa'" in text, name
        assert "github.event.label.name == 'release-ci'" not in text, name
    assert "check_release_transport_state.py" in relation
    assert "check_release_evidence.py" not in relation
    assert "check_handoff_consistency_v2.py" not in relation

    assert "github.event.label.name == 'release-apply'" in apply
    assert "github.event.label.name == 'release-ci'" not in apply
    assert "check_release_transport_state.py" in apply
    assert "write_applied_record.py" in apply
    assert "git status --porcelain" in apply

    phase2 = assert_label_only("ci-train-phase2.yml")
    assert "github.event.label.name == 'finalize-release'" in phase2
    assert "check_release_evidence.py" in phase2
    assert "check_handoff_consistency_v2.py --require-verified" in phase2
    print("OK: pre-Apply checks are light; strict release evidence is phase2-only")


if __name__ == "__main__":
    main()
