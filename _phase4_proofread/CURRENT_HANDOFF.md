# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: private（GitHub repository metadataで確認）
- main HEAD: `2aef4a1b05e758b14bbcebd8247df218c91df4f3`
- PR #124: squash統合済み
- 制度PR #125: squash統合済み
- verified checkpoint: 第92束
- 人物ペア適用済みowner: 1165
- プロジェクト全体適用済み: 1541
- private stage: `translation_frozen`
- train-10 transport: `ready_for_public_ci`
- cycle control: `target_reached / ready_for_public_ci`

## train-10 wave-01

四packet・57行を監査し、15修正を収録した。既存owner更新8キー、新規owner43キー。Apply前なのでcheckpoint累計は第92束・1165 / 1541を維持する。

- 第93束: `5654_8` — 14行 / 8修正
- 第94束: `5756_2 + 5756_5` — 9行 / 3修正
- 第95束: `5781_1 + 5781_10 + 5784_4` — 20行 / 1修正
- 第96束: `5784_8` — 14行 / 3修正

主な修正は、未訳の`道貌岸然`、偽秘笈を巡る動機の主客、`円覚`が`内懐`へ化けた固有名回帰、莫問の伏せた調査、程鈺の憧れと急な誘導である。

## 次の作業

公開CI窓でtrain-10 PRへ`release-ci`を付与し、Release train orchestrator、botの状態確定、`finalize-release`、phase2、未解決review thread 0まで同じcycleで進める。

次wave候補`5784_9`はschema v6のreserved_only。train-10統合前にpreparationを始めない。

## 禁止

- public中に新しい翻訳判断、fix追加、owner変更、正式束追加を行わない。
- phase2成功前に`awaiting_private_merge`へ進めない。
- private確認前にmergeしない。
- ゲームフォルダへ配置しない。
