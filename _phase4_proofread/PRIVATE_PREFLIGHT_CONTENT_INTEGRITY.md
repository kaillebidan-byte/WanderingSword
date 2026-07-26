# private公開前 内容完全性契約

## 目的

公開CIをowner整理・監査範囲修正・制御タグ修復のデバッグ環境にしない。`translation_frozen`後、public化依頼より前に、今回の監査判断と収録物が過去releaseを壊していないことを機械確認する。

正本checkerは`_tools/check_fix_owner_delta.py`、一括入口は次とする。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

## 自動実行入口

`.github/workflows/private-release-preflight.yml`はrepositoryがprivateの間だけ動く。

PRがdraftではなく、次のいずれかが起きた時に現在のPR HEADをcheckoutする。

- PRをopenまたはreopenした
- draftを解除した
- ready状態のPR HEADが更新された

`CI_TRAIN_MANIFEST.status`、`PRIVATE_STAGE_STATE.stage / transport`、`CURRENT_WORK.operation_mode`が`ready_for_public_ci`相当へ揃った時だけ、既存の完全preflightと回帰を実行する。まだ準備・監査・収録の途中なら重い検査をskipする。

このworkflowはread-onlyであり、Relation、Cross、Apply、資産生成、branchへの書き戻しを行わない。draft解除はprivate preflightの起動信号であって、public化許可ではない。public化依頼は最新HEADのprivate preflight成功後にだけ行う。

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

## private preflightに失敗した場合

- repositoryはprivateのまま維持する。
- `PRIVATE_STAGE_STATE.cycle_control.status`を`paused`とする。
- `stop_reason=checker_failure`と機械実行可能な`exact_next_action`を残す。
- 翻訳判断を再開せず、owner・manifest・candidate snapshot・構造だけを修復する。
- 修復commitをpushすると、ready状態のPRではprivate preflightが同じbranchの新HEADへ自動再実行される。
- 最新HEADでcheckerが成功するまで公開CI窓を依頼しない。

## public中の扱い

同じcheckerはorchestrator preflightとphase2でも再検査する。ただしpublic側で初めて検出されることを正常運用としない。publicで失敗した場合はApplyを開始せず、privateへ戻して修復する。
