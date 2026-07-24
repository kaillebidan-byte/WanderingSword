# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. 未統合PRとGitHub Actionsを確認し、PRは開いているだけで現行作業と決めない。
3. privateかつphase2制度改修未完了なら`agent/ci-train-phase2`を優先する。
4. 第61束・人物ペア1166・全1518・verifiedを復元する。
5. checkpointの`release_identity`から`yuwen-mowen-train-01-r1`とrelease evidenceを読む。
6. squash SHAではなくPR番号、成功run、検証HEAD、件数をrelease evidenceから復元する。
7. 第二段階ではpost-merge状態PRを作らないと復元する。
8. public中は制度CI・単一PR最終化だけを行い、第62束へ着手しない。
9. 制度改修統合後はprivate復帰を依頼する。
10. private確認後、第62束`5455_1`へ戻る。

## 現在の期待値

- completed batch: 61
- pair applied: 1166
- project applied: 1518
- checkpoint: verified
- release id: `yuwen-mowen-train-01-r1`
- phase1: completed
- phase2: implementation private
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

すべてが成功しない状態を、第二段階の確定状態として扱わない。
