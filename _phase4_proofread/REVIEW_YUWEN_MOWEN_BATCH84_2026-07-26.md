# 宇文逸↔莫問 第84束レビュー

- 日付: 2026-07-26
- train: `yuwen-mowen-train-07`
- private stage: `private_encoding`
- 場面: `5585_4` + `5586_3` + `5586_5`
- preparation: `_phase4_proofread/PREPARATION_YUWEN_MOWEN_SCENES5585_4_5586_3_5586_5_2026-07-26.md`
- quality audit: `_phase4_proofread/AUDIT_YUWEN_MOWEN_SCENES5585_4_5586_3_5586_5_2026-07-26.md`
- source artifact: Relation audit extraction run `30169356037`
- status: `reviewed_pending_ci`

## 場面機能

莫問が不風山の急変を伝えて出発を促す。後続では宇文逸と欧陽雪が洪飛に再会し、莫問の紹介と初対面の礼、洪飛の口止めと警告へ続く。

## 収録した修正

人物ペアownerで5キーを収録した。うち1キーは既存owner更新、4キーは新規ownerである。

- `5585_4_Dlgs_Index0_Text`: 宇文逸の言いさしを回復。既存owner `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch10.json` を更新
- `5585_4_Dlgs_Index4_Text`: 密偵報告と各派の決定を区別
- `5585_4_Dlgs_Index5_Text`: 未確認の戦況を推測へ戻し、色タグを保持
- `5586_5_Dlgs_Index2_Text`: 時機と場所の含みを回復
- `5586_5_Dlgs_Index5_Text`: 口止めへの具体的な応答へ修正

横断ownerへ7キーを収録した。

- 欧陽雪: `5586_3`の`Index3`、`Index5`
- 洪飛: `5586_3`の`Index6`、`Index7`、`5586_5`の`Index1`、`Index3`、`Index6`

表面転写、謙遜の脱落、人物評価、乞食自称、実質的な警告を各話者の声へ戻した。

## 保持

残る11行は、急報の情報源、即時出発、洪飛との既知の軽口、宇文逸による紹介、莫問自身の名乗りを保つため変更していない。

## 所有

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch10.json`: 既存owner更新1キー
- `_phase4_proofread/fixes_relation_yuwen_mowen_20260726_batch10.json`: 新規人物ペア4キー
- `_phase4_proofread/fixes_cross_register_hongfei_ouyang_20260726.json`: 横断7キー

人物ペア外の洪飛・欧陽雪行を宇文逸↔莫問ownerへ混在させていない。公開CIのpreviewで判明した`5585_4_Dlgs_Index0_Text`の重複ownerは、監査値を既存ownerへ移し新規ownerから削除して解消した。訳文判断は変更していない。

## FACT_DOUBT

密偵報告の確度、攻撃開始時刻と戦況、曹煜天の所在、洪飛が莫問を知る範囲、洪飛が現れた真の目的を確定していない。

## ALLUSION_REVIEW

候補なし。

## encoding結果

quality auditで確定した12候補だけを収録した。保持11行、locres、pak、audit status、verified checkpointは変更していない。
