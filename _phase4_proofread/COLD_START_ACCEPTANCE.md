# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. open PRとActionsを確認し、active列車を復元する。
3. `CURRENT_WORK`、`CI_TRAIN_MANIFEST`、`NEXT_TASK_PACKET`を照合する。
4. 第61束・人物ペア1166・全1518・verifiedを復元する。
5. public中は第62束の翻訳を始めず、PR #106とpost-merge状態同期だけを続ける。
6. 公開CI窓完了後はprivate復帰を依頼する。
7. private確認後、第二段階制度改修へ進む。

## 現在の期待値

- train: `yuwen-mowen-train-01`
- train status: `verified`
- completed batch: 61
- next batch: 62 / `5455_1`
- pair applied: 1166
- project applied: 1518
- checkpoint: verified
- active translation PR: #106（統合前なら継続）
- 実visibility: GitHubで毎回確認

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
