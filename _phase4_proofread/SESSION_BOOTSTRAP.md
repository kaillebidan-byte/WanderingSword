# 新チャット再開プロトコル

再開経路と制度作業優先順位は`INSTITUTION_WORK_QUEUE.json`、現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、waveとcycle状態は`PRIVATE_STAGE_STATE.json`を正本とする。対象repositoryは`PROJECT_SCOPE_LOCK.json`、工場フローは`FACTORY_FLOW_CONTRACT.json`、quality auditの資料還流は`QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json`、実行modeは`EXECUTION_MODES.json`、通常応答と規定終端応答の分離は`FINAL_RESPONSE_POLICY.json`をroutine正本とする。

生の終端契約とlive認可stateはvalidator・controller専用であり、通常cycleの読書対象にしない。`CURRENT_WORK.mandatory_read_order`に古いentryが残っていても、`FINAL_RESPONSE_POLICY.json`を優先し、`sanitize_final_response_read_order.py`で補正する。

## 起動文

```text
現状把握して作業の続きを
```

`作業の続きを`など同じ意図の表現も再開指示として扱う。URLや前回作業を聞き直さず、規定URL、制度キュー、機械状態正本、GitHub metadataから復元する。状況報告だけで終了せず、再開entrypointが指定する正常完了地点まで同じ応答内で実作業を進める。

## 冷間再開の事実確認

1. `kaillebidan-byte/WanderingSword`の実visibilityをrepository metadataから取得する。
2. main、未統合PR、GitHub Actionsを取得する。
3. 未統合PRはactive / superseded / abandoned / unrelatedへ分類する。開いているだけで現行作業と決めない。
4. botの`action_required`は検査失敗と決めつけず、該当job、release evidence、verified checkpoint、review threadを確認する。
5. squash merge後は、制度PRなら制度キューのcompletion、GitHub metadataのmerge SHA、main実装を再確認する。翻訳PRならmerge後reconcilerを実行し、post-merge状態PRは作らない。

## repository lock

通常作業対象は常に`kaillebidan-byte/WanderingSword`である。scope確定前に別repositoryを探索・変更しない。

```bash
python _tools/check_project_scope_lock.py --repository kaillebidan-byte/WanderingSword
```

## 唯一の再開入口

repository metadata、制度キュー、四状態正本を取得した後、次でwork orderと最終応答modeを同時に得る。

```bash
python _tools/resume_work_entrypoint.py --repository-visibility <private|public>
```

旧`resume_work_controller.py`は内部controllerであり、新チャットから直接呼ばない。entrypointの`final_response_gate`はwork orderと同じ強制力を持つ。

`always_public_full_pipeline`で`INSTITUTION_WORK_QUEUE.json`にpending taskがある場合、controllerは`institution_repair`を返す。翻訳cycle、次候補preparation、owner、locres、pakには進まない。PR作成後、同じ制度PRでtaskを`completed`へ更新しPR番号を記録する。squash merge SHAは統合前に確定しないため事前記録を要求せず、統合後にGitHub metadataで検証する。実装・回帰・CI・squash merge・main再検証まで終える。

pending taskがない場合だけ、controllerは`translation_factory_controller.py`へ委譲する。委譲後は一つのaction以外へ進まず、別API、別workflow、別trigger、同一失敗引数の再試行を考案しない。

制度キューのtask orderは引継ぎ文より優先する。新規チャットで別の制度用起動文、長文貼付け、手作業の次タスク選択を要求しない。

翻訳における人間判断stationは次の二つだけ。

- `semantic_bundle_boundary`: 意味単位の束境界と40〜80行の閉じ方
- `translation_quality_audit`: KEEP/FIX、修正訳、人物性・事実・典故、既存ペルソナの維持・修正・追加・保留

branch、PR、workflow、artifact、owner、状態正本、encoding、人物資料への決定的書込み、locres、pak、CI、phase2、merge、reconcileは機械工程である。制度改修はqueue taskのaudit scopeとcompletion contractに従う。

## quality auditの読書と資料還流

`translation_quality_audit`では、candidateの原文・現訳・前後文・話者・時系列だけで典故疑義と設定事実疑義を先に立てる。その後に`quality_audit_context.required_documents`のskill、RUNBOOK、人物資料を照合する。

監査記録には次を必須とする。

- `reading_attestation`
- candidate全行の`fixes` / `keeps`
- `allusion_review_resolved`
- `fact_doubts`
- 全`source_document_targets`を被覆する`source_document_decisions`

人物資料は固定正解ではない。一次資料と衝突した場合は、訳文を資料へ押し込まず、対象path、根拠key、適用scope、`keep/revise/create/unresolved`を記録する。high confidence、digest一致、一意anchorを満たす`revise/create`だけを機械適用する。証拠不足は`unresolved`とし、人物資料を書き換えない。

## 恒久factory adapter

- 新cycle初期化: `translation-factory-execute.yml` → `factory_request_executor.py` → `fixed_cycle_initializer.py` → `quality_audit_context.py`
- 読書・人物資料判断の検査: `check_quality_audit_source_feedback.py`
- 人物資料の決定的還流: `source_document_feedback.py`
- 記録済み監査の収録: `translation-factory-encode.yml` → `factory_encoding_executor.py` → `fixed_encoding_pipeline.py`
- release最終化: `translation-factory-finalize.yml` → `fixed_release_finalizer.py`
- merge後確定: `reconcile_merged_cycle.py` → `sanitize_final_response_read_order.py`
- 最終応答mode: `resume_work_entrypoint.py` → `final_response_policy.py`
- 規定終端suffix: `render_phase_completion_suffix.py`のみ

恒久adapterがなければ安全停止する。安全停止は作業終了ではなく、失敗stepと再開地点を保持した搬送停止である。手動状態編集、一時workflow、trigger実験は禁止する。

## modeと標準完了地点

新cycle開始時だけ、repository visibilityからexecution modeを選び二状態正本へlockする。active cycle中は変更しない。

- `manual_visibility_cycle`: private準備から`ready_for_public_ci`、public CIから`awaiting_private_merge`、private復帰後にmergeとreconcile。
- `always_public_full_pipeline`: 同じstage machineをpublicのまま`merged`まで進める。

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointであり、追加指示を求める正常停止地点ではない。

## 段階権限

- preparationでは翻訳判断、人物資料判断、fix、owner、正式束を書かない。読書manifestと人物資料targetを生成する。
- quality auditでは翻訳判断と人物資料判断だけを行い、人物資料を直接書かない。
- encodingでは記録済み翻訳判断と人物資料判断だけを収録する。
- translation freeze後は翻訳判断、人物資料判断、fix追加、owner変更、次wave準備を行わない。
- release finalizationはorchestrator artifactからrelease evidenceとverified checkpointを生成する。
- phase2成功・未解決review thread 0件の前にmergeしない。
- ゲームフォルダへ配置しない。

## 最終応答ゲート

`final_response_gate.mode=normal_response`では、`safe_completion_label`を用いて通常作業の完了を報告する。予約token、認可ID、result行を本文・引用・説明・例示へ出さない。terminal rendererは実行禁止。

`final_response_gate.mode=authorized_terminal`の場合だけ、次を実行し、生成されたsuffixを改変せず末尾へ付ける。モデルがsuffixを手入力・復元・推測してはならない。

```bash
python _tools/render_phase_completion_suffix.py --output <terminal-suffix.txt>
```

通常応答も含め、送信前draftはUTF-8ファイルへ保存して検査する。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

checkerまたはrendererが失敗した応答は送信しない。train、wave、PR、release phase2、transport merge、cycle target到達はauthorized terminalへ昇格しない。

## 整合検査

```bash
python _tools/resume_work_entrypoint.py --repository-visibility <private|public> --validate-contract-only
python _tools/sanitize_final_response_read_order.py
python _tools/check_factory_adapters.py
python _tools/check_quality_audit_source_feedback.py --audit <AUDIT_DECISIONS_*.json>
python _tools/check_operational_docs_consistency.py
```

handoff、制度キュー、next reservation、mode別文書、release evidence、読書manifest、人物資料還流、最終応答gate、恒久adapter接続が機械正本と一致しなければ次工程へ進まない。

## 例外停止

途中停止は`cycle_control.status=paused`とし、`user_decision_required`、`checker_failure`、`external_dependency_unavailable`、`turn_capacity_checkpoint`だけを許す。`continuation_required=true`、理由、機械実行可能な`exact_next_action`を残す。
