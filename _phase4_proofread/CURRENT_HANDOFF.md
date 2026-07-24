# 現在の申し送り

> 新しいチャットが過去会話なしで現在地を復元するための入口。機械可読の正本は `CURRENT_WORK.json`、公開CI窓の運用正本は `PUBLIC_CI_WINDOW.md`、次作業の具体的な着眼点と所有表・監査行数計画は `NEXT_TASK_PACKET.json`、品質段階と件数は `audit_status.json`。`_handover.md` は履歴であり、現在地として使わない。

## 新チャットで送る一文

同じChatGPTプロジェクト内では、リポジトリURLや前回作業を聞き直さず、次の一文だけで再開する。

```text
現状把握して作業の続きを
```

受けた側は、最初にGitHub repository metadataの実visibilityと`CURRENT_WORK.operation_mode`を照合し、その後に未統合PR、GitHub Actions、main、状態文書、最新artifact、既存修正束の実所有を確認する。短い報告だけで終わらず、実visibilityがprivateで翻訳作業可能なら同じ応答内で実作業へ進む。visibility操作が必要な場合は、それを翻訳より先に依頼する。

## 現在地

- checkpoint: `verified`
- checkpointを生成した翻訳PR: #101（統合済み）
- 直近の統合済み翻訳PR: #101
- 直近の状態同期PR: #102（統合済み）
- 未統合PR: なし
- superseded PR: #74・#75
- クラスタ: 武当師門中核
- 人物ペア: 宇文逸↔莫問
- 段階: 既訳再監査を継続中
- 完了: 第59束
- 宇文逸↔莫問の適用キー: 1165
- プロジェクト全体の適用キー: 1516
- 最新pak: `_work/aaWanderingSword_JP_P.pak`
- build: 検証済み・ゲーム未配置
- game verification: 未開始
- 宣言operation mode: `ready_for_public_ci`
- 実visibility: private（GitHub metadataで確認済み）
- 完成ブランチ: `agent/yuwen-mowen-batch60-review`
- PR: public確認後に作成

## visibilityと作業モード

- 第60束の翻訳判断、修正JSON、レビュー、適用待ち記録はprivateブランチ上で完成済み。
- 宣言状態は`ready_for_public_ci`。実visibilityがprivateなら、完成HEADと終了条件を示してユーザーへ`公開CI窓を開いてください。`と依頼する。
- ユーザーの`公開した`だけで進めず、GitHub metadataでpublicを確認してからPR作成・三本CI・統合へ進む。
- public中はCI、artifact調査、局所修正、レビュー確認、翻訳PRとpost-merge状態PRのsquash統合だけを行い、次束の翻訳は始めない。
- 深い再検討が必要なら`public_ci_blocked`としてprivate復帰を依頼する。
- 公開CI窓の終了後、mainは`private_translation_work`へ戻す。実visibilityがpublicならprivate復帰を依頼する。

## 第60束の公開CI待ち状態

`5450_3`の9行を通読し、6キーを修正対象、3キーを現訳保持とした。

- 既存第6束の再改訂: Index1・2・3・4・6の5キー
- 第60束の人物ペア新規: 莫問Index5の1キー
- 人物ペア累計予定: 1166
- プロジェクト全体累計予定: 1517
- レビュー: `_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH60_2026-07-25.md`
- 適用待ち記録: `_phase4_proofread/APPLIED_FIXES_YUWEN_MOWEN_BATCH60_2026-07-25.md`

主な裁定は次のとおり。

- 元鳴の`有些人`を名指しの断罪へせず、`誰かさん`という遠回しな嫌味と自己保身の棘へ戻した
- 莫問の宇文逸擁護を`侠義を行う`という翻訳調から、短く断定する兄弟子の声へした
- 莫棄の重ねた同意、四大悪人への軽視、再戦の戦意を豪放な常体へ戻した
- 莫問の制止を格言調から即時の`無茶をするな`へした
- 相手の余力と警戒対象は莫問の推測に留め、品剣大会前の不穏さと早めの出航判断を保持した
- `杜彪が再襲すること`、`宇文逸に責任があること`、`相手が全力でなかったこと`を設定事実へ強めていない

`5450_3`の対峙後判断を一場面で閉じる。`5449_2`と`5452_1`は門内大比の結果分岐、`5455_1`は清虚による別時点の出立指示である。数値順や件数合わせでは混在させず、9行の小束例外とした。

今回の崩れは既存skillで扱えたため、skill・人物資料は変更していない。

## 公開CI粒度の見直し

センパイから、翻訳量に対して公開CI窓の往復と状態同期が細かすぎるとの指摘があった。今回は現行制度のまま第60束を完了し、次の公開CI窓終了後に制度案を提示する。

観測値と比較論点は `_phase4_proofread/CI_CADENCE_REVIEW_NOTES_2026-07-25.md` に記録した。現時点では結論を出さず、第60束の実測を追加してから、翻訳量、安全境界、失敗切り分け、冷間再開精度を比較する。

## checkpointと遷移状態

- 現在の確定checkpointは第59束の`verified`。第60束はまだlocres・pak未反映。
- `ready_for_public_ci`: private上で翻訳判断と準備が完成し、PR作成・三本CI・統合のためのpublic化を待つ状態。
- `pending_audit_sync`: 翻訳適用後、botの監査索引書き戻しと最終状態確定を待つ遷移状態。統合禁止。
