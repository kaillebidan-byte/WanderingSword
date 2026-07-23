# 新チャット引継ぎ制度 実地再検証

- 日付: 2026-07-24
- 実地対象: 宇文逸↔莫問 第39束・第40束
- 結論: 一文起動と現在地復元は機能したが、PR継続判定と状態同期の遷移に不備があった。以下を再現し、制度とCIを改修した。

## 1. 開いている旧PRを現行作業と誤認する危険

### 再現

再開時にopen PRを検索するとPR #38が残っていた。

- #38: 第21束の旧PR
- #39: 同じ第21束を固定ブランチから再作成し、恒久CI、locres反映、pak再生成後にmainへ統合済み

単純な `open PRを優先` では、既に完了した第21束へ逆戻りする。

### 是正

- 未統合PRを `active / superseded / abandoned / unrelated` に分類する。
- openであることだけをactiveの根拠にしない。
- PR本文、branch、変更ファイル、後続merged PR、mainへの包含を照合する。
- 置換PRを作成した時点で旧PRへ置換先をコメントし、旧PRを閉じる。
- #38には#39による置換を記録して閉じた。

## 2. 状態文書と監査索引の同期順序

### 再現

第39束と第40束の両方で、次の順序により関係抽出が停止した。

1. 翻訳適用とpak再生成が成功
2. `CURRENT_WORK` を新しい束・件数へ更新
3. 適用記録を追加
4. relation workflowが先に `check_handoff_consistency.py` を実行
5. apply workflowによる `audit_status.record_index` 更新はまだ完了していない
6. 確定状態の不整合として停止

翻訳内容、キー、タグ、locres、pakの失敗ではなく、状態同期途中を確定状態として検査したことが原因。

### 是正

`CURRENT_WORK.checkpoint.status` を導入する。

- `pending_audit_sync`: 状態文書を先に進め、監査索引同期を待つ遷移状態。件数・索引差は警告。merge禁止。
- `verified`: 状態文書、監査索引、適用記録、件数、最終CIが同期済み。merge可能。

`check_handoff_consistency.py` は状態に応じて同じ差分を警告またはエラーへ分ける。統合前は `--require-verified` を使う。

## 3. bot書き戻し後の `action_required`

### 再現

apply workflowがlocres、pak、`audit_status.json` をbot commitとしてPR branchへ書き戻すと、そのbot commitを契機にしたworkflowが `action_required` となった。

### 是正

- `action_required` を翻訳失敗と断定しない。
- 直前のapply job成功とbot差分を確認する。
- 人手コミットでcheckpoint・適用記録を最終化する。
- 最新HEADでrelation、cross-register、applyを再実行する。
- `verified` と最終CI成功を確認してからmergeする。

## 4. 適用記録の曖昧検索

旧checkerは人物ペア別のファイル名トークンから最新適用記録を推測していた。人物ペア変更や命名変更へ弱い。

### 是正

`checkpoint.applied_record` に正確なリポジトリパスを保存し、ファイル実在と `audit_status.record_index` の完全一致を検査する。

## 5. CI改修

- relation workflowでcheckpoint回帰テストを実行
- apply workflowで監査状態更新後にhandoff checkerを実行
- `verified / pending_audit_sync` の差を単体テスト
- 状態文書・適用記録・checker変更でもapply workflowを起動

## 確定した再開契約

ユーザーの起動文は次だけでよい。

```text
現状把握して作業の続きを
```

新チャットはURLを聞き直さず、open PRを分類し、verified checkpointを復元する。active PRがあれば続行し、なければ `CURRENT_WORK.immediate_next` へ進む。現状報告だけで止まらず、同じ応答内で作業を続ける。
