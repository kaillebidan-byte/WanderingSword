# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、確定releaseはcheckpointが指すrelease evidence、次束は`NEXT_TASK_PACKET.json`。

## 新チャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: private
- open PR: 0件
- 管理Issue: #108
- active制度改修branch: `agent/ci-train-phase2`
- operation mode: `ready_for_public_ci`
- 早期release理由: `workflow_change`
- checkpoint: 第61束 / 人物ペア1166 / 全1518 / verified
- release id: `yuwen-mowen-train-01-r1`
- 次の翻訳束: 第62束 `5455_1`（制度改修統合・private復帰まで着手しない）

## 第二段階の実装

- Relation / Cross / Applyの起動を修正JSON・検査コード・当該workflow変更へ限定
- bot actorを重い三本から除外
- locres、pak、audit status、状態文書では重い三本を再起動しない
- 最終状態文書は`CI train phase2 gate`だけで検査
- checkpointをsquash SHA依存からrelease evidenceへ移行
- 同じPR内で状態を確定し、post-merge状態PRを廃止
- 旧phase1自動gateを手動legacyへ退役

## private検証

- release evidence回帰: 成功
- phase2 handoff回帰: 成功
- operation mode回帰: 成功
- Python compile: 成功
- JSON / workflow YAML構文: 成功

## 公開CIで測ること

1. 制度PR初回HEADでRelation / Cross / Apply / phase2 gateが一度ずつ起動する
2. bot書き戻し後に重い三本が再起動しない
3. 最終状態commitでphase2 gateだけが起動する
4. 未解決thread 0件で同じPRをsquash統合する
5. post-merge状態PRを作らない
6. privateへ戻した後、第62束`5455_1`へ進む

public中は新しい翻訳判断を追加しない。
