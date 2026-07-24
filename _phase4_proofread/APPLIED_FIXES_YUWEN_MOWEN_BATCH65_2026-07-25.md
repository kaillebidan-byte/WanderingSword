# 宇文逸↔莫問 第62〜65束 適用記録

- 日付: 2026-07-25
- PR: #111
- CI列車: `yuwen-mowen-train-02`
- release: 通常条件 `bundle_count=4`
- 場面: `5455_1` / `5501_2` / `5502_5` / `5502_6`
- 通読行数: 30
- 修正キー: 8
- 現訳保持: 22
- 既存第7束の再改訂: 5
- 清虚cross-register新規: 2
- 人物ペア新規: 1
- 人物ペア累計: 1167
- プロジェクト全体累計: 1521
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`
- Relation run: `30132675608`
- Cross run: `30132675610`
- Apply run: `30132675582`
- CI HEAD: `4d48cf98e3e86d1f082437e483c516289d1ea24b`
- applied assetsを含むHEAD: `cb6f660e5277a2d9fd75aac9fd82b28741140cd0`

## 適用した修正束

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json` — 第63〜65束の既存所有5キーを再改訂
- `_phase4_proofread/fixes_relation_yuwen_mowen_20260725_batch62.json` — 莫問1キーを新規追加
- `_phase4_proofread/fixes_cross_register_qingxu_sword_manor_departure_20260725.json` — 清虚2キーを新規追加

## 主な校正判断

- 清虚の先行・引率指示を自然な師モードへ戻し、汎用の「お前」を避けた
- 莫問の復命、市中で無辜を守る制止、情報拡散への不審を直訳調から整えた
- 欧陽雪の補佐推論では「行方」を「足取り」へ戻した
- 宇文逸の念押しされた指示と迂回提案を自然な敬体へ整えた
- 瑶姫の千陵渡の位置説明を疑問形へ崩さず、地モードの余裕を保った
- 尾行者、黒幕、目的、人数、旅程を原文以上に確定していない

## 機械検証

- Relation audit extraction run `30132675608` 成功
- Cross register QA run `30132675610` 成功
- Apply curated localization fixes run `30132675582` 成功
- locres反映、pak再生成、LFS確認成功
- 全修正束の未適用0件
- validate、register lint、関係抽出、単体テスト、回帰走査成功
- bot書き戻し後のRelation / Cross / Apply追加起動0件
- audit_statusは全1521キー、人物ペア1167キーへ更新済み

この記録を監査索引へ同期した後、第65束のverified checkpointを確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
