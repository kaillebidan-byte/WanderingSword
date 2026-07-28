#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / ".github" / "workflows" / "translation-factory-plan.yml"
EXECUTE = ROOT / ".github" / "workflows" / "translation-factory-execute.yml"
FINALIZE = ROOT / ".github" / "workflows" / "translation-factory-finalize.yml"


def main() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "name: Translation factory work order" in plan
    assert "workflow_dispatch:" in plan
    assert "pull_request:" in plan
    assert "push:" in plan
    assert "permissions:\n  contents: read" in plan
    for forbidden in ("contents: write", "pull-requests: write", "issues: write"):
        assert forbidden not in plan
    assert "gh api" in plan
    assert "translation_factory_controller.py" in plan
    assert "translation-factory-work-order" in plan

    execute = EXECUTE.read_text(encoding="utf-8")
    assert "name: Translation factory executor" in execute
    assert '      - "agent/yuwen-mowen-train-*"' in execute
    assert "pull_request:" in execute
    assert "github.event.pull_request.head.repo.full_name == github.repository" in execute
    assert '      - "_factory_requests/*.json"' in execute
    assert "permissions:\n  contents: write\n  actions: read" in execute
    assert "github.actor != 'github-actions[bot]'" in execute
    assert "gh run download" in execute
    assert "factory_request_executor.py" in execute
    assert "check_factory_adapters.py" not in execute
    assert "translation_quality_audit" in execute
    assert 'git rm "${{ steps.request.outputs.request }}"' in execute
    assert 'git push origin "HEAD:${branch_name}"' in execute
    for forbidden in ("oneoff", "alternate trigger", "workflow_dispatch:"):
        assert forbidden not in execute

    finalize = FINALIZE.read_text(encoding="utf-8")
    assert "name: Translation factory finalization" in finalize
    assert 'git rm "${{ steps.request.outputs.request }}"' in finalize
    assert "git add _phase4_proofread" in finalize
    assert "git add _phase4_proofread _factory_requests" not in finalize
    assert "fixed_release_finalizer.py" in finalize
    assert "check_release_evidence.py --verify-git-lineage" in finalize

    print("test_translation_factory_workflow: OK")


if __name__ == "__main__":
    main()
