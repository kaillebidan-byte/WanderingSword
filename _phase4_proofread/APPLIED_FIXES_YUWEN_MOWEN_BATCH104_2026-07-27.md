# 宇文逸↔莫問 第101〜104束 適用記録

- 日付: 2026-07-27
- PR: #131
- CI列車: `yuwen-mowen-train-12`
- release: `yuwen-mowen-train-12-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_12.json`
- 場面: `5805_3` / `5805_4` / `5807_1` / `5809_11` / `5809_2` / `5810_7` / `5810_9` / `5811_2` / `5811_3` / `5821_1`
- reviewed keys: 58
- unique reviewed rows: 58
- 修正キー: 12
- 現訳保持キー: 46
- 人物ペア新規: 3
- プロジェクト新規: 3
- cross-register収録: 0
- 既存owner更新: 9
- 人物ペア累計: 1169
- プロジェクト全体累計: 1545
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

この記録はApply workflowがmanifestと実owner件数から自動生成した。CI run ID、CI HEAD、asset HEADはrelease evidenceで確定する。

## 正式束

### 第101束 `5805_3 + 5805_4 + 5807_1`

- reviewed rows: 8
- fix keys: 3
- keep keys: 5
- existing owner updates: 2
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH101_2026-07-27.md`

### 第102束 `5809_11 + 5809_2`

- reviewed rows: 18
- fix keys: 2
- keep keys: 16
- existing owner updates: 2
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH102_2026-07-27.md`

### 第103束 `5810_7 + 5810_9`

- reviewed rows: 18
- fix keys: 6
- keep keys: 12
- existing owner updates: 5
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH103_2026-07-27.md`

### 第104束 `5811_2 + 5811_3 + 5821_1`

- reviewed rows: 14
- fix keys: 1
- keep keys: 13
- existing owner updates: 0
- cross-register keys: 0
- review record: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH104_2026-07-27.md`

## 機械検証

- Relation / Crossを同一release HEADで成功させた後にApplyを実行する
- 未適用差分0件、locres、pak、LFS、lint、関係抽出、回帰を確認する
- この記録を生成してからaudit_status.jsonを更新する
- final run IDとHEADはrelease evidenceおよびCURRENT_WORKへ固定する
