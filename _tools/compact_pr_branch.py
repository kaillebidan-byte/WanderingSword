#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a one-commit PR snapshot without changing the HEAD tree."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class CompactionError(ValueError):
    pass


def git(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=merged_env,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed"
        raise CompactionError(message)
    return result.stdout.strip()


def object_sha(root: Path, value: str) -> str:
    sha = git(root, "rev-parse", "--verify", f"{value}^{{commit}}")
    if not SHA_RE.fullmatch(sha):
        raise CompactionError(f"invalid commit sha resolved from {value}: {sha}")
    return sha


def commit_count(root: Path, base: str, head: str) -> int:
    return int(git(root, "rev-list", "--count", f"{base}..{head}"))


def build_compacted_commit(
    root: Path,
    *,
    base: str,
    head: str,
    message: str,
) -> str:
    base_sha = object_sha(root, base)
    head_sha = object_sha(root, head)
    if base_sha == head_sha:
        raise CompactionError("base and head must differ")
    try:
        git(root, "merge-base", "--is-ancestor", base_sha, head_sha)
    except CompactionError as exc:
        raise CompactionError("head must descend from base") from exc
    if not message.strip():
        raise CompactionError("commit message must be non-empty")

    old_tree = git(root, "rev-parse", f"{head_sha}^{{tree}}")
    commit_env = {
        "GIT_AUTHOR_NAME": "pr-history-compactor",
        "GIT_AUTHOR_EMAIL": "pr-history-compactor@users.noreply.github.com",
        "GIT_COMMITTER_NAME": "pr-history-compactor",
        "GIT_COMMITTER_EMAIL": "pr-history-compactor@users.noreply.github.com",
    }
    new_sha = git(
        root,
        "commit-tree",
        old_tree,
        "-p",
        base_sha,
        "-m",
        message.strip(),
        env=commit_env,
    )
    if not SHA_RE.fullmatch(new_sha):
        raise CompactionError(f"git commit-tree returned invalid sha: {new_sha}")

    new_tree = git(root, "rev-parse", f"{new_sha}^{{tree}}")
    if new_tree != old_tree:
        raise CompactionError("compacted commit tree differs from original head tree")
    if commit_count(root, base_sha, new_sha) != 1:
        raise CompactionError("compacted history must contain exactly one commit")
    return new_sha


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        new_sha = build_compacted_commit(
            args.root.resolve(),
            base=args.base,
            head=args.head,
            message=args.message,
        )
    except (OSError, CompactionError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(new_sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
