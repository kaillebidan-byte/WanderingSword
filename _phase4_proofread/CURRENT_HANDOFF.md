# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、main、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- translation PR #174: merged
- train: `yuwen-mowen-train-28`
- verified checkpoint: 第159束 / pair 1358 / project 1734
- transport: `merged`
- cycle: `target_reached / merged`
- 次候補: `5352_1`（schema v6 minimal reservation）

## 制度改修キュー

正本は`INSTITUTION_WORK_QUEUE.json`。`always_public_full_pipeline`ではpending制度タスクを翻訳cycleより先に処理する。

- 完了: `quality_decision_control_invariants` / PR #176
- 完了: `workflow_duplicate_run_serialization` / PR #180
- 完了（本PR）: `stale_release_label_guard` / PR #181

## 次の作業

PR #181の制度CI、live checker、review threadを確認し、squash mergeする。GitHub metadataでmerge SHAを取得してmain実装と制度キューを再検証する。制度キューが空であることを確認後、`resume_work_controller.py --repository-visibility public`が返すtranslation factoryの一つのactionへ進む。PR番号は同じ実装PR内へ記録済み。

## 禁止

- PR #181のmain再検証前に`5352_1`の翻訳cycleを開始しない。
- merged済みPRのphase2やmergeを再実行しない。
- 翻訳本文、owner値、locres、pak、minimal reservationへ触れない。
- 独自ロック、一時workflow、別triggerを新造しない。
- ゲームフォルダへ配置しない。
