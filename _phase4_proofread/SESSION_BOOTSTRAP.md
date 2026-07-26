# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、次候補予約は`NEXT_TASK_PACKET.json`、private waveは`PRIVATE_STAGE_STATE.json`を正本とする。

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の表現も再開モードとして扱う。URLや前回作業を聞き直さず、privateで許可された作業があれば同じ応答内で実作業へ進む。

## visibility preflight

新規チャット・再開指示・作業継続指示では、最初の外部確認をGitHub repository metadata取得にする。結果が返るまで利用者向けの計画、開始宣言、途中報告を出さない。

利用者の申告ではなくmetadataを実visibilityの正本とする。取得失敗時は作業開始を主張せず停止する。

## 起動順

1. repository metadataで実visibilityを確認する。
2. main、未統合PR、GitHub Actionsを確認する。
3. PRは開いているだけで現行作業と決めない。active / superseded / abandoned / unrelatedへ分類する。
4. `CURRENT_WORK.json`、`CI_TRAIN_MANIFEST.json`、`PRIVATE_STAGE_STATE.json`、`NEXT_TASK_PACKET.json`を照合する。
5. `action_required`がbot起因の既知状態か、実際の失敗かを区別する。
6. checkpointが指すrelease evidenceを確認する。
7. activeな制度改修branchがある場合は、予約済み次候補の翻訳作業より優先する。
8. owner snapshot制度が有効なら、candidateを作る前に`PRIVATE_STAGE_STATE.ownership_policy`を読む。

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

- private + private_translation_work: 現在のprivate stageだけを行う。
- public + private_translation_work: `return_private_required`。翻訳を開始しない。
- private + translation_frozen: 制度作業、輸送準備、public化依頼だけを行える。
- public + translation_frozen: public CI窓。CIと統合だけを行い、翻訳判断を再開しない。
- public_ci_blocked: publicならprivate復帰を依頼し、privateで対象packetをquality auditへ戻す。

## public CIの明示起動

重い三本はPR作成、ready化、通常commitでは起動しない。

- `release-ci`: Relation / Cross / Applyの通常起動
- `ci-heavy-rerun`: 局所修正後の明示再走
- `finalize-release`: 最終状態commit後のphase2専用

bot書き戻しでは重い三本を再起動しない。`finalize-release`ではRelation / Cross / Applyを起動しない。

## 正本の読順

1. README.md
2. AGENTS.md
3. VISIBILITY_PREFLIGHT_CONTRACT.json
4. SESSION_BOOTSTRAP.md
5. PRIVATE_TRANSLATION_STAGES.json
6. PRIVATE_TRANSLATION_STAGES.md
7. PRIVATE_STAGE_STATE.json
8. TRANSLATION_QUALITY_GATE.md
9. PUBLIC_CI_WINDOW.md
10. CI_TRAIN_PHASE1.md
11. CI_TRAIN_PHASE2.md
12. CURRENT_WORK.json
13. CI_TRAIN_MANIFEST.json
14. CURRENT_HANDOFF.md
15. NEXT_TASK_PACKET.json
16. checkpointが指すrelease evidence
17. COLD_START_ACCEPTANCE.md
18. audit_status.json
19. RUNBOOK、skill、人物資料、一次資料

## 現在のcold-start固定点

- 制度PR #121はsquash統合済み。merge SHAは`9a4d7c12521355dcd7a590cff801695862f73c8b`。
- verified checkpointは第84束、人物ペアowner1165、全体1539。
- train-08は第85〜88束をencoding済みで、private stageは`translation_frozen`。
- train-08 totalsは4束・45行・18修正。第86束はkeep-only。
- 輸送は`ready_for_public_ci`。draft PR作成後、public化して`release-ci`を明示起動する。
- 次wave候補`5649_1`はreserved_only。train-08統合前にpreparationを開始しない。

## 禁止事項

- visibility preflight前の利用者向け発言
- 一packetだけを準備して通常sealすること
- 特定owner一つだけを参照した未所有判定
- owner snapshotなしの新規candidate
- quality audit中のmetrics、release残量、正式束番号、fix JSON、owner書込み
- encoding中の新しい翻訳判断
- candidate packetをmanifestへ入れること
- public CIから翻訳判断を再開すること
- 制度改修PRへ訳文、fix JSON、人物owner内容、FACT_DOUBT、ALLUSION_REVIEWを混ぜること
- PR作成・ready化・通常commitによる重いCI自動起動の復活
- post-merge状態PRを復活させること
