# 現在の申し送り

> 機械正本は`CURRENT_WORK.json`、列車は`CI_TRAIN_MANIFEST.json`、確定releaseはcheckpointが指すrelease evidence、次束は`NEXT_TASK_PACKET.json`。turn入口は`VISIBILITY_PREFLIGHT_CONTRACT.json`を最初に適用する。

## 新しいチャットで送る一文

```text
現状把握して作業の続きを
```

## 現在地

- 実visibility: public（GitHub metadataで確認済み）
- open PR: #117
- active Issue: #116
- active branch: `agent/yuwen-mowen-train-05`
- operation mode: `ready_for_public_ci`
- effective mode: `public_ci_window`
- active train: `yuwen-mowen-train-05` / verified
- train totals: 3束 / 53行 / 3修正 / 新規人物ペア0キー
- reviewed / completed: 第76束まで
- checkpoint: 第76束 / 人物ペア1170 / 全1528 / verified
- release evidence: `yuwen-mowen-train-05-r1`
- CI HEAD: `9e767dbd85895fff5b298d605954b0aec91fee22`
- verified asset HEAD: `4d5ad76ebad311de0a6afdd501b02af666b6c6be`
- 未適用fix: 0
- build: verified_not_deployed
- game verification: not_started

## 第74〜76束release

- 第74束`5531_3`・`5531_4`: 28行 / 2修正 / 26保持
- 第75束`5531_7`・`5535_2`: 11行 / 1修正 / 10保持
- 第76束`5536_3`・`5536_4`: 14行 / 0修正 / 14保持
- 3修正は既存第8束所有キーの再改訂で、適用キー件数は人物ペア1170・全1528を維持
- `穷寇莫追`はALLUSION_REVIEW、設定事実疑義はFACT_DOUBTとして分離
- 第77束`5540_4`は13行の短場面例外を`no_adjacent_in_scope_scene`として記録
- Relation run `30148094728` 成功
- Cross run `30148094731` 成功
- Apply run `30148094737` 成功
- locres反映、pak再生成、LFS、register lint、関係抽出、回帰検査成功
- audit_statusは第76束・全1528キー・人物ペア1170キーへ同期済み
- 適用記録、release evidence、verified checkpointを同じPR内で確定済み

## 次に行うこと

1. public phase2 gateを成功させる。
2. 未解決review thread 0件を確認する。
3. 実visibilityをprivateへ戻す。
4. private metadata closeout後、PR #117をsquash統合する。
5. mainの第76束verified checkpointから新しいprivate列車を開始する。
6. 第77束`5540_4`を監査する。

public中は第77束の翻訳判断を始めない。
