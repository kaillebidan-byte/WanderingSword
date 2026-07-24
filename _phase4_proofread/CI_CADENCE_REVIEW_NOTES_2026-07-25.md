# 公開CI窓の粒度 観察メモ

- status: `observation_only`
- proposal timing: 第60束の公開CI窓終了後
- current-cycle rule: 現行制度を変更せず、第60束を同じ手順で完了する

## 問題意識

翻訳束が5〜12行程度の小場面で閉じる一方、公開CI窓では翻訳PR、bot書き戻し、最終HEAD再検証、squash統合、post-merge状態PR、再検証、squash統合、visibility復帰が必要になる。翻訳量に対する状態同期・CI・visibility操作の比率が高い。

## 第59束で観測した実作業

- 通読: 12行
- 修正: 12キー
- 人物ペア新規: 2キー
- 翻訳PR: 1本
- post-merge状態PR: 1本
- 成功したworkflow: 翻訳PRで6本、状態PRで3本
- bot書き戻し直後の`action_required`: 3本（既知のno-op）
- visibility操作: public化とprivate復帰
- squash SHA確定後に、checkpoint・次作業パケットの参照付け替えが必要

## 第60束で観測中の実作業

- 通読: 9行
- 修正: 6キー
- 人物ペア新規: 1キー
- 翻訳PR: #103の1本
- 初回HEADのworkflow: Relation、Cross、Applyの3本成功
- bot書き戻し: 1回
- bot資産HEAD: `a0be407017da5e74af3cd9e004fd1976d56a8b2f`
- 状態同期後の最終HEAD再検証: 実行待ち
- post-merge状態PR: 翻訳PR統合後に実測する
- visibility操作: public化済み、private復帰は公開CI窓終了後

## 安全境界と反復候補

- 翻訳判断と修正JSONの完成はprivateで行う必要がある。
- 所有競合、未適用0件、register lint、回帰、pak・LFS確認は公開適用時の安全境界として残す必要がある。
- bot書き戻し後の同一三本再検証、squash SHA参照の手動付け替え、post-merge状態PR、毎束のHANDOFF・COLD_START全面同期は反復削減候補である。
- ただし、まとめた場合も失敗した束の特定、部分ロールバック、冷間再開の現在地を失わない設計が必要である。

## 次回提案で比較する論点

- `verified checkpoint`を小束ごとではなく複数束をまとめた単位にできるか
- privateで複数の翻訳束を完成させ、一つの公開CI窓でまとめて適用できるか
- squash SHAへの参照付け替えを自動化し、post-merge状態PRをなくせるか
- CURRENT_HANDOFFやCOLD_START_ACCEPTANCEなどの生成・同期を、毎束ではなく確定単位へ寄せられるか
- まとめた場合でも、所有競合、未適用0件、回帰、失敗束の特定、ロールバックを維持できるか

この文書では結論を出さない。第60束のpost-merge状態PRまで実測を加えた後、候補制度と移行手順を提示する。
