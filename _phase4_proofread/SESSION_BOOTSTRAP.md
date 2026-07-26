# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、private waveとcycle完走状態は`PRIVATE_STAGE_STATE.json`を正本とする。

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の表現も再開モードとして扱う。URLや前回作業を聞き直さず、privateで許可された作業があれば同じ応答内で標準完了地点まで進む。

## visibility preflight

新規チャット・再開指示・作業継続指示では、最初の外部確認をGitHub repository metadata取得にする。結果が返るまで利用者向けの計画、開始宣言、途中報告を出さない。

利用者の申告ではなくmetadataを実visibilityの正本とする。取得失敗時は、作業開始を主張せず停止する。

## 起動順

1. repository metadataで実visibilityを確認する。
2. main、未統合PR、GitHub Actionsを確認する。
3. PRは開いているだけで現行作業と決めない。active / superseded / abandoned / unrelatedへ分類する。
4. `CURRENT_WORK.json`、`CI_TRAIN_MANIFEST.json`、`PRIVATE_STAGE_STATE.json`、`NEXT_TASK_PACKET.json`を照合する。
5. `PRIVATE_STAGE_STATE.cycle_control`からrunning / paused / target_reachedとexact next actionを復元する。
6. `action_required`がbot起因の既知状態か、実際の失敗かを区別する。
7. checkpointが指すrelease evidenceを確認する。
8. activeな制度改修branchがある場合は、予約済み次候補の翻訳作業より優先する。
9. schema v6 minimal reservationなら、focus key・人物声・owner・batch planningが未記載であることを正常状態として扱う。
10. private preparation開始時にだけ、最新Relation artifactからcandidate detailとowner snapshotを生成する。

## 一cycleの標準完了地点

詳細は`AUTONOMOUS_VISIBILITY_CYCLE.md`を正本とする。

### private

正常なら一つの応答内で次まで進む。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> private preflight -> PR ready -> ready_for_public_ci`

各private stageは内部checkpointであり、利用者へ追加の「作業の続きを」を要求する理由にしない。

### public

正常なら一つの応答内で次まで進む。

`in_public_ci -> orchestrator success -> state finalization -> phase2 success -> review thread 0 -> awaiting_private_merge`

### private復帰後

privateをmetadataで確認し、同じ検証済みHEADをsquash統合して`merged`へ進める。統合前に次waveを始めない。

## 例外停止

途中停止は`cycle_control.status=paused`として、次の理由だけを許す。

- `user_decision_required`
- `checker_failure`
- `external_dependency_unavailable`
- `turn_capacity_checkpoint`

`paused`は`continuation_required=true`、許可理由、機械実行可能な`exact_next_action`を必須とする。

正常停止は`target_reached`とし、`ready_for_public_ci`、`awaiting_private_merge`、`merged`だけを許す。

## wave v2の裁定

- `private_preparation`: 複数candidate packetを先に準備し、全`fixes_*.json`実測のowner snapshotを付けてqueueをsealする。fix / keep、fix JSON、owner新設、正式束番号は禁止。
- `private_quality_audit`: sealed queue全体を連続監査する。件数、release残量、metricsを見せない。一packetごとにencodingへ移らない。
- `private_encoding`: 全監査済みpacketをまとめて収録する。新しい翻訳判断は禁止。owner更新後にcandidate snapshotを再生成する。
- `translation_frozen`: 全packet収録後の翻訳判断凍結。CI輸送statusとは独立する。

通常順:

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen`

`private_encoding -> private_preparation`は理由コード付きreplenishmentだけを許す。準備不足は`preparation_underfilled`として失敗する。

輸送:

`not_ready -> ready_for_public_ci -> in_public_ci -> verified -> awaiting_private_merge -> merged`

## minimal next reservation

schema v6の`NEXT_TASK_PACKET.json`はrelease輸送用の予約だけを持つ。

保持するもの:

- verified checkpoint
- current pair
- reserved scene groups
- Relation artifact digest / HEAD / freshness rule
- release candidate
- planned batch
- public中の禁止事項

private preparationまで保持しないもの:

- focus key
- scene flow detail
- voice questions
- FACT_DOUBT / ALLUSION_REVIEW
- owner snapshot
- batch planning
- skill review

これらは予約時点の行政情報ではなく、校正準備の成果物である。

## owner snapshot

新規candidate作成時とencoding後に次を使う。

```bash
python _tools/check_candidate_ownership.py --write <candidate paths>
```

人物ペアowner一つだけを見て未所有と判断しない。全`fixes_*.json`を機械走査し、複数owner、stale snapshot、未記録ownerをprivateで失敗させる。

public化依頼前:

```bash
python _tools/check_private_release_preflight.py --with-tests
```

## visibilityとoperation mode

- private + private_translation_work: 現在stageから`ready_for_public_ci`まで連続実行する。
- public + private_translation_work: `return_private_required`。翻訳を開始しない。
- private + translation_frozen + ready_for_public_ci: public化依頼の正常停止。
- public + translation_frozen: public CI窓。`awaiting_private_merge`まで進め、翻訳判断を再開しない。
- private + awaiting_private_merge: 検証済みPRをsquash統合し`merged`へ進める。
- public_ci_blocked: publicならprivate復帰を依頼し、privateで対象packetをquality auditへ戻す。

## public CIの明示起動

PR作成、ready化、通常commitでは重いCIを起動しない。

- `release-ci`: `Release train orchestrator`の通常入口
- `ci-heavy-rerun`: 同じorchestrator全工程の再走
- `finalize-release`: 最終状態commit後のphase2専用

orchestratorは一つのpull_request run内で完全preflightを行い、Relation / Cross再利用workflowを同じHEADで実行し、両方成功後だけApply再利用workflowを開始する。ApplyはAPPLIED_FIXESとaudit statusを同じbot commitへ収録する。

bot書き戻しではorchestratorを再起動しない。`finalize-release`ではRelation / Cross / Applyを再実行しない。

release evidence schema v2はorchestrator run一つとその内部job成功を検証する。既存schema v1 releaseはそのまま保持する。

## 正本の読順

1. README.md
2. AGENTS.md
3. VISIBILITY_PREFLIGHT_CONTRACT.json
4. SESSION_BOOTSTRAP.md
5. AUTONOMOUS_VISIBILITY_CYCLE.md
6. PRIVATE_TRANSLATION_STAGES.json
7. PRIVATE_TRANSLATION_STAGES.md
8. PRIVATE_STAGE_STATE.json
9. TRANSLATION_QUALITY_GATE.md
10. PUBLIC_CI_WINDOW.md
11. CI_TRAIN_PHASE1.md
12. CI_TRAIN_PHASE2.md
13. CURRENT_WORK.json
14. CI_TRAIN_MANIFEST.json
15. CURRENT_HANDOFF.md
16. NEXT_TASK_PACKET.json
17. checkpointが指すrelease evidence
18. COLD_START_ACCEPTANCE.md
19. audit_status.json
20. RUNBOOK、skill、人物資料、一次資料

## 現在のcold-start固定点

- PR #124はsquash統合済み。merge SHAは`a00a39104b35c61440e7a4734aa04fc355b91e06`。
- verified checkpointは第92束、人物ペアowner1165、全体1541。
- train-09 releaseは`yuwen-mowen-train-09-r1`、翻訳段階は`translation_frozen`、輸送は`merged`。
- 制度branch`agent/autonomous-private-cycle-contract`とdraft PR #125がactive。
- PR #125はcycle完走目標、例外停止、scheduler向け機械状態を固定する。
- 次wave候補`5654_8`はschema v6のreserved_only。preparation・quality audit・encodingは未開始。
- 制度改修の統合を翻訳再開より優先する。

## 禁止事項

- visibility preflight前の利用者向け発言
- 内部stageを正常な会話終了地点にすること
- pausedなのに理由やexact next actionを残さないこと
- 一packetだけを準備して通常sealすること
- 特定owner一つだけを参照した未所有判定
- owner snapshotなしの新規candidate
- minimal reservationへprivate preparation detailを戻すこと
- quality audit中のmetrics、release残量、正式束番号、fix JSON、owner書込み
- encoding中の新しい翻訳判断
- candidate packetをmanifestへ入れること
- public CIから翻訳判断を再開すること
- Relation / Cross成功前にApplyを開始すること
- phase2成功前にawaiting_private_mergeへ進めること
- private確認前にmergeすること
- merge前に次waveを開始すること
- 制度改修PRへ訳文、fix JSON、人物owner内容、FACT_DOUBT、ALLUSION_REVIEWを混ぜること
- PR作成・ready化・通常commitによる重いCI自動起動の復活
- post-merge状態PRを復活させること
