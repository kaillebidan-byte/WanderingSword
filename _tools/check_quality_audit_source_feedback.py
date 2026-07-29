#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""現在のquality-audit decisionが読書契約と人物資料還流契約を満たすことを検査する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import source_document_feedback as feedback

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise feedback.SourceFeedbackError(f"top level must be object: {path}")
    return value


def resolve_current_audit() -> Path:
    current = load(P4 / "CURRENT_WORK.json")
    train_id = current.get("ci_train", {}).get("train_id")
    if not isinstance(train_id, str) or not train_id:
        raise feedback.SourceFeedbackError("CURRENT_WORK train_id is missing")
    matches = []
    for path in sorted(P4.glob("AUDIT_DECISIONS_*.json")):
        value = load(path)
        if value.get("train_id") == train_id and value.get("status") == "complete":
            matches.append(path)
    if len(matches) != 1:
        raise feedback.SourceFeedbackError(
            f"expected one complete audit for {train_id}, found {len(matches)}"
        )
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path)
    args = parser.parse_args()
    try:
        audit_path = args.audit or resolve_current_audit()
        audit_path = audit_path if audit_path.is_absolute() else ROOT / audit_path
        results = feedback.validate_audit(load(audit_path), ROOT)
    except (OSError, json.JSONDecodeError, feedback.SourceFeedbackError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"OK: {audit_path.relative_to(ROOT)} satisfies reading and persona feedback contracts "
        f"for {len(results)} decision(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
