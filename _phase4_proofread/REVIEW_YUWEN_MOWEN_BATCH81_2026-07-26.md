# 宇文逸↔莫問 第81束レビュー

- 日付: 2026-07-26
- train: `yuwen-mowen-train-07`
- private stage: `private_encoding`
- 場面: `5581_7` + `5581_8`
- preparation: `_phase4_proofread/PREPARATION_YUWEN_MOWEN_SCENES5581_7_5581_8_2026-07-26.md`
- quality audit: `_phase4_proofread/AUDIT_YUWEN_MOWEN_SCENES5581_7_5581_8_2026-07-26.md`
- source artifact: Relation audit extraction run `30169356037`
- status: `reviewed_pending_ci`

## 場面機能

黎城到着後の鏡写し分岐。莫問が宇文逸を法場へ促し、復命相手だけが清霄師伯または師父へ分かれる。

## 収録した修正

- `5581_7_Dlgs_Index0_Text`: `前の法場`を`この先の法場`へ改め、前方の移動先を示した。
- `5581_8_Dlgs_Index0_Text`: 同じ方向語の誤読を分岐間でそろえて修正した。

色タグ`<Y>法場</>`と話者接頭辞は保持した。

## 保持

宇文逸の`ああ、行こう。`二行を保持した。短い同意へ復命相手の差や説明を持ち込んでいない。

## 所有

4キーすべて既存owner `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json` にある。監査済み2キーだけを更新した。新規ownerはない。

## FACT_DOUBT

二分岐を同時発生として結合せず、法場の用途、復命内容、復命後の反応を補っていない。

## ALLUSION_REVIEW

候補なし。

## encoding結果

quality auditで確定した2候補だけを収録した。保持2行、locres、pak、audit status、verified checkpointは変更していない。
