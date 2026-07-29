# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- PR #192: merged
- transport: `merged`
- cycle: `target_reached / merged`
- translation PR #194: draft。train-40の監査8件と人物資料判断を記録済み
- factory encoding: 翻訳収録と人物資料適用は成功したが、凍結検査で`PRIVATE_STAGE_STATE.json`のowner状態digest不一致を検出
- institution task: `post_feedback_owner_state_attestation_refresh`
- institution branch: `agent/post-feedback-owner-attestation-refresh`

## 次の作業

人物資料還流後に変更された`PRIVATE_STAGE_STATE`だけをowner assignment証跡へ再封印する恒久adapterを制度PRで実装し、CI・squash merge・main再検証を終える。その後、PR #194を更新済みmainへ載せ直し、同じ監査記録からencodingを再開する。

## 禁止

- pendingな制度タスクがある間は翻訳cycleを開始しない。
- 制度修正を翻訳PR #194へ混在させない。
- owner file、candidate、翻訳判断を再生成しない。
- CI_TRAIN_MANIFESTまたはCURRENT_WORKの予期しない差分をdigest更新で隠さない。
- 失敗runの作業treeを手作業でcommitしない。
- ゲームフォルダへ配置しない。
