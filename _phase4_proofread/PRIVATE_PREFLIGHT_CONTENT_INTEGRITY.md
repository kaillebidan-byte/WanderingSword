# private公開前 内容完全性契約

## 目的

公開CIをowner整理・監査範囲修正・制御タグ修復のデバッグ環境にしない。`translation_frozen`後、public化依頼より前に、今回の監査判断と収録物が過去releaseを壊していないことを機械確認する。

正本checkerは`_tools/check_fix_owner_delta.py`、一括入口は次とする。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

## 必須条件

1. 全`fixes_*.json`で一つのfull keyを所有するファイルは一つだけである。
2. verified release基準に存在したowner keyを削除しない。
3. 新規owner key数と現在のunique owner総数がmanifestと一致する。
4. 基準から訳値が変化したfull keyは、現wave candidateの監査済み行に含まれる。
5. 変化した訳値の件数がmanifestの`fix_keys`と一致する。
6. fix値は現在locresに対して話者接頭辞、制御タグ、改行タグ、placeholderの順序を保持する。
7. 次予約`reserved_only`の行を正式ownerやfixへ先行収録しない。

## 許可するowner整理

ownerファイル間の移動は、full keyと訳値が不変で、重複も欠落も生じない場合だけ許可する。ファイル名や配置の変更を新規ownerとして数えない。

## 公開前に失敗した場合

- repositoryはprivateのまま維持する。
- `PRIVATE_STAGE_STATE.cycle_control.status`を`paused`とする。
- `stop_reason=checker_failure`と機械実行可能な`exact_next_action`を残す。
- 翻訳判断を再開せず、owner・manifest・構造だけを修復する。
- checker成功前にPRをready化せず、公開CI窓を依頼しない。

## public中の扱い

同じcheckerはorchestrator preflightとphase2でも再検査する。ただしpublic側で初めて検出されることを正常運用としない。publicで失敗した場合はApplyを開始せず、privateへ戻して修復する。
