# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- translation PR #192: merged
- train: `yuwen-mowen-train-39`
- verified checkpoint: 第170束 / pair 1360 / project 1736
- transport: `merged`
- cycle: `target_reached / merged`
- 次候補: `5786_15`（schema v6 minimal reservation）
- translation試走 PR #194: draft。factory requestを保持したままreading manifest注入失敗地点で停止
- institution task `quality_audit_persona_alias_resolution`: PR #195で完了記録済み

## 次の作業

GitHub metadataでPR #195のsquash mergeとmain実装を確認する。その後、PR #194の既存factory requestを更新済みmainへ載せ直し、同じtrain-40試走をreading manifest生成から再開する。

## 禁止

- PR #195のmain統合確認前に翻訳cycleを開始しない。
- 制度修正を翻訳PR #194へ混在させない。
- `主人公`aliasを人物資料から根拠なく削除しない。
- 曖昧aliasをファイル順や推測で選ばない。
- merged済みPRのphase2やmergeを再実行しない。
- mode lock前に翻訳準備、判断、owner書込みを開始しない。
- minimal reservationへprivate preparation詳細を先書きしない。
- ゲームフォルダへ配置しない。
