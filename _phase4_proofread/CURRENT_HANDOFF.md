# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 機械正本は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、private waveは`PRIVATE_STAGE_STATE.json`、次段階は`NEXT_TASK_PACKET.json`。実visibilityとGitHub PR metadataを文書より優先する。

## 現在地

- 実visibility: public（GitHub repository metadataで確認）
- main HEAD: `eee509ccbf323810df28bebf41ec5cc65f0ec6a9`
- active branch: `agent/yuwen-mowen-train-07`
- active PR: draft PR #120
- verified checkpoint: 第80束
- 人物ペア適用済み: 1171
- プロジェクト全体適用済み: 1529
- 前release: `yuwen-mowen-train-06-r1`
- 翻訳段階: `translation_frozen`
- transport: `in_public_ci`

## train-07 wave-01

Relation artifact run `30169356037` / artifact `8622473127`を使用した。

四packet・57行を一括監査し、正式第81〜84束へencodingした。

- 第81束: `5581_7 + 5581_8` / 4行 / 2修正
- 第82束: `5583_1` / 12行 / 4修正
- 第83束: `5583_2` / 18行 / 10修正
- 第84束: `5585_4 + 5586_3 + 5586_5` / 23行 / 12修正

合計28修正。新規人物ペアキー0、新規プロジェクトキー10、横断キー7。既存owner更新は18キー。

第84束の12修正は、人物ペア既存owner更新5、既存人物ペアownerから横断ownerへの移管6、横断owner新規1に整理した。公開CIで検出されたowner競合は解消済みで、訳文判断は変更していない。

locres、pak、verified checkpoint、audit statusはまだ更新していない。

## 次作業

PR #120の最終人手HEADでRelation・Cross・Applyを再実行する。Applyのbot書き戻し後、release evidenceとverified checkpointを同じPR内で確定し、phase2を通す。

## 禁止

- public中に翻訳判断を再開しない。
- 第85束候補`5603_1`のpreparationを始めない。
- ゲームフォルダへ配置しない。
- CI検証前にcheckpointをverifiedへ進めない。

## 再開時

実visibility、main、PR #120のHEAD、Actionsを確認する。翻訳判断を凍結したままCI輸送だけを続ける。
