# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import build_story_context_candidates as B
import check_story_context_layer as C

HERE = Path(__file__).resolve().parents[1]
Q_NAME = "Quests任务表\x1fQuests\x1f100_Name"
Q = "Quests任务表\x1fQuests\x1f100_RequestDlgs_Index0_Text"
S = "CG表\x1fQuestDlgs\x1f100_1_Dlgs_Index0_Text"
AUTH = [
    "CURRENT_WORK.json",
    "PRIVATE_STAGE_STATE.json",
    "CI_TRAIN_MANIFEST.json",
    "NEXT_TASK_PACKET.json",
    "audit_status.json",
    "relation_audit_queue.json",
]


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class Tests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for relative in (
            "_story_context/STORY_CONTEXT_PREPARATION_CONTRACT.json",
            "_story_context/schemas/candidate_inventory.schema.json",
            "_story_context/schemas/event_manifest.schema.json",
            "_story_context/schemas/scene_context.schema.json",
            "_story_context/schemas/spoiler_context.schema.json",
        ):
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / relative, root / relative)
        write(
            root / "_story_context/REFERENCE_GATE.json",
            {
                "schema_version": 1,
                "contract_id": "story-context-preparation-v1",
                "status": "closed",
                "formal_reference_allowed": False,
                "reason": "fixture gate",
                "required_stage": "reference_ready",
                "required_artifacts": [
                    "event_manifest",
                    "scene_context",
                    "spoiler_context",
                    "crosscheck",
                    "doubt_resolution_trial",
                ],
                "consumer_policy": {
                    "proofreading_may_reference": False,
                    "translation_factory_may_reference": False,
                    "chapter_readthrough_may_reference": False,
                    "checker_may_inspect": True,
                },
                "opening_conditions": {
                    "later_development_checked": True,
                    "unresolved_conflicts": 0,
                    "scene_spoiler_separation_verified": True,
                    "source_keys_verified": True,
                    "phase_authorities_unchanged": True,
                    "phase1_doubt_resolution_trial_passed": True,
                },
            },
        )
        (root / "_story_context/INVESTIGATION_2026-08-02.md").write_text(
            "investigated\n", encoding="utf-8"
        )

        p4 = root / "_phase4_proofread"
        p4.mkdir()
        for index, name in enumerate(AUTH, 1):
            write(p4 / name, {"fixture": index})
        write(
            p4 / "source_zh.json",
            {
                Q_NAME: "0 - 系统 $@$白鹿旧事",
                Q: "1 - 主人公 $@$依頼を受ける",
                S: "1 - 主人公 $@$場面が進む",
            },
        )
        baseline = {
            "schema_version": 1,
            "contract_id": "story-context-preparation-v1",
            "captured_at": "2026-08-02",
            "authority_blobs": {
                f"_phase4_proofread/{name}": C.git_blob_sha(p4 / name)
                for name in AUTH
            },
            "source_index": {
                "path": "_phase4_proofread/source_zh.json",
                "blob": C.git_blob_sha(p4 / "source_zh.json"),
                "entries": 3,
            },
        }
        write(root / "_story_context/PHASE_BASELINE.json", baseline)
        state = {
            "schema_version": 1,
            "contract_id": "story-context-preparation-v1",
            "current_stage": "contract_ready",
            "formal_reference": False,
            "active_event": None,
            "artifacts": {
                "investigation": "_story_context/INVESTIGATION_2026-08-02.md",
                "contract": "_story_context/STORY_CONTEXT_PREPARATION_CONTRACT.json",
                "phase_baseline": "_story_context/PHASE_BASELINE.json",
                "reference_gate": "_story_context/REFERENCE_GATE.json",
                "candidate_inventory": None,
                "event_manifest": None,
                "scene_context": None,
                "spoiler_context": None,
                "crosscheck": None,
                "doubt_resolution_trial": None,
            },
            "history": [
                {
                    "stage": "investigated",
                    "date": "2026-08-02",
                    "evidence": "_story_context/INVESTIGATION_2026-08-02.md",
                },
                {
                    "stage": "contract_ready",
                    "date": "2026-08-02",
                    "evidence": "_story_context/STORY_CONTEXT_PREPARATION_CONTRACT.json",
                },
            ],
            "non_interference": {
                "phase1_phase2_progress_mutation": "none",
                "translation_mutation": "none",
                "locres_mutation": "none",
                "pak_mutation": "none",
                "game_verification_mutation": "none",
            },
            "next_action": "build candidates",
        }
        write(root / "_story_context/STATE.json", state)
        return temporary, root

    def candidate(self, root: Path):
        source_path = root / "_phase4_proofread/source_zh.json"
        source = B.load_source(source_path)
        return B.build_inventory(
            source,
            "_phase4_proofread/source_zh.json",
            C.sha256_file(source_path),
        )

    def manifest(self):
        return {
            "schema_version": 1,
            "event_id": "pilot_event",
            "title": "Pilot",
            "status": "verified",
            "selection_basis": {
                "evidence": ["quest and scene evidence"],
                "limitations": [],
            },
            "quest_lifecycle": [
                {"order": 1, "phase": "request", "source_keys": [Q]}
            ],
            "scenes": [
                {
                    "order": 1,
                    "scene_id": "scene_1",
                    "family": "100_1_Dlgs",
                    "source_keys": [S],
                    "placement_basis": ["direct continuation"],
                    "branch": None,
                }
            ],
            "source_keys": [Q, S],
        }

    def scene(self):
        return {
            "schema_version": 1,
            "event_id": "pilot_event",
            "layer": "scene_time",
            "scenes": [
                {
                    "scene_id": "scene_1",
                    "order": 1,
                    "player_knowledge_before": [],
                    "player_knowledge_after": ["accepted"],
                    "character_knowledge": {"主人公": ["accepted"]},
                    "beliefs_and_misunderstandings": [],
                    "uncertainties": ["outcome unknown"],
                    "source_keys": [S],
                }
            ],
            "source_keys": [S],
        }

    def spoiler(self):
        return {
            "schema_version": 1,
            "event_id": "pilot_event",
            "layer": "full_spoiler",
            "truths": [
                {
                    "truth_id": "truth_1",
                    "statement": "succeeds",
                    "source_keys": [S],
                }
            ],
            "reveal_order": [
                {
                    "order": 1,
                    "truth_id": "truth_1",
                    "reveal_kind": "confirmed",
                    "scene_id": "scene_1",
                    "source_keys": [S],
                }
            ],
            "source_keys": [S],
        }

    def cross(self):
        return {
            "schema_version": 1,
            "event_id": "pilot_event",
            "later_development_checked": True,
            "unresolved_conflicts": [],
            "checks": {
                "source_keys_verified": True,
                "scene_spoiler_separation_verified": True,
                "event_order_verified": True,
            },
        }

    def stage(self, root: Path, name: str):
        stage_index = C.EXPECTED_STAGES.index(name)
        state_path = root / "_story_context/STATE.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["current_stage"] = name
        state["formal_reference"] = name == "reference_ready"
        state["history"] = [
            {
                "stage": stage,
                "date": "2026-08-02",
                "evidence": f"e/{stage}",
            }
            for stage in C.EXPECTED_STAGES[: stage_index + 1]
        ]
        if stage_index >= 2:
            write(root / "_story_context/candidates/pilot.json", self.candidate(root))
            state["artifacts"]["candidate_inventory"] = "_story_context/candidates/pilot.json"
        if stage_index >= 3:
            state["active_event"] = "pilot_event"
            write(root / "_story_context/manifests/pilot.json", self.manifest())
            state["artifacts"]["event_manifest"] = "_story_context/manifests/pilot.json"
        if stage_index >= 4:
            write(root / "_story_context/scene_context/pilot.json", self.scene())
            state["artifacts"]["scene_context"] = "_story_context/scene_context/pilot.json"
        if stage_index >= 5:
            write(root / "_story_context/spoiler_context/pilot.json", self.spoiler())
            state["artifacts"]["spoiler_context"] = "_story_context/spoiler_context/pilot.json"
        if stage_index >= 6:
            write(root / "_story_context/crosschecks/pilot.json", self.cross())
            state["artifacts"]["crosscheck"] = "_story_context/crosschecks/pilot.json"
        write(state_path, state)
        if name == "reference_ready":
            gate_path = root / "_story_context/REFERENCE_GATE.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["status"] = "open"
            gate["formal_reference_allowed"] = True
            for key in (
                "proofreading_may_reference",
                "translation_factory_may_reference",
                "chapter_readthrough_may_reference",
            ):
                gate["consumer_policy"][key] = True
            write(gate_path, gate)

    def test_contract_ready(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        result = C.validate_root(root)
        self.assertEqual(result["current_stage"], "contract_ready")
        self.assertFalse(result["formal_reference"])

    def test_candidate_ready(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "candidate_inventory_ready")
        result = C.validate_root(root)
        self.assertEqual(result["current_stage"], "candidate_inventory_ready")
        self.assertIsNone(result["active_event"])
        self.assertEqual(result["candidate_summary"]["quest_group_count"], 1)

    def test_authority_mutation(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        write(root / "_phase4_proofread/CURRENT_WORK.json", {"bad": 1})
        with self.assertRaisesRegex(C.StoryContextError, "phase authority changed"):
            C.validate_root(root)

    def test_stage_skip(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        state_path = root / "_story_context/STATE.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["current_stage"] = "event_manifest_ready"
        state["history"] = [
            state["history"][0],
            {
                "stage": "event_manifest_ready",
                "date": "2026-08-02",
                "evidence": "x",
            },
        ]
        write(state_path, state)
        with self.assertRaisesRegex(C.StoryContextError, "adjacent stage"):
            C.validate_root(root)

    def test_gate_early(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        gate_path = root / "_story_context/REFERENCE_GATE.json"
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        gate["status"] = "open"
        gate["formal_reference_allowed"] = True
        write(gate_path, gate)
        with self.assertRaisesRegex(C.StoryContextError, "gate must be closed"):
            C.validate_root(root)

    def test_candidate_digest_mismatch(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "candidate_inventory_ready")
        path = root / "_story_context/candidates/pilot.json"
        candidate = json.loads(path.read_text(encoding="utf-8"))
        candidate["source"]["sha256"] = "0" * 64
        write(path, candidate)
        with self.assertRaisesRegex(C.StoryContextError, "source digest mismatch"):
            C.validate_root(root)

    def test_candidate_order_claim_blocks(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "candidate_inventory_ready")
        path = root / "_story_context/candidates/pilot.json"
        candidate = json.loads(path.read_text(encoding="utf-8"))
        candidate["policy"]["ordering_declared"] = True
        write(path, candidate)
        with self.assertRaisesRegex(C.StoryContextError, "became authoritative"):
            C.validate_root(root)

    def test_candidate_unknown_link_blocks(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "candidate_inventory_ready")
        path = root / "_story_context/candidates/pilot.json"
        candidate = json.loads(path.read_text(encoding="utf-8"))
        candidate["candidate_links"].append(
            {
                "quest_id": "999",
                "scene_family_id": "100_1",
                "reasons": ["same_numeric_root"],
                "candidate_only": True,
                "order_inference_allowed": False,
            }
        )
        candidate["summary"]["candidate_link_count"] += 1
        write(path, candidate)
        with self.assertRaisesRegex(C.StoryContextError, "unknown group"):
            C.validate_root(root)

    def test_unknown_key(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "event_manifest_ready")
        path = root / "_story_context/manifests/pilot.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["scenes"][0]["source_keys"] = ["missing"]
        write(path, manifest)
        with self.assertRaisesRegex(C.StoryContextError, "unknown source key"):
            C.validate_root(root)

    def test_scene_spoiler(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "scene_context_ready")
        path = root / "_story_context/scene_context/pilot.json"
        scene = json.loads(path.read_text(encoding="utf-8"))
        scene["scenes"][0]["future_truth"] = "succeeds"
        write(path, scene)
        with self.assertRaisesRegex(C.StoryContextError, "spoiler field"):
            C.validate_root(root)

    def test_reference_ready(self):
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.stage(root, "reference_ready")
        result = C.validate_root(root)
        self.assertTrue(result["formal_reference"])
        self.assertEqual(result["active_event"], "pilot_event")


if __name__ == "__main__":
    unittest.main()
