#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub release evidence checkerの旧三runとorchestrator runを回帰検証する。"""
from __future__ import annotations

import copy

import check_release_evidence_github as target


def sample_v1(mode: str) -> dict:
    merge_sha = "c" * 40 if mode == "squash_merged" else None
    return {
        "schema_version": 1,
        "pr": 106,
        "ci_head": "a" * 40,
        "runs": {"relation": {"id": 1}, "cross": {"id": 2}, "apply": {"id": 3}},
        "lineage": {"mode": mode, "merge_sha": merge_sha},
    }


def sample_v2(mode: str = "branch_ancestor") -> dict:
    return {
        "schema_version": 2,
        "pr": 106,
        "ci_head": "a" * 40,
        "orchestrator": {"id": 10},
        "lineage": {"mode": mode, "merge_sha": ("c" * 40 if mode == "squash_merged" else None)},
    }


def fake_fetch(url: str, token: str) -> dict:
    del token
    if url.endswith("/pulls/106"):
        return {"merged": True, "merge_commit_sha": "c" * 40}
    if url.endswith("/actions/runs/10/jobs?per_page=100"):
        return {
            "jobs": [
                {"name": "relation / extract", "conclusion": "success"},
                {"name": "cross / lint", "conclusion": "success"},
                {"name": "apply / apply-and-build", "conclusion": "success"},
            ]
        }
    run_id = int(url.rsplit("/", 1)[-1])
    names = {
        1: "Relation audit extraction",
        2: "Cross register QA",
        3: "Apply curated localization fixes",
        10: "Release train orchestrator",
    }
    return {
        "name": names[run_id],
        "conclusion": "success",
        "head_sha": "a" * 40,
        "event": "pull_request",
        "pull_requests": [{"number": 106}] if run_id == 10 else [],
    }


def main() -> None:
    squash = sample_v1("squash_merged")
    assert target.verify_github(squash, "owner/repo", "token", fetch_json=fake_fetch) == []

    active = sample_v1("branch_ancestor")
    errors = target.verify_github(active, "owner/repo", "token", fetch_json=fake_fetch)
    assert len([error for error in errors if "not attached to PR #106" in error]) == 3

    assert target.verify_github(sample_v2(), "owner/repo", "token", fetch_json=fake_fetch) == []

    bad_merge = copy.deepcopy(squash)
    bad_merge["lineage"]["merge_sha"] = "d" * 40
    errors = target.verify_github(bad_merge, "owner/repo", "token", fetch_json=fake_fetch)
    assert any("merge SHA" in error for error in errors)

    def missing_apply(url: str, token: str) -> dict:
        value = fake_fetch(url, token)
        if url.endswith("/actions/runs/10/jobs?per_page=100"):
            value["jobs"] = [job for job in value["jobs"] if "apply" not in job["name"]]
        return value

    errors = target.verify_github(sample_v2(), "owner/repo", "token", fetch_json=missing_apply)
    assert any("lacks apply job" in error for error in errors)
    print("test_check_release_evidence_github: OK")


if __name__ == "__main__":
    main()
