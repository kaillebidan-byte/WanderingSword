# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、private段階は`PRIVATE_STAGE_STATE.json`、段階契約は`PRIVATE_TRANSLATION_STAGES.json`、品質制度は`TRANSLATION_QUALITY_GATE.md`、次束は`NEXT_TASK_PACKET.json`。turn入口は`VISIBILITY_PREFLIGHT_CONTRACT.json`を最初に適用する。

## 新しいチャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: private（GitHub metadataで確認済み）
- open PR: #117
- active Issue: #116
- active branch: `agent/yuwen-mowen-train-05`
- operation mode: `ready_for_public_ci`
- private stage: `ready_for_public_ci`
- active train: `yuwen-mowen-train-05` / quality re-audit complete / re-release待ち
- 確定checkpoint: 第73束 / 人物ペア1170 / 全1528 / train-04-r1
- reviewed: 第76束まで
- train totals: 3束 / 47 unique rows / 53 reviewed keys / 7修正キー / 6 unique修正行
- pending fixes: 4キー
- build: candidate_assets_unverified
- game verification: not_started

## 目的逸脱の監査

利用者から、既存の荒い翻訳を直すことより通読行数・束作成が目的化していないかという指摘を受けた。

直近の修正率は次のように低下していた。

- train-02: 30行 / 8修正
- train-03: 32行 / 4修正
- train-04: 34 reviewed keys（実質27 unique rows）/ 3修正
- train-05初回: 53 reviewed keys（47 unique rows）/ 3修正

低修正率自体は誤りではないが、初回keep全44 unique rowsを疑い直したところ4キー・3 unique rowsの見落としを実際に検出した。このためtrain-05-r1のpublic verified判定は無効化した。

品質記録:

- `_phase4_proofread/QUALITY_CHALLENGE_YUWEN_MOWEN_TRAIN_05_2026-07-25.md`

## 追加修正

- `5535_2_Dlgs_Index2_Text`
  - 黄宗政本人の助力をぼかした「何か力」を「私の力」へ戻す。
- `5535_2_Dlgs_Index4_Text`
  - 見送る黄宗政の「失礼する」を、発話役割に合う「さらばだ」へ修正。
- `5536_3_Dlgs_Index5_Text`
- `5536_4_Dlgs_Index5_Text`
  - 原文`带人`へ存在しない「門人」を補っていたため、「人を連れて」へ修正。

## private四段階制度

private作業を次の四段階へ分離した。

1. `private_preparation`
   - 文脈・重複・所有を準備する。翻訳判断、修正JSON、owner新設、正式な束番号は禁止。
2. `private_quality_audit`
   - 読むことと校正判断だけを行う。件数・release閾値を判断材料にせず、pair keyやfix JSONを作らない。
3. `private_encoding`
   - 確定済み判断だけをJSON・所有・レビューへ収録する。新しい疑義はquality auditへ戻す。
4. `ready_for_public_ci`
   - 翻訳判断と収録を凍結し、CI輸送だけを行う。

実装:

- `_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md`
- `_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json`
- `_phase4_proofread/PRIVATE_STAGE_STATE.json`
- `_tools/check_private_translation_stage.py`
- `_tools/test_check_private_translation_stage.py`

段階checkerは既存`check_translation_quality_gate.py`から連鎖実行するため、Relation・Apply・phase2 gateの既存品質入口すべてで必須になる。既存品質testも四段階の正常遷移、飛越拒否、quality audit中のmetrics遮断、encoding中の新規判断拒否を回帰検証する。

train-05は制度導入前の作業を遡及して四段階へ固定した移行列車。次の列車から各段階を順番に実行し、段階遷移そのものを往復テストする。

## 品質制度

- 束数・行数・修正数を品質成果ではなくCI輸送指標と明記。
- `reviewed_keys`と`unique_reviewed_rows`を分離。
- 重複分岐をunique行へ二重計上しない。
- 初回`unique_fix_rows / unique_reviewed_rows < 15%`なら、初回keep全unique rowsの二巡目監査を必須化。
- keep-only束の個数だけでは品質合格にしない。
- quality audit中はmetrics snapshotを持たず、encoding後にだけ集計する。

## 無効化した証跡

- `yuwen-mowen-train-05-r1`
- Relation `30148094728`
- Cross `30148094731`
- Apply `30148094737`
- 旧asset HEAD `4d5ad76ebad311de0a6afdd501b02af666b6c6be`

これらは当時の3修正に対して成功した実runとして履歴に残るが、追加4キーと新品質・段階制度を検証していないためmerge根拠には使わない。

## 次に行うこと

1. public CI窓を開く。
2. PR #117へ`ci-heavy-rerun`を付け、新段階checker・品質ゲート付きRelation / Cross / Applyを同じ新HEADで実行する。
3. 4追加修正をlocres・pakへ適用し、未適用0件を確認する。
4. audit status、適用記録、train-05-r2 release evidence、verified checkpointを再構築する。
5. public phase2 gateと未解決thread 0件を確認する。
6. private復帰後にPR #117をsquash統合する。
7. 次列車で`private_preparation -> private_quality_audit -> private_encoding -> ready_for_public_ci`を順次実測する。
8. 第77束`5540_4`はその段階制度に従って開始する。

第77束の翻訳判断はまだ開始しない。作業報告では修正内容と品質判断を先に、束数・行数を後に示す。
