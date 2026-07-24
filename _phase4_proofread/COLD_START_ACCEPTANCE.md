# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityがprivateであることを確認する。
2. main、未統合PR、GitHub Actionsを確認し、開いているだけで現行作業と決めない。
3. open PR 0件、Issue #112、`agent/yuwen-mowen-train-03`をactiveとして復元する。
4. 第65束・人物ペア1167・全1521・verified checkpointを復元する。
5. release evidence `yuwen-mowen-train-02-r1`とPR #111の完了を履歴として復元する。
6. train-03が0束・0行・0修正・新規人物ペア0キーのaccumulating状態であることを復元する。
7. `NEXT_TASK_PACKET.json`から第66束`5504_3`の14行と所有境界を復元する。
8. privateで作業可能なので、状態報告だけで止まらず同じ応答内で第66束の監査へ進む。
9. 既存第7束、未所有人物ペア、瑶姫cross-registerを分離する。
10. 小束ではlocresとpakを更新せず、last_reviewed_batchとmanifestだけを進める。
11. release条件到達時だけpublic化を依頼し、第二段階の単一PR最終化を使う。
12. post-merge状態PRを作らない。

## 現在の期待値

- completed batch: 65
- reviewed batch: 65
- pair applied: 1167
- project applied: 1521
- checkpoint: verified
- last release id: `yuwen-mowen-train-02-r1`
- last release PR: #111
- active train: `yuwen-mowen-train-03`
- active branch: `agent/yuwen-mowen-train-03`
- tracking issue: #112
- train totals: 0 bundles / 0 rows / 0 fixes / 0 new pair keys
- queued translation: batch66 / `5504_3`
- actual visibility: private（GitHub metadataで毎回再確認）

## 機械検査

```bash
python _tools/check_operation_mode.py --repository-visibility private
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
