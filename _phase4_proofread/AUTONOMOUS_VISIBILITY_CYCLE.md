# 自律visibility cycle契約

## 目的

現在の手動public/private反復を、安全性を保ったまま将来のscheduled automationへ移せる形に固定する。

翻訳の準備・品質監査・収録・凍結という認知段階は維持する。ただし、段階境界は内部checkpointであり、通常の会話終了地点ではない。

## 一cycleの標準完了地点

### private作業

一度の「作業の続きを」で、正常なら次まで連続して進む。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> private preflight -> PR ready -> ready_for_public_ci`

`private_preparation`、`private_quality_audit`、`private_encoding`で、追加の「作業の続きを」を要求しない。

### public作業

public確認後、正常なら次まで連続して進む。

`in_public_ci -> orchestrator success -> state finalization -> phase2 success -> review thread 0 -> awaiting_private_merge`

Relation、Cross、Apply、phase2の間で追加の継続指示を要求しない。

### private復帰後

private確認後、検証済みHEADをsquash統合し、輸送を`merged`へ確定する。次waveのpreparationは、統合確認後の別cycleとして開始する。

## cycle_control

`PRIVATE_STAGE_STATE.json.cycle_control`をschedulerとcold startの機械入口とする。

必須項目:

- `status`: `running | paused | target_reached`
- `private_completion_target`: `ready_for_public_ci`
- `public_completion_target`: `awaiting_private_merge`
- `post_public_completion_target`: `merged`
- `continuation_required`
- `stop_reason`
- `exact_next_action`
- `last_safe_checkpoint`

### running

正常な作業途中。`continuation_required=true`、`stop_reason=null`、`exact_next_action`必須。

### paused

例外停止。`continuation_required=true`で、許可された`stop_reason`と機械実行可能な`exact_next_action`を必須とする。

許可理由:

- `user_decision_required`
- `checker_failure`
- `external_dependency_unavailable`
- `turn_capacity_checkpoint`

### target_reached

visibility変更またはcycle完了を待つ正常停止。`continuation_required=false`、`stop_reason=null`、`exact_next_action=null`とする。

許可checkpoint:

- `ready_for_public_ci`
- `awaiting_private_merge`
- `merged`

## scheduler向け境界

visibility変更はリポジトリ内workflowの責務外とする。schedulerはrepository metadataと`cycle_control`を照合してから外部操作を行う。

- private + `ready_for_public_ci`: public窓を開く候補
- public + `awaiting_private_merge`: privateへ戻す候補
- private + `merged`: cycle完了

schedulerはPR番号、PR HEAD、train ID、transport statusを冪等キーとして保持し、同じ状態へvisibility変更やラベル付与を重複実行しない。

## 禁止

- 内部段階を正常な会話終了地点として扱うこと
- `paused`なのに理由や次操作を残さないこと
- public中に翻訳判断を再開すること
- phase2成功前に`awaiting_private_merge`へ進めること
- private確認前にmergeすること
- merge完了前に次waveを始めること
