# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- translation PR #154: merged
- train: `yuwen-mowen-train-25`
- verified checkpoint: 第153束 / pair 1351 / project 1727
- transport: `merged`
- cycle: `target_reached / merged`
- 次候補: `5274_1`（schema v6 minimal reservation）

## 次の作業

GitHub repository metadataでcycle開始時visibilityを確認し、`EXECUTION_MODES.json`に従って新cycleのmodeを選ぶ。`CURRENT_WORK.operation_mode`と`PRIVATE_STAGE_STATE.cycle_control`へ同じmodeをlockした後、予約候補からwave preparationを開始する。

public開始なら`always_public_full_pipeline`として、段階権限を守りながら同じcycleでmergeまで進める。private開始なら`manual_visibility_cycle`としてvisibility境界を使う。

## 禁止

- merged済みPRのphase2、review thread、squash mergeを再実行しない。
- mode lock前に翻訳準備、判断、owner書込みを開始しない。
- minimal reservationへprivate preparationの詳細を先書きしない。
- ゲームフォルダへ配置しない。
