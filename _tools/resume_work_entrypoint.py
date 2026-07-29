#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""再開controllerへ最終応答modeを付与し、予約tokenをroutine work orderへ露出させない唯一入口。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import final_response_policy as response_policy
import resume_work_controller as resume
import translation_factory_controller as translation

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-visibility", choices=sorted(translation.VALID_VISIBILITIES), required=True)
    parser.add_argument("--validate-contract-only", action="store_true")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        queue = resume.load_object(resume.QUEUE_PATH)
        contract = resume.load_object(resume.CONTRACT_PATH)
        policy = response_policy.load_object(response_policy.POLICY_PATH)
        state = resume.load_object(resume.STATE_PATH)
        errors = [
            *resume.validate_queue(queue),
            *translation.validate_contract(contract),
            *response_policy.validate_policy(policy),
        ]
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        if args.validate_contract_only:
            print("OK: resume, factory, and final response policies are valid")
            return 0

        work_order = resume.build_resume_work_order(
            queue,
            contract,
            resume.load_object(resume.CURRENT_PATH),
            state,
            resume.load_object(resume.MANIFEST_PATH),
            resume.load_object(resume.PACKET_PATH),
            args.repository_visibility,
        )
        work_order["final_response_gate"] = response_policy.build_gate(policy, state)
        response_policy.assert_work_order_is_opaque(work_order)
    except (
        OSError,
        json.JSONDecodeError,
        resume.ResumeStateError,
        translation.FactoryStateError,
        response_policy.FinalResponsePolicyError,
    ) as exc:
        code = getattr(exc, "code", "resume_entrypoint_error")
        detail = getattr(exc, "detail", str(exc))
        print(json.dumps({"status": "blocked", "error_code": code, "detail": detail}, ensure_ascii=False))
        return 1

    text = json.dumps(work_order, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
