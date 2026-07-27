# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、waveとcycle状態は`PRIVATE_STAGE_STATE.json`を正本とする。実行モードは`EXECUTION_MODES.json`を正本とする。

## 起動文

```text
現状把握して作業の続きを
```

`作業の続きを`など同じ意図の表現も再開指示として扱う。モード専用の入力文は設けない。URLや前回作業を聞き直さない。

## visibility preflight

新規チャット、再開、作業継続では、最初の外部確認をGitHub repository metadata取得にする。利用者の申告はhintであり、metadataを実visibilityの正本とする。

進行中cycleがある場合は、記録済み`execution_mode`を使う。現在visibilityだけを見て途中でmodeを切り替えない。

前cycleのtransportが`merged`で、新しいcycleを開始する場合だけ、開始時visibilityからmodeを選ぶ。

```bash
python _tools/select_cycle_execution_mode.py --repository-visibility <private|public> --write
```

- private開始: `manual_visibility_cycle`
- public開始: `always_public_full_pipeline`

選択後は`CURRENT_WORK.operation_mode`と`PRIVATE_STAGE_STATE.cycle_control`のmode、開始visibility、lockが一致しなければ作業を開始しない。

## 起動順

1. repository metadataで実visibilityを確認する。
2. main、未統合PR、GitHub Actionsを確認する。
3. open PRをactive / superseded / abandoned / unrelatedへ分類する。
4. `CURRENT_WORK.json`、`CI_TRAIN_MANIFEST.json`、`PRIVATE_STAGE_STATE.json`、`NEXT_TASK_PACKET.json`を照合する。
5. 実際にはmerge済みだが状態正本が統合前なら、先に`merged`へ整合させる。
6. 新cycleなら開始visibilityからmodeを選び、二つの状態正本へ固定する。
7. `cycle_control`からrunning / paused / target_reachedとexact next actionを復元する。
8. activeな制度改修branchがあれば、予約済み翻訳作業より優先する。
9. 正常なら同じ応答内でmodeの標準完了地点まで進める。

## 標準完了地点

### manual_visibility_cycle

privateでは次まで進む。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> ready_for_public_ci`

public確認後は次まで進む。

`in_public_ci -> orchestrator -> state finalization -> phase2 -> review thread 0 -> awaiting_private_merge`

private復帰後、検証済みHEADをsquash mergeして`merged`へ進める。

### always_public_full_pipeline

repositoryをpublicのまま維持し、次を一cycleで進める。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> orchestrator -> state finalization -> phase2 -> review thread 0 -> squash merge -> merged`

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

## 例外停止

途中停止は`cycle_control.status=paused`とし、次だけを許す。

- `user_decision_required`
- `checker_failure`
- `external_dependency_unavailable`
- `turn_capacity_checkpoint`

`paused`には`continuation_required=true`、理由、機械実行可能な`exact_next_action`を残す。

常時public modeでは失敗時もprivate復帰を要求しない。同じlocked modeで再開する。

## 禁止

- visibility確認前の作業開始
- active cycle中のmode変更
- internal stageを正常な会話終了地点にすること
- quality audit中のfix、owner、正式束書込み
- encoding中の新しい翻訳判断
- translation freeze後の翻訳再開
- manifest ready前の重いCI起動
- phase2成功前のmerge
- merge前の次wave開始
- 常時public modeで`ready_for_public_ci`または`awaiting_private_merge`を正常停止地点にすること
