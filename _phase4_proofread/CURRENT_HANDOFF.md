# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。

## 現在地

- translation PR #162: draft / active
- train: `yuwen-mowen-train-26`
- private stage: `translation_frozen`
- transport: `ready_for_public_ci`
- execution mode: `always_public_full_pipeline`
- wave: 4 packets / 40 rows / 4 fixes / batches 154–157
- verified checkpoint: 第153束 / pair 1351 / project 1727（train-25）
- 次候補: `5296_7`（schema v6 minimal reservation）

## 次の作業

PR #162へ`release-ci`を付与し、preflight、relation、cross-register、apply、release finalization、verified checkpoint、squash mergeまで同一cycleで続ける。

## 禁止

- verified checkpoint前にmergeしない。
- translation_frozen後に翻訳判断やowner手書きを再開しない。
- minimal reservationへprivate preparation詳細を先書きしない。
- ゲームフォルダへ配置しない。
