#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""live認可済みの場合だけ規定フェイズ終端suffixを決定的に生成する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import check_phase_completion_signal as checker
import final_response_policy as response_policy

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"


class TerminalRenderError(ValueError):
    pass


def render_suffix(
    contract: dict[str, Any],
    state: dict[str, Any],
    audit_status: dict[str, Any],
    policy: dict[str, Any],
) -> str:
    errors = [
        *checker.validate_contract(contract),
        *checker.validate_runtime_state(state, audit_status),
        *response_policy.validate_policy(policy),
    ]
    if errors:
        raise TerminalRenderError("; ".join(errors))
    gate = response_policy.build_gate(policy, state)
    if gate.get("mode") != "authorized_terminal":
        raise TerminalRenderError("regulated terminal suffix is not authorized")

    authorization = state["signal_authorization"]
    result = authorization["result"]
    event_id = authorization["event_id"]
    text = (
        f"{checker.AUTH_PREFIX}{event_id}\n"
        f"{checker.STATUS_PREFIX}{result}\n"
        f"{checker.MARKER}\n"
    )
    validation = checker.validate_response(text, state, result)
    if validation:
        raise TerminalRenderError("; ".join(validation))
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = render_suffix(
            response_policy.load_object(checker.CONTRACT_PATH),
            response_policy.load_object(checker.STATE_PATH),
            response_policy.load_object(checker.AUDIT_STATUS_PATH),
            response_policy.load_object(response_policy.POLICY_PATH),
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
