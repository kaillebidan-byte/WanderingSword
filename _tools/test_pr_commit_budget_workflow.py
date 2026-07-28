#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "pr-commit-budget.yml"


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: PR commit budget" in text
    assert "pull_request:" in text
    assert "      - opened" in text
    assert "      - synchronize" in text
    assert "      - reopened" in text
    assert "contents: read" in text
    assert "fetch-depth: 0" in text
    assert "check_pr_commit_budget.py --validate-policy-only" in text
    assert "--base \"${{ github.event.pull_request.base.sha }}\"" in text
    assert "--head \"${{ github.event.pull_request.head.sha }}\"" in text
    assert "test_check_pr_commit_budget.py" in text
    for forbidden in (
        "contents: write",
        "pull-requests: write",
        "release-ci",
        "ci-heavy-rerun",
        "finalize-release",
        "relation-audit.yml",
        "apply-curated-fixes.yml",
    ):
        assert forbidden not in text, forbidden
    print("test_pr_commit_budget_workflow: OK")


if __name__ == "__main__":
    main()
