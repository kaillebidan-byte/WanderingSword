#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh tail release-candidate lineage before the ordinary release guard."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
READY = "ready_for_public_ci"


class RefreshError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RefreshError(f"top level must be object: {path}")
    return value


def refresh(p4: Path = P4) -> dict[str, Any]:
    current = load(p4 / "CURRENT_WORK.json")
    manifest = load(p4 / "CI_TRAIN_MANIFEST.json")
    stage = load(p4 / "PRIVATE_STAGE_STATE.json")
    packet = load(p4 / "NEXT_TASK_PACKET.json")

    train = current.get("ci_train")
    if not isinstance(train, dict):
        raise RefreshError("CURRENT_WORK.ci_train must be an object")
    train_id = train.get("train_id")
    pr = train.get("draft_pr")
    if not isinstance(train_id, str) or not train_id.startswith("yuwen-mowen-train-"):
        raise RefreshError("active tail train_id is invalid")
    if not isinstance(pr, int) or isinstance(pr, bool) or pr <= 0:
        raise RefreshError("active tail PR is invalid")

    expected = (
        train.get("status"),
        train.get("transport_status"),
        manifest.get("status"),
        manifest.get("transport", {}).get("status"),
        stage.get("stage"),
        stage.get("transport", {}).get("status"),
        packet.get("reservation", {}).get("status"),
    )
    if expected != (READY, READY, READY, READY, "translation_frozen", READY, "encoded"):
        raise RefreshError(f"tail release authorities are not ready: {expected!r}")
    if manifest.get("train_id") != train_id or stage.get("train_id") != train_id:
        raise RefreshError("tail train lineage mismatch")
    if manifest.get("draft_pr") != pr or stage.get("transport", {}).get("pr") != pr:
        raise RefreshError("tail PR lineage mismatch")
    if packet.get("ci_train", {}).get("train_id") != train_id:
        raise RefreshError("tail packet train lineage mismatch")

    candidate = {
        "train_id": train_id,
        "release_id": f"{train_id}-r1",
        "pr": pr,
        "status": READY,
    }
    packet["release_candidate"] = candidate
    (p4 / "NEXT_TASK_PACKET.json").write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = refresh(args.root / "_phase4_proofread")
    except (OSError, json.JSONDecodeError, ValueError, RefreshError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
