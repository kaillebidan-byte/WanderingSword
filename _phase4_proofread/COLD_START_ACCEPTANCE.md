# 新チャット冷間再開 受入基準

## 目的

過去会話なしでGitHub上の実状態から、verified checkpoint、active CI列車、蓄積済み小束、次小束、visibility操作を復元する。

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. repository metadataで実visibilityを確認する。
2. open PRをactive / superseded / abandoned / unrelatedへ分類する。
3. phase1 pilotのdraft PRがあればactive CI列車として扱い、head branchを読む。
4. `CURRENT_WORK`、`CI_TRAIN_MANIFEST`、`NEXT_TASK_PACKET`のtrain id、branch、base checkpointを照合する。
5. verified checkpointとreviewed_pending_ci小束を混同しない。
6. manifest totalsを各bundleの合計から再計算する。
7. release条件は4束、40行、20修正キーのOR、上限は6束または60行と復元する。
8. accumulating + privateなら同じbranchで次小束へ進む。
9. accumulating + publicならprivate復帰を依頼する。
10. ready + privateなら完成HEADと集計を示してpublic化を依頼する。
11. ready + publicならCI・レビュー・統合だけを行い、新しい小束を追加しない。
12. 小束ごとの修正JSON、レビュー、所有、疑義を別々に復元できる。
13. 深い翻訳判断が必要ならpublicで試行せずprivateへ戻す。
14. 第一段階ではpost-merge状態PRまで完了後、private復帰を依頼する。

## 現在の期待値

- checkpoint: 第60束 / 人物ペア1166 / 全1517 / verified
- active train: `yuwen-mowen-train-01`
- branch: `agent/ci-train-phase1-pilot`
- status: accumulating
- totals: 0束 / 0行 / 0修正キー
- next: 第61束 `5452_1`
- visibility: GitHubで毎回確認

## 機械検査

```bash
python _tools/test_check_operation_mode.py
python _tools/test_check_ci_train_manifest.py
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_ci_train_manifest.py
python _tools/check_handoff_consistency.py --require-verified
python _tools/check_next_task_packet.py
```

すべてが成功しない状態を、次チャットへ渡せる確定したprivate蓄積状態または公開CI準備状態として扱わない。
