# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. 未統合PRとGitHub Actionsを確認し、PRは開いているだけで現行作業と決めない。
3. PR #109が未統合なら、制度CI・未解決thread確認・squash統合だけを続ける。
4. PR #109が統合済みでpublicなら、post-merge状態PRを作らずprivate復帰を依頼する。
5. 第61束・人物ペア1166・全1518・verifiedを復元する。
6. checkpointのrelease evidence `yuwen-mowen-train-01-r1`を復元する。
7. 第二段階の検証HEAD `a0274dd1fcfa4ac66657d820a6fafaf985c3a209`と四本の成功runを復元する。
8. 最終状態commitではphase2 gateだけが起動し、Relation / Cross / Applyが起動しないことを確認する。
9. private確認後、`yuwen-mowen-train-02`を0束・0行・0修正キーから開始する。
10. 第62束`5455_1`をtrain-02の最初の小束として監査する。
11. 後続`5501_2`を件数合わせで混ぜない。
12. 今後のreleaseも単一PR内でrelease evidenceと状態を確定し、post-merge状態PRを作らない。

## 現在の期待値

- completed batch: 61
- pair applied: 1166
- project applied: 1518
- checkpoint: verified
- release id: `yuwen-mowen-train-01-r1`
- phase2 system PR: #109
- phase2 validation head: `a0274dd1fcfa4ac66657d820a6fafaf985c3a209`
- next train: `yuwen-mowen-train-02`
- next train status: accumulating
- next train totals: 0束 / 0行 / 0修正キー
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

すべてが成功しない状態を第二段階の確定状態またはprivate翻訳再開状態として扱わない。
