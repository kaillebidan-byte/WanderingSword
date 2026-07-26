# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の「作業を続けて」「再開して」も対象とする。

## 最初の無言ゲート

1. 最初の外部確認としてGitHub repository metadataを取得する。
2. metadata結果前に、利用者向けの計画、開始宣言、途中報告を出さない。
3. 利用者のvisibility申告を実状態の正本として扱わない。
4. metadata取得後、実visibilityと有効operation modeを確定してから最初の報告または作業へ進む。
5. metadata取得失敗時は、作業開始を主張しない。

## 合格条件

1. `VISIBILITY_PREFLIGHT_CONTRACT.json`が機械検査を通る。
2. main、未統合PR、GitHub Actionsを確認し、開いているだけで現行作業と決めない。
3. active branchとopen PRをCURRENT_WORK・manifest・GitHub実体から復元する。
4. verified checkpointをCURRENT_WORK.checkpointとrelease evidenceから復元する。
5. active trainの状態・集計・review済み束をCI_TRAIN_MANIFESTから復元する。
6. NEXT_TASK_PACKETから次に許可された作業を復元する。
7. schema v6 minimal reservationではowner・人物声・batch planningが未記載であることを正常と判定する。
8. activeな制度PRがある場合、予約済み次候補の翻訳作業より優先する。
9. visibility、declared state、manifest status、`PRIVATE_STAGE_STATE.cycle_control`の組合せから裁定する。
10. private_translation_work + privateなら、状態報告だけで止まらず同じ応答内で許可されたprivate作業へ進む。
11. privateの正常実行は、preparation・quality audit・encodingの段階境界で止まらず、private preflight成功、PR ready、`ready_for_public_ci`まで進む。
12. public + translation_frozenなら、新規翻訳をせずorchestrator、状態最終化、phase2、review thread 0件、`awaiting_private_merge`まで進む。
13. private復帰後は検証済みHEADをsquash統合して`merged`へ進め、統合前に次waveを開始しない。
14. private_translation_work + publicなら、翻訳を開始せずprivate復帰を依頼する。
15. `cycle_control.status=paused`は許可理由とexact next actionを必須とする。
16. `cycle_control.status=target_reached`は`ready_for_public_ci`、`awaiting_private_merge`、`merged`だけを許す。
17. 正常cycleでは追加の「作業の続きを」を要求しない。
18. verified checkpointと未適用小束を混同しない。
19. `fix_keys=0`のkeep-only束は`fix_files=[]`を正規状態として扱い、架空の修正JSONを要求しない。
20. accumulating中だけCURRENT_WORK.immediate_nextとNEXT_TASK_PACKET.scene_groupsの一致を要求する。
21. ready/in_public_ci/verifiedではCURRENT_WORKはrelease作業、NEXT_TASK_PACKETはrelease後の次束を指し得るため、両者を混同しない。
22. 小束ではlocresとpakを更新せず、release時だけ適用する。
23. 新規candidateは全`fixes_*.json`実測のownership snapshotを持つ。
24. encoding後にowner snapshotを再生成する。
25. `release-ci`または`ci-heavy-rerun`は`Release train orchestrator`一runだけを起動する。
26. orchestrator内でpreflight→Relation/Cross→Applyの依存順が保証される。
27. Apply前は軽量輸送検査だけを行い、release evidence・verified checkpointの厳密一致はphase2へ分離する。
28. release evidence schema v2でorchestrator runと内部job成功を記録する。既存schema v1は維持する。
29. phase2は`finalize-release`で明示起動する。
30. PR作成、ready化、通常commit、bot書き戻しではorchestratorを自動起動しない。
31. post-merge状態専用PRを作らない。

## 動的期待値

固定のbatch番号、件数、Issue番号、branch名をこの文書へ複製しない。各値は次の正本から毎回取得する。

- 実visibility: GitHub repository metadata
- declared state、checkpoint、active train、active branch: `CURRENT_WORK.json`
- 列車集計、review済み束、release readiness: `CI_TRAIN_MANIFEST.json`
- private wave、owner snapshot policy、cycle completion: `PRIVATE_STAGE_STATE.json`
- cycle仕様: `AUTONOMOUS_VISIBILITY_CYCLE.md`
- 次作業と予約状態: `NEXT_TASK_PACKET.json`
- active PR / Actions: GitHub実体
- 確定release: checkpointが指す`RELEASE_EVIDENCE_*.json`

この文書の固定値が現在地を上書きしてはならない。

## 機械検査

private公開前:

```bash
python _tools/check_private_release_preflight.py --with-tests
```

個別検査:

```bash
python _tools/check_visibility_preflight_contract.py
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_candidate_ownership.py --require-current-wave
python _tools/check_private_translation_stage.py
python _tools/check_autonomous_cycle.py
python _tools/check_release_transport_state.py
python _tools/check_release_evidence.py --verify-git-lineage
python _tools/check_handoff_consistency_v2.py --require-verified
python _tools/check_ci_train_manifest_v2.py
python _tools/check_next_task_packet.py
python _tools/check_batch_planning.py
python _tools/test_check_candidate_ownership.py
python _tools/test_check_next_task_packet_minimal.py
python _tools/test_check_release_transport_state.py
python _tools/test_check_autonomous_cycle.py
python _tools/test_write_applied_record.py
python _tools/test_release_ci_triggers.py
python _tools/test_check_visibility_preflight_contract.py
python _tools/test_check_operation_mode.py
python _tools/test_check_release_evidence.py
python _tools/test_check_release_evidence_github.py
python _tools/test_check_handoff_consistency_v2.py
python _tools/test_check_ci_train_manifest.py
python _tools/test_check_next_task_packet_ownership.py
python _tools/test_check_batch_planning.py
python _tools/test_check_ci_train_state_v2.py
```

すべてが成功しない状態を確定状態として扱わない。
