# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、確定releaseはcheckpointが指すrelease evidence、次束は`NEXT_TASK_PACKET.json`。turn入口は`VISIBILITY_PREFLIGHT_CONTRACT.json`を最初に適用する。

## 新しいチャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: private（GitHub metadataで確認済み）
- open PR: 0件
- active Issue: #114
- active branch: `agent/yuwen-mowen-train-04`
- operation mode: `ready_for_public_ci`
- active train: `yuwen-mowen-train-04` / ready_for_public_ci
- train totals: 4束 / 34行 / 3修正 / 新規人物ペア1キー
- reviewed: 第73束まで
- applied checkpoint: 第69束 / 人物ペア1169 / 全1525 / verified
- previous release: `yuwen-mowen-train-03-r1`
- previous PR: #113 / squash merge `e4dd3f79e2facf019b7e4dc0f23d8043dd2bcd7e`
- 未適用fix: 3
- build: verified_not_deployed
- game verification: not_started

## train-04

- 第70束`5522_1`: 7行 / 2修正 / 5保持
  - 徐海の重複罵倒を整理
  - 黄宗政の制止と咳を強化
- 第71束`5523_1`・`5525_3`: 8行 / 1修正 / 7保持
  - 莫問の`改变`を「一人ではどうにもできない」へ修正
- 第72束`5525_6`: 5行 / 0修正 / 5保持
  - 偽傷・天龍幇の目的・受制関係を推測強度のまま保持
- 第73束`5528_7`・重複分岐`5529_5`: 14キー / 0修正 / 14保持
  - 黒白無常の過剰演出を端役registerとして保持
  - 完全重複分岐の文面一致を確認

## 一次資料

- Relation run: `30140191768`
- artifact: `8614192158`
- digest: `sha256:7a38ab3e453d2544fdefd886f8dcc50467b59df1c9d3088547c32297128056ad`
- source HEAD: `1bf29e39de33d22c52291123f64474935adb8eca`

## 次に行うこと

1. ユーザーへpublic化を一度だけ依頼する。
2. public確認後、同じbranchからPRを一つ作る。
3. Relation / Cross / Applyを実行し、3修正をlocres・pak・audit_statusへ反映する。
4. release evidenceと第73束verified checkpointを同じPR内で確定する。
5. public phase2 gate、未解決thread 0件を確認する。
6. private復帰後に同じPRをsquash統合する。
7. 第74束`5531_3`・`5531_4`はprivate復帰後に開始する。

public確認前はPRを作らず、第74束の翻訳判断も始めない。
