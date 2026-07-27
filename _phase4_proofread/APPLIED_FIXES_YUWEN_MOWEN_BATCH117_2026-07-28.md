# 宇文逸↔莫問 第115〜117束 適用記録

- 日付: 2026-07-28
- PR: #142
- CI列車: `yuwen-mowen-train-17`
- release: `yuwen-mowen-train-17-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_17.json`
- 場面: `9150_3` / `9150_4` / `9154_2` / `9209_2` / `9210_1` / `9223_6` / `9228_2` / `9229_2` / `9230_2`
- reviewed keys: 51
- unique reviewed rows: 51
- 修正キー: 22
- 現訳保持キー: 29
- 人物ペア新規: 33
- プロジェクト新規: 33
- cross-register収録: 0
- 既存owner更新: 1
- 人物ペア累計: 1221
- プロジェクト全体累計: 1597
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

この記録はApply workflowがmanifestと実owner件数から自動生成した。CI run ID、CI HEAD、asset HEADはrelease evidenceで確定する。

## 正式束

### 第115束 `9150_3 + 9150_4`

- reviewed rows: 8
- fix keys: 1
- keep keys: 7
- existing owner updates: 1
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH115_2026-07-27.md`

### 第116束 `9154_2 + 9209_2 + 9210_1 + 9223_6`

- reviewed rows: 13
- fix keys: 0
- keep keys: 13
- existing owner updates: 0
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH116_2026-07-27.md`

### 第117束 `9228_2 + 9229_2 + 9230_2`

- reviewed rows: 30
- fix keys: 21
- keep keys: 9
- existing owner updates: 0
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH117_2026-07-27.md`

## 機械検証

- Relation / Crossを同一release HEADで成功させた後にApplyを実行する
- 未適用差分0件、locres、pak、LFS、lint、関係抽出、回帰を確認する
- この記録を生成してからaudit_status.jsonを更新する
- final run IDとHEADはrelease evidenceおよびCURRENT_WORKへ固定する
