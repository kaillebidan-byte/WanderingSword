# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: private
- main HEAD: `cf18ebcdce9c65ef0fd203eeff174b7cdaba5b33`
- PR #122: squash統合済み
- active制度branch: `agent/post-train08-release-orchestration`
- active制度PR: draft PR #123
- verified checkpoint: 第88束
- 人物ペア適用済みowner: 1165
- プロジェクト全体適用済み: 1541
- release: `yuwen-mowen-train-08-r1`
- private stage: `translation_frozen`

## train-08

第85〜88束、45行、18修正をPR #122で統合した。

- merge SHA: `cf18ebcdce9c65ef0fd203eeff174b7cdaba5b33`
- Relation: `30188531193`
- Cross: `30188531212`
- Apply: `30188531216`
- asset HEAD: `adeaea8298897b8f8cc851e99b3c18b230c14bfc`
- 未適用: 0件
- 未解決review thread: 0件

release evidenceは`squash_merged`へ同期済み。

## 制度PR #123

校正後の行政往復を減らす改修を行っている。

- NEXT_TASK_PACKETをschema v6 minimal reservationへ縮小
- focus key、人物声、FACT_DOUBT、owner、batch planningをprivate preparationへ移動
- `release-ci`を単一orchestrator入口へ変更
- 完全preflight後にRelation / Crossを固定HEADで実行
- QA二本成功後だけApplyを起動
- ApplyがAPPLIED_FIXESを自動生成してからaudit statusを更新
- `finalize-release`は状態最終化だけを検査

## 次候補

`5649_1`はreserved_only。scene予約とRelation artifact指紋だけを保持し、preparation・quality audit・encodingは未開始。

## 次の作業

PR #123の静的整合と差分境界を確認する。private検査で問題がなければ、workflow変更の実検証に必要な時点だけ公開CI窓を依頼する。

## 禁止

- 制度PR #123の統合前に翻訳作業を再開しない。
- `5649_1`のpreparationを開始しない。
- 訳文、fix値、人物owner内容、FACT_DOUBT、ALLUSION_REVIEWを制度PRで変更しない。
- Relation / Cross / Applyを手動で同時起動しない。
- ゲームフォルダへ配置しない。
