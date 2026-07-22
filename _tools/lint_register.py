#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""キャラ横断の一人称・二人称・register不整合を候補抽出する。

実行例:
  python _tools/lint_register.py
  python _tools/lint_register.py --out-dir _ws_tmp/register_lint
  python _tools/lint_register.py --character 絶無心 --character 冷鷹

このツールは候補抽出だけを行い、locresを書き換えない。
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import glob
import json
import os
import re
import sys
from typing import Any, Iterable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")
LOC = os.path.join(ROOT, "_work", "jp", "Wandering_Sword", "Content", "Localization")
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
CONFIG_PATH = os.path.join(P4, "register_qa_config.json")

sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres  # noqa: E402

CONTROL_RE = re.compile(r"<[^>]*>|\{[^}]*\}|#nl")
HOSTILE_TERMS = (
    "牛鼻子", "妖道", "妖人", "妖女", "贼", "賊", "找死", "受死", "纳命", "納命",
    "万死", "萬死", "休想", "放肆", "滚", "滾", "老匹夫", "小贼", "小賊",
    "狗贼", "狗賊", "混账", "混帳", "该死", "該死", "畜生", "逆贼", "逆賊",
)
RESPECT_TERMS = (
    "大师兄", "大師兄", "师兄", "師兄", "师父", "師父", "前辈", "前輩",
    "大人", "神侯", "盟主", "宗主", "掌门", "掌門", "方丈", "大师", "大師", "长老", "長老",
)
POLITE_RE = re.compile(
    r"(?:です|ます|ません|ました|ましょう|でしょう|ください|下さい|"
    r"いただ(?:く|き|け|いた)|頂戴|いたします|致します|ございます|ございません)"
)
RAW_YO_RE = re.compile(r"(?:^|[\s「『（(【])余(?:$|[はがもにをの、。！？!?…])")

DEFAULT_SECOND_PERSON_TERMS = (
    "あなた", "お前", "おまえ", "貴様", "そなた", "貴殿", "少侠",
    "宇文逸", "宇文少侠", "宇文の坊主", "小僧",
)


def body(text: str | None) -> str:
    """話者接頭辞と制御タグを除いた本文を返す。"""
    value = text or ""
    if "$@$" in value:
        value = value.split("$@$", 1)[1]
    return CONTROL_RE.sub("", value).strip()


def matched_terms(text: str, terms: Iterable[str]) -> list[str]:
    return [term for term in terms if term in text]


def has_polite_register(text: str) -> bool:
    return bool(POLITE_RE.search(text))


def has_raw_yo(text: str) -> bool:
    return bool(RAW_YO_RE.search(text))


def find_second_person_terms(
    text: str,
    terms: Iterable[str] = DEFAULT_SECOND_PERSON_TERMS,
) -> list[str]:
    return matched_terms(text, terms)


def load_config(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {"schema_version": 1, "focus_characters": {}}
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def localization_path(target: str) -> str:
    paths = glob.glob(os.path.join(LOC, target, "zh-Hans", "*.locres"))
    if not paths:
        raise FileNotFoundError(f"locresが見つからない: {target}")
    return paths[0]


def scan_rows(
    data: dict[str, Any],
    source_zh: dict[str, str],
    config: dict[str, Any],
    selected_characters: set[str] | None = None,
) -> dict[str, Any]:
    lines = data["lines"]
    order = data.get("order") or list(lines)
    focus = config.get("focus_characters", {})
    ja_cache: dict[str, dict[str, str]] = {}

    def ja_of(target: str, ns: str, key: str) -> str:
        if target not in ja_cache:
            _, ja_cache[target], *_ = locres.parse(localization_path(target))
        return ja_cache[target].get(ns + "\x1f" + key, "") or ""

    l1: list[dict[str, Any]] = []
    l3: list[dict[str, Any]] = []
    l4: dict[str, dict[str, Any]] = {}

    for character in order:
        if selected_characters and character not in selected_characters:
            continue
        char_cfg = focus.get(character, {})
        checks = set(char_cfg.get("checks", []))
        second_terms = tuple(
            char_cfg.get("second_person_terms", DEFAULT_SECOND_PERSON_TERMS)
        )
        second_counts: Counter[str] = Counter()
        second_rows: list[dict[str, Any]] = []

        for target, ns, key in lines.get(character, []):
            full_key = target + "\x1f" + ns + "\x1f" + key
            zh_full = source_zh.get(full_key, "") or ""
            ja_full = ja_of(target, ns, key)
            zh_body = body(zh_full)
            ja_body = body(ja_full)
            base = {
                "character": character,
                "target": target,
                "ns": ns,
                "key": key,
                "zh": zh_full,
                "ja": ja_full,
            }

            if has_raw_yo(ja_body):
                l1.append({**base, "rule": "L1_raw_yo"})

            hostile = matched_terms(zh_body, HOSTILE_TERMS)
            if hostile and has_polite_register(ja_body):
                respectful = matched_terms(zh_body, RESPECT_TERMS)
                severity = "medium" if respectful else "high"
                l3.append(
                    {
                        **base,
                        "rule": "L3_hostile_polite",
                        "severity": severity,
                        "hostile_terms": hostile,
                        "respect_context_terms": respectful,
                    }
                )

            if "second_person_drift" in checks:
                found = find_second_person_terms(ja_body, second_terms)
                if found:
                    second_counts.update(found)
                    second_rows.append({**base, "terms": found})

        if "second_person_drift" in checks:
            direct = {
                key: count
                for key, count in second_counts.items()
                if key in {"あなた", "お前", "おまえ", "貴様", "そなた", "貴殿"}
            }
            l4[character] = {
                "counts": dict(second_counts.most_common()),
                "direct_pronoun_counts": direct,
                "has_drift": len([count for count in direct.values() if count > 0]) >= 2,
                "rows": second_rows,
            }

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "L1_raw_yo": len(l1),
            "L3_hostile_polite": len(l3),
            "L4_focus_characters": len(l4),
            "L4_rows": sum(len(value["rows"]) for value in l4.values()),
        },
        "L1_raw_yo": l1,
        "L3_hostile_polite": l3,
        "L4_second_person_drift": l4,
    }


def md_cell(text: str | None, limit: int = 120) -> str:
    value = (
        (text or "")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "\\|")
    )
    return value if len(value) <= limit else value[: limit - 1] + "…"


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    out = [
        "# register横断lint レポート",
        "",
        f"- 生成時刻(UTC): {report['generated_at']}",
        f"- L1 生「余」候補: {counts['L1_raw_yo']}件",
        f"- L3 敵対原文×敬体訳候補: {counts['L3_hostile_polite']}件",
        f"- L4 二人称追跡行: {counts['L4_rows']}件",
        "",
        "> 候補抽出のみ。registerは相手・場面で変化するため、一括置換しない。原文・前後文・ペルソナを照合して採否を決める。",
        "",
        "## L3 敵対原文×敬体訳",
        "",
        "|重要度|キャラ|対象|key|敵対語|原文|現訳|",
        "|---|---|---|---|---|---|---|",
    ]
    for row in report["L3_hostile_polite"]:
        out.append(
            "|{severity}|{character}|{target}|{key}|{terms}|{zh}|{ja}|".format(
                severity=row["severity"],
                character=md_cell(row["character"]),
                target=md_cell(row["target"]),
                key=md_cell(row["key"], 80),
                terms=md_cell("/".join(row["hostile_terms"]), 40),
                zh=md_cell(body(row["zh"])),
                ja=md_cell(body(row["ja"])),
            )
        )

    out.extend(
        [
            "",
            "## L1 生「余」",
            "",
            "|キャラ|対象|key|原文|現訳|",
            "|---|---|---|---|---|",
        ]
    )
    for row in report["L1_raw_yo"]:
        out.append(
            f"|{md_cell(row['character'])}|{md_cell(row['target'])}|"
            f"{md_cell(row['key'], 80)}|{md_cell(body(row['zh']))}|"
            f"{md_cell(body(row['ja']))}|"
        )

    out.extend(["", "## L4 二人称ドリフト追跡", ""])
    for character, result in report["L4_second_person_drift"].items():
        out.append(f"### {character}")
        out.append("")
        out.append(
            "- 直接二人称: `"
            + json.dumps(result["direct_pronoun_counts"], ensure_ascii=False)
            + "`"
        )
        out.append(
            f"- 複数形混在候補: `{'yes' if result['has_drift'] else 'no'}`"
        )
        out.append("")
        out.append("|語|対象|key|原文|現訳|")
        out.append("|---|---|---|---|---|")
        for row in result["rows"]:
            out.append(
                f"|{md_cell('/'.join(row['terms']), 40)}|{md_cell(row['target'])}|"
                f"{md_cell(row['key'], 80)}|{md_cell(body(row['zh']))}|"
                f"{md_cell(body(row['ja']))}|"
            )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--character",
        action="append",
        default=[],
        help="対象キャラ。複数指定可",
    )
    parser.add_argument("--config", default=CONFIG_PATH)
    parser.add_argument(
        "--out-dir",
        default=os.path.join(TMP, "register_lint"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with open(os.path.join(P4, "by_character.json"), encoding="utf-8") as fp:
        data = json.load(fp)
    with open(os.path.join(P4, "source_zh.json"), encoding="utf-8") as fp:
        source_zh = json.load(fp)
    config = load_config(args.config)
    selected = set(args.character) if args.character else None
    report = scan_rows(data, source_zh, config, selected)

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = os.path.join(args.out_dir, "register_lint.json")
    md_path = os.path.join(args.out_dir, "register_lint.md")
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    with open(md_path, "w", encoding="utf-8") as fp:
        fp.write(render_markdown(report))

    counts = report["counts"]
    print(
        f"register lint: L1={counts['L1_raw_yo']} "
        f"L3={counts['L3_hostile_polite']} "
        f"L4行={counts['L4_rows']} -> {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
