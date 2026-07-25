# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、private段階は`PRIVATE_STAGE_STATE.json`、候補入力は`CANDIDATE_YUWEN_MOWEN_SCENE5540_4_2026-07-25.json`。

## 現在地

- 実visibility: private（GitHub metadataで確認）
- active draft PR: #118
- active branch: `agent/yuwen-mowen-train-06`
- operation mode: `private_translation_work`
- private stage: `private_quality_audit`
- preparation: complete
- checkpoint: 第76束 / 人物ペア1171 / 全1529 / 未適用0件
- release checkpoint: `yuwen-mowen-train-05-r2` / verified
- build: `verified_not_deployed`
- game verification: `not_started`

## 四段階実走の状態

### 1. private preparation — 完了

対象`5540_4`について、次だけを固定した。

- Relation artifactの原文・現訳・話者順
- 直前`5536_3` / `5536_4`と後続`5551_2` / `5572_6` / `5572_9`
- 重複familyの有無
- 既存ownerと未所有キー
- FACT_DOUBT候補とquality auditの確認軸

証拠:

- `_phase4_proofread/PREPARATION_YUWEN_MOWEN_SCENE5540_4_2026-07-25.md`
- `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5540_4_2026-07-25.json`

この段階ではfix / keep判断、修正JSON、owner新設、正式な束完了、件数集計、locres、pakを扱っていない。

### 2. private quality audit — active

次は`_phase4_proofread/AUDIT_YUWEN_MOWEN_SCENE5540_4_2026-07-25.md`へ、次の順で翻訳判断だけを記録する。

1. fix candidatesと理由
2. 疑ったが保持した箇所
3. 追加文脈が必要な箇所
4. FACT_DOUBTとALLUSION_REVIEWの分離

この段階では修正JSON、owner、正式な束、manifest件数、release残量を触らない。

### 3. private encoding — 未開始

quality auditで確定した判断だけを収録する。新しい疑義が出た場合はquality auditへ戻す。

### 4. ready for public CI — 未開始

翻訳判断と収録を凍結した後にだけ移る。

## 現在の対象場面

`5540_4`: 瑶姫が合流し、宇文逸が黎城へ向かう前に遼城へ戻る意向を示す。莫問と欧陽雪が同行を申し出る。瑶姫は遼城の状況を言いさして伏せる。

quality auditでは、瑶姫の軽さと含み、宇文逸の叔父への推測、莫問の保護責任、欧陽雪の同行意思、発話の遮られ方を原文・現訳・前後から判断する。

## drift

PR #117はすでにsquash統合済み。旧申し送りの「#117統合待ち」は履歴であり、現行作業ではない。

次の作業はPR #118のbranch上でquality auditを進めること。public化はまだ不要。
