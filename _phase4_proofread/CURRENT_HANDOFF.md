# 現在の引継ぎ

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを優先する。

## 現在地

- active train: `yuwen-mowen-train-81`
- branch: `agent/yuwen-mowen-train-81`
- PR: `#239`
- stage: `translation_frozen`
- transport: `ready_for_public_ci`
- base checkpoint: 第211束 / pair 1436 / project 1812
- tail: 14行 / 2packet / FIX 2 / KEEP 12
- formal batches: 第212束・第213束
- release candidate: `yuwen-mowen-train-81-r1`
- previous release: `yuwen-mowen-train-80-r1` / PR #237 / `dee19812149e901b6d057cdd48a23e980e5731fb`

## exact next action

`release-ci` labelで固定release trainを起動し、完全preflight、Relation、Cross、Apply、pak一回再生成、未適用差分0件、fixed finalization、phase2、review thread 0件を確認してPR #239をsquash統合する。

## pair tail

現Relation artifactの`explicit_reference`全keyから第206〜211束candidateの既監査keyを除いた残件14行を、`CG表/QuestDlgs` 2行と`Quests任务表/Quests` 12行に分けて収録した。隣接する未監査explicit-reference行は存在しない。統合後は実sceneを再予約せず、宇文逸↔莫問のpair completion checkpointへ遷移する。

## 禁止

- translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない。
- 同じexplicit-reference行を再監査しない。
- release orchestrator以外の一時CIを作らない。
- ゲームフォルダへ配置しない。
