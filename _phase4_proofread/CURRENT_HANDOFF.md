# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、確定releaseはcheckpointが指すrelease evidence、次束は`NEXT_TASK_PACKET.json`。turn入口は`VISIBILITY_PREFLIGHT_CONTRACT.json`を最初に適用する。

## 新しいチャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: private（GitHub metadataで確認済み）
- open PR: 0件
- active Issue: #116
- active branch: `agent/yuwen-mowen-train-05`
- operation mode: `ready_for_public_ci`
- active train: `yuwen-mowen-train-05` / ready_for_public_ci
- train totals: 3束 / 53行 / 3修正 / 新規人物ペア0キー
- reviewed: 第76束まで
- applied checkpoint: 第73束 / 人物ペア1170 / 全1528 / verified
- previous release: `yuwen-mowen-train-04-r1`
- previous PR: #115 / squash merge `4dba3a33788cc0a1bdf6480656e0237661678ac4`
- 未適用fix: 3
- build: verified_not_deployed
- game verification: not_started

## train-05

- 第74束`5531_3`・`5531_4`: 28行 / 2修正 / 26保持
  - 腕輪確認の不自然な省略形を修正
  - 徐海の`放心了`を娘の無事への安堵へ戻した
  - `穷寇莫追`はALLUSION_REVIEWへ分離し、深追い禁止の機能訳を保持
- 第75束`5531_7`・`5535_2`: 11行 / 1修正 / 10保持
  - 天龍幇の人さらい目的を断定から高い可能性へ戻した
- 第76束`5536_3`・`5536_4`: 14行 / 0修正 / 14保持
  - 清霄師伯を待つ指示の有無だけを分岐差として保持
- 修正は既存`fixes_relation_yuwen_mowen_20260723_batch8.json`の所有を維持
- locres・pak・audit_statusは第73束checkpointのまま未更新

## 一次資料

- Relation run: `30145143325`
- artifact: `8615729248`
- digest: `sha256:fff1a96381862320176a51915722f7aee4bf3d85242253c4e504221a0922f27b`
- source HEAD: `abda35f9d742d71e1562c8cdebdf2fdc07643210`

## 次に行うこと

1. ユーザーへpublic化を一度だけ依頼する。
2. public確認後、同じbranchからPRを一つ作る。
3. Relation / Cross / Applyを実行し、3修正をlocres・pak・audit_statusへ反映する。
4. release evidenceと第76束verified checkpointを同じPR内で確定する。
5. public phase2 gate、未解決thread 0件を確認する。
6. private復帰後に同じPRをsquash統合する。
7. 第77束`5540_4`はprivate復帰後に開始する。

public確認前はPRを作らず、第77束の翻訳判断も始めない。
