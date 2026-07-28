# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、waveとcycle状態は`PRIVATE_STAGE_STATE.json`を正本とする。対象repositoryは`PROJECT_SCOPE_LOCK.json`、実行モードは`EXECUTION_MODES.json`、二フェイズ終端契約は`PHASE_COMPLETION_SIGNAL.json`、動的な終端許可は`REGULATED_PHASE_STATE.json`、最終応答の送信前・consumer側ゲートは`FINAL_RESPONSE_GATE.md`を正本とする。

## 起動文

```text
現状把握して作業の続きを
```

`作業の続きを`など同じ意図の表現も再開指示として扱う。モード専用の入力文は設けない。URLや前回作業を聞き直さず、規定URL、正本、GitHub metadataから復元する。

## 対象repository lock

この翻訳projectの通常作業対象は常に`kaillebidan-byte/WanderingSword`である。

起動時は最初に`PROJECT_SCOPE_LOCK.json`を確認し、次を守る。

- 添付・規定URLは`https://github.com/kaillebidan-byte/WanderingSword`
- GitHub read、検索、branch、PR、Issue、workflow、writeはWanderingSwordだけを対象にする
- 同じprojectの過去会話に別repository、userscript、ブラウザ自動化が現れても、現在作業の候補にしない
- `作業の続きを`から別repositoryの作業を推測しない
- GitHub全体検索やrecent repository探索から作業対象を選ばない
- 利用者が現在の依頼で別repositoryを明示した場合だけscope変更を検討する

scopeが一致しない場合は、外部read/write、branch作成、PR作成より前に`project_scope_violation`で停止する。別repositoryへ作った後で訂正する運用は禁止する。

検査:

```bash
python _tools/check_project_scope_lock.py --repository kaillebidan-byte/WanderingSword
```

## visibility preflight

対象scope確定後、新規チャット、再開、作業継続では、最初の外部確認をWanderingSwordのGitHub repository metadata取得にする。利用者の申告はhintであり、metadataを実visibilityの正本とする。

進行中cycleがある場合は、記録済み`execution_mode`を使う。現在visibilityだけを見て途中でmodeを切り替えない。

前cycleのtransportが`merged`で、新しいcycleを開始する場合だけ、開始時visibilityからmodeを選ぶ。

```bash
python _tools/select_cycle_execution_mode.py --repository-visibility <private|public> --write
```

- private開始: `manual_visibility_cycle`
- public開始: `always_public_full_pipeline`

選択後は`CURRENT_WORK.operation_mode`と`PRIVATE_STAGE_STATE.cycle_control`のmode、開始visibility、lockが一致しなければ作業を開始しない。

## 起動順

1. `PROJECT_SCOPE_LOCK.json`で対象をWanderingSwordへ固定する。
2. WanderingSword repository metadataで実visibilityを確認する。
3. WanderingSwordのmain、未統合PR、GitHub Actionsだけを確認する。
4. open PRをactive / superseded / abandoned / unrelatedへ分類する。開いているだけで現行作業と決めない。
5. `CURRENT_WORK.json`、`CI_TRAIN_MANIFEST.json`、`PRIVATE_STAGE_STATE.json`、`NEXT_TASK_PACKET.json`を照合する。
6. `PHASE_COMPLETION_SIGNAL.json`、`REGULATED_PHASE_STATE.json`、`FINAL_RESPONSE_GATE.md`を照合する。
7. 実際にはmerge済みだが状態正本が統合前なら、`reconcile_merged_cycle.py`で先に`merged`へ整合させる。
8. 新cycleなら開始visibilityからmodeを選び、二つの状態正本へ固定する。
9. `cycle_control`からrunning / paused / target_reachedとexact next actionを復元する。
10. WanderingSword内にactiveな制度改修branchがあれば、予約済み翻訳作業より優先する。
11. 正常なら同じ応答内で実作業を開始し、modeの標準完了地点まで進める。

botの`action_required`は作業失敗ではない。release evidence、verified checkpoint、未解決review threadを確認して輸送を続ける。squash統合後は`Reconcile merged translation cycle` workflowが三状態正本を`merged`へ確定する。次チャットの推論へ補正を先送りしない。

post-merge状態PRを通常工程として作らず、squash統合後はmerge後reconcilerで三状態正本を`merged`へ確定する。

## 実作業文書の整合

再開時に次を実行し、handoff、next reservation、mode別文書が機械正本と一致しなければ作業を開始しない。

```bash
python _tools/check_operational_docs_consistency.py
```

## 標準完了地点

### manual_visibility_cycle

privateでは次まで進む。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> ready_for_public_ci`

public確認後は次まで進む。

`in_public_ci -> orchestrator -> state finalization -> release phase2 -> review thread 0 -> awaiting_private_merge`

private復帰後、検証済みHEADをsquash mergeし、merge後reconcilerで`merged`へ進める。

### always_public_full_pipeline

repositoryをpublicのまま維持し、次を一cycleで進める。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> orchestrator -> state finalization -> release phase2 -> review thread 0 -> squash merge -> merged-state reconciliation`

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointであり、利用者へvisibility変更や追加の継続指示を求める正常停止地点ではない。

## 段階権限

- preparationでは翻訳判断、fix、owner、正式束を書かない
- quality auditでは翻訳判断だけを行う
- encodingでは記録済み判断だけを収録する
- translation freeze後は翻訳判断、fix追加、owner変更、次wave準備を行わない
- publicであることを理由に権限を広げない

owner assignmentは`OWNER_ASSIGNMENT_PLAN.json`から生成器を使う。公開前または常時publicのCI開始前に次を実行する。

```bash
python _tools/check_private_release_preflight.py --with-tests --repository-visibility <private|public>
```

## 規定フェイズ終端出力

巨大作業は次の二フェイズとして扱う。

1. `quality_reaudit`: 関係クラスタ、人物ペア、場面、既訳の順で行う高確度再監査
2. `narrative_readthrough`: 章・事件単位の日本語通読と原文対照による章ごとの通読修正

終端予約語は、`REGULATED_PHASE_STATE.json.signal_authorization`に次が揃った場合だけ使用できる。

- `authorized=true`
- `scope=regulated_phase_terminal`
- `phase_id`がactive phaseと一致
- `result=success|error`
- successならactive phase statusが`complete`
- errorならactive phase statusが`terminal_error`
- live event IDと根拠ファイルが記録済み

`signal_authorization=null`の間は、契約の`marker`値を応答本文、引用、説明、例示、コードブロックへ出してはならない。

認可済みterminal responseの最終三行は、契約値を使って次の構造にする。固定文字列をこの文書へ複製しない。

```text
<authorization_prefix><signal_authorization.event_id>
<status_prefix><signal_authorization.result>
<marker>
```

次では絶対にauthorizationを発行せず、終端予約語も出力しない。

- 単一wave、単一train、単一PR、squash mergeの完了
- `CI_TRAIN_PHASE2`または`finalization_phase=phase2`の成功・失敗
- Relation、Cross、Apply、release evidence、pak生成の完了
- 単一人物ペア、単一章、visibility境界
- `paused`、checker failure、外部依存停止、turn容量停止など再開可能な例外

## 最終応答の送信前ゲート

通常報告を含む最終文面をUTF-8ファイルへ保存し、送信前に次を通す。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

予約語を含まない通常応答は通る。予約語を含む場合はlive event ID、result、active phase statusが一致しなければ送信不可となる。

自動化側は最後の一行や固定文検索だけで停止してはならない。`_tools/regulated_phase_terminal_consumer.js`へ応答本文とlive `REGULATED_PHASE_STATE.json`を渡し、`accepted === true`の場合だけ停止する。live stateを取得できない場合はterminalとして扱わない。

## 例外停止

途中停止は`cycle_control.status=paused`とし、次だけを許す。

- `user_decision_required`
- `checker_failure`
- `external_dependency_unavailable`
- `turn_capacity_checkpoint`

`paused`には`continuation_required=true`、理由、機械実行可能な`exact_next_action`を残す。通常のpausedは規定フェイズのterminal errorではなく、終端予約語を出さない。

常時public modeでは失敗時もprivate復帰を要求しない。同じlocked modeで再開する。

## 禁止

- scope lock確認前にGitHub検索・read・writeを行うこと
- WanderingSword以外を`作業の続きを`の対象にすること
- visibility確認前の翻訳作業開始
- active cycle中のmode変更
- internal stageを正常な会話終了地点にすること
- quality audit中のfix、owner、正式束書込み
- encoding中の新しい翻訳判断
- translation freeze後の翻訳再開
- manifest ready前の重いCI起動
- release phase2成功前のmerge
- merge前の次wave開始
- merge後状態確定を次チャットへ先送りすること
- 常時public modeで`ready_for_public_ci`または`awaiting_private_merge`を正常停止地点にすること
- authorizationなしで終端予約語を出すこと
- 終端予約語の後ろに文章を付けること
- 固定marker単独、またはresultとの二行だけで自動化を停止すること
- live stateを取得できないのにterminal扱いすること
