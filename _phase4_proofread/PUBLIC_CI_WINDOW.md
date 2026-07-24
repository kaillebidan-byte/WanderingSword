# 公開CI窓 運用契約

## 目的

翻訳判断と準備作業はprivateで行い、GitHub-hosted runnerがprivate Actions利用枠のため起動できない場合だけ、完成したHEADの検証と統合に必要な短時間をpublicにする。

public化はリポジトリ全体、履歴、branches、Actionsログ、artifact、LFS参照を公開する。作業回を分けても公開範囲は狭まらないため、公開時間と公開回数を最小化する制度として扱う。

リポジトリvisibilityを変更できるのはユーザーだけとする。エージェントは勝手に変更せず、必要な時点で定型文により依頼し、ユーザーの明示的な完了報告を受けてから次へ進む。

## 状態

`CURRENT_WORK.operation_mode.declared_state` に保存する状態は次の三つ。

- `private_translation_work`: 翻訳、一次資料確認、訳文裁定、修正束、レビュー記録、状態文書、テスト、workflow修正をprivateで準備する。原則としてPRはまだ開かない。
- `ready_for_public_ci`: 完成HEADがあり、残る作業がRelation、Cross、Apply、レビュー確認、squash統合、post-merge状態同期だけである。ユーザーへpublic化を依頼する。
- `public_ci_blocked`: public中に深い再検討または複数回の試行が必要と判明した。ユーザーへprivate復帰を依頼し、翻訳作業回へ戻す。

GitHub上の実visibilityと宣言状態から、次の二状態を導出する。

- `public_ci_window`: `ready_for_public_ci` かつ実visibilityがpublic。完成HEADのCIと統合だけを行う。
- `return_private_required`: 宣言状態が`private_translation_work`または`public_ci_blocked`なのに実visibilityがpublic。翻訳作業や追加commitへ入らず、private復帰を依頼する。

実visibilityは毎回GitHub repository metadataから取得し、状態文書の値を事実として代用しない。

## 標準遷移

### 1. private翻訳作業回

1. リポジトリがprivateであることを確認する。
2. active PRがなければ`NEXT_TASK_PACKET`の場面を監査する。
3. 原文、現訳、前後、人物、相手、時系列、分岐、所有を確認する。
4. 翻訳判断、修正JSON、レビュー記録、必要な資料・テスト・状態文書を完成させる。
5. 複数ファイルを可能な限り一つのatomic commitへまとめる。
6. CI前に深い判断が残っていないことを確認する。
7. 作業branch上の`declared_state`を`ready_for_public_ci`へ変更する。
8. PRを開く前にユーザーへpublic化を依頼する。

定型文:

```text
公開CI窓を開いてください。
対象: <束または事務PR>
完成HEAD: <SHA>
実行: Relation / Cross / Apply
終了条件: 三本成功、未適用0件、未解決スレッド0件、翻訳PRとpost-merge状態PRのsquash統合
```

### 2. public化の確認

ユーザーが`公開した`と報告しても、その言葉だけでは進めない。GitHub metadataで実visibilityがpublicであることを確認する。

確認後、必要ならPRを開き、同じHEADで三本を一回実行する。既に成功したrunを理由なく再実行しない。

### 3. 公開CI窓

public中に許可する作業:

- PR作成
- 最新HEADのRelation audit extraction
- 最新HEADのCross register QA
- 最新HEADのApply curated localization fixes
- job log、artifact、所有表、未適用差分の確認
- 軽微で局所的な構造・テスト・checkpoint修正
- 未解決レビュー確認
- squash統合
- squash commitへcheckpoint参照を付け替えるpost-merge状態PR
- post-merge状態PRの三本確認とsquash統合

public中に行わない作業:

- 新しい場面の翻訳開始
- 人物声や意味の大幅な再検討
- 複数場面の追加通読
- 原因不明のcommit試行を繰り返す
- skillやworkflowの大規模再設計
- 次束のPR作成

### 4. 深い失敗

次のいずれかなら`public_ci_blocked`として扱う。

- 訳文判断を一次資料からやり直す必要がある
- 人物資料またはskillの大幅改修が必要
- 原因不明で二回以上の追加commitが見込まれる
- 複数場面、複数target、所有境界を再設計する必要がある
- CIの安全性または公開可否に疑義が出た

この場合はその場で試行を続けず、ユーザーへ次を依頼する。

```text
公開CI窓を閉じてprivateへ戻してください。深い修正はprivate翻訳作業回で行います。
```

### 5. 終了

公開CI窓の終了条件はすべて満たす。

1. Relation audit extraction成功
2. Cross register QA成功
3. Apply curated localization fixes成功
4. 全修正束の未適用0件
5. locres、pak、lint、関係抽出、回帰、LFS確認成功
6. checkpointが`verified`
7. 未解決レビューthread 0件
8. 翻訳PRをsquash統合
9. post-merge状態PRでsquash commit参照へ同期
10. 状態PRの三本成功とsquash統合

終了後、mainの`declared_state`は`private_translation_work`とする。実visibilityがまだpublicなら導出状態は`return_private_required`となるため、直ちに次を依頼する。

```text
公開CI窓の作業は完了しました。privateへ戻してください。
```

ユーザーが`privateに戻した`と報告したら、GitHub metadataでprivateを確認する。その後に限り次の翻訳作業回へ入る。

## 冷間再開時の裁定表

| 宣言状態 | 実visibility | 裁定 |
|---|---|---|
| `private_translation_work` | private | active PRを確認し、なければ次束の翻訳へ進む |
| `private_translation_work` | public | `return_private_required`。private復帰を依頼し、翻訳を始めない |
| `ready_for_public_ci` | private | public化を依頼する。PR作成・再実行は待つ |
| `ready_for_public_ci` | public | `public_ci_window`。CI・統合を続ける |
| `public_ci_blocked` | public | private復帰を依頼する。追加試行を止める |
| `public_ci_blocked` | private | 原因をprivateで修正し、準備完了後に`ready_for_public_ci`へ戻す |

## 禁止事項

- public化をActions節約の通常手段にする
- 翻訳途中でpublic化する
- PRを開いてから一ファイル一commitで準備を続ける
- ユーザーの明示確認なしにvisibility変更済みと仮定する
- GitHub metadataを確認せず、会話だけでvisibilityを決める
- 三本成功前にmerge条件を弱める
- 公開中に次束の翻訳へ進む
- 終了後もpublicのまま放置する
