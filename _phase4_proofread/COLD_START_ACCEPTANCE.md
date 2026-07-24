# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. 未統合PRとGitHub Actionsを確認し、PRは開いているだけで現行作業と決めない。
3. 管理Issue #108、`agent/ci-train-phase2`、CURRENT_WORKを照合する。
4. 第61束・人物ペア1166・全1518・verifiedを復元する。
5. checkpointのrelease evidence `yuwen-mowen-train-01-r1`を復元する。
6. operation mode `ready_for_public_ci`と早期release理由`workflow_change`を復元する。
7. privateなら完成HEADと検証項目を示して公開CI窓を依頼する。
8. publicなら制度CI・単一PR最終化だけを行い、第62束へ着手しない。
9. bot書き戻し後の重い三本再起動0件を確認する。
10. 最終状態commitではphase2 gateだけを確認する。
11. 同じPRをsquash統合し、post-merge状態PRを作らない。
12. private復帰後、第62束`5455_1`へ戻る。

## 現在の期待値

- completed batch: 61
- pair applied: 1166
- project applied: 1518
- checkpoint: verified
- release id: `yuwen-mowen-train-01-r1`
- phase2: ready for public CI
- tracking issue: #108
- active branch: `agent/ci-train-phase2`
- queued translation: batch62 / `5455_1`
- actual visibility: GitHubで毎回確認

## 機械検査

```bash
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_release_evidence.py
python _tools/check_handoff_consistency_v2.py --require-verified
python _tools/check_ci_train_manifest.py
python _tools/check_next_task_packet.py
python _tools/test_check_operation_mode.py
python _tools/test_check_release_evidence.py
python _tools/test_check_handoff_consistency_v2.py
python _tools/test_check_ci_train_manifest.py
python _tools/test_check_next_task_packet_ownership.py
```

すべてが成功しない状態を第二段階の確定状態として扱わない。
