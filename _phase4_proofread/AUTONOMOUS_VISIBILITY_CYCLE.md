# 自律作業cycle契約

## 目的

現在の手動private/public/private反復を、まず安全で決定的な形に固定する。

将来はrepositoryをpublicのまま維持し、現在privateで行っている準備・品質監査・収録と、public CI・統合までをscheduled automationで一続きに実行する。その将来モードでも同じ段階機械と`cycle_control`を再利用する。

翻訳の準備・品質監査・収録・凍結という認知段階は維持する。ただし、段階境界は内部checkpointであり、通常の会話終了地点ではない。

## 現在の手動cycle

### private作業

一度の「作業の続きを」で、正常なら次まで連続して進む。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> private preflight -> PR ready -> ready_for_public_ci`

`private_preparation`、`private_quality_audit`、`private_encoding`で、追加の「作業の続きを」を要求しない。

private中はGitHub Actionsを使わない。checkerは作業環境で実行し、GitHub-hosted runnerが必要な輸送検査だけをpublic CI窓へ送る。

private完了時は次の一命令を正規入口とする。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

private modeではこの入口がcurrent waveのcandidate ownership snapshotを全fix owner実測値へ自動更新してから、strict UTF-8 JSON、前releaseとの差分、current candidate範囲、manifest、quality gate、輸送状態、回帰を検査する。表示された変更をrelease HEADへ一括commitし、その後public CI窓を開くまでrelease filesを編集しない。

### public作業

public確認後、正常なら次まで連続して進む。

`in_public_ci -> orchestrator success -> state finalization -> phase2 success -> review thread 0 -> awaiting_private_merge`

Relation、Cross、Apply、phase2の間で追加の継続指示を要求しない。

orchestratorはApplyの結果として`ci_head`、`asset_head`、`apply_changed`を`release-finalization-inputs-<PR>` artifactへ出力する。finalizationはこの値を正本とし、bot commitの有無からHEADを推測しない。

release evidence、CURRENT_WORK、manifest、private stage、handoffを更新した後、push前に次を成功させる。

```bash
python _tools/check_release_finalization.py --with-tests
```

このローカルphase2相当検査がstrict UTF-8 JSON、release lineage、handoff、owner、manifest、quality、minimal reservation、回帰を確認する。GitHub上のphase2はこれに加えてworkflow runとPR attachmentを検証する。

### private復帰後

private確認後、検証済みHEADをsquash統合し、輸送を`merged`へ確定する。次waveのpreparationは、統合確認後の別cycleとして開始する。

## cycle_control

`PRIVATE_STAGE_STATE.json.cycle_control`をcold start、現在の手動cycle、将来のschedulerの共通機械入口とする。

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

現在の手動cycleではvisibility変更またはcycle完了を待つ正常停止。`continuation_required=false`、`stop_reason=null`、`exact_next_action=null`とする。

許可checkpoint:

- `ready_for_public_ci`
- `awaiting_private_merge`
- `merged`

## public-only移行の観測条件

常時public化を自動決定しない。次の条件を満たす翻訳release cycleが**2回連続**した時点で、`always_public_full_pipeline`への移行設計を検討対象にする。

- private preflightが公開前に一度で成功し、公開後のowner snapshot・train scope修復がない
- 最初のorchestrator runが成功し、人間の修復push、手動再ラベル、workflow権限修正がない
- `release-finalization-inputs`の値をそのまま使用し、asset HEADまたはlineageの修正がない
- push前のlocal finalization検査が成功し、最初のphase2 runが成功する
- 未解決review threadが0で、private復帰後の統合前に状態修正を必要としない

一つでも修復push、再ラベル、証跡補正、転送破損、lineage修正が発生したcycleはsmooth cycleへ数えず、連続数を0へ戻す。2回到達は移行の検討開始条件であり、visibility変更を自動実行する条件ではない。

## 将来のscheduled mode

将来モードは`always_public_full_pipeline`とする。repository visibilityをschedulerが変更する方式ではない。

- repositoryはpublicのまま維持する。
- 現在privateで行う`private_preparation`、`private_quality_audit`、`private_encoding`も、段階境界と禁止事項を維持したままscheduled workerが実行する。
- `private_*`は認知段階の識別子であり、repository visibilityやprivate Actions利用を意味しない。
- 同じ実行でtranslation freeze、preflight、orchestrator、Apply、phase2、review thread確認、squash mergeまで進める。
- schedulerはvisibilityを変更せず、時刻起動、排他制御、冪等性、失敗時停止、再開だけを担当する。
- publicであることを翻訳判断の自由化とは解釈しない。各段階の権限と認知分離は現在の契約をそのまま使う。
- private Actions、private runner、月間private Actions利用枠の回復を前提条件へ入れない。

将来のschedulerはPR番号、PR HEAD、train ID、stage、transport statusを冪等キーとして保持し、同じ段階、ラベル、Apply、mergeを重複実行しない。

## 現在のscheduler境界

このPRではscheduled workflow、時刻設定、常時public運用を実装しない。現在は手動のvisibility反復を安全に確定することだけを対象とする。

現在のvisibility変更は引き続きユーザーの外部操作であり、各応答の最初にrepository metadataを確認する。

## 禁止

- 内部段階を正常な会話終了地点として扱うこと
- `paused`なのに理由や次操作を残さないこと
- 現在のmanual public CI窓で翻訳判断を再開すること
- phase2成功前に`awaiting_private_merge`へ進めること
- 現在の手動cycleでprivate確認前にmergeすること
- merge完了前に次waveを始めること
- 将来schedulerがrepository visibilityを切り替える前提を置くこと
- 将来schedulerがprivate Actions利用枠の回復を待つ前提を置くこと
- 常時public化だけを理由に段階分離・owner検査・quality gateを省略すること
