#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人物ペアの関係性再監査用に、原文・現訳・前後文を会話ブロック単位で抽出する。

一次資料の棚卸し専用。ペルソナや関係性マップの正しさは仮定せず、
両者が同席する会話ブロックと相互呼称候補を収集する。

使い方:
  python _tools/extract_relation_context.py
  python _tools/extract_relation_context.py --id yuwen_qingxu --out-dir _ws_tmp/relation_audit
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
import os
import re
import sys
from typing import Any, Iterable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")
LOC = os.path.join(ROOT, "_work", "jp", "Wandering_Sword", "Content", "Localization")
CONFIG_PATH = os.path.join(P4, "relation_audit_queue.json")
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))

sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres  # noqa: E402

DIALOGUE_INDEX_RE = re.compile(r"^(?P<family>.*?_Dlgs)_Index(?P<index>\d+)_Text$")
CONTROL_RE = re.compile(r"<[^>]*>|\{[^}]*\}|#nl")
NORMALIZE_TABLE = str.maketrans(
    {
        "长": "長",
        "门": "門",
        "师": "師",
        "儿": "兒",
        "虚": "虚",
        "问": "問",
        "启": "啓",
        "风": "風",
    }
)


def normalize(text: str | None) -> str:
    return (text or "").translate(NORMALIZE_TABLE).replace(" ", "").strip()


def dialogue_parts(text: str | None) -> tuple[str, str]:
    """`ID - 話者 $@$本文` を話者と本文に分ける。"""
    value = text or ""
    if "$@$" not in value:
        return "", CONTROL_RE.sub("", value).strip()
    prefix, body = value.split("$@$", 1)
    speaker = prefix.rsplit(" - ", 1)[-1].strip()
    return speaker, CONTROL_RE.sub("", body).strip()


def dialogue_family(key: str) -> tuple[str, int | None]:
    """連番台詞keyを会話ブロック名とIndexへ分解する。"""
    match = DIALOGUE_INDEX_RE.match(key)
    if not match:
        return key, None
    return match.group("family"), int(match.group("index"))


def speaker_matches(speaker: str, aliases: Iterable[str]) -> bool:
    target = normalize(speaker)
    if not target:
        return False
    for alias in aliases:
        candidate = normalize(alias)
        if target == candidate or target.endswith(candidate):
            return True
    return False


def contains_marker(texts: Iterable[str], markers: Iterable[str]) -> list[str]:
    found: list[str] = []
    normalized_texts = [normalize(text) for text in texts]
    for marker in markers:
        nmarker = normalize(marker)
        if nmarker and any(nmarker in text for text in normalized_texts):
            found.append(marker)
    return found


def load_relation(config_path: str, relation_id: str | None) -> dict[str, Any]:
    with open(config_path, encoding="utf-8") as fp:
        config = json.load(fp)
    wanted = relation_id or config.get("current")
    for item in config.get("items", []):
        if item.get("id") == wanted:
            return item
    raise KeyError(f"関係IDが見つからない: {wanted}")


def localization_path(target: str) -> str:
    paths = glob.glob(os.path.join(LOC, target, "zh-Hans", "*.locres"))
    if not paths:
        raise FileNotFoundError(f"locresが見つからない: {target}")
    return paths[0]


def split_full_key(full_key: str) -> tuple[str, str, str] | None:
    parts = full_key.split("\x1f", 2)
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def collect_rows(source_zh: dict[str, str]) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    ja_cache: dict[str, dict[str, str]] = {}
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    def ja_of(target: str, ns: str, key: str) -> str:
        if target not in ja_cache:
            _, ja_cache[target], *_ = locres.parse(localization_path(target))
        return ja_cache[target].get(ns + "\x1f" + key, "") or ""

    for full_key, zh_value in source_zh.items():
        split = split_full_key(full_key)
        if split is None:
            continue
        target, ns, key = split
        ja_value = ja_of(target, ns, key)
        zh_speaker, zh_body = dialogue_parts(zh_value)
        ja_speaker, ja_body = dialogue_parts(ja_value)
        speaker = zh_speaker or ja_speaker
        if not speaker and "$@$" not in (zh_value or "") and "$@$" not in ja_value:
            continue
        family, index = dialogue_family(key)
        groups[(target, ns, family)].append(
            {
                "target": target,
                "ns": ns,
                "key": key,
                "index": index,
                "speaker": speaker,
                "zh_speaker": zh_speaker,
                "ja_speaker": ja_speaker,
                "zh": zh_value or "",
                "ja": ja_value,
                "zh_body": zh_body,
                "ja_body": ja_body,
            }
        )

    for rows in groups.values():
        rows.sort(key=lambda row: (row["index"] is None, row["index"] or 0, row["key"]))
    return groups


def classify_group(rows: list[dict[str, Any]], relation: dict[str, Any]) -> dict[str, Any] | None:
    left_aliases = relation["left"]["aliases"]
    right_aliases = relation["right"]["aliases"]
    left_markers = relation.get("left_to_right_markers", [])
    right_markers = relation.get("right_to_left_markers", [])

    left_present = any(speaker_matches(row["speaker"], left_aliases) for row in rows)
    right_present = any(speaker_matches(row["speaker"], right_aliases) for row in rows)
    left_hits: list[dict[str, Any]] = []
    right_hits: list[dict[str, Any]] = []

    for row in rows:
        texts = [row["zh_body"], row["ja_body"]]
        if speaker_matches(row["speaker"], left_aliases):
            markers = contains_marker(texts, left_markers)
            if markers:
                left_hits.append({"key": row["key"], "markers": markers})
        if speaker_matches(row["speaker"], right_aliases):
            markers = contains_marker(texts, right_markers)
            if markers:
                right_hits.append({"key": row["key"], "markers": markers})

    if left_present and right_present:
        kind = "direct_exchange"
    elif left_hits or right_hits:
        kind = "explicit_reference"
    else:
        return None

    return {
        "kind": kind,
        "left_present": left_present,
        "right_present": right_present,
        "left_to_right_hits": left_hits,
        "right_to_left_hits": right_hits,
    }


def build_report(relation: dict[str, Any], groups: dict[tuple[str, str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    selected: list[dict[str, Any]] = []
    speakers: Counter[str] = Counter()
    marker_counts: Counter[str] = Counter()

    for (target, ns, family), rows in groups.items():
        classification = classify_group(rows, relation)
        if classification is None:
            continue
        for row in rows:
            if row["speaker"]:
                speakers[row["speaker"]] += 1
        for hit in classification["left_to_right_hits"] + classification["right_to_left_hits"]:
            marker_counts.update(hit["markers"])
        selected.append(
            {
                "target": target,
                "ns": ns,
                "family": family,
                **classification,
                "rows": rows,
            }
        )

    selected.sort(
        key=lambda group: (
            0 if group["kind"] == "direct_exchange" else 1,
            group["target"],
            group["ns"],
            group["family"],
        )
    )
    return {
        "schema_version": 1,
        "relation": relation,
        "counts": {
            "groups": len(selected),
            "direct_exchange_groups": sum(group["kind"] == "direct_exchange" for group in selected),
            "explicit_reference_groups": sum(group["kind"] == "explicit_reference" for group in selected),
            "rows": sum(len(group["rows"]) for group in selected),
        },
        "speaker_inventory": dict(speakers.most_common()),
        "marker_inventory": dict(marker_counts.most_common()),
        "groups": selected,
    }


def md_cell(text: str | None, limit: int = 180) -> str:
    value = (text or "").replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return value if len(value) <= limit else value[: limit - 1] + "…"


def render_markdown(report: dict[str, Any]) -> str:
    relation = report["relation"]
    counts = report["counts"]
    out = [
        f"# 関係性一次資料 — {relation['left']['name']} ↔ {relation['right']['name']}",
        "",
        "> ペルソナや関係性マップを正しいと仮定せず、原文・現訳・会話前後を棚卸しした候補集。抽出結果だけでは結論にしない。",
        "",
        f"- 会話ブロック: {counts['groups']}",
        f"- 両者が同席: {counts['direct_exchange_groups']}",
        f"- 明示呼称のみ: {counts['explicit_reference_groups']}",
        f"- 収録行: {counts['rows']}",
        f"- 呼称マーカー: `{json.dumps(report['marker_inventory'], ensure_ascii=False)}`",
        "",
        "## 監査質問",
        "",
    ]
    for question in relation.get("audit_questions", []):
        out.append(f"- {question}")

    for number, group in enumerate(report["groups"], 1):
        out.extend(
            [
                "",
                f"## {number}. {group['kind']} — {group['target']} / {group['ns']} / {group['family']}",
                "",
                f"- 左→右呼称: `{json.dumps(group['left_to_right_hits'], ensure_ascii=False)}`",
                f"- 右→左呼称: `{json.dumps(group['right_to_left_hits'], ensure_ascii=False)}`",
                "",
                "|Index|話者|key|原文|現訳|",
                "|---:|---|---|---|---|",
            ]
        )
        for row in group["rows"]:
            index = "" if row["index"] is None else str(row["index"])
            out.append(
                f"|{index}|{md_cell(row['speaker'], 40)}|{md_cell(row['key'], 80)}|"
                f"{md_cell(row['zh_body'])}|{md_cell(row['ja_body'])}|"
            )
    return "\n".join(out).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=CONFIG_PATH)
    parser.add_argument("--id", dest="relation_id")
    parser.add_argument("--out-dir", default=os.path.join(TMP, "relation_audit"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    relation = load_relation(args.config, args.relation_id)
    with open(os.path.join(P4, "source_zh.json"), encoding="utf-8") as fp:
        source_zh = json.load(fp)
    report = build_report(relation, collect_rows(source_zh))
    os.makedirs(args.out_dir, exist_ok=True)
    relation_id = relation["id"]
    json_path = os.path.join(args.out_dir, relation_id + ".json")
    md_path = os.path.join(args.out_dir, relation_id + ".md")
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    with open(md_path, "w", encoding="utf-8") as fp:
        fp.write(render_markdown(report))
    counts = report["counts"]
    print(
        f"relation audit: {relation_id}: {counts['groups']} blocks / "
        f"{counts['direct_exchange_groups']} direct / {counts['rows']} rows -> {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
