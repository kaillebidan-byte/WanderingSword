# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- PR #192: merged
- transport: `merged`
- cycle: `target_reached / merged`
- translation PR #194: draft。train-40の監査8件と人物資料判断を記録済み
- institution task `post_feedback_owner_state_attestation_refresh`: PR #196で完了記録済み
- PR #196: CI成功。人物資料還流後の`PRIVATE_STAGE_STATE`だけをowner証跡へ再封印するadapterを実装

## 次の作業

GitHub metadataでPR #196のsquash mergeとmain実装を確認する。その後、PR #194を更新済みmainへ載せ直し、同じ監査記録からencodingを再開してrelease・merge・reconcileまで進める。

## 禁止

- PR #196のmain統合確認前に翻訳cycleを開始しない。
- 制度修正を翻訳PR #194へ混在させない。
- owner file、candidate、翻訳判断を再生成しない。
- CI_TRAIN_MANIFESTまたはCURRENT_WORKの予期しない差分をdigest更新で隠さない。
- 失敗runの作業treeを手作業でcommitしない。
- ゲームフォルダへ配置しない。
