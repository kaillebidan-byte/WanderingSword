# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. open PRとActionsを確認する。
3. 第61束・人物ペア1166・全1518・verifiedを復元する。
4. 第一段階パイロットがPR #106・squash `f12089d1d74b18b6e25a916b9e8eb3536de0064a`で完了したと復元する。
5. public中は状態同期だけを行い、新しい翻訳を始めない。
6. 状態PR統合後はprivate復帰を依頼する。
7. private確認後、第二段階制度改修を翻訳より先に開始する。
8. 第二段階完了後、第62束`5455_1`へ戻る。

## 現在の期待値

- completed batch: 61
- pair applied: 1166
- project applied: 1518
- checkpoint: verified
- phase1: completed
- phase2: pending private system-work
- queued translation: batch62 / `5455_1`
- actual visibility: GitHubで毎回確認

## 機械検査

```bash
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_ci_train_manifest.py
python _tools/check_next_task_packet.py
python _tools/check_handoff_consistency.py --require-verified
python _tools/test_check_operation_mode.py
python _tools/test_check_ci_train_manifest.py
python _tools/test_check_next_task_packet_ownership.py
python _tools/test_check_handoff_consistency.py
```
