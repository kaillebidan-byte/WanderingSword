#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a deterministic, candidate-only bridge between Quest lifecycle rows and QuestDlgs scene families."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "_phase4_proofread" / "source_zh.json"
DEFAULT_OUTPUT = ROOT / "_story_context" / "candidates" / "quest_scene_candidates.json"
CONTRACT_ID = "story-context-preparation-v1"
GENERATOR_VERSION = 1
SEP = "\x1f"

QUEST_RECORD_RE = re.compile(r"^(?P<quest_id>\d+)_(?P<tail>.+)$")
SCENE_RECORD_RE = re.compile(
    r"^(?P<root_id>\d+)(?:_(?P<variant_id>\d+))?_Dlgs_Index(?P<line_index>\d+)_Text$"
)
LIFECYCLE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^RequestDlgs(?P<slot>\d*)_Index(?P<index>\d+)_Text$"), "request"),
    (re.compile(r"^ProcessedDlgs(?P<slot>\d*)_Index(?P<index>\d+)_Text$"), "processed"),
    (re.compile(r"^OptionDlgs(?P<slot>\d+)_Index(?P<index>\d+)_Text$"), "option"),
    (re.compile(r"^OptionText(?P<slot>\d+)$"), "option_label"),
    (re.compile(r"^FinishingDlgs(?P<slot>\d*)_Index(?P<index>\d+)_Text$"), "finishing"),
    (re.compile(r"^Dlgs_Index(?P<index>\d+)_Text$"), "embedded_scene"),
    (re.compile(r"^Name$"), "name"),
)
LIFECYCLE_RANK = {
    "name": 0,
    "request": 10,
    "processed": 20,
    "option_label": 30,
    "option": 40,
    "embedded_scene": 50,
    "finishing": 60,
    "other": 90,
}
MIN_SHARED_TEXT_LENGTH = 6
MAX_FINGERPRINT_FANOUT = 8
MAX_TITLE_SCENE_FANOUT = 12
MAX_SAMPLE_SPEAKERS = 12


class CandidateBuildError(ValueError):
    pass


def load_source(path: Path) -> dict[str, str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CandidateBuildError(f"source index missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CandidateBuildError(f"source index is invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CandidateBuildError("source index must be a JSON object")
    bad = [key for key, row in value.items() if not isinstance(key, str) or not isinstance(row, str)]
    if bad:
        raise CandidateBuildError("source index keys and values must be strings")
    return value


def split_full_key(full_key: str) -> tuple[str, str, str]:
    parts = full_key.split(SEP, 2)
    if len(parts) != 3 or not all(parts):
        raise CandidateBuildError(f"malformed source key: {full_key!r}")
    return parts[0], parts[1], parts[2]


def natural_id(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("_"))


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", "", value).strip()


def dialogue_parts(value: str) -> tuple[str | None, str | None, str]:
    left, marker, body = value.partition("$@$")
    text = body if marker else value
    match = re.match(r"^\s*(?P<speaker_id>\d+)\s*-\s*(?P<speaker>.*?)\s*$", left)
    if not match:
        return None, None, text.strip()
    return match.group("speaker_id"), match.group("speaker").strip(), text.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def row_digest(rows: Iterable[dict[str, Any]]) -> str:
    payload = json.dumps(list(rows), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def classify_lifecycle(tail: str) -> tuple[str, int, int]:
    for pattern, phase in LIFECYCLE_PATTERNS:
        match = pattern.match(tail)
        if not match:
            continue
        slot_text = match.groupdict().get("slot") or "0"
        index_text = match.groupdict().get("index") or "0"
        return phase, int(slot_text), int(index_text)
    return "other", 0, 0


def title_from_rows(rows: list[dict[str, Any]]) -> str | None:
    names = [row["text"] for row in rows if row["phase"] == "name" and row["text"]]
    return names[0] if names else None


def compact_speakers(rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    pairs = {
        (row["speaker_id"], row["speaker"])
        for row in rows
        if row.get("speaker_id") and row.get("speaker")
    }
    return [
        {"speaker_id": speaker_id, "speaker": speaker}
        for speaker_id, speaker in sorted(pairs, key=lambda item: (int(item[0]), item[1]))[:MAX_SAMPLE_SPEAKERS]
    ]


def build_inventory(source: dict[str, str], source_path: str, source_digest: str) -> dict[str, Any]:
    quest_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    scene_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    malformed_namespaces: Counter[str] = Counter()

    for full_key, value in source.items():
        target, namespace, key = split_full_key(full_key)
        speaker_id, speaker, text = dialogue_parts(value)
        normalized = normalize_text(text)

        if namespace == "Quests":
            match = QUEST_RECORD_RE.match(key)
            if not match:
                malformed_namespaces[namespace] += 1
                continue
            quest_id = match.group("quest_id")
            tail = match.group("tail")
            phase, slot, index = classify_lifecycle(tail)
            quest_rows[quest_id].append(
                {
                    "full_key": full_key,
                    "target": target,
                    "key": key,
                    "phase": phase,
                    "slot": slot,
                    "index": index,
                    "speaker_id": speaker_id,
                    "speaker": speaker,
                    "text": text,
                    "normalized_text": normalized,
                }
            )
            continue

        if namespace == "QuestDlgs":
            match = SCENE_RECORD_RE.match(key)
            if not match:
                malformed_namespaces[namespace] += 1
                continue
            root_id = match.group("root_id")
            variant_id = match.group("variant_id")
            family_id = root_id if variant_id is None else f"{root_id}_{variant_id}"
            scene_rows[family_id].append(
                {
                    "full_key": full_key,
                    "target": target,
                    "key": key,
                    "root_id": root_id,
                    "variant_id": variant_id,
                    "line_index": int(match.group("line_index")),
                    "speaker_id": speaker_id,
                    "speaker": speaker,
                    "text": text,
                    "normalized_text": normalized,
                }
            )

    quest_groups: list[dict[str, Any]] = []
    quest_fingerprints: dict[str, set[str]] = defaultdict(set)
    title_to_quest_ids: dict[str, list[str]] = defaultdict(list)

    for quest_id in sorted(quest_rows, key=lambda value: int(value)):
        rows = sorted(
            quest_rows[quest_id],
            key=lambda row: (
                LIFECYCLE_RANK[row["phase"]],
                row["slot"],
                row["index"],
                row["key"],
            ),
        )
        title = title_from_rows(rows)
        if title:
            normalized_title = normalize_text(title)
            if normalized_title:
                title_to_quest_ids[normalized_title].append(quest_id)
        counts = Counter(row["phase"] for row in rows)
        for row in rows:
            if len(row["normalized_text"]) >= MIN_SHARED_TEXT_LENGTH:
                quest_fingerprints[row["normalized_text"]].add(quest_id)
        key_rows = [
            {
                "source_key": row["full_key"],
                "phase": row["phase"],
                "slot": row["slot"],
                "index": row["index"],
            }
            for row in rows
        ]
        quest_groups.append(
            {
                "quest_id": quest_id,
                "title": title,
                "record_count": len(rows),
                "lifecycle_counts": {phase: counts[phase] for phase in LIFECYCLE_RANK if counts[phase]},
                "first_source_key": rows[0]["full_key"],
                "last_source_key": rows[-1]["full_key"],
                "speakers": compact_speakers(rows),
                "record_digest": row_digest(key_rows),
            }
        )

    scene_families: list[dict[str, Any]] = []
    scene_fingerprints: dict[str, set[str]] = defaultdict(set)
    title_mentions: dict[str, set[str]] = defaultdict(set)
    usable_titles = [
        title
        for title in title_to_quest_ids
        if len(title) >= 4
    ]

    for family_id in sorted(scene_rows, key=natural_id):
        rows = sorted(scene_rows[family_id], key=lambda row: (row["line_index"], row["key"]))
        root_id = rows[0]["root_id"]
        variant_id = rows[0]["variant_id"]
        for row in rows:
            normalized = row["normalized_text"]
            if len(normalized) >= MIN_SHARED_TEXT_LENGTH:
                scene_fingerprints[normalized].add(family_id)
            for title in usable_titles:
                if title in normalized:
                    title_mentions[title].add(family_id)
        key_rows = [
            {"source_key": row["full_key"], "line_index": row["line_index"]}
            for row in rows
        ]
        scene_families.append(
            {
                "family_id": family_id,
                "root_id": root_id,
                "variant_id": variant_id,
                "line_count": len(rows),
                "first_line_index": rows[0]["line_index"],
                "last_line_index": rows[-1]["line_index"],
                "first_source_key": rows[0]["full_key"],
                "last_source_key": rows[-1]["full_key"],
                "speakers": compact_speakers(rows),
                "record_digest": row_digest(key_rows),
            }
        )

    edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    scene_by_root: dict[str, list[str]] = defaultdict(list)
    for family in scene_families:
        scene_by_root[family["root_id"]].append(family["family_id"])

    for quest_id in quest_rows:
        for family_id in scene_by_root.get(quest_id, []):
            edges[(quest_id, family_id)].add("same_numeric_root")

    ambiguous_fingerprints = 0
    for fingerprint, quest_ids in quest_fingerprints.items():
        family_ids = scene_fingerprints.get(fingerprint)
        if not family_ids:
            continue
        if len(quest_ids) > MAX_FINGERPRINT_FANOUT or len(family_ids) > MAX_FINGERPRINT_FANOUT:
            ambiguous_fingerprints += 1
            continue
        for quest_id in quest_ids:
            for family_id in family_ids:
                edges[(quest_id, family_id)].add("shared_dialogue_fingerprint")

    truncated_title_mentions = 0
    for title, quest_ids in title_to_quest_ids.items():
        family_ids = sorted(title_mentions.get(title, ()), key=natural_id)
        if not family_ids:
            continue
        if len(family_ids) > MAX_TITLE_SCENE_FANOUT:
            truncated_title_mentions += 1
            family_ids = family_ids[:MAX_TITLE_SCENE_FANOUT]
        for quest_id in quest_ids:
            for family_id in family_ids:
                edges[(quest_id, family_id)].add("quest_title_mention")

    candidate_links = [
        {
            "quest_id": quest_id,
            "scene_family_id": family_id,
            "reasons": sorted(reasons),
            "candidate_only": True,
            "order_inference_allowed": False,
        }
        for (quest_id, family_id), reasons in sorted(
            edges.items(), key=lambda item: (int(item[0][0]), natural_id(item[0][1]))
        )
    ]
    linked_quests = {row["quest_id"] for row in candidate_links}
    linked_scenes = {row["scene_family_id"] for row in candidate_links}
    duplicate_title_clusters = [
        {"title": title, "quest_ids": sorted(ids, key=int)}
        for title, ids in sorted(title_to_quest_ids.items())
        if len(ids) > 1
    ]

    return {
        "schema_version": 1,
        "contract_id": CONTRACT_ID,
        "generator_version": GENERATOR_VERSION,
        "status": "candidate_only",
        "source": {
            "path": source_path,
            "sha256": source_digest,
            "entries": len(source),
        },
        "policy": {
            "read_only": True,
            "ordering_declared": False,
            "formal_reference_allowed": False,
            "active_event_selected": False,
            "allowed_link_reasons": [
                "same_numeric_root",
                "shared_dialogue_fingerprint",
                "quest_title_mention",
            ],
            "numeric_proximity_is_not_evidence": True,
            "candidate_links_require_manual_event_review": True,
        },
        "summary": {
            "quest_group_count": len(quest_groups),
            "scene_family_count": len(scene_families),
            "candidate_link_count": len(candidate_links),
            "linked_quest_count": len(linked_quests),
            "linked_scene_family_count": len(linked_scenes),
            "duplicate_title_cluster_count": len(duplicate_title_clusters),
            "ambiguous_shared_fingerprints_skipped": ambiguous_fingerprints,
            "title_mentions_truncated": truncated_title_mentions,
            "unparsed_namespace_rows": dict(sorted(malformed_namespaces.items())),
        },
        "quest_groups": quest_groups,
        "scene_families": scene_families,
        "candidate_links": candidate_links,
        "duplicate_title_clusters": duplicate_title_clusters,
        "next_action": (
            "Review candidate links and duplicate-title clusters to choose one coherent Quest event group; "
            "do not declare event order or set active_event in this stage."
        ),
    }


def write_inventory(path: Path, inventory: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source = load_source(args.source)
    source_digest = sha256_bytes(args.source.read_bytes())
    try:
        source_path = args.source.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        source_path = args.source.as_posix()
    inventory = build_inventory(source, source_path, source_digest)
    write_inventory(args.output, inventory)
    print(
        json.dumps(
            {
                "status": "ok",
                "output": args.output.as_posix(),
                **inventory["summary"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
