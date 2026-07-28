#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "check_pr_commit_budget.py"
POLICY_PATH = ROOT / "_phase4_proofread" / "GITHUB_API_WRITE_POLICY.json"


def load_module():
    spec = importlib.util.spec_from_file_location("check_pr_commit_budget", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load check_pr_commit_budget.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout.strip()


def commit_file(root: Path, name: str, content: str) -> str:
    (root / name).write_text(content, encoding="utf-8")
    git(root, "add", name)
    git(root, "commit", "-m", f"update {name}")
    return git(root, "rev-parse", "HEAD")


def main() -> None:
    module = load_module()
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert module.validate_policy(policy) == []

    bad = json.loads(json.dumps(policy))
    bad["write_transport"]["file_by_file_contents_commit_loop_forbidden"] = False
    assert any("file-by-file" in error for error in module.validate_policy(bad))

    bad = json.loads(json.dumps(policy))
    bad["discovery"]["web_search_for_github_api_usage_forbidden"] = False
    assert any("web search" in error for error in module.validate_policy(bad))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        git(root, "init")
        git(root, "config", "user.name", "test")
        git(root, "config", "user.email", "test@example.invalid")
        base = commit_file(root, "base.txt", "base\n")
        for index in range(3):
            head = commit_file(root, "work.txt", f"{index}\n")
        assert module.count_commits(base, head, root=root) == 3

    print("test_check_pr_commit_budget: OK")


if __name__ == "__main__":
    main()
