#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import source_document_feedback as feedback


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture() -> tuple[Path, dict, dict]:
    root = Path(tempfile.mkdtemp())
    contract = {
        "schema_version": 1,
        "contract_id": "quality-audit-source-feedback-v1",
        "candidate_schema_version": 3,
        "audit_decision_schema_version": 2,
        "reading_order": [
            "primary_evidence",
            "independent_allusion_and_fact_gates",
            "source_document_crosscheck",
        ],
        "required_documents": ["10_人物/宇文逸.md"],
        "persona_document_root": "10_人物",
        "source_document_types": ["persona"],
        "decision_values": ["keep", "revise", "create", "unresolved"],
        "required_attestation_fields": [],
        "required_source_decision_fields": [],
        "auto_apply": {
            "allowed_document_types": ["persona"],
            "allowed_roots": ["10_人物"],
            "required_confidence": "high",
            "revise_operation": "replace_exact",
            "create_operation": "append_under_heading",
            "unresolved_is_non_applying": True,
            "fail_closed_on_stale_digest": True,
            "fail_closed_on_ambiguous_anchor": True,
        },
    }
    contract_path = root / "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"
    write(contract_path, json.dumps(contract, ensure_ascii=False))
    persona_path = root / "10_人物/宇文逸.md"
    write(persona_path, "---\nname: 宇文逸\n---\n\n## 声\n\n旧主張\n")
    required = [
        {
            "path": "10_人物/宇文逸.md",
            "digest": feedback.digest_path(persona_path),
            "role": "current_pair_persona",
        }
    ]
    context = {
        "contract_id": contract["contract_id"],
        "contract_path": "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json",
        "reading_order": contract["reading_order"],
        "primary_evidence": {
            "candidate_rows": True,
            "scene_context": True,
            "source_artifact": True,
        },
        "required_documents": required,
        "source_document_targets": [
            {
                "path": "10_人物/宇文逸.md",
                "digest": feedback.digest_path(persona_path),
                "document_type": "persona",
                "name": "宇文逸",
                "aliases": ["宇文逸"],
                "evidence_keys": ["k1"],
            }
        ],
        "unresolved_speakers": [],
        "source_feedback_required": True,
    }
    context["manifest_digest"] = feedback.canonical_digest(context)
    candidate = {
        "schema_version": 3,
        "scene_groups": ["demo"],
        "rows": [{"key": "k1", "speaker": "宇文逸", "zh": "zh", "ja": "ja"}],
        "quality_audit_context": context,
    }
    decision = {
        "status": "audited",
        "scene_groups": ["demo"],
        "reading_attestation": {
            "contract_id": contract["contract_id"],
            "manifest_digest": context["manifest_digest"],
            "primary_evidence_reviewed": True,
            "doubt_gates_completed_before_reference_crosscheck": True,
            "documents": [
                {
                    "path": "10_人物/宇文逸.md",
                    "digest": feedback.digest_path(persona_path),
                    "status": "reviewed",
                }
            ],
        },
        "source_document_decisions": [
            {
                "target": "10_人物/宇文逸.md",
                "document_type": "persona",
                "decision": "revise",
                "evidence_keys": ["k1"],
                "reason": "一次資料の反例",
                "scope": {"speaker": "宇文逸", "timeline": "demo"},
                "confidence": "high",
                "operation": "replace_exact",
                "current_claim": "旧主張",
                "replacement_claim": "新主張",
            }
        ],
    }
    write(
        root / "_phase4_proofread/CANDIDATE_TEST.json",
        json.dumps(candidate, ensure_ascii=False),
    )
    write(
        root / "_phase4_proofread/PRIVATE_STAGE_STATE.json",
        json.dumps({"wave": {"packets": [{"packet_id": "p1"}]}}, ensure_ascii=False),
    )
    write(root / "_phase4_proofread/NEXT_TASK_PACKET.json", "{}")
    return root, candidate, decision


def expect_failure(root: Path, candidate: dict, decision: dict, marker: str) -> None:
    try:
        feedback.validate_decision(decision, candidate, root)
    except feedback.SourceFeedbackError as exc:
        assert marker in str(exc), str(exc)
    else:
        raise AssertionError(f"expected failure: {marker}")


def main() -> None:
    root, candidate, decision = fixture()
    result = feedback.validate_decision(decision, candidate, root)
    assert result["mutating_decision_count"] == 1
    record = feedback.apply_plans(result["plans"], root)
    assert (root / "10_人物/宇文逸.md").read_text(encoding="utf-8").count("新主張") == 1
    assert record["changed_documents"] == ["10_人物/宇文逸.md"]
    assert feedback.verify_record(record, root) == []

    root, candidate, decision = fixture()
    decision = copy.deepcopy(decision)
    decision["candidate"] = "_phase4_proofread/CANDIDATE_TEST.json"
    audit = {
        "schema_version": 2,
        "train_id": "yuwen-mowen-train-40",
        "wave_id": "yuwen-mowen-train-40-wave-01",
        "stage": "private_quality_audit",
        "status": "complete",
        "decisions": [decision],
    }
    audit_path = root / "_phase4_proofread/AUDIT_DECISIONS_YUWEN_MOWEN_TRAIN40_WAVE01_2026-07-30.json"
    write(audit_path, json.dumps(audit, ensure_ascii=False))
    applied = feedback.apply_audit(audit_path, root=root)
    record_path = feedback.feedback_record_path(audit_path, root)
    assert record_path.is_file()
    assert applied["changed_documents"] == ["10_人物/宇文逸.md"]
    state = feedback.load_object(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json")
    assert state["wave"]["packets"][0]["source_document_feedback_record"]["status"] == "complete"
    packet = feedback.load_object(root / "_phase4_proofread/NEXT_TASK_PACKET.json")
    assert packet["source_document_feedback"]["status"] == "complete"

    root, candidate, decision = fixture()
    broken = copy.deepcopy(decision)
    broken.pop("reading_attestation")
    expect_failure(root, candidate, broken, "reading_attestation")

    root, candidate, decision = fixture()
    broken = copy.deepcopy(decision)
    broken["reading_attestation"]["manifest_digest"] = "sha256:bad"
    expect_failure(root, candidate, broken, "manifest digest")

    root, candidate, decision = fixture()
    broken = copy.deepcopy(decision)
    broken["source_document_decisions"][0]["evidence_keys"] = ["outside"]
    expect_failure(root, candidate, broken, "outside candidate target scope")

    root, candidate, decision = fixture()
    broken = copy.deepcopy(decision)
    broken["source_document_decisions"][0]["confidence"] = "medium"
    expect_failure(root, candidate, broken, "high confidence")

    root, candidate, decision = fixture()
    broken = copy.deepcopy(decision)
    broken["source_document_decisions"] = []
    expect_failure(root, candidate, broken, "coverage mismatch")

    root, candidate, decision = fixture()
    keep = copy.deepcopy(decision)
    keep["source_document_decisions"][0] = {
        "target": "10_人物/宇文逸.md",
        "document_type": "persona",
        "decision": "keep",
        "evidence_keys": ["k1"],
        "reason": "一次資料と整合",
        "scope": {"speaker": "宇文逸", "timeline": "demo"},
        "confidence": "high",
    }
    result = feedback.validate_decision(keep, candidate, root)
    record = feedback.apply_plans(result["plans"], root)
    assert record["changed_documents"] == []

    root, candidate, decision = fixture()
    create = copy.deepcopy(decision)
    create["source_document_decisions"][0] = {
        "target": "10_人物/宇文逸.md",
        "document_type": "persona",
        "decision": "create",
        "evidence_keys": ["k1"],
        "reason": "相手別モードが未収録",
        "scope": {"speaker": "宇文逸", "timeline": "demo"},
        "confidence": "high",
        "operation": "append_under_heading",
        "anchor_heading": "## 声",
        "replacement_claim": "- demoでは短く応じる。",
    }
    result = feedback.validate_decision(create, candidate, root)
    feedback.apply_plans(result["plans"], root)
    assert "- demoでは短く応じる。" in (root / "10_人物/宇文逸.md").read_text(encoding="utf-8")

    print("test_source_document_feedback: OK")


if __name__ == "__main__":
    main()
