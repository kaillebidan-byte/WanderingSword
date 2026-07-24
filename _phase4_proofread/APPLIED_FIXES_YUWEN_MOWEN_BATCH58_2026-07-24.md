# 宇文逸↔莫問 第58束 適用記録

- 日付: 2026-07-24
- PR: #98
- 場面: `5370_1`・`5388_1`・`5389_2`・`5389_4`
- 通読行数: 19
- 修正キー: 5
- 現訳保持: 14
- 人物ペア新規: 3
- プロジェクト全体新規: 5
- 人物ペア累計: 1163
- プロジェクト全体累計: 1514
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

## 適用する修正束

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260724_batch58.json` — 3キー
- `_phase4_proofread/fixes_cross_register_fangkuohai_injury_threat_20260724.json` — 2キー

## 主な校正判断

- 莫問の大会開始判断を、読点でつないだ実況文から短い観察へ戻した
- 宇文逸の返答を復命調ではなく簡潔な`はい`へした
- 負傷後の咳を`ゴホッ、ゴホッ……`として身体状態に合う発声へ直した
- 方闊海の勝ち誇りと見下しを、粗暴な人物声として一息で出る台詞へ戻した
- 次の一刀の脅しを、説明的な`保証はない`から直接的な凄みへ再構成した
- 既存第5束11キーと、未所有だが成立する莫問2キーは変更していない

## 機械検証

- locres反映、pak再生成、全1514キー差分0を恒久workflowで確認する
- register lint、Relation audit extraction、Cross register QA、回帰走査、pak実体・LFSを確認する

ゲームフォルダへの配置とゲーム内確認は行わない。
