# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: private
- PR #141: squash merged (`2d9f4790a8075b27b0c7981607e81c88b579fef1`)
- train: `yuwen-mowen-train-17`
- verified checkpoint: 第114束
- 人物ペア適用済みowner: 1188
- プロジェクト全体適用済み: 1564
- private stage: `private_preparation`
- train-17 transport: `not_ready`
- queue: sealed / 3packet / 51 unique rows

## train-17 prepared queue

1. `9150_3 + 9150_4` — 救出の呼びかけと、戻れないと拒む莫問。
2. `9154_2 + 9209_2 + 9210_1 + 9223_6` — 和解後の短い協働会話。
3. `9228_2 + 9229_2 + 9230_2` — 悪人谷残党戦の同行者差分三分岐。

全candidateはtrain-16の最新Relation artifactから生成し、全`fixes_*.json`のowner snapshotを準備時点で固定する。

## 次の作業

sealed queue全体をprivate品質監査し、各行のfix / keep判断、人物声、典故候補、FACT_DOUBTを監査記録へ確定する。品質監査中は輸送件数を判断材料へ出さない。

## 禁止

- private品質監査前にfix JSONやownerを書き換えない。
- 正式束番号はprivate encodingまで付けない。
- ゲームフォルダへ配置しない。
