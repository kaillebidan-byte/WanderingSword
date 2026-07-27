# 宇文逸↔莫問 第111〜112束 適用記録

- 日付: 2026-07-27
- PR: #138
- CI列車: `yuwen-mowen-train-15`
- release: `yuwen-mowen-train-15-r1`
- release evidence: `None`
- 場面: `6151_2` / `6151_3` / `6155_1` / `6155_3` / `6158_5` / `6171_5`
- reviewed keys: 50
- unique reviewed rows: 50
- 修正キー: 8
- 現訳保持キー: 42
- 人物ペア新規: 12
- プロジェクト新規: 12
- cross-register収録: 0
- 既存owner更新: 7
- 人物ペア累計: 1182
- プロジェクト全体累計: 1558
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

この記録はApply workflowがmanifestと実owner件数から自動生成した。CI run ID、CI HEAD、asset HEADはrelease evidenceで確定する。

## 正式束

### 第111束 `6151_2 + 6151_3`

- reviewed rows: 25
- fix keys: 4
- keep keys: 21
- existing owner updates: 4
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH111_2026-07-27.md`

### 第112束 `6155_1 + 6155_3 + 6158_5 + 6171_5`

- reviewed rows: 25
- fix keys: 4
- keep keys: 21
- existing owner updates: 3
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH112_2026-07-27.md`

## 機械検証

- Relation / Crossを同一release HEADで成功させた後にApplyを実行する
- 未適用差分0件、locres、pak、LFS、lint、関係抽出、回帰を確認する
- この記録を生成してからaudit_status.jsonを更新する
- final run IDとHEADはrelease evidenceおよびCURRENT_WORKへ固定する
