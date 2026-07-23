# 現在の申し送り

> 新しいチャットが過去会話なしで現在地を復元するための入口。機械可読の正本は `CURRENT_WORK.json`、次作業の具体的な着眼点は `NEXT_TASK_PACKET.json`、品質段階と件数は `audit_status.json`。`_handover.md` は履歴であり、現在地として使わない。

## 新チャットで送る一文

同じChatGPTプロジェクト内では、リポジトリURLや前回作業を聞き直さず、次の一文だけで再開する。

```text
現状把握して作業の続きを
```

受けた側は、未統合PR、GitHub Actions、main、状態文書、最新artifact、既存修正束の所有を照合する。短い報告だけで終わらず、同じ応答内で実作業へ進む。現状だけ必要な場合はユーザーが明示する。

## 現在地

- checkpoint: `verified`
- checkpointを生成した翻訳PR: #64
- active PR: #64 `agent/yuwen-mowen-batch42-review`
- クラスタ: 武当師門中核
- 人物ペア: 宇文逸↔莫問
- 段階: 既訳再監査を継続中
- 完了: 第42束
- 宇文逸↔莫問の適用キー: 1117
- プロジェクト全体の適用キー: 1370
- 最新pak: `_work/aaWanderingSword_JP_P.pak`
- build: 検証済み・ゲーム未配置
- game verification: 未開始

PR #64が開いている間は `active` としてCIと差分を先に確認する。統合済みなら、`CURRENT_WORK.immediate_next` と `NEXT_TASK_PACKET.json` から第43束へ入る。PRは開いているだけで現行作業と決めない。

## 第42束で完了したこと

`5274_1 / 5278_1` の21行を通読し、18キーを再監査した。

- 宇文逸の新規6キー
- 莫問の既存第3束4キーと第4束3キーを再改訂
- 莫棄のcross-register新規5キー
- 人物ペア累計1117、全体1370
- locres反映、pak再生成、全修正束ゼロ差分、register lint、関係抽出、単体テスト、回帰走査、LFS確認済み

初回relation CIは `5278_1` の莫問3キーが既存第4束の所有であることを検出した。新規束へ重複させず、第4束を直接再改訂した。

莫棄の人物資料にあった `哈哈→はは` の固定規則は一次資料と衝突したため、浮かれ・ごまかし・得意げなど発話機能で笑いを裁定する規則へ改訂した。skill本体は変更していない。

## 直ちに着手する作業

active PRがなければ、`5291_1 / 5292_3 / 5293_6 / 5293_7` を連続場面として監査する。

- 李府潜入前の推測
- 莫問の制止と具体的な潜入方針
- 小声の緊急連絡と救出・足止めの役割分担
- 絶無心が公門を盾にした脅しと、莫問の公道宣言
- 莫問帰還時の短い応答

推測を客観事実へ強めない。宇文逸・莫問の人物ペア行と、莫棄・絶無心のcross-register所有を分ける。既存第4束所有の六キーは新規第43束へ重複させず、必要なら元の束を直接再改訂する。

具体的な発話順、全キー、ALLUSION_REVIEW、FACT_DOUBT、所有境界、完了条件は `NEXT_TASK_PACKET.json` に固定した。パケット自体も作業仮説であり、最新artifactと一次資料の反例を優先する。

## checkpointと遷移状態

- `verified`: 状態文書、監査索引、件数、適用記録、次作業パケットが同期済み。統合可能。
- `pending_audit_sync`: 翻訳適用後、監査索引の書き戻しを待つ遷移状態。作業続行は可能だが統合禁止。
- bot書き戻し後の `action_required` は自動的に翻訳失敗と扱わない。bot差分を確認し、人手最終化後のHEADで再検証する。
- 統合前に `python _tools/check_handoff_consistency.py --require-verified` と `python _tools/check_next_task_packet.py` を成功させる。

第42束では、`pending_audit_sync`中は新しい `NEXT_TASK_PACKET`をまだ公開できない一方、workflowが無条件にパケット一致を要求して索引同期を止める循環を発見した。`check_next_task_packet.py --allow-pending` を追加し、遷移中は旧verifiedパケットの構造だけを検査する。checkpointが`verified`になれば従来どおり完全一致を要求する。apply workflowとrelation workflowの両方へ反映済み。

## 再開時の確認順

1. mainの最新状態
2. 未統合PR、head SHA、変更ファイル
3. PRを `active / superseded / abandoned / unrelated` に分類
4. レビュー、未解決スレッド、GitHub Actions
5. `CURRENT_WORK.checkpoint`
6. `README.md`、`AGENTS.md`、`SESSION_BOOTSTRAP.md`
7. `CURRENT_WORK.json`、`CURRENT_HANDOFF.md`、`NEXT_TASK_PACKET.json`
8. `audit_status.json` と適用記録
9. 人物ペアRUNBOOK、skill、style guide、register軸
10. `10_人物/宇文逸.md`、`10_人物/莫問.md`、必要なcross-register人物資料
11. 最新relation artifactの対象場面、重複座標、既存修正束

## 作業精度の関門

- 最優先は、その人物がその相手へその時点で実際に発する声として成立すること。
- 笑い、咳、息、叫び、間、反復、文字種を表記統一へ押し込まない。
- 中国語構文を移した硬い台詞は、日本語で口から出る語順、長さ、切れ目、助詞省略へ再構成する。
- `ALLUSION_REVIEW` と `FACT_DOUBT` を別々に通す。
- 客観事実、人物の認識、推測、嘘・演技、未解決を混同しない。
- ペルソナ、関係性マップ、完成例、適用済み訳、次作業パケットは正本ではない。一次資料の反例があれば資料側を直す。
- skillは毎束変更しない。複数人物・複数場面へ一般化できる新知見か、既存規則への反例がある場合だけ改修する。
- 高確度の実変更だけを修正束へ入れ、同一キー異値競合、話者接頭辞、タグ、改行、プレースホルダを適用前に検査する。
- Steamゲームフォルダへの配置とゲーム内確認は行わない。
