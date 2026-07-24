# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、確定releaseはcheckpointが指すrelease evidence、次束は`NEXT_TASK_PACKET.json`。

## 新チャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: private
- open PR: 0件
- active制度改修branch: `agent/ci-train-phase2`
- 第61束翻訳PR #106: squash統合済み
- translation squash: `f12089d1d74b18b6e25a916b9e8eb3536de0064a`
- state squash: `18d076faf820097bd0cb1455b040dd0bc48caa7b`
- checkpoint: 第61束 / 人物ペア1166 / 全1518 / verified
- release id: `yuwen-mowen-train-01-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_01.json`
- 次の翻訳束: 第62束 `5455_1`（制度改修完了まで着手しない）

## 第二段階の実装内容

- Relation / Cross / Applyの起動を修正JSON・検査コード変更へ限定する
- bot actorを重い三本から除外する
- locres、pak、audit status書き戻しでは重い三本を再起動しない
- 最終状態文書は`CI train phase2 gate`だけで検査する
- checkpointから`translation_head`と`verified_head`を廃止する
- PR番号、成功run、検証HEAD、件数をrelease evidenceへ固定する
- 同じ翻訳PR内で状態を確定し、post-merge状態PRを作らない

## 次の作業

1. phase2 branchのローカル回帰を完了する
2. 制度改修だけを早期release理由`workflow_change`で公開CIへ出す
3. Relation / Cross / Apply / phase2 gateの起動境界を実測する
4. 同じPRをsquash統合し、post-merge状態PRが不要なことを確認する
5. privateへ戻す
6. 第62束`5455_1`から新しい列車を開始する

public検証までは新しい翻訳判断を追加しない。
