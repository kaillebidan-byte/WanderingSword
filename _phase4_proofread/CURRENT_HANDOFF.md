# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、private段階は`PRIVATE_STAGE_STATE.json`、品質判断は`AUDIT_YUWEN_MOWEN_SCENE5540_4_2026-07-25.md`。

## 現在地

- 実visibility: private（GitHub metadataで確認）
- active draft PR: #118
- active branch: `agent/yuwen-mowen-train-06`
- operation mode: `private_translation_work`
- private stage: `private_encoding`
- preparation: complete
- quality audit: complete
- checkpoint: 第76束 / 人物ペア1171 / 全1529 / 未適用0件
- release checkpoint: `yuwen-mowen-train-05-r2` / verified
- build: `verified_not_deployed`
- game verification: `not_started`

## 四段階実走の状態

### 1. private preparation — 完了

`5540_4`の原文・現訳・前後・話者順、重複、既存owner、未所有キー、FACT_DOUBT候補を固定した。

証拠:

- `_phase4_proofread/PREPARATION_YUWEN_MOWEN_SCENE5540_4_2026-07-25.md`
- `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5540_4_2026-07-25.json`

### 2. private quality audit — 完了

品質判断は`_phase4_proofread/AUDIT_YUWEN_MOWEN_SCENE5540_4_2026-07-25.md`へ固定した。

修正候補:

- `5540_4_Dlgs_Index0_Text`: 瑶姫の笑いと伸ばしの不自然な衝突を修正
- `5540_4_Dlgs_Index5_Text`: 宇文逸の先行提案から消えた問いかけ機能を回復
- `5540_4_Dlgs_Index8_Text`: 欧陽雪の硬い`同行します`を対宇文逸の柔らかい同行意思へ戻す
- `5540_4_Dlgs_Index9_Text`: 瑶姫が伏せる遼城の不穏な様子への含みを回復

莫問の保護責任、半月の条件、宇文逸の叔父への推測などは原文の強さを越えていないため保持した。追加文脈が必要な箇所とALLUSION_REVIEW候補はない。

quality audit中には修正JSON、owner、正式な束、manifest件数を変更していない。

### 3. private encoding — active

監査記録で確定した上記候補だけを既存ownerへ収録する。対象候補はすべて既存owner内のキーであり、新規ownerを作る必要はない。

次の作業:

1. 既存fix fileへ確定候補だけを反映する
2. レビュー記録を作成する
3. 所有・FACT_DOUBT・ALLUSION_REVIEWを整形する
4. 最後に正式な束と輸送件数を確定する

encoding中に新しい訳文疑義が生じた場合は収録せず、`private_quality_audit`へ戻す。

### 4. ready for public CI — 未開始

翻訳判断と収録を凍結した後にだけ移る。現時点でpublic化は不要。

## drift

PR #117はすでにsquash統合済み。旧申し送りの「#117統合待ち」は履歴であり、現行作業ではない。
