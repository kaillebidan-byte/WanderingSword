#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factory生成candidateへdigest付き読書manifestと人物資料targetを決定的に付与する。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import source_document_feedback as feedback

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CONTRACT_REL = "_phase4_proofread/QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json"
PAIR = "宇文逸↔莫問"


class ContextError(ValueError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContextError(f"top level must be object: {path}")
    return value


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_json(path: Path, value: dict[str, Any]) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest_path(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _frontmatter(path: Path) -> tuple[str | None, list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, []
    name: str | None = None
    aliases: list[str] = []
    for line in lines[1:80]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("name:"):
            value = stripped.split(":", 1)[1].strip().strip("'\"")
            name = value or None
        elif stripped.startswith("aliases:"):
            raw = stripped.split(":", 1)[1].strip()
            if raw.startswith("[") and raw.endswith("]"):
                aliases = [
                    item.strip().strip("'\"")
                    for item in raw[1:-1].split(",")
                    if item.strip().strip("'\"")
                ]
    return name, aliases


def persona_index(root: Path) -> dict[str, dict[str, Any]]:
    directory = root / "10_人物"
    if not directory.is_dir():
        raise ContextError("persona document root is missing: 10_人物")
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.glob("*.md")):
        name, aliases = _frontmatter(path)
        if not name:
            continue
        relative = path.relative_to(root).as_posix()
        record = {
            "path": relative,
            "digest": digest_path(path),
            "document_type": "persona",
            "name": name,
            "aliases": list(dict.fromkeys([name, *aliases])),
        }
        for alias in record["aliases"]:
            existing = result.get(alias)
            if existing is not None and existing["path"] != relative:
                raise ContextError(f"persona alias resolves to multiple documents: {alias}")
            result[alias] = record
    return result


def build_context(candidate: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    contract = load_object(root / CONTRACT_REL)
    contract_errors = feedback.validate_contract(contract)
    if contract_errors:
        raise ContextError("source feedback contract invalid: " + "; ".join(contract_errors))
    rows = candidate.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ContextError("candidate.rows must be a non-empty list")

    documents: dict[str, dict[str, Any]] = {}
    for relative in contract.get("required_documents", []):
        if not isinstance(relative, str) or not relative:
            raise ContextError("contract required document path is invalid")
        path = root / relative
        if not path.is_file():
            raise ContextError(f"required quality-audit document is missing: {relative}")
        documents[relative] = {
            "path": relative,
            "digest": digest_path(path),
            "role": "translation_quality_rule",
        }

    index = persona_index(root)
    pair = candidate.get("current_pair", PAIR)
    if not isinstance(pair, str) or "↔" not in pair:
        raise ContextError("candidate current_pair is invalid")
    for name in pair.split("↔"):
        record = index.get(name)
        if record is None:
            raise ContextError(f"current pair persona is unresolved: {name}")
        documents[record["path"]] = {
            "path": record["path"],
            "digest": record["digest"],
            "role": "current_pair_persona",
        }

    targets: dict[str, dict[str, Any]] = {}
    unresolved: list[str] = []
    seen_keys: set[str] = set()
    for row_index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ContextError(f"candidate.rows[{row_index}] must be an object")
        key = row.get("key")
        if not isinstance(key, str) or not key or key in seen_keys:
            raise ContextError(f"candidate.rows[{row_index}].key is invalid or duplicate")
        seen_keys.add(key)
        speaker = str(row.get("speaker") or "").strip()
        if not speaker:
            continue
        record = index.get(speaker)
        if record is None:
            if speaker not in unresolved:
                unresolved.append(speaker)
            continue
        documents[record["path"]] = {
            "path": record["path"],
            "digest": record["digest"],
            "role": "speaker_persona",
        }
        target = targets.setdefault(
            record["path"],
            {
                "path": record["path"],
                "digest": record["digest"],
                "document_type": "persona",
                "name": record["name"],
                "aliases": record["aliases"],
                "evidence_keys": [],
            },
        )
        target["evidence_keys"].append(key)

    context: dict[str, Any] = {
        "contract_id": contract["contract_id"],
        "contract_path": CONTRACT_REL,
        "reading_order": list(contract["reading_order"]),
        "primary_evidence": {
            "candidate_rows": True,
            "scene_context": True,
            "source_artifact": True,
        },
        "required_documents": list(documents.values()),
        "source_document_targets": list(targets.values()),
        "unresolved_speakers": unresolved,
        "source_feedback_required": True,
    }
    context["manifest_digest"] = canonical_digest(context)
    return context


def inject(candidate_path: Path, root: Path = ROOT) -> dict[str, Any]:
    candidate = load_object(candidate_path)
    if candidate.get("schema_version") not in {2, 3}:
        raise ContextError("candidate schema must be 2 or 3 before context injection")
    context = build_context(candidate, root)
    candidate["schema_version"] = 3
    candidate["quality_audit_context"] = context
    forbidden = candidate.get("forbidden_outputs")
    if isinstance(forbidden, list):
        for marker in ("source_document_decision", "source_document_write"):
            if marker not in forbidden:
                forbidden.append(marker)
    write_json(candidate_path, candidate)

    current = load_object(root / "_phase4_proofread/CURRENT_WORK.json")
    current.setdefault("immediate_next", {})["source_feedback_contract"] = CONTRACT_REL
    current["immediate_next"]["quality_audit_context_digest"] = context["manifest_digest"]
    write_json(root / "_phase4_proofread/CURRENT_WORK.json", current)

    state = load_object(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json")
    packets = state.get("wave", {}).get("packets", [])
    if not isinstance(packets, list) or len(packets) != 1:
        raise ContextError("context injection requires one prepared packet")
    packets[0].setdefault("preparation_record", {})["quality_audit_context_digest"] = context["manifest_digest"]
    packets[0]["source_document_target_count"] = len(context["source_document_targets"])
    write_json(root / "_phase4_proofread/PRIVATE_STAGE_STATE.json", state)

    packet = load_object(root / "_phase4_proofread/NEXT_TASK_PACKET.json")
    packet["quality_audit_source_feedback"] = {
        "contract": CONTRACT_REL,
        "candidate_schema": 3,
        "audit_decision_schema": 2,
        "manifest_digest": context["manifest_digest"],
    }
    write_json(root / "_phase4_proofread/NEXT_TASK_PACKET.json", packet)

    handoff_path = root / "_phase4_proofread/CURRENT_HANDOFF.md"
    handoff = handoff_path.read_text(encoding="utf-8")
    addition = (
        "\n## quality audit資料還流\n\n"
        "candidateの一次資料だけで典故・事実疑義を先に立て、その後に"
        "`quality_audit_context.required_documents`を照合する。全人物資料targetへ"
        "`keep/revise/create/unresolved`を記録し、人物資料を直接編集しない。\n"
    )
    if "## quality audit資料還流" not in handoff:
        write_text(handoff_path, handoff.rstrip() + "\n" + addition)

    return {
        "candidate": candidate_path.relative_to(root).as_posix(),
        "manifest_digest": context["manifest_digest"],
        "required_document_count": len(context["required_documents"]),
        "source_document_target_count": len(context["source_document_targets"]),
        "unresolved_speakers": context["unresolved_speakers"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--execution-result", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        candidate = args.candidate
        if candidate is None:
            if args.execution_result is None:
                raise ContextError("--candidate or --execution-result is required")
            result = load_object(args.execution_result)
            candidate_value = result.get("candidate_path")
            if not isinstance(candidate_value, str) or not candidate_value:
                raise ContextError("execution result lacks candidate_path")
            candidate = Path(candidate_value)
        candidate_path = candidate if candidate.is_absolute() else ROOT / candidate
        if not args.write:
            value = build_context(load_object(candidate_path))
            summary = {"status": "valid", "manifest_digest": value["manifest_digest"]}
        else:
            summary = {"status": "written", **inject(candidate_path)}
    except (OSError, json.JSONDecodeError, ContextError) as exc:
        print(json.dumps({"status": "blocked", "error_code": "quality_audit_context_invalid", "detail": str(exc)}, ensure_ascii=False))
        return 1
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        write_text(args.output, text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
