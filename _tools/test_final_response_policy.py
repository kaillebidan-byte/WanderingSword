#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
import sys

import check_phase_completion_signal as checker
import final_response_policy as policy_module
import render_phase_completion_suffix as renderer
import test_check_phase_completion_signal as fixtures


def main() -> None:
    policy = policy_module.load_object(policy_module.POLICY_PATH)
    assert policy_module.validate_policy(policy) == []
    assert checker.MARKER not in json.dumps(policy, ensure_ascii=False)

    normal_state = fixtures.state()
    normal_gate = policy_module.build_gate(policy, normal_state)
    assert normal_gate["mode"] == "normal_response"
    assert normal_gate["reserved_terminal_token_allowed"] is False
    assert normal_gate["renderer_execution_forbidden"] is True
    assert normal_gate["safe_completion_label"] == "通常作業cycle完了"
    assert checker.MARKER not in json.dumps(normal_gate, ensure_ascii=False)

    current = {
        "mandatory_read_order": [
            "README.md",
            "AGENTS.md",
            "_phase4_proofread/EXECUTION_MODES.json",
            "_phase4_proofread/PHASE_COMPLETION_SIGNAL.json",
            "_phase4_proofread/REGULATED_PHASE_STATE.json",
            "_phase4_proofread/SESSION_BOOTSTRAP.md",
        ]
    }
    sanitized, changed = policy_module.sanitize_mandatory_read_order(current)
    assert changed is True
    order = sanitized["mandatory_read_order"]
    assert policy_module.SAFE_POLICY_ENTRY in order
    assert not policy_module.RAW_ROUTINE_ENTRIES.intersection(order)

    bad_normal = "trainはmerged / target_reachedまで完走した。\n" + checker.MARKER + "\n"
    errors = checker.validate_response(bad_normal, normal_state)
    assert errors

    try:
        renderer.render_suffix(fixtures.contract(), normal_state, fixtures.audit(), policy)
    except renderer.TerminalRenderError as exc:
        assert "not authorized" in str(exc)
    else:
        raise AssertionError("unauthorized renderer must fail closed")

    authorized_state = fixtures.state(
        "complete",
        authorization=fixtures.authorization("success"),
    )
    authorized_gate = policy_module.build_gate(policy, authorized_state)
    assert authorized_gate["mode"] == "authorized_terminal"
    assert authorized_gate["renderer_required"] is True
    assert checker.MARKER not in json.dumps(authorized_gate, ensure_ascii=False)

    suffix = renderer.render_suffix(
        fixtures.contract(),
        authorized_state,
        fixtures.audit("complete"),
        policy,
    )
    assert checker.validate_response(suffix, authorized_state, "success") == []

    completed = subprocess.run(
        [
            sys.executable,
            "_tools/resume_work_entrypoint.py",
            "--repository-visibility",
            "public",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    work_order = json.loads(completed.stdout)
    assert work_order["final_response_gate"]["mode"] == "normal_response"
    assert checker.MARKER not in completed.stdout

    print("test_final_response_policy: OK")


if __name__ == "__main__":
    main()
