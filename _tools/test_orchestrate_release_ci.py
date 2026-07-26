#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import orchestrate_release_ci as orchestrator


def main() -> None:
    sha = "a" * 40
    runs = [
        {"id": 10, "name": "Relation audit extraction", "head_sha": sha, "status": "completed", "conclusion": "success"},
        {"id": 12, "name": "Relation audit extraction", "head_sha": sha, "status": "completed", "conclusion": "success"},
        {"id": 13, "name": "Relation audit extraction", "head_sha": "b" * 40, "status": "completed", "conclusion": "success"},
        {"id": 14, "name": "Cross register QA", "head_sha": sha, "status": "in_progress", "conclusion": None},
    ]
    selected = orchestrator.select_new_run(runs, "Relation audit extraction", 10, sha)
    assert selected is not None and selected["id"] == 12
    assert orchestrator.select_new_run(runs, "Relation audit extraction", 12, sha) is None
    cross = orchestrator.select_new_run(runs, "Cross register QA", 0, sha)
    assert cross is not None and cross["id"] == 14
    print("OK: orchestrator selects only new runs on the frozen release HEAD")


if __name__ == "__main__":
    main()
