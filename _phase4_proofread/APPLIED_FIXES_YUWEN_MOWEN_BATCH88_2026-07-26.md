# 宇文逸↔莫問 第85〜88束 適用記録

- 日付: 2026-07-26
- PR: #122
- CI列車: `yuwen-mowen-train-08`
- release: `yuwen-mowen-train-08-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_08.json`
- 品質条件: `quality_passed` / low yieldなし
- 場面: `5603_1` / `5610_2` / `5611_8` / `5637_1` / `5646_1`
- reviewed keys: 45
- unique reviewed rows: 45
- 修正キー: 18
- unique修正行: 18
- 現訳保持キー: 27
- 人物ペア新規: 0
- プロジェクト新規: 2
- cross-register収録: 2
- 既存owner更新: 16
- 人物ペア累計: 1165
- プロジェクト全体累計: 1541
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

CI run ID・CI HEAD・asset HEADの機械正本はrelease evidenceとする。この適用記録は、適用した翻訳判断・所有・件数の正本である。

## 第85束 `5603_1`

11キーを収録した。莫棄の親しい警告と玄火教への疑念、斬無刑の硬質な任務報告、宇文逸の慎重な応答を場面の急ぎと情報状態へ戻した。

- 人物ペア既存owner更新: 9キー
- 莫棄・斬無刑のcross-register新規: 2キー

`信誓旦旦`は一般成句として処理し、玄火教の関与や不在理由を推測以上へ強めていない。

## 第86束 `5610_2 + 5611_8`

5キーを監査し、全行を保持した。短い移動・追跡場面の勢いと、山頂の異変を先取りしない情報境界を維持した。

## 第87束 `5637_1`

2キーを既存ownerへ再収録し、粗末な瓶への疑問と仕掛けを見抜く流れを自然化した。瓶を隠した目的は推理以上へ確定していない。

## 第88束 `5646_1`

5キーを既存ownerへ再収録し、暗道へ進む決断、宇文逸の危険評価、莫問の同行判断を人物関係と行動の流れへ戻した。出口、曹煜天の所在、各派の到着時刻は補っていない。

## 所有と件数

人物ペアownerは既存16キーの値更新のみで、新規キーはないため累計1165を維持した。

莫棄・斬無刑の2キーを新しいcross-register ownerへ収録したため、プロジェクト全体累計は1539から1541へ増えた。

## 機械検証

- Relation audit extraction、Cross register QA、Apply curated localization fixesを同一CI HEADで成功させる
- 未適用差分0件を確認する
- locres、pak、LFS、validate、register lint、関係抽出、単体テスト、回帰走査を確認する
- bot生成asset HEADでプロジェクト全体1541、人物ペア1165を機械集計する
- final run ID、CI HEAD、asset HEAD、phase2 runはrelease evidenceとCURRENT_WORKへ固定する
- public中に次候補`5649_1`のpreparation・quality audit・encodingは行わない

この記録とrelease evidenceを使って第88束checkpointを確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
