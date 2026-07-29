#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import quality_audit_context as context


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture() -> tuple[Path, Path]:
    root = Path(tempfile.mkdtemp())
    contract = json.loads(
        (
            Path(__file__).resolve().parent.parent
            / "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"
        ).read_text(encoding="utf-8")
    )
    write(
        root / "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json",
        json.dumps(contract, ensure_ascii=False),
    )
    for relative in contract["required_documents"]:
        write(root / relative, f"# fixture {relative}\n")
    write(
        root / "10_人物/宇文逸.md",
        "---\nname: 宇文逸\naliases: [宇文逸]\n---\n\n# 宇文逸\n",
    )
    write(
        root / "10_人物/莫問.md",
        "---\nname: 莫問\naliases: [莫問, 莫问]\n---\n\n# 莫問\n",
    )
    candidate_path = root / "_phase4_proofread/CANDIDATE_TEST.json"
    write(
        candidate_path,
        json.dumps(
            {
                "schema_version": 2,
                "current_pair": "宇文逸↔莫問",
                "rows": [
                    {"key": "k1", "speaker": "宇文逸", "zh": "zh", "ja": "ja"},
                    {"key": "k2", "speaker": "莫问", "zh": "zh", "ja": "ja"},
                    {"key": "k3", "speaker": "未登録", "zh": "zh", "ja": "ja"},
                ],
                "forbidden_outputs": [],
            },
            ensure_ascii=False,
        ),
    )
    write(
        root / "_phase4_proofread/CURRENT_WORK.json",
        json.dumps({"immediate_next": {}}, ensure_ascii=False),
    )
    write(
        root / "_phase4_proofread/PRIVATE_STAGE_STATE.json",
        json.dumps(
            {
                "wave": {
                    "packets": [
                        {
                            "packet_id": "p1",
                            "preparation_record": {
                                "candidate_packet": "_phase4_proofread/CANDIDATE_TEST.json"
                            },
                        }
                    ]
                }
            },
            ensure_ascii=False,
        ),
    )
    write(root / "_phase4_proofread/NEXT_TASK_PACKET.json", "{}")
    write(root / "_phase4_proofread/CURRENT_HANDOFF.md", "# 現在の引継ぎ\n")
    return root, candidate_path


def main() -> None:
    root, candidate_path = fixture()
    result = context.inject(candidate_path, root)
    assert result["source_document_target_count"] == 2
    assert result["unresolved_speakers"] == ["未登録"]
    candidate = context.load_object(candidate_path)
    assert candidate["schema_version"] == 3
    audit_context = candidate["quality_audit_context"]
    assert audit_context["manifest_digest"].startswith("sha256:")
    targets = {item["path"] for item in audit_context["source_document_targets"]}
    assert targets == {"10_人物/宇文逸.md", "10_人物/莫問.md"}
    required = {item["path"] for item in audit_context["required_documents"]}
    assert "10_人物/宇文逸.md" in required
    assert "10_人物/莫問.md" in required
    assert "source_document_decision" in candidate["forbidden_outputs"]
    state = context.load_object(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json")
    assert state["wave"]["packets"][0]["source_document_target_count"] == 2
    packet = context.load_object(root / "_phase4_proofread/NEXT_TASK_PACKET.json")
    assert packet["quality_audit_source_feedback"]["candidate_schema"] == 3

    root, candidate_path = fixture()
    contract_path = root / context.CONTRACT_REL
    contract = context.load_object(contract_path)
    missing = root / contract["required_documents"][0]
    missing.unlink()
    try:
        context.inject(candidate_path, root)
    except context.ContextError as exc:
        assert "required quality-audit document is missing" in str(exc)
    else:
        raise AssertionError("missing required document must block")

    root, candidate_path = fixture()
    duplicate = root / "10_人物/重複.md"
    write(
        duplicate,
        "---\nname: 重複\naliases: [宇文逸]\n---\n\n# 重複\n",
    )
    try:
        context.inject(candidate_path, root)
    except context.ContextError as exc:
        assert "multiple documents" in str(exc)
    else:
        raise AssertionError("duplicate persona alias must block")

    print("test_quality_audit_context: OK")


if __name__ == "__main__":
    main()
