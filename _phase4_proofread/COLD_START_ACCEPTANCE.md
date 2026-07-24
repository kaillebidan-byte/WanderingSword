# 新チャット冷間再開 受入基準

## 目的

同じChatGPTプロジェクトの新しいチャットが、過去会話の要約を前提にせず、GitHub上の正本だけから現在地、実visibility、作業モード、次作業の判断精度を復元できることを検証する。

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

新チャットは次を順に実行する。

1. GitHub repository metadataから実visibilityを確認する。会話中の申告や状態文書だけでpublic/privateを決めない。
2. `CURRENT_WORK.operation_mode`と`PUBLIC_CI_WINDOW.md`を読み、宣言状態と実visibilityから有効状態を導出する。
3. main、未統合PR、レビュー、未解決スレッド、Actionsを確認し、PRを`active / superseded / abandoned / unrelated`へ分類する。
4. `CURRENT_WORK.json`のverified checkpointを復元する。
5. `NEXT_TASK_PACKET.json`を読み、対象場面、一次資料の取得方法、発話順、所有者境界、疑義候補、skill改修判定、完了条件を復元する。
6. artifactは最新成功runから取得し、パケット中の観点を一次資料で再検証する。パケットの判断を答えとして盲信しない。
7. 実visibilityがprivateかつ有効状態が`private_translation_work`なら、短い報告だけで止まらず、active PRがなければ同じ応答内で次場面の通読へ入る。
8. 宣言状態が`ready_for_public_ci`で実visibilityがprivateなら、完成HEADと終了条件を示してユーザーへpublic化を依頼し、PR作成や再実行を先走らない。
9. 宣言状態が`ready_for_public_ci`で実visibilityがpublicなら、`public_ci_window`としてCI・レビュー・squash統合・post-merge状態同期だけを続け、新しい翻訳を始めない。
10. 宣言状態が`private_translation_work`または`public_ci_blocked`なのに実visibilityがpublicなら、`return_private_required`としてprivate復帰を依頼し、翻訳作業へ入らない。
11. skillは毎束変更しない。既存規則で扱える場合は監査記録だけに残し、一般化可能な新知見または反例が出た場合だけ適切な層を改修する。
12. 人物ペア所有、cross-register所有、他人物所有を分け、同一場面という理由で一束へ混在させない。
13. 最終的にlocres、pak、ゼロ差分、lint、関係抽出、回帰、LFS、状態文書、次の作業パケット、verified checkpointまで更新する。
14. 公開CI窓の終了後はmainを`private_translation_work`へ戻し、実visibilityがpublicならユーザーへprivate復帰を依頼する。

## 現在の冷間再開期待値

- 人物ペア: 宇文逸↔莫問
- 完了: 第60束
- 人物ペア適用キー: 1166
- 全体適用キー: 1517
- checkpoint: verified
- 宣言operation mode: `ready_for_public_ci`
- 実visibility: GitHubで毎回確認
- 実visibilityがpublicなら導出状態: `public_ci_window`
- active PR: #103をGitHubで実確認
- PR #103が統合済みでactive PRがなくprivateなら次場面: `5452_1`

## 機械検査

```bash
python _tools/test_check_operation_mode.py
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_handoff_consistency.py --require-verified
python _tools/check_next_task_packet.py
```

すべてが成功しない状態を、新しいチャットへ渡せる確定状態とは扱わない。`check_operation_mode.py`が`ACTION REQUIRED`を表示した場合は構造エラーではないが、表示されたvisibility操作を翻訳作業より先に処理する。
