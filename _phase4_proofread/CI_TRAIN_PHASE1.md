# CI列車 第一段階 wave方式

## 単位

- candidate packet: preparationで作る未判断単位。PRIVATE_STAGE_STATEだけに置く。
- wave: 複数packetをまとめたpreparation、quality audit、encodingのqueue。
- 正式束: encodingでreview record、owner、fix JSON、番号が確定した単位。
- CI列車: encoding済み正式束をまとめて輸送する単位。

## wave準備

通常sealは4 packet以上または40 unique reviewed rows相当以上。追加候補が意味境界上存在しない場合だけ`scope_exhausted`を使う。40〜60 rowsを標準範囲とし、60行付近で意味単位が完結していない場合は最大6 packet / 80 rowsまで延長できる。80行を埋めることを目的にしない。

## quality auditとencoding

sealed queueの全packetを続けて監査し、一packetごとにencodingへ進まない。全packet監査後、記録済み判断だけをfix JSON、owner、review record、正式束、manifestへ収録する。candidate packetはmanifestへ入れない。

## release条件

次のいずれかでrelease可能になる。

- 完成正式束4
- 通読40 unique rows
- 修正20キー

40〜60行は標準範囲、60〜80行は意味単位完結のための延長範囲、80行は強制上限とする。packet上限6は維持する。

## transport

全packet encoding後に`translation_frozen`へ進め、transportを次の順で動かす。

`not_ready -> ready_for_public_ci -> in_public_ci -> verified -> awaiting_private_merge -> merged`

manual public CI窓では翻訳判断、packet追加、owner変更、正式束追加を禁止する。always-publicではrepository visibilityではなくstage権限で同じ境界を守り、private_*段階の作業はpublicのまま実行できる。

## replenishment

`private_encoding -> private_preparation`はpacket invalidation、重複正規化、未解決context、source stale、scope境界訂正に限り、理由コード付きで使う。一packetしか準備しなかったことをreplenishment理由にしない。
