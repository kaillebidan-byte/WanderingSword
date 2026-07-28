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
- 現在: `workflow_duplicate_run_serialization`
- 次: `stale_release_label_guard`

## 次の作業

`resume_work_controller.py --repository-visibility public`のwork orderに従い、`workflow_duplicate_run_serialization`を原因特定、恒久修正、正常・競合回帰、制度CI、squash merge、main再検証まで進める。PR作成後、同じPRで現在taskを`completed`へ更新しPR番号を記録する。merge SHAは統合後にGitHub metadataで検証する。

## 禁止

- 制度キューにpendingがある間、`5352_1`の翻訳cycleを開始しない。
- merged済みPRのphase2やmergeを再実行しない。
- 翻訳本文、owner値、locres、pak、minimal reservationへ触れない。
- 独自ロック、一時workflow、別triggerを新造しない。
- ゲームフォルダへ配置しない。
