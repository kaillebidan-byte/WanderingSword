#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / ".github" / "workflows" / "translation-factory-plan.yml"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    assert "name: Translation factory work order" in text
    assert "workflow_dispatch:" in text
    assert "pull_request:" in text
    assert "push:" in text
    assert "permissions:\n  contents: read" in text
    for forbidden in ("contents: write", "pull-requests: write", "issues: write"):
        assert forbidden not in text
    assert "gh api" in text
    assert "translation_factory_controller.py" in text
    assert "--validate-contract-only" in text
    assert "test_translation_factory_controller.py" in text
    assert "translation-factory-work-order" in text
    assert "actions/upload-artifact@v4" in text
    print("test_translation_factory_workflow: OK")


if __name__ == "__main__":
    main()
