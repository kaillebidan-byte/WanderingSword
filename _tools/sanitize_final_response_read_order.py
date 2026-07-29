#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CURRENT_WORKのroutine read orderから生の終端契約を除き、安全policyへ置換する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import final_response_policy as response_policy

ROOT = Path(__file__).resolve().parent.parent
CURRENT_PATH = ROOT / "_phase4_proofread" / "CURRENT_WORK.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        policy = response_policy.load_object(response_policy.POLICY_PATH)
        errors = response_policy.validate_policy(policy)
        if errors:
            raise response_policy.FinalResponsePolicyError("; ".join(errors))
        current = response_policy.load_object(CURRENT_PATH)
        updated, changed = response_policy.sanitize_mandatory_read_order(current)
        if args.write and changed:
            CURRENT_PATH.write_text(
                json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print("updated" if changed else "NOOP: final response read order already safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
