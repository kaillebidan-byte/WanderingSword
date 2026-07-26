#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def assert_labeled_repair_rerun(name: str, labels: tuple[str, ...]) -> str:
    text = read(name)
    assert "types:\n      - labeled\n      - synchronize" in text, name
    for forbidden in ("      - opened\n", "      - reopened\n", "      - ready_for_review\n"):
        assert forbidden not in text, f"{name}: unexpected automatic trigger {forbidden.strip()}"
    assert "github.actor != 'github-actions[bot]'" in text, name
    assert "github.event.repository.visibility == 'public'" in text, name
    assert "github.event.action == 'labeled'" in text, name
    assert "github.event.action == 'synchronize'" in text, name
    for label in labels:
        assert f"github.event.label.name == '{label}'" in text, f"{name}: missing labeled trigger for {label}"
        assert f"contains(github.event.pull_request.labels.*.name, '{label}')" in text, f"{name}: missing repair rerun for {label}"
    return text


def assert_reusable(name: str) -> str:
    text = read(name)
    assert "workflow_call:" in text, name
    assert "pull_request:" not in text, name
    return text


def assert_release_label_cleanup(orchestrator: str) -> None:
    complete = orchestrator.split("\n  complete:\n", 1)[1]
    assert "needs: apply" in complete
    assert "issues: write" in complete
    assert "uses: actions/github-script@v7" in complete
    assert "github.rest.issues.removeLabel" in complete
    assert "['release-ci', 'ci-heavy-rerun']" in complete
    assert "release-label-cleanup" in complete


def main() -> None:
    orchestrator = assert_labeled_repair_rerun(
        "release-train-orchestrator.yml",
        ("release-ci", "ci-heavy-rerun"),
    )
    assert "check_private_release_preflight.py" in orchestrator
    assert "uses: ./.github/workflows/relation-audit.yml" in orchestrator
    assert "uses: ./.github/workflows/cross-register-qa.yml" in orchestrator
    assert "uses: ./.github/workflows/apply-curated-fixes.yml" in orchestrator
    assert "needs: preflight" in orchestrator
    assert "      - relation\n      - cross" in orchestrator
    assert_release_label_cleanup(orchestrator)

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

    phase2 = assert_labeled_repair_rerun("ci-train-phase2.yml", ("finalize-release",))
    assert "check_release_evidence.py" in phase2
    assert "check_handoff_consistency_v2.py --require-verified" in phase2
    assert "check_autonomous_cycle.py" in phase2
    assert "test_check_autonomous_cycle.py" in phase2
    print("OK: failed labeled runs rerun on repair pushes; successful orchestrator labels stop before finalization")


if __name__ == "__main__":
    main()
