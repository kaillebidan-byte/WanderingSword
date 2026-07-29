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
- translation試走 PR #194: draft。factory初期化後のreading manifest注入で`主人公`alias衝突を検出し、requestを保持したまま停止
- institution task: `quality_audit_persona_alias_resolution`
- institution PR #195: 人物alias衝突をcurrent pairで決定的に解決する制度修正

## 次の作業

PR #195でalias解決規則、正常系・失敗系回帰、制度CIを完了し、squash mergeしてmainを再検証する。その後だけPR #194の既存factory requestから試走を再開する。

## 禁止

- pendingな制度タスクより先に翻訳PR #194を進めない。
- 制度修正を翻訳PR #194へ混在させない。
- `主人公`aliasを人物資料から根拠なく削除しない。
- 曖昧aliasをファイル順や推測で選ばない。
- merged済みPRのphase2やmergeを再実行しない。
- mode lock前に翻訳準備、判断、owner書込みを開始しない。
- minimal reservationへprivate preparation詳細を先書きしない。
- ゲームフォルダへ配置しない。
