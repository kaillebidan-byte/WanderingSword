# 宇文逸↔莫問 `5581_7` / `5581_8` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-07`
- translation judgment: 未実施
- source: Relation audit extraction run `30169356037`
- artifact: `relation-audit-evidence` / `yuwen_mowen.json`
- artifact id: `8622473127`
- artifact digest: `sha256:497d03bf8bb1eeb1723b4064025486e626ca59fa26ea2bd4b2ecf2be9e32ad19`
- artifact head: `6f0648976b548164a30fb3b65bc0e70c310f293b`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5581_7_5581_8_2026-07-26.json`

## 場面境界

黎城到着後、瑶姫と別れた直後の分岐。莫問が宇文逸を法場へ促し、復命相手が清霄師伯か師父かで分かれる。

二つは鏡写しの分岐familyで、同時発生として結合しない。いずれもduplicate_locationsはない。

## 話者順

莫問 → 宇文逸 → 莫問 → 宇文逸

## 所有境界

既存ownerは`_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json`。

既存ownerに含まれるキー:

- `5581_7_Dlgs_Index0_Text`
- `5581_7_Dlgs_Index1_Text`
- `5581_8_Dlgs_Index0_Text`
- `5581_8_Dlgs_Index1_Text`

未所有キーはない。

ownerはこの段階では変更しない。quality auditで修正判断が確定した場合だけ、encoding段階で更新する。

## quality auditへ渡す確認軸

- 莫問の兄弟子としての簡潔な促しを、命令的または過度に丁寧な調子へ変えていないか
- 清霄師伯と師父という復命相手の差を壊していないか
- 法場をこの二場面にない処刑描写や具体的用途で補っていないか
- 宇文逸の短い同意を儀礼的な返答へ整えすぎていないか

## 未確定ゲート

ALLUSION_REVIEW候補は現時点でない。

FACT_DOUBT候補:

- 5581_7と5581_8を同一時系列で同時に起きた行動へ結合しない
- 法場の用途、状態、そこで起きた出来事をこの二場面だけから補わない
- 復命する内容、清霄師伯または師父の反応、後続命令を先取りしない

## この段階で行っていないこと

fix / keep判断、修正JSON、owner新設、正式な束完了、件数集計、locres書き戻し、pak再生成は行っていない。
