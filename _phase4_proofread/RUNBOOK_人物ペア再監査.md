# Wandering Sword 人物ペア再監査RUNBOOK

この文書はプロジェクト固有の入口。翻訳判断はskillのpair reauditとQA資料、資料還流は`QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json`、実行制御は`EXECUTION_MODES.json`、`PRIVATE_TRANSLATION_STAGES.json`、`AUTONOMOUS_VISIBILITY_CYCLE.md`を正本とする。

## 1. 再開とmode

1. scope lock後、repository metadata、main、open PR、Actionsを確認する。
2. 前cycleがmergedなら開始時visibilityからmodeを選び、二状態正本へlockする。
3. public開始のalways-publicでは、publicのままprivate_*段階を実行できる。
4. manual modeのpublic CI窓では翻訳判断を行わない。

## 2. wave作業

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen`

- preparation: 原文、現訳、前後、話者、相手、時系列、分岐を固定し、candidate packet、snapshot、digest付き読書manifest、人物資料targetを作る。翻訳判断、人物資料判断、fixは禁止。
- quality audit: sealed queue全体を監査し、fix / keep / needs_context / FACT_DOUBT / ALLUSION_REVIEWに加え、人物資料の`keep/revise/create/unresolved`を記録する。fix、人物資料、owner、正式束の直接書込みは禁止。
- encoding: 記録済み判断だけを人物資料、fix JSON、owner生成器、review record、正式束へ決定的に収録する。新しい翻訳判断・人物資料判断は禁止。
- translation frozen: 翻訳判断と人物資料判断を閉じ、CI輸送だけを進める。

## 3. quality auditの読書順序

人物資料や既訳へ引っ張られないよう、次の順序を固定する。

1. candidateの原文・現訳・前後文・話者・相手・時系列だけを読む。
2. 典故疑義と設定事実疑義を別々に立てる。
3. candidateの`quality_audit_context.required_documents`を読む。
4. skill、人物資料、関係資料の主張を一次資料と照合する。
5. 翻訳のKEEP/FIXを決める。
6. 各`source_document_target`へ人物資料の判断を記録する。

`reading_attestation`はcandidateのmanifest digestと必須資料path/digestを完全一致で記録する。資料を読んだという自由記述だけでは完了にならない。

人物資料は作業仮説であり、一次資料より下位である。反例が出た場合は訳文を既存資料へ押し込まない。

- `keep`: 一次資料と現行資料が整合する。
- `revise`: 現行主張を一意な別主張へ置換する。
- `create`: 相手・時期・分岐別の規則が欠けており、既存headingへ追記する。
- `unresolved`: 反例らしいが証拠不足で資料へ適用しない。

`revise/create`には一次資料key、適用scope、理由、high confidence、元資料digest、一意な置換対象またはheadingを必須とする。人物全体への過剰一般化、別時系列・別分岐の合成は禁止する。

## 4. 意味単位と作業量

一packetの通読目標は原則15〜30行。短い場面は意味境界を壊さない範囲で隣接場面を併合する。waveは40〜60 unique rowsを標準とし、意味単位を完結させる場合だけ最大80行まで延長する。80行を埋める義務はない。

小束例外やfocus keyはcandidate/preparation recordへ記録する。schema v6 minimal reservationの`NEXT_TASK_PACKET.json`へ`batch_planning`を戻さない。

## 5. owner契約

candidate作成時に全`fixes_*.json`を走査したownership snapshotを作る。snapshotはquality audit時点の監査記録であり、encoding後に上書きしない。encoding後は次のlive検査を使う。

```bash
python _tools/check_candidate_ownership.py --release-live
python _tools/check_fix_owner_delta.py
```

owner assignmentは構造化planと生成器を使い、手作業でownerファイルを選ばない。

## 6. 人物資料の決定的適用

`check_quality_audit_source_feedback.py`がencoding前に次を検査する。

- candidate schema 3
- audit decision schema 2
- reading manifestとattestationの完全一致
- 必須資料の存在とdigest
- 全source targetのdecision被覆
- evidence keyがcandidate内か
- scopeが空でないか
- `revise/create`がhigh confidenceか
- 置換対象またはheadingが一意か
- targetが`10_人物/*.md`内か

`source_document_feedback.py`は検査済みdecisionだけを適用する。複数人物資料の変更は全件を先に検証し、temp fileを作ってから置換する。失敗時はcommitしない。適用結果は`SOURCE_DOCUMENT_FEEDBACK_*.json`へbefore/after digest付きで残す。

## 7. release

private release preflight成功後、modeに従って輸送する。

- manual: ready_for_public_ciでvisibility境界を使い、awaiting_private_merge後にprivateでmergeする。
- always-public: 同じcycleでorchestrator、phase2、review thread 0件、squash merge、reconciliationまで進む。

post-merge状態専用PRは作らない。merge後reconcilerが三状態正本、NEXT_TASK_PACKET、CURRENT_HANDOFFを同期する。

## 8. GitHub書込み

複数pathの一つの論理状態はlocal gitまたはGit Data APIで原子的commitへまとめる。Contents APIの一ファイル一commitを繰り返さない。PR作成前に翻訳判断と準備物を可能な限り一commitへまとめ、commit budgetを守る。

encoding workflowは`_phase4_proofread`と`10_人物`を同じcommitへ収録する。人物資料だけ先にcommitしたり、翻訳適用だけを後から別commitへ分離したりしない。

## 9. 作業境界

エージェントは修正適用、記録済み人物資料修正、locres書戻し、pak再生成、lint、回帰、LFS確認まで行う。ゲームフォルダへの配置、ゲーム起動、ゲーム内確認はユーザー側。ゲーム内確認前は`game_verified: not_started`を維持する。
