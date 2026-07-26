# 宇文逸↔莫問 第105〜108束 適用記録

- 日付: 2026-07-27
- PR: #133
- CI列車: `yuwen-mowen-train-13`
- release: `yuwen-mowen-train-13-r1`
- release evidence: `None`
- 場面: `5825_1` / `5828_1` / `5829_5` / `5831_3` / `5831_4` / `5897_6` / `5923_2` / `5926_2` / `5926_3` / `5928_1` / `5928_2`
- reviewed keys: 58
- unique reviewed rows: 58
- 修正キー: 9
- 現訳保持キー: 49
- 人物ペア新規: 1
- プロジェクト新規: 1
- cross-register収録: 0
- 既存owner更新: 8
- 人物ペア累計: 1170
- プロジェクト全体累計: 1546
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

この記録はApply workflowがmanifestと実owner件数から自動生成した。CI run ID、CI HEAD、asset HEADはrelease evidenceで確定する。

## 正式束

### 第105束 `5825_1 + 5828_1 + 5829_5`

- reviewed rows: 19
- fix keys: 4
- keep keys: 15
- existing owner updates: 4
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH105_2026-07-27.md`

### 第106束 `5831_3 + 5831_4 + 5897_6 + 5923_2`

- reviewed rows: 13
- fix keys: 1
- keep keys: 12
- existing owner updates: 1
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH106_2026-07-27.md`

### 第107束 `5926_2 + 5926_3 + 5928_1`

- reviewed rows: 18
- fix keys: 4
- keep keys: 14
- existing owner updates: 3
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH107_2026-07-27.md`

### 第108束 `5928_2`

- reviewed rows: 8
- fix keys: 0
- keep keys: 8
- existing owner updates: 0
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH108_2026-07-27.md`

## 機械検証

- Relation / Crossを同一release HEADで成功させた後にApplyを実行する
- 未適用差分0件、locres、pak、LFS、lint、関係抽出、回帰を確認する
- この記録を生成してからaudit_status.jsonを更新する
- final run IDとHEADはrelease evidenceおよびCURRENT_WORKへ固定する
