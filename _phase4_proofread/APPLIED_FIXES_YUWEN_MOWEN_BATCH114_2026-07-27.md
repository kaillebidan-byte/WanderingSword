# 宇文逸↔莫問 第113〜114束 適用記録

- 日付: 2026-07-27
- PR: #141
- CI列車: `yuwen-mowen-train-16`
- release: `yuwen-mowen-train-16-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_16.json`
- 場面: `6195_3` / `6198_3` / `6206_3` / `6213_1` / `6214_4` / `6229_1`
- reviewed keys: 40
- unique reviewed rows: 40
- 修正キー: 8
- 現訳保持キー: 32
- 人物ペア新規: 6
- プロジェクト新規: 6
- cross-register収録: 0
- 既存owner更新: 8
- 人物ペア累計: 1188
- プロジェクト全体累計: 1564
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

この記録はApply workflowがmanifestと実owner件数から自動生成した。CI run ID、CI HEAD、asset HEADはrelease evidenceで確定する。

## 正式束

### 第113束 `6195_3 + 6198_3 + 6206_3`

- reviewed rows: 19
- fix keys: 5
- keep keys: 14
- existing owner updates: 5
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH113_2026-07-27.md`

### 第114束 `6213_1 + 6214_4 + 6229_1`

- reviewed rows: 21
- fix keys: 3
- keep keys: 18
- existing owner updates: 3
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH114_2026-07-27.md`

## 機械検証

- Relation / Crossを同一release HEADで成功させた後にApplyを実行する
- 未適用差分0件、locres、pak、LFS、lint、関係抽出、回帰を確認する
- この記録を生成してからaudit_status.jsonを更新する
- final run IDとHEADはrelease evidenceおよびCURRENT_WORKへ固定する
