# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、段階は`PRIVATE_STAGE_STATE.json`、公開CI入力は`NEXT_TASK_PACKET.json`。

## 現在地

- 実visibility: private（GitHub metadataで確認）
- active draft PR: #118
- active branch: `agent/yuwen-mowen-train-06`
- operation mode: `ready_for_public_ci`
- private stage: `ready_for_public_ci`
- checkpoint: 第76束 / 人物ペア1171 / 全1529 / 未適用0件
- last reviewed: 第80束
- release checkpoint: `yuwen-mowen-train-05-r2` / verified
- build: `verified_not_deployed`
- game verification: `not_started`

## train-06へ収録済み

- 第77束 `5540_4`: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH77_2026-07-25.md`
- 第78束 `5551_2`: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH78_2026-07-25.md`
- 第79束 `5572_6`: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH79_2026-07-25.md`
- 第80束 `5572_9 + 5581_5`: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH80_2026-07-26.md`

第80束では監査済み5候補だけを既存ownerへ収録した。

- 宇文逸の師兄への案じ方を自然な連続した問いへ戻した
- 瑶姫の不自然な復命表現を整理した
- `出手太狠`の暴力強度を回復した
- 欧陽雪の短い否定を柔らかな言いさしへ戻した
- `太想我`を恋愛へ固定せず、別れの軽口へ戻した

保持9行、新規owner、新規cross-registerには触れていない。未所有の莫問`5572_9_Dlgs_Index0_Text`は保持のため未所有のまま維持した。locres、pak、audit status、verified checkpointも未更新。

## release候補

- bundle_count: 4
- reviewed_rows / unique_reviewed_rows: 50
- reviewed_keys: 50
- fix_keys / unique_fix_rows: 16
- new_pair_keys: 0
- 修正率: 32%
- low_yield_detected: false
- quality_gate.release_decision: `quality_passed`
- manifest status: `ready_for_public_ci`

通常release条件は4束・40行・20修正のOR。第80束で4束かつ50行に達したため、次小束へ進まず公開CIへ送る。

一度、第81束候補のpreparation入口を作成したが、OR条件の再確認後に誤りと判定し、candidate・preparation・audit stubの3ファイルを削除済み。第81束の翻訳判断は一切行っていない。

## 次作業

公開CI窓を開く必要がある。

1. ユーザーがrepositoryをpublicへ変更する。
2. metadataでpublicを確認する。
3. draft PR #118をready化する。
4. Relation / Cross / Applyを同じCI HEADで実行する。
5. Applyの資産書き戻し後、release evidence、checkpoint、manifest、handoff、next packetを同じPR内で最終化する。
6. phase2 gateと未解決thread 0件を確認する。
7. private復帰を依頼し、metadataでprivateを確認する。
8. PR #118をsquash統合する。

public中に新しい翻訳判断、次小束追加、人物声・FACT_DOUBT・ALLUSION_REVIEWの変更は行わない。