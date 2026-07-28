# Wandering Sword 人物ペア再監査RUNBOOK

この文書はプロジェクト固有の入口。翻訳判断はskillのpair reauditとQA資料、実行制御は`EXECUTION_MODES.json`、`PRIVATE_TRANSLATION_STAGES.json`、`AUTONOMOUS_VISIBILITY_CYCLE.md`を正本とする。

## 1. 再開とmode

1. scope lock後、repository metadata、main、open PR、Actionsを確認する。
2. 前cycleがmergedなら開始時visibilityからmodeを選び、二状態正本へlockする。
3. public開始のalways-publicでは、publicのままprivate_*段階を実行できる。
4. manual modeのpublic CI窓では翻訳判断を行わない。

## 2. wave作業

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen`

- preparation: 原文、現訳、前後、話者、相手、時系列、分岐を固定し、candidate packetとsnapshotを作る。翻訳判断やfixは禁止。
- quality audit: sealed queue全体を監査し、fix / keep / needs_context / FACT_DOUBT / ALLUSION_REVIEWを記録する。fix、owner、正式束の書込みは禁止。
- encoding: 記録済み判断だけをfix JSON、owner生成器、review record、正式束へ収録する。新しい翻訳判断は禁止。
- translation frozen: 翻訳判断を閉じ、CI輸送だけを進める。

## 3. 意味単位と作業量

一packetの通読目標は原則15〜30行。短い場面は意味境界を壊さない範囲で隣接場面を併合する。waveは40〜60 unique rowsを標準とし、意味単位を完結させる場合だけ最大80行まで延長する。80行を埋める義務はない。

小束例外やfocus keyはcandidate/preparation recordへ記録する。schema v6 minimal reservationの`NEXT_TASK_PACKET.json`へ`batch_planning`を戻さない。

## 4. owner契約

candidate作成時に全`fixes_*.json`を走査したownership snapshotを作る。snapshotはquality audit時点の監査記録であり、encoding後に上書きしない。encoding後は次のlive検査を使う。

```bash
python _tools/check_candidate_ownership.py --release-live
python _tools/check_fix_owner_delta.py
```

owner assignmentは構造化planと生成器を使い、手作業でownerファイルを選ばない。

## 5. release

private release preflight成功後、modeに従って輸送する。

- manual: ready_for_public_ciでvisibility境界を使い、awaiting_private_merge後にprivateでmergeする。
- always-public: 同じcycleでorchestrator、phase2、review thread 0件、squash merge、reconciliationまで進む。

post-merge状態専用PRは作らない。merge後reconcilerが三状態正本、NEXT_TASK_PACKET、CURRENT_HANDOFFを同期する。

## 6. GitHub書込み

複数pathの一つの論理状態はlocal gitまたはGit Data APIで原子的commitへまとめる。Contents APIの一ファイル一commitを繰り返さない。PR作成前に翻訳判断と準備物を可能な限り一commitへまとめ、commit budgetを守る。

## 7. 作業境界

エージェントは修正適用、locres書戻し、pak再生成、lint、回帰、LFS確認まで行う。ゲームフォルダへの配置、ゲーム起動、ゲーム内確認はユーザー側。ゲーム内確認前は`game_verified: not_started`を維持する。
