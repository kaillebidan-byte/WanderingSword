# private翻訳四段階 wave v2

## 目的

準備・品質監査・収録・翻訳凍結を別の認知モードとして維持する。複数packetを先に準備し、sealed queue全体を監査し、その後にまとめて収録する。

機械契約は`PRIVATE_TRANSLATION_STAGES.json`、現在状態は`PRIVATE_STAGE_STATE.json`、段階検査は`check_private_translation_stage.py`、owner検査は`check_candidate_ownership.py`を正本とする。

## 1. private_preparation

一列車分のcandidate packetを先に作る。

許可:

- 原文、現訳、前後、話者、相手、時系列、分岐を固定する。
- 重複familyを確認する。
- candidate packetとpreparation recordをwaveへ追加する。
- packet数とunique reviewed rows相当を輸送設計として集計する。

禁止:

- fix / keep判断
- 修正JSON、review record、正式束番号
- owner新設・移管
- candidateをmanifestへ入れること

### owner snapshot

candidate作成直後に次を実行する。

```bash
python _tools/check_candidate_ownership.py --write <candidate paths>
```

このsnapshotは`fixes_*.json`全件を走査する。人物ペアowner一つだけを参照して未所有判定してはならない。

snapshotには次を持つ。

- ownerごとの既存キー
- 未所有キー
- 複数owner衝突
- 対象行数
- target / namespace

複数ownerが存在するcandidateはsealできない。

通常seal条件:

- 4 packet以上
- 40 unique reviewed rows相当以上
- 追加候補が存在しない`scope_exhausted`

上限は6 packet / 60 rows。underfilledな一packet sealは失敗する。

## 2. private_quality_audit

sealed queue全体を続けて監査する。

記録:

- fix_candidate
- challenged_keep
- needs_context
- FACT_DOUBT
- ALLUSION_REVIEW

許可:

- 原文の意味、強弱、発話役割、人物声、設定追加、欠落、不自然さの判断
- snapshot済みowner情報の参照

禁止:

- 一packetごとのencoding移動
- fix JSON、owner、正式束番号、manifest件数
- release残量、処理件数、閾値を監査判断へ渡すこと

## 3. private_encoding

全packetの監査完了後、確定判断だけを収録する。

許可:

- fix JSONへの収録
- owner更新、新設、横断owner移管
- review recordと正式束番号
- encoding済み正式束のmanifest追加
- review_status / apply_statusの分離

禁止:

- 新しい翻訳判断
- 未監査packetの収録
- 一部未収録での凍結

encoding後、fix ownerの実状態が変わるため、全candidateへ再度`--write`を実行する。その後、次を必須とする。

```bash
python _tools/check_candidate_ownership.py --require-current-wave
```

preparation時snapshotのまま凍結してはならない。

## 4. translation_frozen

全packetのencoding完了後、翻訳判断と収録を凍結する。輸送軸だけを次の順に進める。

`not_ready -> ready_for_public_ci -> in_public_ci -> verified -> awaiting_private_merge -> merged`

public化を依頼する前に次を実行する。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

public中は翻訳判断、fix追加、owner変更、正式束追加を再開しない。

## replenishment例外

`private_encoding -> private_preparation`は通常遷移ではない。次の理由コードを必須とする。

- packet_invalidated
- duplicate_normalization_reduced_scope
- needs_context_unresolved
- prepared_source_became_stale
- scope_boundary_corrected

単に準備packetが足りない場合は例外ではなく`preparation_underfilled`である。

## manifest境界

candidate packetは`PRIVATE_STAGE_STATE.json`だけに置く。manifestにはencoding済み正式束と輸送集計だけを置く。

- review_status: complete
- apply_status: pending | verified

## legacy candidate

snapshot制度導入前のcandidateは、`PRIVATE_STAGE_STATE.ownership_policy.legacy_candidate_paths`へ正確なpathを列挙する。legacy指定を新規candidateへ流用してはならない。
