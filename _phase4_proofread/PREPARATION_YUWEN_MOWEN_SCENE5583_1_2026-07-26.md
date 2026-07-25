# 宇文逸↔莫問 `5583_1` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-07`
- translation judgment: 未実施
- source run: `30169356037`
- artifact id: `8622473127`
- artifact digest: `sha256:497d03bf8bb1eeb1723b4064025486e626ca59fa26ea2bd4b2ecf2be9e32ad19`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5583_1_2026-07-26.json`

## 場面境界

法場で清虚道長へ復命する場面。清虚が一行を称え、宇文逸と莫問が応じた後、宇文逸の顔色と遼城帰還の話へ移る。

`5581_8`からの連続が明示的。`5581_7`は別分岐として参照する。duplicate locationはない。

## 所有境界

既存ownerは`_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json`。

既存キー:

- `5583_1_Dlgs_Index0_Text`
- `5583_1_Dlgs_Index4_Text`
- `5583_1_Dlgs_Index5_Text`
- `5583_1_Dlgs_Index9_Text`

その他の抽出キーは未所有として保持する。ownerはquality audit後のencodingまで変更しない。

## quality auditへ渡す確認軸

- 宇文逸の拝礼と謙遜が弟子として自然か
- 莫問の対清虚registerと発話役割を保てているか
- 清虚の称賛から心配への切り替わりを保てているか
- 後続場面の内容を先取りしていないか

ALLUSION_REVIEW候補は`後生可畏`。

fix / keep判断、修正JSON、owner新設、正式束番号、件数集計は行っていない。
