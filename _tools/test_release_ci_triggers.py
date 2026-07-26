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


def assert_reusable(name: str) -> str:
    text = read(name)
    assert "workflow_call:" in text, name
    assert "pull_request:" not in text, name
    return text


def assert_private_preflight() -> str:
    text = read("private-release-preflight.yml")
    for trigger in ("      - opened\n", "      - reopened\n", "      - ready_for_review\n", "      - synchronize\n"):
        assert trigger in text, f"private preflight lacks {trigger.strip()} trigger"
    assert "github.event.repository.visibility == 'private'" in text
    assert "github.event.pull_request.draft == false" in text
    assert "ready_for_public_ci" in text
    assert "check_private_release_preflight.py" in text
    assert "--repository-visibility private" in text
    assert "--with-tests" in text
    assert "contents: write" not in text
    for forbidden in (
        "uses: ./.github/workflows/relation-audit.yml",
        "uses: ./.github/workflows/cross-register-qa.yml",
        "uses: ./.github/workflows/apply-curated-fixes.yml",
    ):
        assert forbidden not in text, f"private preflight must stay lightweight: {forbidden}"
    return text


def main() -> None:
    private_preflight = assert_private_preflight()
    assert "private-release-preflight-${{ github.event.pull_request.number }}" in private_preflight

    orchestrator = assert_label_only("release-train-orchestrator.yml")
    assert "github.event.label.name == 'release-ci'" in orchestrator
    assert "github.event.label.name == 'ci-heavy-rerun'" in orchestrator
    assert "check_private_release_preflight.py" in orchestrator
    assert "uses: ./.github/workflows/relation-audit.yml" in orchestrator
    assert "uses: ./.github/workflows/cross-register-qa.yml" in orchestrator
    assert "uses: ./.github/workflows/apply-curated-fixes.yml" in orchestrator
    assert "needs: preflight" in orchestrator
    assert "      - relation\n      - cross" in orchestrator

    preflight = (ROOT / "_tools" / "check_private_release_preflight.py").read_text(encoding="utf-8")
    assert "check_autonomous_cycle.py" in preflight
    assert "test_check_autonomous_cycle.py" in preflight

    relation = assert_reusable("relation-audit.yml")
    cross = assert_reusable("cross-register-qa.yml")
    apply = assert_reusable("apply-curated-fixes.yml")
    assert "check_release_transport_state.py" in relation
    assert "check_release_evidence.py" not in relation
    assert "check_handoff_consistency_v2.py" not in relation
    assert "target_sha:" in relation and "target_sha:" in cross
    assert "target_sha:" in apply and "head_ref:" in apply
    assert "check_release_transport_state.py" in apply
    assert "write_applied_record.py" in apply
    assert "git status --porcelain" in apply

    phase2 = assert_label_only("ci-train-phase2.yml")
    assert "github.event.label.name == 'finalize-release'" in phase2
    assert "check_release_evidence.py" in phase2
    assert "check_handoff_consistency_v2.py --require-verified" in phase2
    assert "check_autonomous_cycle.py" in phase2
    assert "test_check_autonomous_cycle.py" in phase2
    print("OK: private preflight runs before public transport; public CI remains label-only and ordered")


if __name__ == "__main__":
    main()
