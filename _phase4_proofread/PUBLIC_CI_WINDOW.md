# 公開CI窓 運用契約

## 目的

翻訳判断と準備はprivateで行う。GitHub-hosted runnerがprivate Actions利用枠のため起動できない場合だけ、
完成したCI列車の検証と統合に必要な短時間をpublicにする。
public化はリポジトリ全体、履歴、branches、Actionsログ、artifact、LFS参照を公開するため、公開時間と公開回数を最小化する。

visibilityを変更できるのはユーザーだけである。エージェントは実metadataを確認して依頼・確認する。

## 第一段階: 小束とCI列車を分ける

詳細は`CI_TRAIN_PHASE1.md`、機械可読の列車状態は`CI_TRAIN_MANIFEST.json`を正本とする。

- 小束は意味境界で閉じ、別分岐・別時点を件数合わせで混ぜない。
- privateで完成小束を`reviewed_pending_ci`として列車へ蓄積する。
- 通常releaseは4束、40行、20修正キーのいずれか。
- 上限は6束または60行。
- releaseまではlocres・pakへ適用せず、verified checkpointを直近統合点のまま保持する。
- 第一段階では既存の三本CI、bot書き戻し後の最終検証、post-merge状態PRを維持する。

## 状態

`CURRENT_WORK.operation_mode.declared_state`:

- `private_translation_work`: 翻訳、一次資料確認、修正JSON、レビュー、manifest蓄積をprivateで行う。
- `ready_for_public_ci`: manifestがrelease可能で、残作業がCI・統合だけ。
- `public_ci_blocked`: public中に深い再検討が必要と判明した。

実visibilityから導出:

- `public_ci_window`: ready + public。CIと統合だけを行う。
- `return_private_required`: private作業状態またはblockedなのにpublic。

## private蓄積

1. privateをmetadataで確認する。
2. activeなdraft CI列車PRがあれば、そのbranchとmanifestを継続する。
3. なければ`CURRENT_WORK.ci_train.branch`を作り、private draft PRを一つだけ開いてよい。
4. `NEXT_TASK_PACKET`の小束を監査する。
5. 修正JSON、レビュー、所有・疑義を完成させる。
6. manifestへ追加し、次束パケットへ進む。
7. release条件未達ならpublic化を依頼しない。
8. release条件到達時だけmanifestとdeclared_stateをreadyへする。

private draft PRは所在保存用であり、CI開始要求ではない。ready化前に別の列車PRを作らない。

## public化の依頼

```text
公開CI窓を開いてください。
対象: <train_id、含む束>
完成HEAD: <SHA>
集計: <束数 / 通読行 / 修正キー>
実行: Relation / Cross / Apply
終了条件: 三本成功、未適用0件、未解決thread 0件、翻訳PRとpost-merge状態PRのsquash統合
```

ユーザーの申告だけで進めずmetadataでpublicを確認する。

## public中に行うこと

- draft PRのready化または最終commitによるCI起動
- Relation audit extraction
- Cross register QA
- Apply curated localization fixes
- artifact、所有表、未適用差分、回帰、pak、LFS確認
- 局所的な構造・テスト・checkpoint修正
- 未解決thread確認
- squash統合
- 第一段階のpost-merge状態同期PRと三本確認
- private復帰依頼

## public中に行わないこと

- 新しい場面の翻訳
- 次の小束の追加
- 人物声や意味の大幅な再検討
- 原因不明のcommit試行の反復
- 次のCI列車作成

## 深い失敗

訳文再判断、人物資料・skillの大幅改修、所有境界再設計、原因不明の複数試行が必要なら`public_ci_blocked`とする。

```text
公開CI窓を閉じてprivateへ戻してください。深い修正はprivate翻訳作業回で行います。
```

## 第一段階の終了条件

1. manifestと列車内各束の対応が完全
2. Relation成功
3. Cross成功
4. Apply成功
5. 全修正束未適用0件
6. locres、pak、lint、関係抽出、回帰、LFS成功
7. checkpoint verified
8. 未解決review thread 0件
9. 列車翻訳PRをsquash統合
10. post-merge状態PRをsquash統合
11. mainを次列車の`private_translation_work`へ戻す
12. 実visibilityをprivateへ戻す

## 冷間再開裁定

| 宣言 | visibility | manifest | 裁定 |
|---|---|---|---|
| private_translation_work | private | accumulating | active train branchで次小束へ進む |
| private_translation_work | public | any | return_private_required |
| ready_for_public_ci | private | ready_for_public_ci | public化を依頼 |
| ready_for_public_ci | public | ready_for_public_ci | public_ci_window |
| public_ci_blocked | public | any | private復帰を依頼 |
| public_ci_blocked | private | any | 深い修正をprivateで行う |

## 禁止事項

- 小束一つごとにpublic化する
- release条件未達なのに理由なしで公開する
- 列車内の小束を一つの巨大修正JSONへ潰す
- 翻訳途中でpublic化する
- ready化後に新しい小束を追加する
- metadataを確認せずvisibilityを決める
- 三本成功前に統合条件を弱める
- 公開CI終了後もpublicのまま放置する
