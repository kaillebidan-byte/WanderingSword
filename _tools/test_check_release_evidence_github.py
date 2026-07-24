#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub release evidence checkerのlineage別PR対応を回帰検証する。"""
from __future__ import annotations

import copy

import check_release_evidence_github as target


def sample_evidence(mode: str) -> dict:
    merge_sha = "c" * 40 if mode == "squash_merged" else None
    return {
        "pr": 106,
        "ci_head": "a" * 40,
        "runs": {
            "relation": {"id": 1},
            "cross": {"id": 2},
            "apply": {"id": 3},
        },
        "lineage": {"mode": mode, "merge_sha": merge_sha},
    }


def fake_fetch(url: str, token: str) -> dict:
    del token
    if url.endswith("/pulls/106"):
        return {"merged": True, "merge_commit_sha": "c" * 40}
    run_id = int(url.rsplit("/", 1)[-1])
    names = {
        1: "Relation audit extraction",
        2: "Cross register QA",
        3: "Apply curated localization fixes",
    }
    return {
        "name": names[run_id],
        "conclusion": "success",
        "head_sha": "a" * 40,
        "event": "pull_request",
        "pull_requests": [],
    }


def main() -> None:
    squash = sample_evidence("squash_merged")
    assert target.verify_github(
        squash, "owner/repo", "token", fetch_json=fake_fetch
    ) == []

    active = sample_evidence("branch_ancestor")
    errors = target.verify_github(
        active, "owner/repo", "token", fetch_json=fake_fetch
    )
    assert len([error for error in errors if "not attached to PR #106" in error]) == 3

    bad_merge = copy.deepcopy(squash)
    bad_merge["lineage"]["merge_sha"] = "d" * 40
    errors = target.verify_github(
        bad_merge, "owner/repo", "token", fetch_json=fake_fetch
    )
    assert any("merge SHA" in error for error in errors)

    print("test_check_release_evidence_github: OK")


if __name__ == "__main__":
    main()
