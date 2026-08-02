#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "_tools" / "compact_pr_branch.py"


def load_module():
    spec = importlib.util.spec_from_file_location("compact_pr_branch", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load compact_pr_branch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def commit_file(root: Path, name: str, content: str) -> str:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    git(root, "add", name)
    git(root, "commit", "-m", f"update {name}")
    return git(root, "rev-parse", "HEAD")


def main() -> None:
    module = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        git(root, "init")
        git(root, "config", "user.name", "test")
        git(root, "config", "user.email", "test@example.invalid")
        base = commit_file(root, "base.txt", "base\n")
        for index in range(5):
            head = commit_file(root, "work/value.txt", f"{index}\n")

        old_tree = git(root, "rev-parse", f"{head}^{{tree}}")
        old_diff = git(root, "diff", "--binary", base, head)
        compacted = module.build_compacted_commit(
            root,
            base=base,
            head=head,
            message="compact test",
        )
        assert module.commit_count(root, base, compacted) == 1
        assert git(root, "rev-parse", f"{compacted}^{{tree}}") == old_tree
        assert git(root, "diff", "--binary", base, compacted) == old_diff

        try:
            module.build_compacted_commit(
                root,
                base=head,
                head=base,
                message="invalid",
            )
        except module.CompactionError as exc:
            assert "descend" in str(exc)
        else:
            raise AssertionError("non-descendant compaction must fail")

        try:
            module.build_compacted_commit(
                root,
                base=base,
                head=head,
                message=" ",
            )
        except module.CompactionError as exc:
            assert "non-empty" in str(exc)
        else:
            raise AssertionError("empty message must fail")

    print("test_compact_pr_branch: OK")


if __name__ == "__main__":
    main()
