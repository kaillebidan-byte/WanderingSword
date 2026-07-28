# 新チャット再開プロトコル

再開経路と制度作業優先順位は`INSTITUTION_WORK_QUEUE.json`、現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、waveとcycle状態は`PRIVATE_STAGE_STATE.json`を正本とする。対象repositoryは`PROJECT_SCOPE_LOCK.json`、工場フローは`FACTORY_FLOW_CONTRACT.json`、実行modeは`EXECUTION_MODES.json`、終端契約は`PHASE_COMPLETION_SIGNAL.json`、動的認可は`REGULATED_PHASE_STATE.json`を正本とする。

## 起動文

```text
現状把握して作業の続きを
```

`作業の続きを`など同じ意図の表現も再開指示として扱う。URLや前回作業を聞き直さず、規定URL、制度キュー、機械状態正本、GitHub metadataから復元する。状況報告だけで終了せず、再開controllerが指定する正常完了地点まで同じ応答内で実作業を進める。

## 冷間再開の事実確認

1. `kaillebidan-byte/WanderingSword`の実visibilityをrepository metadataから取得する。
2. main、未統合PR、GitHub Actionsを取得する。
3. 未統合PRはactive / superseded / abandoned / unrelatedへ分類する。開いているだけで現行作業と決めない。
4. botの`action_required`は検査失敗と決めつけず、該当job、release evidence、verified checkpoint、review threadを確認する。
5. squash merge後は、制度PRなら制度キューのcompletionとmain実装を再確認する。翻訳PRならmerge後reconcilerを実行し、post-merge状態PRは作らない。

## repository lock

通常作業対象は常に`kaillebidan-byte/WanderingSword`である。scope確定前に別repositoryを探索・変更しない。

```bash
python _tools/check_project_scope_lock.py --repository kaillebidan-byte/WanderingSword
```

## 唯一の再開入口

repository metadata、制度キュー、四状態正本を取得した後、次でwork orderを得る。

```bash
python _tools/resume_work_controller.py --repository-visibility <private|public>
```

`always_public_full_pipeline`で`INSTITUTION_WORK_QUEUE.json`にpending taskがある場合、controllerは`institution_repair`を返す。翻訳cycle、次候補preparation、owner、locres、pakには進まない。現在タスクを実装・回帰・CI・squash merge・main再検証まで終え、同じ制度PRでtaskを`completed`へ更新する。

pending taskがない場合だけ、controllerは`translation_factory_controller.py`へ委譲する。委譲後は一つのaction以外へ進まず、別API、別workflow、別trigger、同一失敗引数の再試行を考案しない。

制度キューのtask orderは引継ぎ文より優先する。新規チャットで別の制度用起動文、長文貼付け、手作業の次タスク選択を要求しない。

翻訳における人間判断stationは次の二つだけ。

- `semantic_bundle_boundary`: 意味単位の束境界と40〜80行の閉じ方
- `translation_quality_audit`: KEEP/FIX、修正訳、人物性・事実・典故の監査

branch、PR、workflow、artifact、owner、状態正本、encoding、locres、pak、CI、phase2、merge、reconcileは機械工程である。制度改修はqueue taskのaudit scopeとcompletion contractに従う。

## 恒久factory adapter

- 新cycle初期化: `translation-factory-execute.yml` → `factory_request_executor.py` → `fixed_cycle_initializer.py`
- 記録済み監査の収録: `translation-factory-encode.yml` → `factory_encoding_executor.py` → `fixed_encoding_pipeline.py`
- release最終化: `translation-factory-finalize.yml` → `fixed_release_finalizer.py`
- merge後確定: `reconcile_merged_cycle.py`

恒久adapterがなければ`factory_adapter_missing`で安全停止する。安全停止は作業終了ではなく、失敗stepと再開地点を保持した搬送停止である。手動状態編集、一時workflow、trigger実験は禁止する。

## modeと標準完了地点

新cycle開始時だけ、repository visibilityからexecution modeを選び二状態正本へlockする。active cycle中は変更しない。

- `manual_visibility_cycle`: private準備から`ready_for_public_ci`、public CIから`awaiting_private_merge`、private復帰後にmergeとreconcile。
- `always_public_full_pipeline`: 同じstage machineをpublicのまま`merged`まで進める。

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointであり、追加指示を求める正常停止地点ではない。

## 段階権限

- preparationでは翻訳判断、fix、owner、正式束を書かない。
- quality auditでは翻訳判断だけを行う。
- encodingでは記録済み判断だけを収録する。
- translation freeze後は翻訳判断、fix追加、owner変更、次wave準備を行わない。
- release finalizationはorchestrator artifactからrelease evidenceとverified checkpointを生成する。
- phase2成功・未解決review thread 0件の前にmergeしない。
- ゲームフォルダへ配置しない。

## 整合検査

```bash
python _tools/resume_work_controller.py --repository-visibility <private|public> --validate-contract-only
python _tools/check_factory_adapters.py
python _tools/check_operational_docs_consistency.py
```

handoff、制度キュー、next reservation、mode別文書、release evidence、恒久adapter接続が機械正本と一致しなければ次工程へ進まない。

## 規定フェイズ終端

終端予約語は`REGULATED_PHASE_STATE.json.signal_authorization`がliveに認可した場合だけconsumerへ渡す。単一wave、単一train、単一PR、CI、pak生成、visibility境界、paused状態では認可を発行しない。認可がない固定文字列を応答、引用、説明、例示へ出さない。

## 例外停止

途中停止は`cycle_control.status=paused`とし、`user_decision_required`、`checker_failure`、`external_dependency_unavailable`、`turn_capacity_checkpoint`だけを許す。`continuation_required=true`、理由、機械実行可能な`exact_next_action`を残す。
