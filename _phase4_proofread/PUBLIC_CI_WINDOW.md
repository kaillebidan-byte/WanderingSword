# 公開CI窓 運用契約

## 目的

翻訳判断と準備はprivateで行う。GitHub-hosted runnerがprivate Actions利用枠のため起動できない場合だけ、完成したCI列車の検証と統合に必要な短時間をpublicにする。
public化はリポジトリ全体、履歴、branches、Actionsログ、artifact、LFS参照を公開するため、公開時間と公開回数を最小化する。

visibilityを変更できるのはユーザーだけである。エージェントは実metadataを確認して依頼・確認する。

## 制度

- 小束蓄積の基礎は`CI_TRAIN_PHASE1.md`
- 単一PR最終化は`CI_TRAIN_PHASE2.md`
- 機械可読の列車状態は`CI_TRAIN_MANIFEST.json`
- verified releaseの正本は`RELEASE_EVIDENCE_*.json`

第二段階では、review済み小束と適用済みcheckpointの分離を維持しつつ、bot書き戻し後の重複CIとpost-merge状態PRを廃止する。

## 状態

`CURRENT_WORK.operation_mode.declared_state`:

- `private_translation_work`: 翻訳、制度改修、修正JSON、レビュー、manifest蓄積をprivateで行う
- `ready_for_public_ci`: manifestがrelease可能で、残作業がCI・単一PR最終化だけ
- `public_ci_blocked`: public中に深い再検討が必要と判明した

実visibilityから導出:

- `public_ci_window`: ready + public
- `return_private_required`: private作業状態またはblockedなのにpublic

## private蓄積

1. metadataでprivateを確認する。
2. 未統合PRとGitHub Actionsを確認し、PRは開いているだけで現行作業と決めない。
3. active列車branch、manifest、NEXT_TASK_PACKETを照合する。
4. 小束を意味境界で監査し、修正JSON、レビュー、所有、疑義を完成する。
5. manifestへ追加し、release条件未達ならpublic化しない。
6. 到達時だけmanifestとdeclared stateをreadyへする。

## public化の依頼

```text
公開CI窓を開いてください。
対象: <train_id、含む束>
完成HEAD: <SHA>
集計: <束数 / 通読行 / 修正キー>
実行: Relation / Cross / Apply / phase2 gate
終了条件: 三本成功、release evidence成功、未適用0件、未解決thread 0件、翻訳PR一つのsquash統合
```

ユーザーの申告だけで進めずmetadataでpublicを確認する。

## public中に行うこと

- 同じ翻訳PRでRelation / Cross / Applyを実行
- Applyによるlocres、pak、audit statusの一度の書き戻し
- 適用記録、release evidence、CURRENT_WORK、manifest、next packet、handoffの最終化
- `CI train phase2 gate`で成功run、HEAD、lineage、checkpointを検証
- 未解決thread確認
- 同じ翻訳PRのsquash統合
- private復帰依頼

## public中に行わないこと

- 新しい場面の翻訳
- 次の小束の追加
- 人物声や意味の大幅な再検討
- 原因不明のcommit試行の反復
- bot書き戻しだけを理由に重い三本を再実行
- post-merge状態PRの作成

## 第二段階の終了条件

1. manifestと各小束の対応が完全
2. Relation / Cross / Apply成功
3. 全修正束未適用0件
4. locres、pak、lint、関係抽出、回帰、LFS成功
5. release evidenceがGitHub Actions実体と一致
6. checkpoint verified
7. phase2 gate成功
8. 未解決review thread 0件
9. 翻訳PR一つをsquash統合
10. mainに次列車のprivate作業状態と次束packetが含まれる
11. post-merge状態PR 0件
12. 実visibilityをprivateへ戻す

## 深い失敗

訳文再判断、人物資料・skillの大幅改修、所有境界再設計、原因不明の複数試行が必要なら`public_ci_blocked`とする。

```text
公開CI窓を閉じてprivateへ戻してください。深い修正はprivate翻訳作業回で行います。
```

## 冷間再開裁定

| 宣言 | visibility | manifest | 裁定 |
|---|---|---|---|
| private_translation_work | private | accumulating/verified | active branchで制度改修または次小束へ進む |
| private_translation_work | public | any | return_private_required |
| ready_for_public_ci | private | ready_for_public_ci | public化を依頼 |
| ready_for_public_ci | public | ready_for_public_ci | public_ci_window |
| public_ci_blocked | public | any | private復帰を依頼 |
| public_ci_blocked | private | any | 深い修正をprivateで行う |

## 禁止事項

- 小束一つごとのpublic化
- release条件未達で理由なしの公開
- 列車内小束を巨大修正JSONへ潰す
- 翻訳途中でpublic化する
- ready化後に新しい小束を追加する
- metadataを確認せずvisibilityを決める
- release evidenceなしで統合する
- squash SHA同期のためだけにpost-merge状態PRを作る
- 公開CI終了後もpublicのまま放置する
