# CI列車 第一段階パイロット

## 目的

翻訳の意味境界を小束のまま保ちつつ、公開CI窓への往復を複数束ごとへまとめる。
第61束から最初の一往復を試験し、翻訳精度、所有分離、失敗切り分け、冷間再開を落とさずに公開回数を減らせるか確認する。

## 単位の分離

- **翻訳小束**: 場面、分岐、人物関係、同じ崩れ方で閉じる。件数合わせで別場面を混ぜない。
- **CI列車**: privateで完成した複数の小束を一つのbranch・一つの翻訳PR・一つの公開CI窓へまとめる。
- 小束ごとの修正JSON、レビュー記録、所有境界は統合せず、列車内でも別ファイルのまま残す。

## 第一段階のrelease条件

通常releaseは次のいずれか一つへ達した時点とする。

- 完成小束 4
- 通読 40行
- 修正 20キー

蓄積上限は次のとおり。

- 完成小束 6
- 通読 60行

上限へ達する前でも、workflow変更、schema変更、security/visibility上の理由、緊急のbuild確認がある場合は、
`CI_TRAIN_MANIFEST.release_trigger`へ理由と説明を記録して早期releaseできる。

## private蓄積中

1. verified checkpointは直近の公開CI統合点のまま保持する。
2. 小束を通読し、fix/keep、FACT_DOUBT、ALLUSION_REVIEW、所有を確定する。
3. 修正JSONとレビュー記録を完成させる。
4. locres、pak、audit_statusの適用件数はまだ更新しない。
5. 完成小束を`reviewed_pending_ci`として`CI_TRAIN_MANIFEST.json`へ追加する。
6. `CURRENT_WORK.last_reviewed_batch`と`NEXT_TASK_PACKET`だけを次束へ進める。
7. release条件未達なら`private_translation_work`を維持し、public化を依頼しない。

## draft PR

第一段階では、列車branchの所在を新チャットから復元できるよう、private中に一つのdraft PRを開いてよい。

- draft PRはCI実行・統合要求ではない。
- `open_pr_only_after_ready`はready状態の通常PRに対する制限として維持する。
- draft PRのhead branch、`CI_TRAIN_MANIFEST`、`CURRENT_WORK.ci_train`が一致しなければならない。
- release時は同じPRを使用し、最終commitをpushしてからready化する。別PRへ束を分散しない。

## release時

1. manifestのtotalsと各束記録を検査する。
2. release条件または許可された早期release理由を確認する。
3. `CI_TRAIN_MANIFEST.status`と`CURRENT_WORK.ci_train.status`を`ready_for_public_ci`へする。
4. `CURRENT_WORK.operation_mode.declared_state`を`ready_for_public_ci`へする。
5. ユーザーへ一度だけpublic化を依頼する。
6. 同じdraft PRをready化し、Relation / Cross / Applyを実行する。
7. 列車内の全修正をまとめてlocresへ適用し、pakを一度再生成する。
8. 未適用0件、所有競合0件、lint、関係抽出、回帰、LFS、未解決thread 0件を確認する。
9. 第一段階では既存のcheckpoint最終化とpost-merge状態PRを残す。
10. 公開CI窓終了後にprivateへ戻す。

## 失敗時

- 問題のある小束が特定できる場合は、その束だけmanifestから外すか修正する。
- 訳文・人物声・所有境界の深い再検討が必要ならpublicで試行を重ねず、`public_ci_blocked`としてprivateへ戻す。
- 列車全体を一つの巨大修正JSONへまとめないため、束単位の除外とロールバックを可能にする。

## パイロット合格条件

- 第61束以降を複数束蓄積してからpublic化する。
- visibility往復は一回。
- 翻訳PRは一つ。
- 小束ごとのレビュー・所有・疑義が復元可能。
- 全修正束未適用0件と回帰検査が成功。
- private復帰後、新チャットがmanifestから次の列車開始位置を復元できる。
