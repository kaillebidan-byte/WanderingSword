# 宇文逸↔莫問 `5583_2` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-07`
- translation judgment: 未実施
- source run: `30169356037`
- artifact id: `8622473127`
- artifact digest: `sha256:497d03bf8bb1eeb1723b4064025486e626ca59fa26ea2bd4b2ecf2be9e32ad19`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5583_2_2026-07-26.json`

## 場面境界

宇文逸が清虚も遼城の事情を知っていたと確かめる。清虚が秘匿理由と天龍幇の残虐さを説明し、その後、休息・合流・警戒と莫問への世話役の指示へ移る。

Relation artifactではIndex6を含まない18行が抽出対象。対象familyにduplicate locationはない。抽出外行を推測で補わない。

## 所有境界

既存owner:

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json`: `5583_2_Dlgs_Index0_Text`、`Index7`、`Index8`、`Index14`、`Index17`
- `_phase4_proofread/fixes_relation_yuwen_qingxu_20260723_batch2.json`: `5583_2_Dlgs_Index2_Text`、`Index5`、`Index11`、`Index18`

その他の抽出キーは未所有として保持する。ownerはquality audit後のencodingまで変更しない。

## quality auditへ渡す確認軸

- 清虚の説明を自己正当化へ強めていないか
- 宇文逸の理解と仇討ちへの言及を過剰に膨らませていないか
- 清虚の対欧陽雪registerと莫問への師命を分けているか
- 莫問の返答を父親的・監視的な保護責任へ強めていないか

ALLUSION_REVIEW候補は現時点でない。

FACT_DOUBTは、秘匿情報の範囲、法場の具体的描写、後続作戦、莫問の経験の過剰拡張を避ける。

fix / keep判断、修正JSON、owner新設、正式束番号、件数集計は行っていない。
