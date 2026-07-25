# 宇文逸↔莫問 第82束レビュー

- 日付: 2026-07-26
- train: `yuwen-mowen-train-07`
- private stage: `private_encoding`
- 場面: `5583_1`
- preparation: `_phase4_proofread/PREPARATION_YUWEN_MOWEN_SCENE5583_1_2026-07-26.md`
- quality audit: `_phase4_proofread/AUDIT_YUWEN_MOWEN_SCENE5583_1_2026-07-26.md`
- source artifact: Relation audit extraction run `30169356037`
- status: `reviewed_pending_ci`

## 場面機能

法場で清虚道長へ復命する。清虚の称賛、宇文逸と莫問の応答を経て、宇文逸の顔色と遼城帰還の話へ移る。

## 収録した修正

- `5583_1_Dlgs_Index2_Text`: 清虚の期待を硬い名詞構文から口頭説明へ戻した。
- `5583_1_Dlgs_Index3_Text`: `後生可畏`の称賛を清虚の師モードで自然に成立させた。
- `5583_1_Dlgs_Index5_Text`: 阻止済みの企みを振り返る反実仮想の時制を整えた。
- `5583_1_Dlgs_Index11_Text`: `看来`を予想どおりの`やはり`ではなく、その場の推認へ戻した。

## 保持

残る8行は、復命の礼、謙遜、称賛から心配への切替、遼城帰還の言いさしを保つため変更していない。

## 所有

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json`: 莫問の`Index5`
- `_phase4_proofread/fixes_relation_yuwen_qingxu_20260723_batch2.json`: 清虚の`Index2`、`Index3`、`Index11`

清虚の既存師モードownerを優先し、新規ownerは作っていない。

## FACT_DOUBT

清虚が宇文逸の顔色だけで遼城の事情を知ったとは確定せず、天龍幇の計画破壊と峋谷関解囲の功績配分、宇文逸が遼城で知った内容を補っていない。

## ALLUSION_REVIEW

`後生可畏`は一般成句として解決した。典拠説明は訳文へ追加していない。

## encoding結果

quality auditで確定した4候補だけを収録した。保持8行、locres、pak、audit status、verified checkpointは変更していない。
