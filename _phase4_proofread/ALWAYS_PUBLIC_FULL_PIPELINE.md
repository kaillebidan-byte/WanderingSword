# 常時public full pipeline

## 選択

新しいcycleを始める直前にrepository metadataを確認する。

- privateなら`manual_visibility_cycle`
- publicなら`always_public_full_pipeline`

選択は次で二つの状態正本へ固定する。

```bash
python _tools/select_cycle_execution_mode.py --repository-visibility public --write
```

入力文は従来と同じ`作業の続きを`を使う。モード専用の起動文は設けない。

進行中cycleの`execution_mode`と`cycle_start_visibility`は変更しない。前cycleのtransportが`merged`になった後だけ次cycleのモードを選べる。

## 実行順

常時publicでも段階機械は変えない。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> orchestrator -> state finalization -> phase2 -> review thread 0 -> squash merge -> merged`

`private_*`は認知段階の名前であり、repository visibilityを意味しない。

## 権限

- `private_preparation`: 翻訳判断、fix書込み、owner書込みを行わない
- `private_quality_audit`: 翻訳判断だけを行う。fix、owner、正式束を書かない
- `private_encoding`: 記録済み判断だけを収録する。新しい翻訳判断を行わない
- `translation_frozen`以後: 翻訳判断、fix追加、owner変更、次wave準備を行わない

publicであることを理由に段階権限を広げない。

## CI境界

通常commit、PR作成、ready化だけでは重いCIを起動しない。

manifest ready、translation freeze、release preflight成功後に既存の`release-ci`入口を使う。Relation、Cross、Apply、finalization、phase2は既存経路をそのまま使う。

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointとして記録する。ただし常時public modeでは正常停止地点にしない。追加のvisibility操作を求めず、同じcycleで`merged`まで進む。

## 失敗

checker failure、外部依存停止、判断要求、turn容量停止だけを`paused`として許す。

常時public modeの失敗を理由にprivate復帰を要求しない。状態正本へ失敗分類とexact next actionを残し、同じlocked modeで再開する。

## merge

phase2成功、未解決review thread 0、検証済みHEAD一致を確認してpublicのままsquash mergeする。

merge前に次waveを始めない。merge後に次cycleの開始visibilityを再確認し、次のmodeを選ぶ。
