#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quality-auditの読書証跡とペルソナ修正判断を検査し、記録済み変更だけを決定的に適用する。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "_phase4_proofread" / "QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"


class SourceFeedbackError(ValueError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceFeedbackError(f"top level must be object: {path}")
    return value


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def _non_empty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourceFeedbackError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise SourceFeedbackError(f"{label} must be a list")
    if not allow_empty and not value:
        raise SourceFeedbackError(f"{label} must not be empty")
    if any(not isinstance(item, str) or not item for item in value):
        raise SourceFeedbackError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise SourceFeedbackError(f"{label} contains duplicates")
    return list(value)


def _safe_target(root: Path, relative: str, allowed_roots: list[str]) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise SourceFeedbackError(f"unsafe source document path: {relative}")
    if not any(rel.parts and rel.parts[0] == allowed for allowed in allowed_roots):
        raise SourceFeedbackError(f"source document path is outside allowed roots: {relative}")
    target = root / rel
    if not target.is_file():
        raise SourceFeedbackError(f"missing source document: {relative}")
    return target


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("source feedback schema_version must be 1")
    if contract.get("contract_id") != "quality-audit-source-feedback-v1":
        errors.append("source feedback contract_id mismatch")
    if contract.get("candidate_schema_version") != 3:
        errors.append("candidate_schema_version must be 3")
    if contract.get("audit_decision_schema_version") != 2:
        errors.append("audit_decision_schema_version must be 2")
    reading_order = contract.get("reading_order")
    if reading_order != [
        "primary_evidence",
        "independent_allusion_and_fact_gates",
        "source_document_crosscheck",
    ]:
        errors.append("reading_order mismatch")
    required_documents = contract.get("required_documents")
    if (
        not isinstance(required_documents, list)
        or not required_documents
        or any(not isinstance(item, str) or not item for item in required_documents)
        or len(required_documents) != len(set(required_documents))
    ):
        errors.append("required_documents must be a unique non-empty string list")
    if contract.get("source_document_types") != ["persona"]:
        errors.append("source_document_types must contain only persona")
    decisions = set(contract.get("decision_values", []))
    if decisions != {"keep", "revise", "create", "unresolved"}:
        errors.append("decision_values mismatch")
    auto_apply = contract.get("auto_apply")
    if not isinstance(auto_apply, dict):
        errors.append("auto_apply must be an object")
    else:
        if auto_apply.get("allowed_document_types") != ["persona"]:
            errors.append("auto_apply.allowed_document_types must contain only persona")
        if auto_apply.get("allowed_roots") != ["10_人物"]:
            errors.append("auto_apply.allowed_roots must contain only 10_人物")
        if auto_apply.get("required_confidence") != "high":
            errors.append("auto_apply.required_confidence must be high")
        for key in (
            "unresolved_is_non_applying",
            "fail_closed_on_stale_digest",
            "fail_closed_on_ambiguous_anchor",
        ):
            if auto_apply.get(key) is not True:
                errors.append(f"auto_apply.{key} must be true")
    return errors


def validate_reading_attestation(
    decision: dict[str, Any],
    candidate: dict[str, Any],
    root: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    context = candidate.get("quality_audit_context")
    if candidate.get("schema_version") != contract["candidate_schema_version"] or not isinstance(context, dict):
        raise SourceFeedbackError("candidate lacks quality_audit_context schema 3")
    if context.get("contract_id") != contract["contract_id"]:
        raise SourceFeedbackError("candidate source feedback contract mismatch")

    stored_digest = context.get("manifest_digest")
    unsigned_context = dict(context)
    unsigned_context.pop("manifest_digest", None)
    calculated = canonical_digest(unsigned_context)
    if stored_digest != calculated:
        raise SourceFeedbackError("candidate quality_audit_context digest mismatch")

    attestation = decision.get("reading_attestation")
    if not isinstance(attestation, dict):
        raise SourceFeedbackError("reading_attestation is required")
    if attestation.get("contract_id") != contract["contract_id"]:
        raise SourceFeedbackError("reading_attestation contract mismatch")
    if attestation.get("manifest_digest") != stored_digest:
        raise SourceFeedbackError("reading_attestation manifest digest mismatch")
    if attestation.get("primary_evidence_reviewed") is not True:
        raise SourceFeedbackError("primary evidence review must be attested")
    if attestation.get("doubt_gates_completed_before_reference_crosscheck") is not True:
        raise SourceFeedbackError("independent doubt gates must precede source document crosscheck")

    required_documents = context.get("required_documents")
    if not isinstance(required_documents, list) or not required_documents:
        raise SourceFeedbackError("candidate required_documents must be non-empty")
    required: dict[str, str] = {}
    for index, item in enumerate(required_documents):
        if not isinstance(item, dict):
            raise SourceFeedbackError(f"required_documents[{index}] must be an object")
        path = _non_empty_text(item.get("path"), f"required_documents[{index}].path")
        digest = _non_empty_text(item.get("digest"), f"required_documents[{index}].digest")
        if path in required:
            raise SourceFeedbackError(f"duplicate required document: {path}")
        target = root / path
        if not target.is_file():
            raise SourceFeedbackError(f"required document is missing: {path}")
        if digest_path(target) != digest:
            raise SourceFeedbackError(f"required document digest is stale: {path}")
        required[path] = digest

    contract_required = set(contract.get("required_documents", []))
    manifest_paths = set(required)
    missing_contract_documents = sorted(contract_required - manifest_paths)
    if missing_contract_documents:
        raise SourceFeedbackError(
            "candidate reading manifest lacks contract-required documents: "
            + ", ".join(missing_contract_documents)
        )

    reviewed_items = attestation.get("documents")
    if not isinstance(reviewed_items, list):
        raise SourceFeedbackError("reading_attestation.documents must be a list")
    reviewed: dict[str, str] = {}
    for index, item in enumerate(reviewed_items):
        if not isinstance(item, dict):
            raise SourceFeedbackError(f"reading_attestation.documents[{index}] must be an object")
        path = _non_empty_text(item.get("path"), f"reading_attestation.documents[{index}].path")
        digest = _non_empty_text(item.get("digest"), f"reading_attestation.documents[{index}].digest")
        if item.get("status") != "reviewed":
            raise SourceFeedbackError(f"reading status must be reviewed: {path}")
        if path in reviewed:
            raise SourceFeedbackError(f"duplicate reading attestation: {path}")
        reviewed[path] = digest
    if reviewed != required:
        missing = sorted(set(required) - set(reviewed))
        extra = sorted(set(reviewed) - set(required))
        mismatched = sorted(path for path in required.keys() & reviewed.keys() if required[path] != reviewed[path])
        raise SourceFeedbackError(
            f"reading attestation does not match manifest: missing={missing} extra={extra} digest_mismatch={mismatched}"
        )
    return {
        "manifest_digest": stored_digest,
        "documents": [{"path": path, "digest": digest} for path, digest in sorted(required.items())],
    }


def validate_source_document_decisions(
    decision: dict[str, Any],
    candidate: dict[str, Any],
    root: Path,
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    context = candidate["quality_audit_context"]
    targets = context.get("source_document_targets")
    if not isinstance(targets, list):
        raise SourceFeedbackError("source_document_targets must be a list")
    target_by_path: dict[str, dict[str, Any]] = {}
    for index, target in enumerate(targets):
        if not isinstance(target, dict):
            raise SourceFeedbackError(f"source_document_targets[{index}] must be an object")
        path = _non_empty_text(target.get("path"), f"source_document_targets[{index}].path")
        if path in target_by_path:
            raise SourceFeedbackError(f"duplicate source document target: {path}")
        target_by_path[path] = target

    raw_decisions = decision.get("source_document_decisions")
    if not isinstance(raw_decisions, list):
        raise SourceFeedbackError("source_document_decisions must be a list")
    decision_by_path: dict[str, dict[str, Any]] = {}
    candidate_keys = {
        row.get("key")
        for row in candidate.get("rows", [])
        if isinstance(row, dict) and isinstance(row.get("key"), str)
    }
    allowed_values = set(contract["decision_values"])
    auto_apply = contract["auto_apply"]
    plans: list[dict[str, Any]] = []

    for index, item in enumerate(raw_decisions):
        if not isinstance(item, dict):
            raise SourceFeedbackError(f"source_document_decisions[{index}] must be an object")
        path = _non_empty_text(item.get("target"), f"source_document_decisions[{index}].target")
        if path in decision_by_path:
            raise SourceFeedbackError(f"duplicate source document decision: {path}")
        decision_by_path[path] = item
        target = target_by_path.get(path)
        if target is None:
            raise SourceFeedbackError(f"source document decision targets an undeclared document: {path}")
        document_type = item.get("document_type")
        if document_type != target.get("document_type") or document_type not in contract["source_document_types"]:
            raise SourceFeedbackError(f"source document type mismatch: {path}")
        value = item.get("decision")
        if value not in allowed_values:
            raise SourceFeedbackError(f"invalid source document decision for {path}: {value!r}")
        evidence_keys = _string_list(item.get("evidence_keys"), f"{path}.evidence_keys")
        declared_keys = set(target.get("evidence_keys", []))
        if not set(evidence_keys) <= declared_keys or not set(evidence_keys) <= candidate_keys:
            raise SourceFeedbackError(f"source document evidence is outside candidate target scope: {path}")
        reason = _non_empty_text(item.get("reason"), f"{path}.reason")
        scope = item.get("scope")
        if not isinstance(scope, dict) or not scope:
            raise SourceFeedbackError(f"{path}.scope must be a non-empty object")
        confidence = item.get("confidence")
        if confidence not in {"high", "medium", "low"}:
            raise SourceFeedbackError(f"{path}.confidence is invalid")

        expected_digest = _non_empty_text(target.get("digest"), f"{path}.target_digest")
        target_file = _safe_target(root, path, auto_apply["allowed_roots"])
        if digest_path(target_file) != expected_digest:
            raise SourceFeedbackError(f"source document changed after candidate generation: {path}")

        plan: dict[str, Any] = {
            "target": path,
            "document_type": document_type,
            "decision": value,
            "evidence_keys": evidence_keys,
            "reason": reason,
            "scope": scope,
            "confidence": confidence,
            "before_digest": expected_digest,
            "operation": None,
        }
        if value == "revise":
            if confidence != auto_apply["required_confidence"]:
                raise SourceFeedbackError(f"revise requires high confidence: {path}")
            if item.get("operation") != auto_apply["revise_operation"]:
                raise SourceFeedbackError(f"revise operation must be replace_exact: {path}")
            current_claim = _non_empty_text(item.get("current_claim"), f"{path}.current_claim")
            replacement_claim = _non_empty_text(item.get("replacement_claim"), f"{path}.replacement_claim")
            if current_claim == replacement_claim:
                raise SourceFeedbackError(f"replacement must differ from current claim: {path}")
            text = target_file.read_text(encoding="utf-8")
            if text.count(current_claim) != 1:
                raise SourceFeedbackError(f"current_claim must match exactly once: {path}")
            plan.update(
                {
                    "operation": "replace_exact",
                    "current_claim": current_claim,
                    "replacement_claim": replacement_claim,
                }
            )
        elif value == "create":
            if confidence != auto_apply["required_confidence"]:
                raise SourceFeedbackError(f"create requires high confidence: {path}")
            if item.get("operation") != auto_apply["create_operation"]:
                raise SourceFeedbackError(f"create operation must be append_under_heading: {path}")
            heading = _non_empty_text(item.get("anchor_heading"), f"{path}.anchor_heading")
            replacement_claim = _non_empty_text(item.get("replacement_claim"), f"{path}.replacement_claim")
            lines = target_file.read_text(encoding="utf-8").splitlines()
            if sum(line == heading for line in lines) != 1:
                raise SourceFeedbackError(f"anchor_heading must match exactly once: {path}")
            plan.update(
                {
                    "operation": "append_under_heading",
                    "anchor_heading": heading,
                    "replacement_claim": replacement_claim,
                }
            )
        elif value == "unresolved":
            if item.get("operation") not in (None, "none"):
                raise SourceFeedbackError(f"unresolved decision must not apply a mutation: {path}")
        elif value == "keep":
            if item.get("operation") not in (None, "none"):
                raise SourceFeedbackError(f"keep decision must not apply a mutation: {path}")
        plans.append(plan)

    if set(decision_by_path) != set(target_by_path):
        missing = sorted(set(target_by_path) - set(decision_by_path))
        extra = sorted(set(decision_by_path) - set(target_by_path))
        raise SourceFeedbackError(f"source document target coverage mismatch: missing={missing} extra={extra}")
    return plans


def validate_audit(
    audit: dict[str, Any],
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    contract = load_object(root / "_phase4_proofread" / "QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json")
    errors = validate_contract(contract)
    if errors:
        raise SourceFeedbackError("; ".join(errors))
    if audit.get("schema_version") != contract["audit_decision_schema_version"]:
        raise SourceFeedbackError("audit decision schema must be 2")
    if audit.get("status") != "complete" or audit.get("stage") != "private_quality_audit":
        raise SourceFeedbackError("audit must be complete private_quality_audit")
    decisions = audit.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise SourceFeedbackError("audit decisions must be a non-empty list")
    results: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise SourceFeedbackError(f"decisions[{index}] must be an object")
        candidate_value = decision.get("candidate")
        if not isinstance(candidate_value, str) or not candidate_value:
            raise SourceFeedbackError(f"decisions[{index}].candidate is missing")
        candidate_path = root / candidate_value
        candidate = load_object(candidate_path)
        results.append(
            {
                "candidate": candidate_value,
                **validate_decision(decision, candidate, root, contract),
            }
        )
    return results


def validate_decision(
    decision: dict[str, Any],
    candidate: dict[str, Any],
    root: Path = ROOT,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_object(root / "_phase4_proofread" / "QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json")
    errors = validate_contract(contract)
    if errors:
        raise SourceFeedbackError("; ".join(errors))
    reading = validate_reading_attestation(decision, candidate, root, contract)
    plans = validate_source_document_decisions(decision, candidate, root, contract)
    return {
        "reading_attestation": reading,
        "plans": plans,
        "source_document_decision_count": len(plans),
        "mutating_decision_count": sum(plan["operation"] is not None for plan in plans),
    }


def _updated_text(original: str, plan: dict[str, Any]) -> str:
    operation = plan.get("operation")
    if operation is None:
        return original
    if operation == "replace_exact":
        current = plan["current_claim"]
        if original.count(current) != 1:
            raise SourceFeedbackError(f"current_claim became ambiguous before apply: {plan['target']}")
        return original.replace(current, plan["replacement_claim"], 1)
    if operation == "append_under_heading":
        heading = plan["anchor_heading"]
        lines = original.splitlines()
        positions = [index for index, line in enumerate(lines) if line == heading]
        if len(positions) != 1:
            raise SourceFeedbackError(f"anchor_heading became ambiguous before apply: {plan['target']}")
        insertion = plan["replacement_claim"].splitlines()
        position = positions[0] + 1
        lines[position:position] = ["", *insertion]
        suffix = "\n" if original.endswith("\n") else ""
        return "\n".join(lines) + suffix
    raise SourceFeedbackError(f"unknown source document operation: {operation}")


def apply_plans(plans: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    mutating_by_target: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for plan in plans:
        target = plan["target"]
        if plan.get("operation") is not None:
            if target in mutating_by_target:
                raise SourceFeedbackError(f"multiple mutations target the same source document: {target}")
            mutating_by_target[target] = plan

    staged: dict[Path, tuple[bytes, bytes]] = {}
    for target, plan in mutating_by_target.items():
        path = root / target
        before = path.read_bytes()
        if sha256_bytes(before) != plan["before_digest"]:
            raise SourceFeedbackError(f"source document digest changed before apply: {target}")
        try:
            original = before.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SourceFeedbackError(f"source document is not strict UTF-8: {target}: {exc}") from exc
        after_text = _updated_text(original, plan)
        after = after_text.encode("utf-8")
        staged[path] = (before, after)

    temp_paths: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, (_, after) in staged.items():
            fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
            temp = Path(temp_name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(after)
            temp_paths[path] = temp
        for path, temp in temp_paths.items():
            os.replace(temp, path)
            replaced.append(path)
    except BaseException:
        for path in replaced:
            before = staged[path][0]
            fd, temp_name = tempfile.mkstemp(prefix=path.name + ".rollback.", dir=path.parent)
            with os.fdopen(fd, "wb") as handle:
                handle.write(before)
            os.replace(temp_name, path)
        for temp in temp_paths.values():
            try:
                temp.unlink()
            except FileNotFoundError:
                pass
        raise

    for plan in plans:
        target = plan["target"]
        path = root / target
        records.append(
            {
                "target": target,
                "document_type": plan["document_type"],
                "decision": plan["decision"],
                "operation": plan.get("operation"),
                "evidence_keys": plan["evidence_keys"],
                "reason": plan["reason"],
                "scope": plan["scope"],
                "confidence": plan["confidence"],
                "before_digest": plan["before_digest"],
                "after_digest": digest_path(path),
                "changed": plan.get("operation") is not None,
            }
        )
    return {
        "schema_version": 1,
        "contract_id": "quality-audit-source-feedback-v1",
        "status": "applied",
        "decisions": records,
        "changed_documents": sorted(record["target"] for record in records if record["changed"]),
        "unresolved_documents": sorted(
            record["target"] for record in records if record["decision"] == "unresolved"
        ),
    }


def verify_record(record: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != 1 or record.get("contract_id") != "quality-audit-source-feedback-v1":
        errors.append("source feedback record identity mismatch")
    decisions = record.get("decisions")
    if not isinstance(decisions, list):
        return [*errors, "source feedback record decisions must be a list"]
    for index, item in enumerate(decisions):
        if not isinstance(item, dict):
            errors.append(f"decisions[{index}] must be an object")
            continue
        target = item.get("target")
        after = item.get("after_digest")
        if not isinstance(target, str) or not isinstance(after, str):
            errors.append(f"decisions[{index}] target/digest invalid")
            continue
        path = root / target
        if not path.is_file():
            errors.append(f"record target missing: {target}")
        elif digest_path(path) != after:
            errors.append(f"record after_digest mismatch: {target}")
    return errors


def feedback_record_path(audit_path: Path, root: Path = ROOT) -> Path:
    name = audit_path.name.replace("AUDIT_DECISIONS_", "SOURCE_DOCUMENT_FEEDBACK_")
    return root / "_phase4_proofread" / name


def apply_audit(
    audit_path: Path,
    *,
    root: Path = ROOT,
    record_path: Path | None = None,
) -> dict[str, Any]:
    audit = load_object(audit_path)
    results = validate_audit(audit, root)
    plans = [plan for result in results for plan in result["plans"]]
    record = apply_plans(plans, root)
    record.update(
        {
            "train_id": audit.get("train_id"),
            "wave_id": audit.get("wave_id"),
            "audit": audit_path.relative_to(root).as_posix(),
            "candidate_manifests": [
                {
                    "candidate": result["candidate"],
                    "manifest_digest": result["reading_attestation"]["manifest_digest"],
                }
                for result in results
            ],
        }
    )
    target_record = record_path or feedback_record_path(audit_path, root)
    write_path = target_record if target_record.is_absolute() else root / target_record
    write_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=write_path.name + ".", dir=write_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        os.replace(temporary, write_path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise

    relative_record = write_path.relative_to(root).as_posix()
    state_path = root / "_phase4_proofread/PRIVATE_STAGE_STATE.json"
    state = load_object(state_path)
    packets = state.get("wave", {}).get("packets", [])
    if not isinstance(packets, list) or len(packets) != len(results):
        raise SourceFeedbackError("source feedback packet alignment mismatch")
    for packet in packets:
        if not isinstance(packet, dict):
            raise SourceFeedbackError("source feedback packet must be an object")
        packet["source_document_feedback_record"] = {
            "status": "complete",
            "record": relative_record,
        }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    packet_path = root / "_phase4_proofread/NEXT_TASK_PACKET.json"
    packet = load_object(packet_path)
    packet["source_document_feedback"] = {
        "status": "complete",
        "record": relative_record,
        "changed_documents": record["changed_documents"],
        "unresolved_documents": record["unresolved_documents"],
    }
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--record", type=Path)
    parser.add_argument("--verify-record", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    try:
        if args.verify_record:
            if args.record is None:
                raise SourceFeedbackError("--record is required with --verify-record")
            record_path = args.record if args.record.is_absolute() else ROOT / args.record
            errors = verify_record(load_object(record_path))
            if errors:
                raise SourceFeedbackError("; ".join(errors))
            print("OK: source document feedback record matches current documents")
            return 0
        if args.audit is None:
            raise SourceFeedbackError("--audit is required")
        audit_path = args.audit if args.audit.is_absolute() else ROOT / args.audit
        if args.apply:
            record_path = args.record
            result = apply_audit(audit_path, record_path=record_path)
            output = {
                "status": "applied",
                "record": (record_path if record_path else feedback_record_path(audit_path)).relative_to(ROOT).as_posix()
                if (record_path if record_path else feedback_record_path(audit_path)).is_absolute()
                else str(record_path),
                "changed_documents": result["changed_documents"],
                "unresolved_documents": result["unresolved_documents"],
            }
        elif args.candidate is not None:
            candidate_path = args.candidate if args.candidate.is_absolute() else ROOT / args.candidate
            audit = load_object(audit_path)
            decisions = audit.get("decisions")
            if not isinstance(decisions, list) or len(decisions) != 1:
                raise SourceFeedbackError("candidate-specific validation requires one audit decision")
            output = {
                "status": "valid",
                **validate_decision(decisions[0], load_object(candidate_path)),
            }
        else:
            results = validate_audit(load_object(audit_path))
            output = {
                "status": "valid",
                "decision_count": len(results),
                "source_document_decision_count": sum(result["source_document_decision_count"] for result in results),
                "mutating_decision_count": sum(result["mutating_decision_count"] for result in results),
            }
    except (OSError, json.JSONDecodeError, SourceFeedbackError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "source_feedback_invalid", "detail": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
