# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 機械正本は`CURRENT_WORK.json`、正式束と輸送は`CI_TRAIN_MANIFEST.json`、private waveは`PRIVATE_STAGE_STATE.json`、次候補は`NEXT_TASK_PACKET.json`。実visibilityとGitHub PR metadataを文書より優先する。

## 現在地

- 実visibility: private（GitHub repository metadataで確認）
- main HEAD: `ad6dfe2996a20d2bc6184be17ae1330fea7b6977`
- PR #120: squash統合済み
- active制度branch: `agent/post-train07-process-hardening`
- active制度PR: draft PR #121
- verified checkpoint: 第84束
- 人物ペア適用済みowner: 1165
- プロジェクト全体適用済み: 1539
- release: `yuwen-mowen-train-07-r1`
- 翻訳段階: `translation_frozen`
- train-07輸送: `merged`

## train-07

第81〜84束、57行、28修正をPR #120で統合した。

- Relation: `30172834036`
- Cross: `30172833998`
- Apply: `30172834003`
- final phase2: `30173414360`
- merge SHA: `ad6dfe2996a20d2bc6184be17ae1330fea7b6977`
- 未適用: 0件
- 未解決review thread: 0件

release evidenceは`squash_merged`へ同期済み。人物ペアowner数1165は洪飛・欧陽雪6キーを正しいcross-register ownerへ移管した現在所有数であり、翻訳キー削除ではない。

## 制度PR #121

校正時間をowner行政とCI再走から守る制度改修を行っている。

- candidate作成時に全`fixes_*.json`実測の`ownership_snapshot`を必須化
- encoding後にsnapshotを再生成
- owner重複・stale snapshotをpublic前に失敗させる
- `check_private_release_preflight.py --with-tests`で公開前検査を一括化
- Relation / Cross / Applyは`release-ci`ラベルだけで通常起動
- 局所再走は`ci-heavy-rerun`
- phase2は`finalize-release`ラベルだけで起動
- PR作成、ready化、通常commit、bot書き戻しでは重いCIを自動起動しない

## 次候補

`5603_1`は第85束候補としてreserved_only。preparation・quality audit・encoding・正式束番号は未開始。

## 禁止

- 制度PR #121の統合前に翻訳作業を再開しない。
- `5603_1`のpreparationを開始しない。
- 訳文、fix値、人物owner内容、FACT_DOUBT、ALLUSION_REVIEWを制度PRで変更しない。
- ゲームフォルダへ配置しない。

## 再開時

最初に実visibilityを無言で確認する。privateならPR #121のbranch、静的検査、PR状態を確認する。private検査完了後、workflow変更の検証に必要な時点でだけ公開CI窓を依頼する。publicなら翻訳を始めず、`release-ci`または`finalize-release`の対象を確認する。
