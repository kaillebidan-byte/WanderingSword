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
    assert "pull-requests: write" in complete
    assert "uses: actions/github-script@v7" in complete
    assert "github.rest.issues.removeLabel" in complete
    assert "['release-ci', 'ci-heavy-rerun']" in complete
    assert "error.status !== 404" in complete
    assert "release-label-cleanup" in complete


def assert_deterministic_heads(orchestrator: str, apply: str) -> None:
    assert "asset_head:" in apply
    assert "apply_changed:" in apply
    assert "jobs.apply-and-build.outputs.asset_head" in apply
    assert "steps.release_result.outputs.asset_head" in apply
    assert "id: release_result" in apply
    assert 'asset_head="$(git rev-parse HEAD)"' in apply
    assert "needs.apply.outputs.asset_head" in orchestrator
    assert "needs.apply.outputs.apply_changed" in orchestrator
    assert "finalization-inputs.json" in orchestrator
    assert "release-finalization-inputs-" in orchestrator


def assert_institution_contract_workflow() -> None:
    text = read("institution-contract-tests.yml")
    assert "name: Institution contract tests" in text
    assert "pull_request:" in text
    assert "      - opened" in text
    assert "      - synchronize" in text
    assert "      - reopened" in text
    assert "release-ci" not in text
    assert "ci-heavy-rerun" not in text
    assert "finalize-release" not in text
    assert "test_check_operation_mode.py" in text
    assert "test_check_autonomous_cycle.py" in text
    assert "test_select_cycle_execution_mode.py" in text
    assert "check_phase_completion_signal.py" in text
    assert "test_check_phase_completion_signal.py" in text
    assert "check_state_json_integrity.py" in text
    assert "test_release_ci_triggers.py" in text


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
    assert "check_state_json_integrity.py" in preflight
    assert "check_phase_completion_signal.py" in preflight
    assert '["check_candidate_ownership.py", "--release-live"]' in preflight
    assert 'check_candidate_ownership.py", "--write' not in preflight
    assert "check_autonomous_cycle.py" in preflight
    assert "test_check_state_json_integrity.py" in preflight
    assert "test_check_phase_completion_signal.py" in preflight
    assert "test_check_autonomous_cycle.py" in preflight

    relation = assert_reusable("relation-audit.yml")
    cross = assert_reusable("cross-register-qa.yml")
    apply = assert_reusable("apply-curated-fixes.yml")
    assert "check_release_transport_state.py" in relation
    assert "check_release_evidence.py" not in relation
    assert "check_handoff_consistency_v2.py" not in relation
    assert "target_sha:" in relation and "target_sha:" in cross
    assert "check_candidate_ownership.py --release-live" in relation
    assert "check_candidate_ownership.py --release-live" in cross
    assert "check_candidate_ownership.py --require-current-wave" not in relation
    assert "check_candidate_ownership.py --require-current-wave" not in cross
    assert "target_sha:" in apply and "head_ref:" in apply
    assert "check_release_transport_state.py" in apply
    assert "check_candidate_ownership.py --release-live" in apply
    assert "check_candidate_ownership.py --require-current-wave" not in apply
    assert "write_applied_record.py" in apply
    assert "git status --porcelain" in apply
    assert_deterministic_heads(orchestrator, apply)

    phase2 = assert_labeled_repair_rerun("ci-train-phase2.yml", ("finalize-release",))
    assert "check_release_finalization.py --with-tests" in phase2
    assert "check_release_evidence_github.py" in phase2
    finalization = (ROOT / "_tools" / "check_release_finalization.py").read_text(encoding="utf-8")
    assert "check_state_json_integrity.py" in finalization
    assert "check_release_evidence.py" in finalization
    assert "check_handoff_consistency_v2.py" in finalization
    assert '("check_candidate_ownership.py", "--release-live")' in finalization
    assert "check_autonomous_cycle.py" in finalization

    assert_institution_contract_workflow()
    print("OK: release reruns stay bounded, institution tests are lightweight, and finalization inputs are deterministic")


if __name__ == "__main__":
    main()
