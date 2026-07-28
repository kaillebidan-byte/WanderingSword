#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""意味単位を切らないため、waveの標準40〜60行・強制上限80行へ移行する。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def update_json(path: str, mutator) -> None:
    data = json.loads(read(path))
    mutator(data)
    write(path, json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


def replace_once_or_accept(path: str, old: str, new: str) -> None:
    text = read(path)
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"migration anchor missing in {path}: {old!r}")
    write(path, text.replace(old, new, 1))


def update_contract(data: dict) -> None:
    data["contract_id"] = "private-translation-stages-v6-semantic-wave-cap-80"
    policy = data["wave_policy"]
    policy["standard_reviewed_rows"] = {"min": 40, "max": 60}
    policy["caps"]["unique_reviewed_rows"] = 80
    policy["semantic_extension"] = {
        "allowed": True,
        "after_standard_max": 60,
        "hard_max": 80,
        "reason": "complete_semantic_unit",
        "fill_to_hard_max_required": False,
    }


def main() -> None:
    update_json("_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json", update_contract)
    update_json(
        "_phase4_proofread/CI_TRAIN_MANIFEST.json",
        lambda data: data["caps"].__setitem__("reviewed_rows", 80),
    )
    update_json(
        "_phase4_proofread/CURRENT_WORK.json",
        lambda data: data["ci_train"]["caps"].__setitem__("reviewed_rows", 80),
    )

    replace_once_or_accept(
        "_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md",
        "上限は6 packet / 60 rows。underfilledな一packet sealは失敗する。",
        "40〜60 rowsを標準範囲とする。60 rows付近で意味単位が完結していない場合は、その意味単位を切らずに6 packet / 80 rowsまで延長できる。80 rowsを埋めることを目的にしてはならない。underfilledな一packet sealは失敗する。",
    )
    replace_once_or_accept(
        "_phase4_proofread/CI_TRAIN_PHASE1.md",
        "preparationでは複数packetを先に準備する。通常sealは4 packet以上または40 unique reviewed rows相当以上。追加候補が意味境界上存在しない場合だけ`scope_exhausted`を使う。上限は6 packet / 60 rows。",
        "preparationでは複数packetを先に準備する。通常sealは4 packet以上または40 unique reviewed rows相当以上。追加候補が意味境界上存在しない場合だけ`scope_exhausted`を使う。40〜60 rowsを標準範囲とし、60 rows付近で意味単位が完結していない場合は、その意味単位を切らずに最大6 packet / 80 rowsまで延長できる。80 rowsを埋めることを目的にしてはならない。",
    )
    replace_once_or_accept(
        "_phase4_proofread/CI_TRAIN_PHASE1.md",
        "蓄積上限は完成正式束6、通読60 unique rowsとする。workflow変更、schema変更、security/visibility、緊急build確認は許可された早期release理由として別に記録する。",
        "標準範囲は通読40〜60 unique rowsとする。意味単位を完結させる場合に限り、完成正式束6を維持したまま通読80 unique rowsまで延長でき、80 rowsを強制上限とする。workflow変更、schema変更、security/visibility、緊急build確認は許可された早期release理由として別に記録する。",
    )

    path = "_tools/check_private_translation_stage.py"
    text = read(path)
    text = text.replace(
        'if policy.get("caps") != {"packet_count": 6, "unique_reviewed_rows": 60}:',
        'if policy.get("caps") != {"packet_count": 6, "unique_reviewed_rows": 80}:',
    )
    text = text.replace("if rows > 60:", "if rows > 80:")
    if "contract.wave_policy.standard_reviewed_rows mismatch" not in text:
        anchor = (
            '        if policy.get("normal_seal") != {"packet_count": 4, "unique_reviewed_rows": 40}:\n'
            '            errors.append("contract.wave_policy.normal_seal mismatch")\n'
        )
        addition = (
            '        if policy.get("standard_reviewed_rows") != {"min": 40, "max": 60}:\n'
            '            errors.append("contract.wave_policy.standard_reviewed_rows mismatch")\n'
        )
        if anchor not in text:
            raise SystemExit(f"checker anchor missing in {path}")
        text = text.replace(anchor, anchor + addition, 1)
    if "contract.wave_policy.semantic_extension mismatch" not in text:
        anchor = (
            '        if policy.get("caps") != {"packet_count": 6, "unique_reviewed_rows": 80}:\n'
            '            errors.append("contract.wave_policy.caps mismatch")\n'
        )
        addition = (
            '        if policy.get("semantic_extension") != {\n'
            '            "allowed": True,\n'
            '            "after_standard_max": 60,\n'
            '            "hard_max": 80,\n'
            '            "reason": "complete_semantic_unit",\n'
            '            "fill_to_hard_max_required": False,\n'
            '        }:\n'
            '            errors.append("contract.wave_policy.semantic_extension mismatch")\n'
        )
        if anchor not in text:
            raise SystemExit(f"cap checker anchor missing in {path}")
        text = text.replace(anchor, anchor + addition, 1)
    write(path, text)

    path = "_tools/check_ci_train_manifest.py"
    write(
        path,
        read(path).replace(
            'PILOT_CAPS = {"bundle_count": 6, "reviewed_rows": 60}',
            'PILOT_CAPS = {"bundle_count": 6, "reviewed_rows": 80}',
        ),
    )

    path = "_tools/test_check_private_translation_stage.py"
    text = read(path).replace(
        '"caps": {"packet_count": 6, "unique_reviewed_rows": 60},',
        '"caps": {"packet_count": 6, "unique_reviewed_rows": 80},',
    )
    if '"standard_reviewed_rows": {"min": 40, "max": 60}' not in text:
        anchor = '            "normal_seal": {"packet_count": 4, "unique_reviewed_rows": 40},\n'
        text = text.replace(
            anchor,
            anchor + '            "standard_reviewed_rows": {"min": 40, "max": 60},\n',
            1,
        )
    if '"reason": "complete_semantic_unit"' not in text:
        anchor = '            "caps": {"packet_count": 6, "unique_reviewed_rows": 80},\n'
        text = text.replace(
            anchor,
            anchor
            + '            "semantic_extension": {\n'
            + '                "allowed": True,\n'
            + '                "after_standard_max": 60,\n'
            + '                "hard_max": 80,\n'
            + '                "reason": "complete_semantic_unit",\n'
            + '                "fill_to_hard_max_required": False,\n'
            + '            },\n',
            1,
        )
    if "# 2b. 60行を超えても意味単位を完結させる80行までは成功" not in text:
        anchor = "    # 3. queue未sealedでquality auditへ進んだら失敗\n"
        addition = (
            "    # 2b. 60行を超えても意味単位を完結させる80行までは成功\n"
            '    state, current, manifest = sample("private_preparation", count=6)\n'
            '    state["wave"]["preparation_summary"]["unique_reviewed_rows"] = 80\n'
            "    assert errors(checker, state, current, manifest) == []\n\n"
            "    # 2c. 80行を超えたら失敗\n"
            '    state["wave"]["preparation_summary"]["unique_reviewed_rows"] = 81\n'
            '    assert any("wave row cap exceeded" in error for error in errors(checker, state, current, manifest))\n\n'
        )
        if anchor not in text:
            raise SystemExit(f"regression anchor missing in {path}")
        text = text.replace(anchor, addition + anchor, 1)
    write(path, text)

    path = "_tools/test_check_ci_train_manifest.py"
    text = read(path).replace(
        '{"bundle_count": 6, "reviewed_rows": 60}',
        '{"bundle_count": 6, "reviewed_rows": 80}',
    )
    text = text.replace(
        'rows=11, fixes=1) for i in range(6)]',
        'rows=14, fixes=1) for i in range(6)]',
    )
    if "scene-cap-" not in text:
        anchor = '    over = base_manifest("ready_for_public_ci", "ready_for_public_ci")\n'
        addition = (
            '    at_cap = base_manifest("ready_for_public_ci", "ready_for_public_ci")\n'
            '    at_cap["bundles"] = [bundle(61 + i, f"scene-cap-{i}", rows=16, fixes=1) for i in range(5)]\n'
            "    recalc(at_cap)\n"
            "    assert module.validate_manifest(\n"
            "        at_cap,\n"
            '        current("ready_for_public_ci", "translation_frozen", "ready_for_public_ci"),\n'
            "        require_ready=True,\n"
            "    ) == []\n\n"
        )
        if anchor not in text:
            raise SystemExit(f"manifest regression anchor missing in {path}")
        text = text.replace(anchor, addition + anchor, 1)
    write(path, text)


if __name__ == "__main__":
    main()
