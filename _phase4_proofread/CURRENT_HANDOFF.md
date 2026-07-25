# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、private段階は`PRIVATE_STAGE_STATE.json`、品質制度は`TRANSLATION_QUALITY_GATE.md`、確定releaseはcheckpointが指すevidence、次束は`NEXT_TASK_PACKET.json`。

## 新しいチャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: public（GitHub metadataで確認済み）
- open PR: #117
- active Issue: #116
- active branch: `agent/yuwen-mowen-train-05`
- operation mode: `ready_for_public_ci`
- private stage: `ready_for_public_ci`
- release: `yuwen-mowen-train-05-r2` / verified
- checkpoint: 第76束 / 人物ペア1171 / 全1529 / 未適用0件
- reviewed: 53 keys / 47 unique rows
- 修正: 7 keys / 6 unique rows
- build: `verified_not_deployed`
- game verification: `not_started`

## r2で直した内容

初回3修正に加え、低収穫時の全keep再監査で次の4キーを追加した。

- `5535_2_Dlgs_Index2_Text`: 黄宗政本人の助力を「私の力」と明示
- `5535_2_Dlgs_Index4_Text`: 見送る黄宗政の「失礼する」を「さらばだ」へ修正
- `5536_3_Dlgs_Index5_Text`
- `5536_4_Dlgs_Index5_Text`: 原文`带人`にない「門人」の設定追加を除去

`5535_2_Dlgs_Index4_Text`は旧ownerになかったため、新規人物ペア1キー。人物ペア累計1171・全体1529となった。

## 品質・private段階制度

- 束数・行数・修正数は品質成果ではなくCI輸送指標
- reviewed keysとunique rowsを分離
- 初回修正率15%未満なら初回keep全unique rowsを第二巡で疑い直す
- private作業を`preparation -> quality audit -> encoding -> ready for public CI`へ分離
- preparationでは判断・fix・owner・正式束を作らない
- quality auditでは読むことと校正判断だけを行い、件数を判断材料にしない
- encodingでは確定済み判断だけを収録し、新しい疑義はquality auditへ戻す
- publicでは翻訳判断を再開しない

train-05は既存証拠から四段階を遡及固定した移行列車。次列車では第77束を`private_preparation`から順に実測する。

## 新しい成功証跡

- CI HEAD: `a568f731dcf419c766dc6a3845461aed1f83d46a`
- Relation: `30149789606` success
- Cross: `30149789605` success
- Apply: `30149789594` success
- asset HEAD: `1b84e1586fa13802525904cfbe192ebd3f4972bc`
- Apply QA: 適用前4件、適用後0件、適用済み1529件
- quality checker: success
- private-stage checker / regression: success
- audit status: 第76束・人物ペア1171・全1529
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_05.json`

旧`yuwen-mowen-train-05-r1`と旧run群は履歴として残るが、merge根拠には使わない。

## 次に行うこと

1. 最終状態HEADのpublic phase2 gateを成功させる。
2. 未解決review thread 0件を確認する。
3. repositoryをprivateへ戻す。
4. private metadata closeout後、PR #117をsquash統合する。
5. 新しいprivate列車を`private_preparation`で開始する。
6. 第77束`5540_4`は文脈・重複・所有の準備から始め、同じ回では翻訳判断しない。

public中は第77束を読まず、fix・owner・束を追加しない。
