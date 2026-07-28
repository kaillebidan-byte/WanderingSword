# CI列車 第一段階 wave方式

## 目的

翻訳の意味境界をpacketとして保ちつつ、準備・品質監査・収録を一列車分のwaveへまとめる。public CI窓への往復は複数正式束ごとに一回とする。

## 単位

- **candidate packet**: preparationで作る未判断単位。`PRIVATE_STAGE_STATE.json`にだけ置く。
- **wave**: 一回のpreparation、quality audit、encodingで処理する複数packetのqueue。
- **正式束**: encodingでreview record、owner、fix JSON、正式束番号が確定した単位。
- **CI列車**: encoding済み正式束をまとめてpublic CIへ送る単位。

## wave準備

preparationでは複数packetを先に準備する。通常sealは4 packet以上または40 unique reviewed rows相当以上。追加候補が意味境界上存在しない場合だけ`scope_exhausted`を使う。40〜60 rowsを標準範囲とし、60 rows付近で意味単位が完結していない場合は、その意味単位を切らずに最大6 packet / 80 rowsまで延長できる。80 rowsを埋めることを目的にしてはならない。

一packetしか準備しなかったことをreplenishment理由にしてはならない。checkerは`preparation_underfilled`として失敗させる。

## quality audit

sealed queueの全packetを続けて監査する。一packet完了ごとにencodingへ進まない。件数、release閾値、残量、manifest totalsは監査判断へ見せない。

## encoding

全packetが監査済みになってから収録する。ここでfix JSON、owner、重複family、review record、正式束番号、manifest集計を作る。

bundle状態は次へ分ける。

- `review_status: complete`
- `apply_status: pending | verified`

candidate packetはmanifestへ入れない。

## release条件

通常releaseは次のいずれか一つへ達した時点とする。

- 完成正式束4
- 通読40 unique rows
- 修正20キー

標準範囲は通読40〜60 unique rowsとする。意味単位を完結させる場合に限り、完成正式束6を維持したまま通読80 unique rowsまで延長でき、80 rowsを強制上限とする。workflow変更、schema変更、security/visibility、緊急build確認は許可された早期release理由として別に記録する。

全packetのencoding完了後に翻訳段階を`translation_frozen`へする。CI輸送は別軸で次へ進める。

`not_ready -> ready_for_public_ci -> in_public_ci -> verified -> awaiting_private_merge -> merged`

## replenishment

`private_encoding -> private_preparation`は通常loopではない。packet invalidation、重複正規化によるscope縮小、未解決context、source stale、scope境界訂正に限り、理由コード付きで使う。

## private中の所在ポインタ

制度改修branchまたは列車branchはdraft PRを所在ポインタとして使える。draft PRはCI実行や統合要求ではない。active branch、CURRENT_WORK、PRIVATE_STAGE_STATE、manifestを一致させる。

## public CI

public中は翻訳判断、packet追加、owner変更、正式束追加を禁止する。Relation / Cross / Apply、phase2 gate、release evidence、未解決thread、squash統合だけを行う。
