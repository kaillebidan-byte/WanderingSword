# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、確定releaseはcheckpointが指すrelease evidence、次束は`NEXT_TASK_PACKET.json`。

## 新しいチャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: private
- open PR: 0件
- active Issue: #112
- active branch: `agent/yuwen-mowen-train-03`
- operation mode: `ready_for_public_ci`
- active train: `yuwen-mowen-train-03` / ready_for_public_ci
- train totals: 4束 / 32行 / 4修正 / 新規人物ペア2キー
- reviewed: 第69束まで
- checkpoint: 第65束 / 人物ペア1167 / 全1521 / verified
- last release: `yuwen-mowen-train-02-r1`
- release PR: #111 / squash merge `5503402b430291739f3da84a5d439a7e62a173e6`
- 未適用fix: 4
- build: verified_not_deployed
- game verification: not_started

## 第66〜69束で行ったこと

- 第66束`5504_3`は14行を通読し、3修正・11保持で閉じた
- 第67束`5506_3`は3行すべて保持した
- 第68束`5508_13`は11行を通読し、欧陽雪Index6の1修正・10保持で閉じた
- 第69束`5509_4`は4行すべて保持した
- FACT_DOUBTとALLUSION_REVIEWを分離した
- locres、pak、audit_status、適用件数は更新していない
- 完成4束へ達したため通常release条件`bundle_count=4`を満たした

## 次に行うこと

1. ユーザーへ一度だけpublic化を依頼する。
2. public確認後、同じ`agent/yuwen-mowen-train-03`からPRを一つ作る。
3. Relation / Cross / Applyを実行し、locres・pak・audit statusを書き戻す。
4. bot書き戻し後に重い三本が再起動しないことを確認する。
5. 同じPR内でrelease evidenceとverified checkpointを確定する。
6. 未解決thread 0件を確認し、squash統合する。
7. private復帰後に第70束`5522_1`を次列車で開始する。

public確認前はPRを作らず、第70束の翻訳判断も始めない。
