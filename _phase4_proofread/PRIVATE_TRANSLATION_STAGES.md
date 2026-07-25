# private翻訳四段階 wave v2

## 目的

翻訳判断と制度操作を分離するだけでなく、準備・品質監査・収録の認知モードを一列車の中でまとまった区間として維持する。

schema v1では、一packetだけを`private_preparation`から渡し、`private_quality_audit -> private_encoding -> private_preparation`を一束ごとに繰り返した。これは停止を避けたが、認知モードを再び混在させた。wave v2では、複数packetを先に準備し、sealed queue全体を監査し、その後にまとめて収録する。

機械契約は`PRIVATE_TRANSLATION_STAGES.json`、現在状態は`PRIVATE_STAGE_STATE.json`、検査は`python _tools/check_private_translation_stage.py`を正本とする。

## 1. `private_preparation`

一列車分のcandidate packetを先に作る。

許可:

- 原文、現訳、前後、話者、相手、時系列、分岐を固定する。
- 重複familyと既存ownerを参照する。
- candidate packetとpreparation recordを`PRIVATE_STAGE_STATE.wave.packets`へ追加する。
- queueのpacket数とunique reviewed rows相当を輸送設計として集計する。

禁止:

- fix / keep判断を行う。
- fix JSON、review record、owner新設、正式束番号を作る。
- candidate packetを`CI_TRAIN_MANIFEST.json`へ入れる。

通常sealは次のいずれかを満たす。

- 4 packet以上
- 40 unique reviewed rows相当以上
- 意味境界上、追加候補が存在しない`scope_exhausted`

上限は6 packet / 60 rowsとする。`scope_exhausted`は具体的なattestationを必須とする。一packetを作っただけで通常sealすることは`preparation_underfilled`として失敗する。

## 2. `private_quality_audit`

sealed queueの全packetを続けて監査する。

packetごとに、少なくとも次を記録する。

- `fix_candidate`
- `challenged_keep`
- `needs_context`
- `FACT_DOUBT`
- `ALLUSION_REVIEW`

許可:

- 原文の意味、強弱、発話役割、人物声、設定追加、欠落、不自然さを判断する。
- 既存ownerと重複情報を参照する。
- packetを`audited`または`needs_repreparation`へ更新する。

禁止:

- 一packet完了ごとにencodingへ移る。
- fix JSON、owner、review record、正式束番号、manifest件数を書く。
- `metrics_snapshot`、release残量、閾値、処理件数を監査判断へ渡す。

queueがsealedでない場合、quality auditへ進めない。

## 3. `private_encoding`

全packetの監査完了後、確定済み判断だけをまとめて収録する。

許可:

- fix JSONへ確定済み修正を収録する。
- owner、重複family、review record、FACT_DOUBT、ALLUSION_REVIEWを制度化する。
- 正式束番号を割り当てる。
- encoding済み正式束だけをmanifestへ追加する。
- `review_status`と`apply_status`を別々に記録する。

禁止:

- 新しい翻訳判断を行う。
- 未監査packetを残したまま収録を開始する。
- 一部packetを未収録のまま翻訳凍結へ進む。

新しい疑義が出たpacketだけを`needs_reaudit`へし、`private_quality_audit`へ戻す。他packetの監査を無効化しない。

## 4. `translation_frozen`

全packetのencoding完了後、翻訳判断と収録を凍結する。これはCI輸送状態ではない。

翻訳段階を`translation_frozen`に保ったまま、輸送軸だけを次の順に進める。

`not_ready -> ready_for_public_ci -> in_public_ci -> verified -> awaiting_private_merge -> merged`

public CI中も翻訳判断、fix追加、owner変更、正式束追加を再開しない。品質上の疑義が出た場合はprivateへ戻し、対象packetを`needs_reaudit`としてquality auditへ戻す。

## replenishment例外

`private_encoding -> private_preparation`は通常遷移ではない。次の理由コードを伴うreplenishmentだけを許す。

- `packet_invalidated`
- `duplicate_normalization_reduced_scope`
- `needs_context_unresolved`
- `prepared_source_became_stale`
- `scope_boundary_corrected`

第一段階が十分なpacketを準備しなかっただけの場合は例外にしない。checkerは`preparation_underfilled`として失敗させる。

## manifest境界

candidate packetは`PRIVATE_STAGE_STATE.json`だけで管理する。

`CI_TRAIN_MANIFEST.json`にはencoding済みの正式束、review/apply状態、輸送集計だけを置く。旧`reviewed_pending_ci`へ複数意味を押し込まず、次へ分ける。

- `review_status: complete`
- `apply_status: pending | verified`

## 現行状態の移行

train-06第77〜80束の既存記録は改変せず、schema v1の四往復を一つの移行waveへ統合して表現する。PR #118はsquash統合済みであり、輸送状態は`merged`、翻訳段階は`translation_frozen`とする。

`5581_7 + 5581_8`は次waveの予約だけであり、preparation・quality audit・encoding・正式束番号は未開始とする。
