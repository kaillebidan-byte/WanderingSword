#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""キャラ横断の一人称・二人称・register不整合を候補抽出する。

実行例:
  python _tools/lint_register.py
  python _tools/lint_register.py --out-dir _ws_tmp/register_lint
  python _tools/lint_register.py --character 絶無心 --character 冷鷹

読み取り専用。locres・進捗・pakは変更しない。
出力は候補であり、registerを一括置換してはならない。
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
POLITE_RE = re.compile(
    r"(?:です|ます|ません|ました|ましょう|でしょう|ください|下さい|"
    r"いただ(?:く|き|け|いた)|頂戴|いたします|致します|ございます|ございません)"
)
RAW_YO_RE = re.compile(r"(?:^|[\s「『（(【])余(?:$|[はがもにをの、。！？!?…])")
KEY_INDEX_RE = re.compile(r"^(?P<prefix>.*?_Dlgs_Index)(?P<index>\d+)(?P<suffix>_Text)$")

SECOND_PERSON_ZH = r"(?:你|您|尔|爾|汝|阁下|閣下|你们|你們)"
THREAT_RE = re.compile(
    SECOND_PERSON_ZH
    + r"[^。！？!?]{0,36}(?:找死|受死|纳命|納命|罪该万死|罪該萬死|"
    r"休想|放肆|滚开|滾開)"
)
# 侮蔑名詞は「你这／你这种」のように相手へ明示された場合だけ拾う。
INSULT_RE = re.compile(
    SECOND_PERSON_ZH
    + r"(?:这|這|这种|這種|等)[^。！？!?]{0,16}"
    r"(?:无耻之徒|無恥之徒|败类|敗類|人渣|畜生|小贼|小賊|狗贼|狗賊)"
)
# 固有名詞「妖僧迦摩」などを除くため、呼格直後の句読点を必須にする。
HOSTILE_VOCATIVE_RE = re.compile(
    r"^(?:妖僧|妖道|牛鼻子|老匹夫|狗贼|狗賊|逆贼|逆賊|"
    r"小贼|小賊|畜生)[，,！!]"
)
HOSTILE_IMPERATIVE_RE = re.compile(r"^(?:放肆|滚开|滾開|受死|纳命|納命)[！!。]?")

DEFAULT_SECOND_PERSON_TERMS = (
    "あなた", "お前", "おまえ", "貴様", "そなた", "貴殿", "少侠",
    "宇文逸", "宇文少侠", "宇文の坊主", "小僧",
)
DIRECT_PRONOUNS = {"あなた", "お前", "おまえ", "貴様", "そなた", "貴殿"}


def body(text: str | None) -> str:
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


def directed_hostility(text: str) -> list[str]:
    rules = (
        ("second_person_threat", THREAT_RE),
        ("second_person_insult", INSULT_RE),
        ("hostile_vocative", HOSTILE_VOCATIVE_RE),
        ("hostile_imperative", HOSTILE_IMPERATIVE_RE),
    )
    return [name for name, pattern in rules if pattern.search(text)]


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
    allowed_raw_yo = set(config.get("allowed_raw_yo_characters", []))
    ja_cache: dict[str, dict[str, str]] = {}

    def table_of(target: str) -> dict[str, str]:
        if target not in ja_cache:
            _, ja_cache[target], *_ = locres.parse(localization_path(target))
        return ja_cache[target]

    def ja_of(target: str, ns: str, key: str) -> str:
        return table_of(target).get(ns + "\x1f" + key, "") or ""

    def context_of(target: str, ns: str, key: str, radius: int = 1) -> list[dict[str, Any]]:
        match = KEY_INDEX_RE.match(key)
        if not match:
            return []
        center = int(match.group("index"))
        rows: list[dict[str, Any]] = []
        table = table_of(target)
        for index in range(max(0, center - radius), center + radius + 1):
            neighbor = f"{match.group('prefix')}{index}{match.group('suffix')}"
            full = target + "\x1f" + ns + "\x1f" + neighbor
            ja_value = table.get(ns + "\x1f" + neighbor, "") or ""
            zh_value = source_zh.get(full, "") or ""
            if ja_value or zh_value:
                rows.append({
                    "key": neighbor,
                    "zh": zh_value,
                    "ja": ja_value,
                    "is_current": neighbor == key,
                })
        return rows

    raw_yo: list[dict[str, Any]] = []
    hostile_polite: list[dict[str, Any]] = []
    focus_register: dict[str, dict[str, Any]] = {}
    second_person: dict[str, dict[str, Any]] = {}

    for character in order:
        if selected_characters and character not in selected_characters:
            continue
        char_cfg = focus.get(character, {})
        checks = set(char_cfg.get("checks", []))
        second_terms = tuple(char_cfg.get("second_person_terms", DEFAULT_SECOND_PERSON_TERMS))
        second_counts: Counter[str] = Counter()
        second_rows: list[dict[str, Any]] = []
        polite_rows: list[dict[str, Any]] = []

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

            if character not in allowed_raw_yo and has_raw_yo(ja_body):
                raw_yo.append({**base, "rule": "L1_raw_yo"})

            hostility = directed_hostility(zh_body)
            if hostility and has_polite_register(ja_body):
                hostile_polite.append({
                    **base,
                    "rule": "L3_directed_hostility_polite",
                    "hostility_patterns": hostility,
                    "context": context_of(target, ns, key),
                })

            if "polite_inventory" in checks and has_polite_register(ja_body):
                polite_rows.append({**base, "context": context_of(target, ns, key)})

            if "second_person_drift" in checks:
                found = find_second_person_terms(ja_body, second_terms)
                if found:
                    second_counts.update(found)
                    second_rows.append({
                        **base,
                        "terms": found,
                        "context": context_of(target, ns, key),
                    })

        if "polite_inventory" in checks:
            focus_register[character] = {"count": len(polite_rows), "rows": polite_rows}
        if "second_person_drift" in checks:
            direct = {term: count for term, count in second_counts.items() if term in DIRECT_PRONOUNS}
            second_person[character] = {
                "counts": dict(second_counts.most_common()),
                "direct_pronoun_counts": direct,
                "has_drift": len([count for count in direct.values() if count > 0]) >= 2,
                "rows": second_rows,
            }

    return {
        "schema_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "L1_raw_yo": len(raw_yo),
            "L3_directed_hostility_polite": len(hostile_polite),
            "focus_polite_rows": sum(v["count"] for v in focus_register.values()),
            "second_person_focus_characters": len(second_person),
            "second_person_rows": sum(len(v["rows"]) for v in second_person.values()),
        },
        "L1_raw_yo": raw_yo,
        "L3_directed_hostility_polite": hostile_polite,
        "focus_register_inventory": focus_register,
        "second_person_drift": second_person,
    }


def md_cell(text: str | None, limit: int = 120) -> str:
    value = (text or "").replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return value if len(value) <= limit else value[: limit - 1] + "…"


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    out = [
        "# register横断lint レポート",
        "",
        f"- 生成時刻(UTC): {report['generated_at']}",
        f"- L1 生『余』候補: {counts['L1_raw_yo']}件",
        f"- L3 二人称への敵対原文×敬体訳候補: {counts['L3_directed_hostility_polite']}件",
        f"- 指定キャラ敬体行: {counts['focus_polite_rows']}件",
        f"- 二人称追跡行: {counts['second_person_rows']}件",
        "",
        "> 候補抽出のみ。相手・場面・ペルソナを照合し、一括置換しない。",
        "",
        "## L3 二人称への敵対原文×敬体訳",
        "",
        "|キャラ|対象|key|検出|原文|現訳|",
        "|---|---|---|---|---|---|",
    ]
    for row in report["L3_directed_hostility_polite"]:
        out.append(
            f"|{md_cell(row['character'])}|{md_cell(row['target'])}|{md_cell(row['key'], 80)}|"
            f"{md_cell('/'.join(row['hostility_patterns']), 40)}|{md_cell(body(row['zh']))}|"
            f"{md_cell(body(row['ja']))}|"
        )

    out.extend(["", "## L1 生『余』", "", "|キャラ|対象|key|原文|現訳|", "|---|---|---|---|---|"])
    for row in report["L1_raw_yo"]:
        out.append(
            f"|{md_cell(row['character'])}|{md_cell(row['target'])}|{md_cell(row['key'], 80)}|"
            f"{md_cell(body(row['zh']))}|{md_cell(body(row['ja']))}|"
        )

    out.extend(["", "## 指定キャラの敬体インベントリ", ""])
    for character, result in report["focus_register_inventory"].items():
        out.extend([
            f"### {character} ({result['count']}件)",
            "",
            "|対象|key|原文|現訳|",
            "|---|---|---|---|",
        ])
        for row in result["rows"]:
            out.append(
                f"|{md_cell(row['target'])}|{md_cell(row['key'], 80)}|"
                f"{md_cell(body(row['zh']))}|{md_cell(body(row['ja']))}|"
            )
        out.append("")

    out.extend(["", "## 二人称ドリフト追跡", ""])
    for character, result in report["second_person_drift"].items():
        out.extend([
            f"### {character}",
            "",
            "- 直接二人称: `" + json.dumps(result["direct_pronoun_counts"], ensure_ascii=False) + "`",
            f"- 複数形混在候補: `{'yes' if result['has_drift'] else 'no'}`",
            "",
            "|語|対象|key|原文|現訳|",
            "|---|---|---|---|---|",
        ])
        for row in result["rows"]:
            out.append(
                f"|{md_cell('/'.join(row['terms']), 40)}|{md_cell(row['target'])}|"
                f"{md_cell(row['key'], 80)}|{md_cell(body(row['zh']))}|{md_cell(body(row['ja']))}|"
            )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", action="append", default=[], help="対象キャラ。複数指定可")
    parser.add_argument("--config", default=CONFIG_PATH)
    parser.add_argument("--out-dir", default=os.path.join(TMP, "register_lint"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with open(os.path.join(P4, "by_character.json"), encoding="utf-8") as fp:
        data = json.load(fp)
    with open(os.path.join(P4, "source_zh.json"), encoding="utf-8") as fp:
        source_zh = json.load(fp)
    report = scan_rows(
        data,
        source_zh,
        load_config(args.config),
        set(args.character) if args.character else None,
    )
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "register_lint.json"), "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out_dir, "register_lint.md"), "w", encoding="utf-8") as fp:
        fp.write(render_markdown(report))
    c = report["counts"]
    print(
        f"register lint: L1={c['L1_raw_yo']} L3={c['L3_directed_hostility_polite']} "
        f"敬体={c['focus_polite_rows']} 二人称={c['second_person_rows']} -> {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
