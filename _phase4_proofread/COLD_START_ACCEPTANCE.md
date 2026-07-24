# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. 未統合PRとGitHub Actionsを確認し、開いているだけで現行作業と決めない。
3. PR #111が未統合なら、最終phase2 gate、未解決thread確認、squash統合だけを続ける。
4. PR #111が統合済みでpublicなら、post-merge状態PRを作らずprivate復帰を依頼する。
5. 第65束・人物ペア1167・全1521・verifiedを復元する。
6. release evidence `yuwen-mowen-train-02-r1`を復元する。
7. Relation `30132675608`、Cross `30132675610`、Apply `30132675582`の成功を復元する。
8. release CI HEAD `4d48cf98e3e86d1f082437e483c516289d1ea24b`とasset HEAD `c002f38238b489967cc3c7d5bcf4581f790a882a`を復元する。
9. 二度のbot push後にRelation / Cross / Apply追加起動0件だったことを復元する。
10. 最終状態commitではphase2 gateだけを確認する。
11. post-merge状態PRを作らない。
12. private確認後、第66束`5504_3`を次のCI列車で開始する。

## 現在の期待値

- completed batch: 65
- reviewed batch: 65
- pair applied: 1167
- project applied: 1521
- checkpoint: verified
- release id: `yuwen-mowen-train-02-r1`
- tracking issue: #110
- release PR: #111
- active branch: `agent/yuwen-mowen-train-02`
- queued translation after private return: batch66 / `5504_3`
- actual visibility: GitHubで毎回確認

## 機械検査

```bash
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_release_evidence.py --verify-git-lineage
python _tools/check_handoff_consistency_v2.py --require-verified
python _tools/check_ci_train_manifest.py
python _tools/check_next_task_packet.py
python _tools/test_check_operation_mode.py
python _tools/test_check_release_evidence.py
python _tools/test_check_release_evidence_github.py
python _tools/test_check_handoff_consistency_v2.py
python _tools/test_check_ci_train_manifest.py
python _tools/test_check_next_task_packet_ownership.py
```

すべてが成功しない状態を確定状態として扱わない。
