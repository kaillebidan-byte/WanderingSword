#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from factory_request_executor import classify_branch_update


def main() -> None:
    base = "a" * 40
    assert classify_branch_update(base, base, []) == "ready_to_push"

    remote = "b" * 40
    assert classify_branch_update(base, remote, []) == "already_applied"

    differing = ["_phase4_proofread/CURRENT_WORK.json"]
    assert classify_branch_update(base, remote, differing) == "conflict"

    print("test_factory_request_executor: OK")


if __name__ == "__main__":
    main()
