# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、waveとcycle状態は`PRIVATE_STAGE_STATE.json`を正本とする。対象repositoryは`PROJECT_SCOPE_LOCK.json`、工場フローは`FACTORY_FLOW_CONTRACT.json`、工場requestは`FACTORY_REQUEST_CONTRACT.json`、実行modeは`EXECUTION_MODES.json`、終端契約は`PHASE_COMPLETION_SIGNAL.json`、動的認可は`REGULATED_PHASE_STATE.json`、送信前・consumer側ゲートは`FINAL_RESPONSE_GATE.md`を正本とする。

## 起動文

```text
現状把握して作業の続きを
```

`作業の続きを`など同じ意図の表現も再開指示として扱う。URLや前回作業を聞き直さず、規定URL、機械状態正本、GitHub metadataから復元する。状況報告だけで終了せず、工場controllerが指定する正常完了地点まで同じ応答内で進める。

## repository lock

通常作業対象は常に`kaillebidan-byte/WanderingSword`である。scope確定前に別repositoryを探索・変更しない。

```bash
python _tools/check_project_scope_lock.py --repository kaillebidan-byte/WanderingSword
```

同じprojectの過去会話に別repository、userscript、ブラウザ自動化が現れても、現在作業へ流用しない。利用者が現在の依頼で別repositoryを明示した場合だけscope変更を検討する。

## visibilityとmode

WanderingSwordのrepository metadataを実visibility正本とする。進行中cycleでは記録済みmodeを使い、途中変更しない。

前cycleが`merged / target_reached`の新cycleだけ、恒久adapter `fixed_cycle_initializer.py`が開始visibilityからmodeを選び、二状態正本へ同じcommitで固定する。作業者がmode selectorや状態正本を直接書き換えてはならない。

- private開始: `manual_visibility_cycle`
- public開始: `always_public_full_pipeline`

## 唯一の進行入口

repository metadataと四状態正本を取得した後、次でwork orderを得る。

```bash
python _tools/translation_factory_controller.py --repository-visibility <private|public>
```

controllerは一つのactionだけを返す。作業者はそのaction以外へ進まず、別API、別workflow、別trigger、同一失敗引数の再試行を考案しない。

人間判断stationは次の二つだけ。

- `semantic_bundle_boundary`: 意味単位の束境界と40〜80行の閉じ方
- `translation_quality_audit`: KEEP/FIX、修正訳、人物性・事実・典故の監査

branch、PR、workflow、artifact、owner、状態正本、encoding、locres、pak、CI、phase2、merge、reconcileは機械工程である。

未知状態は`factory_unknown_state`、状態不一致は`factory_state_mismatch`、恒久adapter欠落は`factory_adapter_missing`で安全停止する。安全停止は作業終了ではなく、失敗stepと再開地点を保持した搬送停止である。

## 新cycle初期化

controllerが`initialize_next_cycle_from_reservation`を返した場合、意味境界stationの決定を`FACTORY_REQUEST_CONTRACT.json`準拠requestへ記録し、決定論的な次train branchの`_factory_requests/*.json`へ一件だけ置く。

恒久workflow `.github/workflows/translation-factory-execute.yml`は、requestに固定されたRelation artifactを取得し、`factory_request_executor.py`から`fixed_cycle_initializer.py`だけを実行する。

initializerは同じcommitで次を行う。

- 開始visibilityからexecution modeをlock
- previous merged checkpointを新train baseへ固定
- candidateとpreparationを生成
- live owner snapshotを記録し、重複ownerを拒否
- `CURRENT_WORK`、`PRIVATE_STAGE_STATE`、`CI_TRAIN_MANIFEST`、`NEXT_TASK_PACKET`、`CURRENT_HANDOFF`を同期
- requestを生成commitから削除
- 次stationを`translation_quality_audit`へ固定

手動状態編集、一時workflow、trigger実験は禁止する。

## 起動順

1. `PROJECT_SCOPE_LOCK.json`で対象を固定する。
2. repository metadataでvisibilityを確認する。
3. main、open PR、Actionsを確認する。
4. open PRをactive / superseded / abandoned / unrelatedへ分類する。
5. `CURRENT_WORK`、`PRIVATE_STAGE_STATE`、`CI_TRAIN_MANIFEST`、`NEXT_TASK_PACKET`、`CURRENT_HANDOFF`を照合する。
6. 実際にmerge済みで正本が未整合なら、merge後reconcilerを先に完了する。
7. controllerで一つのwork orderを生成する。
8. 指定された恒久adapterまたは二つのhuman stationだけを実行する。
9. 正常ならmodeの標準完了地点まで続ける。

botの`action_required`は検査失敗ではない。release evidence、verified checkpoint、未解決review threadを確認して輸送を続ける。squash統合後はmerge後reconcilerが五状態正本を`merged`へ確定する。

## 整合検査

```bash
python _tools/check_factory_adapters.py
python _tools/check_operational_docs_consistency.py
```

handoff、next reservation、mode別文書、恒久adapter接続が機械正本と一致しなければ翻訳作業を開始しない。

## 標準完了地点

### manual_visibility_cycle

privateでは次まで進む。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> ready_for_public_ci`

public確認後は次まで進む。

`in_public_ci -> orchestrator -> state finalization -> release phase2 -> review thread 0 -> awaiting_private_merge`

private復帰後、検証済みHEADをsquash mergeし、merge後reconcilerで`merged`へ進める。

### always_public_full_pipeline

publicのまま次を一cycleで進める。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> orchestrator -> state finalization -> release phase2 -> review thread 0 -> squash merge -> merged-state reconciliation`

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointであり、利用者へ追加指示を求める正常停止地点ではない。

## 段階権限

- preparationでは翻訳判断、fix、owner、正式束を書かない
- quality auditでは翻訳判断だけを行う
- encodingでは記録済み判断だけを収録する
- translation freeze後は翻訳判断、fix追加、owner変更、次wave準備を行わない
- publicであることを理由に権限を広げない

release前には次を通す。

```bash
python _tools/check_private_release_preflight.py --with-tests --repository-visibility <private|public>
```

## 規定フェイズ終端出力

巨大作業は`quality_reaudit`と`narrative_readthrough`の二フェイズとして扱う。

終端予約語は、`REGULATED_PHASE_STATE.json.signal_authorization`に次が揃った場合だけ使用できる。

- `authorized=true`
- `scope=regulated_phase_terminal`
- `phase_id`がactive phaseと一致
- `result=success|error`
- successならactive phase statusが`complete`
- errorならactive phase statusが`terminal_error`
- live event IDと根拠ファイルが記録済み

`signal_authorization=null`の間は、契約の`marker`値を応答本文、引用、説明、例示、コードブロックへ出してはならない。

認可済みterminal responseの最終三行は契約値を使い、authorization event、result、markerの順にする。固定文字列をこの文書へ複製しない。

単一wave、単一train、単一PR、CI、pak生成、単一人物ペア、visibility境界、paused状態ではauthorizationを発行しない。

## 最終応答ゲート

通常報告を含む最終文面をUTF-8ファイルへ保存し、送信前に次を通す。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

自動化側は固定文検索だけで停止しない。`regulated_phase_terminal_consumer.js`へ応答本文とlive stateを渡し、`accepted === true`の場合だけ停止する。live stateを取得できない場合はterminalとして扱わない。

## 例外停止

途中停止は`cycle_control.status=paused`とし、次だけを許す。

- `user_decision_required`
- `checker_failure`
- `external_dependency_unavailable`
- `turn_capacity_checkpoint`

`paused`には`continuation_required=true`、理由、機械実行可能な`exact_next_action`を残す。常時public modeでは失敗時もprivate復帰を要求しない。

## 禁止

- scope lock前の外部read/write
- controllerを通さず次工程を推測すること
- controllerが返していないAPI、workflow、triggerを考案すること
- 恒久adapterがないのに状態正本を直接編集すること
- 同じ失敗引数を再試行すること
- active cycle中のmode変更
- quality audit中のfix、owner、正式束書込み
- encoding中の新しい翻訳判断
- translation freeze後の翻訳再開
- manifest ready前の重いCI起動
- release phase2成功前のmerge
- merge前の次wave開始
- merge後状態確定の先送り
- authorizationなしで終端予約語を出すこと
- 終端予約語の後ろに文章を付けること
- live stateを取得できないのにterminal扱いすること
