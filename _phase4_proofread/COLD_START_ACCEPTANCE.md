# 新チャット冷間再開 受入基準

## 目的

同じChatGPTプロジェクトの新しいチャットが、過去会話の要約を前提にせず、GitHub上の正本だけから現在地と次作業の判断精度を復元できることを検証する。

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

新チャットは次を順に実行する。

1. main、未統合PR、レビュー、未解決スレッド、Actionsを確認し、PRを`active / superseded / abandoned / unrelated`へ分類する。
2. `CURRENT_WORK.json`のverified checkpointを復元する。
3. `NEXT_TASK_PACKET.json`を読み、対象場面、一次資料の取得方法、発話順、所有者境界、疑義候補、skill改修判定、完了条件を復元する。
4. artifactは最新成功runから取得し、パケット中の観点を一次資料で再検証する。パケットの判断を答えとして盲信しない。
5. 短い現状報告だけで止まらず、active PRがなければ同じ応答内で次場面の通読へ入る。
6. skillは毎束変更しない。既存規則で扱える場合は監査記録だけに残し、一般化可能な新知見または反例が出た場合だけ適切な層を改修する。
7. 人物ペア所有、cross-register所有、他人物所有を分け、同一場面という理由で一束へ混在させない。
8. 最終的にlocres、pak、ゼロ差分、lint、関係抽出、回帰、LFS、状態文書、次の作業パケット、verified checkpointまで更新する。

## 現在の冷間再開期待値

- 人物ペア: 宇文逸↔莫問
- 完了: 第41束
- 人物ペア適用キー: 1111
- 全体適用キー: 1359
- checkpoint: verified
- active PR: GitHubで実検索して判定
- active PRがない場合の次場面: `5274_1 / 5278_1`

## 機械検査

```bash
python _tools/check_handoff_consistency.py --require-verified
python _tools/check_next_task_packet.py
```

両方が成功しない状態を、新チャットへ渡せる確定状態とは扱わない。
