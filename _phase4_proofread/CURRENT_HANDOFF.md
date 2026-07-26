# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: private
- PR #133: open / draft（private preflightと参照同期後にready化）
- train: `yuwen-mowen-train-13`
- verified checkpoint: 第104束
- last reviewed batch: 第108束
- 人物ペア適用済みowner: 1169
- プロジェクト全体適用済み: 1545
- private stage: `translation_frozen`
- train-13 transport: `ready_for_public_ci`
- cycle control: `target_reached / ready_for_public_ci`

## train-13

`5825_1`から`5928_2`まで四packet・58行を連続監査し、9行を修正、49行を意図的保持とした。既存owner更新8、新規owner1、keep-only束1。程鈺の母から宇文逸への手紙で母の所属と宛先を戻し、烏長老殺害への断罪、包閔の死の脅し、`罄竹難書`の逐語訳、清虚から任務を受ける宇文逸の返答を修正した。

街の噂、程鈺の母の予感、程鈺が去った理由、悪人谷の親分の目的、莫問の天山での過去、瑶姫の説明は場面内の知識以上に確定していない。

## 次の作業

private preflightを一命令で完了し、PR #133をreadyへ移す。ユーザーがpublic化した後、`release-ci`でorchestratorを起動し、Apply、state finalization、phase2、review thread 0件まで同一PRで進める。

## 禁止

- public中に翻訳判断、fix追加、owner変更、正式束追加を行わない。
- private確認前にPR #133をmergeしない。
- PR #133統合前に`5928_6`のpreparationを始めない。
- ゲームフォルダへ配置しない。
