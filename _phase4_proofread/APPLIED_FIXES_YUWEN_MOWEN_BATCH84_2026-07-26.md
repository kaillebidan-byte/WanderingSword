# 宇文逸↔莫問 第81〜84束 適用記録

- 日付: 2026-07-26
- PR: #120
- CI列車: `yuwen-mowen-train-07`
- release: `yuwen-mowen-train-07-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_07.json`
- 品質条件: `quality_passed` / low yieldなし
- 場面: `5581_7` / `5581_8` / `5583_1` / `5583_2` / `5585_4` / `5586_3` / `5586_5`
- reviewed keys: 57
- unique reviewed rows: 57
- 修正キー: 28
- unique修正行: 28
- 現訳保持キー: 29
- 人物ペア新規: 0
- プロジェクト新規: 10
- cross-register収録: 7
- 既存owner更新・移管: 18
- 人物ペア累計: 1165
- プロジェクト全体累計: 1539
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

CI run ID・CI HEAD・asset HEADの機械正本はrelease evidenceとする。この適用記録は、適用した翻訳判断・所有・件数の正本である。

## 第81束 `5581_7 + 5581_8`

2キーを既存ownerへ再収録し、復命先が異なる二分岐を混同せず、`前の法場`を前方位置として自然化した。

## 第82束 `5583_1`

4キーを収録し、清虚の称賛、`後生可畏`、莫問の反実仮想、清虚の推認を人物声と情報状態へ戻した。

## 第83束 `5583_2`

10キーを収録し、法場説明、秘匿理由、宇文逸の理解、攻撃前夜の案内と欧陽雪への礼を自然化した。清虚の情報源や後続作戦は補っていない。

## 第84束 `5585_4 + 5586_3 + 5586_5`

12キーを収録した。

- 人物ペア既存owner更新: 5キー
- 既存人物ペアownerからcross-register ownerへの移管: 6キー
- cross-register新規: 1キー

急報の確度、宇文逸の言いさし、欧陽雪の謙遜、洪飛の評価・乞食自称・警告を修正した。公開CI previewで検出したowner競合は、訳文判断を変えずに既存owner更新と横断owner移管で解消した。

## 所有と件数

第82・83束で清虚ownerへ9キーを新規追加し、第84束でcross-registerへ1キーを新規追加したため、プロジェクト全体累計は1529から1539へ増えた。

第84束で洪飛・欧陽雪の6キーを宇文逸↔莫問ownerからcross-register ownerへ移管したため、人物ペア累計は1171から1165へ減った。翻訳キー自体を削除したのではなく、所有範囲を正した結果である。

## 機械検証

- Relation audit extraction、Cross register QA、Apply curated localization fixesを同一人手HEADで成功
- Applyで28修正を反映し、未適用差分0件を確認
- locres、pak、LFS、validate、register lint、関係抽出、単体テスト、回帰走査成功
- bot生成HEADでプロジェクト全体1539、人物ペア1165を機械集計
- final run ID、CI HEAD、asset HEAD、state-only phase2 runはrelease evidenceへ固定する
- public中に第85束候補`5603_1`のpreparation・quality audit・encodingは行っていない

この記録とrelease evidenceを使って第84束checkpointを確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
