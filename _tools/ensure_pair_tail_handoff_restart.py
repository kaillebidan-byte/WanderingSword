#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ensure pair-tail handoff exposes the standard restart phrase."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
RESTART = "現状把握して作業の続きを"
HEADING = "# 現在の引継ぎ"
NOTICE = (
    f"> 再開指示: `{RESTART}`\n"
    ">\n"
    "> 実visibility、open PR、ActionsはGitHub metadataを優先する。\n"
)


class HandoffError(ValueError):
    pass


def ensure(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if RESTART in text:
        return False
    if not text.startswith(HEADING):
        raise HandoffError(f"handoff must start with {HEADING!r}")
    tail = text[len(HEADING):]
    updated = HEADING + "\n\n" + NOTICE + tail.lstrip("\n")
    path.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        changed = ensure(args.root / "_phase4_proofread" / "CURRENT_HANDOFF.md")
    except (OSError, HandoffError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print("OK: restart phrase inserted" if changed else "NOOP: restart phrase already present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
