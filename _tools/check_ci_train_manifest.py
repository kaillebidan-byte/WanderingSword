#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI_TRAIN_MANIFEST.jsonの第一段階release条件、集計、checkpoint整合を検査する。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / "_phase4_proofread"
CURRENT_PATH = P4 / "CURRENT_WORK.json"
MANIFEST_PATH = P4 / "CI_TRAIN_MANIFEST.json"

VALID_STATUSES = {
    "accumulating",
    "ready_for_public_ci",
    "in_public_ci",
    "verified",
    "aborted",
}
BUNDLE_STATUS = "reviewed_pending_ci"
PILOT_THRESHOLDS = {"bundle_count": 4, "reviewed_rows": 40, "fix_keys": 20}
PILOT_CAPS = {"bundle_count": 6, "reviewed_rows": 60}
ALLOWED_EARLY_RELEASE = {
    "workflow_change",
    "schema_change",
    "security_or_visibility",
    "urgent_build_verification",
}


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: top level must be object: {path.relative_to(ROOT)}")
    return value


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def release_state(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    totals = manifest.get("totals", {})
    thresholds = manifest.get("thresholds", {})
    reached: list[str] = []
    for key in ("bundle_count", "reviewed_rows", "fix_keys"):
        total = totals.get(key)
        threshold = thresholds.get(key)
        if _nonnegative_int(total) and _positive_int(threshold) and total >= threshold:
            reached.append(key)

    trigger = manifest.get("release_trigger")
    if isinstance(trigger, dict):
        reason = trigger.get("reason")
        detail = trigger.get("detail")
        if reason in ALLOWED_EARLY_RELEASE and isinstance(detail, str) and detail.strip():
            reached.append(f"early:{reason}")
    return bool(reached), reached


def _compare_mapping(
    label: str,
    observed: dict[str, Any],
    expected: dict[str, Any],
    errors: list[str],
) -> None:
    for key, value in expected.items():
        if observed.get(key) != value:
            errors.append(
                f"{label} {key} mismatch: observed={observed.get(key)!r} expected={value!r}"
            )


def _checkpoint_asset_head(checkpoint: dict[str, Any]) -> Any:
    """phase2はrelease identity、phase1は旧translation_headを使う。"""
    identity = checkpoint.get("release_identity")
    if isinstance(identity, dict):
        validated = identity.get("validated_head")
        if isinstance(validated, str) and validated:
            return validated
    return checkpoint.get("translation_head")


def validate_manifest(
    manifest: dict[str, Any],
    current: dict[str, Any],
    *,
    require_ready: bool = False,
) -> list[str]:
    errors: list[str] = []

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if manifest.get("phase") != "phase1_pilot":
        errors.append("phase must be phase1_pilot")

    train_id = manifest.get("train_id")
    branch = manifest.get("branch")
    if not isinstance(train_id, str) or not train_id.strip():
        errors.append("train_id must be a non-empty string")
    if not isinstance(branch, str) or not branch.startswith("agent/"):
        errors.append("branch must be an agent/* branch")

    status = manifest.get("status")
    if status not in VALID_STATUSES:
        errors.append(f"status must be one of {sorted(VALID_STATUSES)!r}")

    thresholds = manifest.get("thresholds")
    caps = manifest.get("caps")
    if thresholds != PILOT_THRESHOLDS:
        errors.append(f"thresholds must equal phase1 pilot values {PILOT_THRESHOLDS!r}")
    if caps != PILOT_CAPS:
        errors.append(f"caps must equal phase1 pilot values {PILOT_CAPS!r}")

    allowed = manifest.get("allowed_early_release_reasons")
    if not isinstance(allowed, list) or set(allowed) != ALLOWED_EARLY_RELEASE:
        errors.append("allowed_early_release_reasons must match the phase1 allowlist")

    checkpoint = current.get("checkpoint")
    if not isinstance(checkpoint, dict):
        errors.append("CURRENT_WORK.checkpoint must be an object")
        checkpoint = {}

    current_train = current.get("ci_train")
    if not isinstance(current_train, dict):
        errors.append("CURRENT_WORK.ci_train must be an object")
        current_train = {}
    for key in ("phase", "train_id", "branch", "status"):
        if current_train.get(key) != manifest.get(key):
            errors.append(
                f"CURRENT_WORK.ci_train.{key} mismatch: "
                f"current={current_train.get(key)!r} manifest={manifest.get(key)!r}"
            )
    if current_train.get("manifest") != "_phase4_proofread/CI_TRAIN_MANIFEST.json":
        errors.append("CURRENT_WORK.ci_train.manifest path is invalid")
    if current_train.get("thresholds") != PILOT_THRESHOLDS:
        errors.append("CURRENT_WORK.ci_train.thresholds mismatch")
    if current_train.get("caps") != PILOT_CAPS:
        errors.append("CURRENT_WORK.ci_train.caps mismatch")

    base = manifest.get("base_checkpoint")
    if not isinstance(base, dict):
        errors.append("base_checkpoint must be an object")
        base = {}

    base_batch = base.get("batch")
    declared_base_batch = current_train.get("base_checkpoint_batch")
    if base_batch != declared_base_batch:
        errors.append(
            "base_checkpoint batch must match CURRENT_WORK.ci_train.base_checkpoint_batch: "
            f"manifest={base_batch!r} current_train={declared_base_batch!r}"
        )

    checkpoint_batch = checkpoint.get("batch")
    checkpoint_advanced = (
        isinstance(base_batch, int)
        and isinstance(checkpoint_batch, int)
        and checkpoint_batch > base_batch
    )

    # 蓄積中とrelease直前は、列車の出発checkpointとCURRENT_WORKの確定点が同一。
    # 適用後はmanifest.base_checkpointを出発点として固定し、進んだcheckpointは
    # applied_resultと束末尾に対して別に検査する。
    if not checkpoint_advanced:
        expected_base = {
            "batch": checkpoint.get("batch"),
            "pair_applied_keys": checkpoint.get("pair_applied_keys"),
            "project_applied_keys": checkpoint.get("project_applied_keys"),
            "produced_by_pr": checkpoint.get("produced_by_pr"),
        }
        identity = checkpoint.get("release_identity")
        if isinstance(identity, dict):
            expected_base["release_identity"] = identity
        else:
            expected_base["translation_head"] = checkpoint.get("translation_head")
            expected_base["verified_head"] = checkpoint.get("verified_head")
        _compare_mapping("base_checkpoint", base, expected_base, errors)
    else:
        if status not in {"in_public_ci", "verified"}:
            errors.append("checkpoint may advance beyond train base only in_public_ci or verified")
        checkpoint_status = checkpoint.get("status")
        if checkpoint_status not in {"pending_audit_sync", "verified"}:
            errors.append(
                "advanced train checkpoint must be pending_audit_sync or verified: "
                f"{checkpoint_status!r}"
            )
        applied = current_train.get("applied_result")
        if not isinstance(applied, dict):
            errors.append("advanced train checkpoint requires CURRENT_WORK.ci_train.applied_result")
        else:
            expected_applied = {
                "pair_applied_keys": checkpoint.get("pair_applied_keys"),
                "project_applied_keys": checkpoint.get("project_applied_keys"),
                "asset_head": _checkpoint_asset_head(checkpoint),
            }
            _compare_mapping("ci_train.applied_result", applied, expected_applied, errors)
            if applied.get("pending_fixes") != 0:
                errors.append("ci_train.applied_result.pending_fixes must be 0")

    bundles = manifest.get("bundles")
    if not isinstance(bundles, list):
        errors.append("bundles must be a list")
        bundles = []

    seen_batches: set[int] = set()
    seen_scenes: set[str] = set()
    sums = {
        "bundle_count": len(bundles),
        "reviewed_rows": 0,
        "fix_keys": 0,
        "new_pair_keys": 0,
    }
    expected_batch = base_batch + 1 if isinstance(base_batch, int) else None

    for index, bundle in enumerate(bundles):
        label = f"bundles[{index}]"
        if not isinstance(bundle, dict):
            errors.append(f"{label} must be an object")
            continue
        batch = bundle.get("batch")
        if not _positive_int(batch):
            errors.append(f"{label}.batch must be a positive integer")
        else:
            if batch in seen_batches:
                errors.append(f"duplicate bundle batch: {batch}")
            seen_batches.add(batch)
            if expected_batch is not None and batch != expected_batch:
                errors.append(
                    "bundle batches must be consecutive from checkpoint: "
                    f"expected {expected_batch}, got {batch}"
                )
            expected_batch = batch + 1

        if bundle.get("status") != BUNDLE_STATUS:
            errors.append(f"{label}.status must be {BUNDLE_STATUS}")

        scenes = bundle.get("scene_groups")
        if not isinstance(scenes, list) or not scenes or any(
            not isinstance(scene, str) or not scene for scene in scenes
        ):
            errors.append(f"{label}.scene_groups must be a non-empty string list")
            scenes = []
        for scene in scenes:
            if scene in seen_scenes:
                errors.append(f"scene appears in multiple bundles: {scene}")
            seen_scenes.add(scene)

        for key in ("reviewed_rows", "fix_keys", "new_pair_keys"):
            value = bundle.get(key)
            if not _nonnegative_int(value):
                errors.append(f"{label}.{key} must be a non-negative integer")
            else:
                sums[key] += value

        fix_files = bundle.get("fix_files")
        if not isinstance(fix_files, list) or not fix_files:
            errors.append(f"{label}.fix_files must be a non-empty list")
        else:
            for path in fix_files:
                if not isinstance(path, str) or not path.startswith(
                    "_phase4_proofread/fixes_"
                ) or not path.endswith(".json"):
                    errors.append(f"{label} invalid fix file: {path!r}")

        review = bundle.get("review_record")
        if not isinstance(review, str) or not review.startswith(
            "_phase4_proofread/REVIEW_"
        ) or not review.endswith(".md"):
            errors.append(f"{label}.review_record is invalid")

        ownership = bundle.get("ownership_summary")
        if not isinstance(ownership, dict):
            errors.append(f"{label}.ownership_summary must be an object")
        else:
            for key in ("existing_keys", "new_keys", "cross_register_keys"):
                if not _nonnegative_int(ownership.get(key)):
                    errors.append(f"{label}.ownership_summary.{key} must be non-negative")

    if checkpoint_advanced:
        last_bundle_batch = bundles[-1].get("batch") if bundles and isinstance(bundles[-1], dict) else None
        if checkpoint_batch != last_bundle_batch:
            errors.append(
                "advanced checkpoint batch must equal final train bundle: "
                f"checkpoint={checkpoint_batch!r} final_bundle={last_bundle_batch!r}"
            )
    if status == "verified" and checkpoint.get("status") != "verified":
        errors.append("verified manifest requires verified CURRENT_WORK checkpoint")

    totals = manifest.get("totals")
    if not isinstance(totals, dict):
        errors.append("totals must be an object")
        totals = {}
    for key, expected in sums.items():
        if totals.get(key) != expected:
            errors.append(
                f"totals.{key} mismatch: manifest={totals.get(key)!r}, calculated={expected}"
            )

    if sums["bundle_count"] > PILOT_CAPS["bundle_count"]:
        errors.append("bundle_count exceeds phase1 cap")
    if sums["reviewed_rows"] > PILOT_CAPS["reviewed_rows"]:
        errors.append("reviewed_rows exceeds phase1 cap")

    trigger = manifest.get("release_trigger")
    if trigger is not None:
        if not isinstance(trigger, dict):
            errors.append("release_trigger must be null or an object")
        else:
            reason = trigger.get("reason")
            detail = trigger.get("detail")
            if reason not in ALLOWED_EARLY_RELEASE:
                errors.append(f"release_trigger.reason is not allowed: {reason!r}")
            if not isinstance(detail, str) or not detail.strip():
                errors.append("release_trigger.detail must be a non-empty string")

    ready, reasons = release_state(manifest)
    if status == "accumulating" and ready:
        errors.append(
            "manifest reached a release condition but status is still accumulating: "
            + ", ".join(reasons)
        )
    if status in {"ready_for_public_ci", "in_public_ci"} and not ready:
        errors.append("ready/in_public_ci manifest needs a threshold or allowed early release")
    if require_ready and status not in {"ready_for_public_ci", "in_public_ci"}:
        errors.append("manifest must be ready_for_public_ci or in_public_ci")

    declared = current.get("operation_mode", {}).get("declared_state")
    if status == "accumulating" and declared != "private_translation_work":
        errors.append("accumulating train requires private_translation_work")
    if status in {"ready_for_public_ci", "in_public_ci"} and declared != "ready_for_public_ci":
        errors.append("ready train requires operation_mode ready_for_public_ci")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="公開CIへ出す列車としてrelease可能な状態を要求する",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = load_object(CURRENT_PATH)
    manifest = load_object(MANIFEST_PATH)
    errors = validate_manifest(manifest, current, require_ready=args.require_ready)
    ready, reasons = release_state(manifest)

    totals = manifest.get("totals", {})
    print("=== CI train phase1 ===")
    print(f"train: {manifest.get('train_id')}")
    print(f"branch: {manifest.get('branch')}")
    print(f"status: {manifest.get('status')}")
    print(
        "totals: "
        f"{totals.get('bundle_count')} bundle(s), "
        f"{totals.get('reviewed_rows')} row(s), "
        f"{totals.get('fix_keys')} fix key(s)"
    )
    print(f"release ready: {ready}")
    if reasons:
        print("release reasons: " + ", ".join(reasons))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: CI train manifest is structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
