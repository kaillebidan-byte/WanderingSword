# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- translation PR #231: merged
- train: `yuwen-mowen-train-74`
- verified checkpoint: 第205束 / pair 1407 / project 1783
- transport: `merged`
- cycle: `target_reached / merged`
- 次候補: `9261_1`（schema v6 minimal reservation）

## 次の作業

cycle開始時visibilityからmodeを選び、CURRENT_WORKとPRIVATE_STAGE_STATEへlockした後、予約候補のpreparationを開始する。

## 禁止

- merged済みPRのphase2やmergeを再実行しない。
- mode lock前に翻訳準備、判断、owner書込みを開始しない。
- minimal reservationへprivate preparation詳細を先書きしない。
- ゲームフォルダへ配置しない。
