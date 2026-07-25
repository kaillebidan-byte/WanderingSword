# 宇文逸↔莫問 `5585_4` / `5586_3` / `5586_5` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-07`
- translation judgment: 未実施
- source run: `30169356037`
- artifact id: `8622473127`
- artifact digest: `sha256:497d03bf8bb1eeb1723b4064025486e626ca59fa26ea2bd4b2ecf2be9e32ad19`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5585_4_5586_3_5586_5_2026-07-26.json`

## 場面境界

翌朝、莫問が不風山の急変を伝え、一行が出発する。その後、宇文逸と欧陽雪が洪飛に再会し、莫問を紹介する流れと、莫問が洪飛へ名乗って礼を取る流れをまとめる。

`5586_3`は莫問紹介まで、`5586_5`は紹介後の対面を含む連続候補。三familyにduplicate locationはない。移動中の出来事は補わない。

## 所有境界

現行の宇文逸↔莫問owner内に、このpacketの抽出キーは確認されていない。全キーを未所有として保持する。

ownerはquality audit後のencodingまで新設・変更しない。

## quality auditへ渡す確認軸

- 莫問の急報説明で伝聞・推測・各派決定を区別しているか
- 宇文逸の急ぐ反応が師兄への過剰な敬体または軽すぎる調子になっていないか
- 洪飛と宇文逸の軽口、欧陽雪の礼、莫問の初対面の礼を話者ごとに分けているか
- 宇文逸による紹介と莫問自身の名乗りを削っていないか
- 洪飛の警告を具体的な企みの確定情報へ強めていないか

ALLUSION_REVIEW候補は現時点でない。

FACT_DOUBTは、密偵報告の確度、戦況、洪飛の認識と目的を本文以上に確定しない。

fix / keep判断、修正JSON、owner新設、正式束番号、件数集計は行っていない。
