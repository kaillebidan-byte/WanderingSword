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
- operation mode: `private_translation_work`
- effective mode: `private_translation_work`
- active train: `yuwen-mowen-train-04` / accumulating
- train totals: 2束 / 15行 / 3修正 / 新規人物ペア1キー
- reviewed: 第71束まで
- applied checkpoint: 第69束 / 人物ペア1169 / 全1525 / verified
- previous release: `yuwen-mowen-train-03-r1`
- previous PR: #113 / squash merge `e4dd3f79e2facf019b7e4dc0f23d8043dd2bcd7e`
- 未適用fix: 3
- build: verified_not_deployed
- game verification: not_started

## train-04で行ったこと

### 第70束 `5522_1`

- 7行 / 2修正 / 5保持
- 徐海Index3: 重複する罵倒を整理し、威圧的な命令調を保った
- 黄宗政Index6: 将軍らしい制止と切迫した咳表現へ整えた
- 人物ペア新規0 / cross-register新規2

### 第71束 `5523_1` / `5525_3`

- 8行 / 1修正 / 7保持
- 莫問Index1: `改变`を勝敗の「覆し」に限定せず、一人では戦況をどうにもできないという実務判断へ戻した
- 宇文逸の常体確認と混成同行者への敬体提案は場面内切替として保持した
- 人物ペア新規1 / cross-register新規0

## 一次資料

- workflow: Relation audit extraction
- run: `30140191768`
- artifact: `8614192158`
- digest: `sha256:7a38ab3e453d2544fdefd886f8dcc50467b59df1c9d3088547c32297128056ad`
- source HEAD: `1bf29e39de33d22c52291123f64474935adb8eca`
- 第70〜71束の対象キーはtrain-03修正対象外で、release後も本文不変

## 次に行うこと

1. 第72束`5525_6`の5行を監査する。
2. 徐海の偽傷、天龍幇の目的、夜襲時の離脱、受制関係を観察・伝聞・推測・確定へ分ける。
3. 既存第7束の所有を維持し、重複ownerを作らない。
4. `5528_7`の黒白無常戦は別束にする。
5. release条件到達までlocres・pak・audit_statusを更新しない。

## release条件

- 通常条件: 4束 OR 40行 OR 20修正キー
- 現在: 2束 / 15行 / 3修正
- public化不要。private蓄積を継続する。
