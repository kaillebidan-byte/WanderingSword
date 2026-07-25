# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 機械正本は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、private waveは`PRIVATE_STAGE_STATE.json`、次候補予約は`NEXT_TASK_PACKET.json`。

## 現在地

- 実visibility: private（GitHub repository metadataで確認）
- main HEAD: `56c8eecfc4eb1a44a23708d25d9566d68cea016c`
- PR #118: squash統合済み
- active制度branch: `agent/four-stage-wave-v2`
- active制度PR: #119（draft / private）
- verified checkpoint: 第80束
- 人物ペア適用済み: 1171
- プロジェクト全体適用済み: 1529
- release: `yuwen-mowen-train-06-r1`
- 翻訳段階: `translation_frozen`
- train-06輸送: `merged`

## 今回の制度改修

四段階制度を一packet loopからmulti-packet waveへ置き換える。

- preparationで複数packetを先に準備してsealする。
- sealed queue全体をquality auditする。
- 全監査済みpacketをまとめてencodingする。
- 全収録後は`translation_frozen`にし、CI輸送statusを別軸で進める。
- `encoding -> preparation`は理由コード付きreplenishmentだけにする。
- candidate packetをmanifestから外す。
- bundleの`review_status`と`apply_status`を分ける。

## 次候補

`5581_7 + 5581_8`は予約だけ。preparation・quality audit・encoding・正式束番号は未開始。制度改修PRを統合するまで翻訳作業へ進まない。

## 禁止

- 訳文、fix JSON、人物owner、FACT_DOUBT、ALLUSION_REVIEWを変更しない。
- 第81束の翻訳監査を開始しない。
- PR #118の履歴を変更しない。
- public中に翻訳判断を再開しない。

## 再開時

最初に実visibilityを無言で確認する。その後、main、未統合PR、GitHub Actions、制度正本を読む。active制度PR #119があれば、その監査・CI・統合を次候補翻訳より優先する。private中はpublic限定CIを待ち、公開依頼を出した時点で停止する。
