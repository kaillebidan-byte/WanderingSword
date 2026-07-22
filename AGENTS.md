# AGENTS.md — Wandering Sword 翻訳プロジェクト

> このファイルは**地図**。手順の正本ではない。詳細は各正本へ飛ぶこと。重複を増やさない。

## これは何か
中国製武侠RPG「Wandering Sword」の**日本語翻訳MOD**。ゲームの locres/pak を直接書き換えてビルドする。
2つの顔: (1) Obsidian Vault = 翻訳設定資料、(2) `_tools/` の Python パイプライン(repakで再パック)。

## 正本(まずここを読む)
- **デプロイ境界の正本・最優先**: [00_ルール/デプロイ境界.md](00_ルール/デプロイ境界.md)。修正適用・locres書き戻し・pak再生成・検証まではエージェント側、ゲームフォルダへの配置だけユーザー側。RUNBOOKや過去ログの古いデプロイ指示より優先する。
- **初回翻訳・校正の正本**: [_tools/RUNBOOK_翻訳自動実行.md](_tools/RUNBOOK_翻訳自動実行.md)。フェーズ判定・1回の作業量・進め方はRUNBOOKを参照。ただしデプロイ範囲は上記正本が上書きする。
- **人物ペア再監査の入口**: [_phase4_proofread/RUNBOOK_人物ペア再監査.md](_phase4_proofread/RUNBOOK_人物ペア再監査.md)。判断の一般正本は `.agents/skills/zhja-game-translation-codex/references/08_pair_reaudit.md`。
- **現在地**: `python _tools/status.py`。初回校正と品質再監査を分けて表示する。
- **再監査の段階・順序**: [_phase4_proofread/audit_status.json](_phase4_proofread/audit_status.json)。
- **横断TODO**: [_phase4_proofread/_TODO.md](_phase4_proofread/_TODO.md)(開いてる項目のみ)。
- **恒久ルール**: `00_ルール/`(口調・一人称・基本翻訳・世界観口調指針・典故ノート)。
- **キャラ別ペルソナ**: `10_人物/<キャラ>.md`(声の仮説・校正変換規則・原文根拠)。

## 一次資料と派生資料の優先順位 ★最重要
判断が矛盾したときは、次の順で上書きする。

1. **原文zh・現訳ja・会話前後・ゲーム内場面**
2. 同一人物・同一関係の別出現と時系列
3. 用語・設定の正本
4. ペルソナと関係性・呼称マップ
5. 過去の校正ログ・完了記録

ペルソナと関係性マップは、一次資料から作った**作業仮説**。反例が出たら訳文を無理に合わせず、資料側を改訂する。既訳からペルソナを循環的に正当化しない。

## 校正の芯
**最優先は「声の非平坦化」＝場面なりきりと文脈理解**。「このキャラがこの相手へ、この時点でどう喋るか」を再現する。
- 一人称修正と誤訳検出は前提条件であって目的ではない。これだけに痩せると、チェックは通るのにキャラが死ぬ。
- 多モードキャラのモード落差・比喩・相槌を平板に均さない。
- ペルソナは着手時に読むが、**一次資料との整合を毎回検証する**。「直しすぎより触らない」。
- 行単位で自然でも、連続会話の息切れ・言いさし・感情・因果を壊していないか場面単位で確認する。

## 「完了」と `status: 確定` の意味
- `char_progress.json` の完走 = **初回キャラ校正を一巡した**。最終品質保証ではない。
- ペルソナの `status: 確定` = **初回作業へ着手可能な仮説がある**。正当性の最終確認ではない。
- 最終的な進捗は `audit_status.json` の段階で管理する:
  - initial_pass
  - evidence_inventory
  - persona_reviewed
  - relation_reviewed
  - translation_reaudited
  - build_verified
  - game_verified
- `build_verified` = locres反映、pak再生成、機械検証済み。ゲーム内確認ではない。
- 再監査では、人物単独ではなく**関係クラスタ→人物ペア→場面→既訳**の順で見る。相手不明のままregisterを一括統一しない。

## ペルソナ着手関門(初回作業用)
`10_人物/<キャラ>.md` の `status:` を確認:
- `確定` → 初回翻訳・校正の足場として使用可。ただし反例を見つけたら監督へ戻し、資料を修正する。
- `確定でない(仮訳/なし)` → 初回校正に進まず停止して報告。ペルソナ作成はメイン直轄。
- `保留` → 着手しない。

## 修正束と適用フロー
- 高確度の実変更だけを `_phase4_proofread/fixes_*.json` へ収録する。既一致行、好みだけの言い換え、宛先・時系列不明は含めない。
- 複数修正束は `python _tools/apply_fixes_json.py _phase4_proofread/fixes_*.json` でまとめてプレビューできる。
- 同一キー・異なる値は競合として書き込み前に停止する。
- 適用時は対象locresを各1回だけ書き、pakを1回だけ再生成する。未適用0件ならrepakしない。
- PRでは `.github/workflows/apply-curated-fixes.yml` を使う。人物名・日付・バッチ番号をハードコードした一時apply workflowは作らない。
- 読み取りCIは relation/register 修正束をglobで動的検出する。

## 作業境界
- mainは、修正案の作成だけで止めず、原則として**修正適用→locres書き戻し→pak再生成→構造・lint・プレビュー検証**まで行う。
- `_tools/deploy_to_game.py` は実行しない。Steamのゲームフォルダへpakをコピー・置換しない。
- 生成物は `_work/aaWanderingSword_JP_P.pak` を基準とし、ゲーム内確認前の `game_verified` は未完了のままにする。
- 実行環境上適用できない場合は、未適用であることと理由を明示し、修正JSON・検証結果・適用コマンドを残す。

## エージェント編成
main=Opus(計画・決定・統合・難所・修正適用・再パック・検証) / Sonnet(反復校正・提案のみ・デプロイ不可・完了報告必須) / Haiku(計数・整形・決定的変換)。
優先度: `accuracy > source_intent > consistency > efficiency > style`。glossary優先・捏造禁止。

## 実行環境(Windowsネイティブ / 2026-06-15 移行)
- **Python**: `python` / `python3` どちらも 3.12.10(`python3.exe` はシム)。外部パッケージ不要(標準ライブラリのみ)。
- **repak**: `_tools/repak.exe`(0.2.3)。スクリプトは `os.name=="nt"` 分岐で `.exe` を選ぶ。Linux版ELF `_tools/repak` は残置。
- **中間ファイル**: 環境変数 **`WS_TMP`** を作業フォルダ内(`_ws_tmp/`)に設定。素の `/tmp` は同期ラグがあるため避ける。
- **`PYTHONIOENCODING=utf-8` 必須**: 無いと `pending_char.py` 等が cp932 でcrash(exit 1)・出力文字化け。
- **CJKを含むPython/JSONはstdinで渡さない**: PowerShellのパイプやheredocで日本語・中国語リテラルを化けさせない。必ずUTF-8ファイルに書いて実行する。
- 設定メニュー等のUIラベルは `系统` locres のhexキー。texture/FTextではなく通常のlocres編集で短縮・改名できる。
- **ユーザー専用デプロイ先**: `C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks`。エージェントは操作しない。
- **移行の残**: deploy_to_game の Windows パス分岐と `/tmp/_deployverify` は未対応。deployスクリプトはユーザー側のローカル作業用であり、通常のエージェント実行には含めない。詳細 [_tools/PLAN_Windows移行.md](_tools/PLAN_Windows移行.md)。

## 制御タグは絶対に壊さない
`$@$`(話者区切り。これより前=ID・話者名は変更しない)、`<Y>…</>` `<B>` `<G>` 等の色タグ、`#nl`・`\r\n`(改行)、`{0}` 等のプレースホルダ。本文だけを訳す/直す。

## 失敗時
`_backup/aaWanderingSword_JP_P.original.pak` から復元可能。pak形式は `--version V11` 固定。

## Imported Claude Cowork project instructions

# Wandering Sword Translation Project

## Priority
accuracy > source_intent > consistency > efficiency > style

## Goal
Improve translation quality.
Interpret source intent conservatively.
Avoid invention.
Glossary has precedence.

---

## Agent topology

main:
- model: Opus
- responsibility:
  - planning
  - decisions
  - integration
  - correction application
  - locres writeback
  - pak build and verification
  - difficult cases
- constraint:
  - deployment to the game folder is user-only

workers:

  sonnet:
    use_when:
      - repetitive proofreading
      - glossary normalization
      - independent pipeline execution
    constraints:
      - output proposal only
      - no deployment
      - must include completion report

  haiku:
    use_when:
      - counting
      - formatting checks
      - deterministic transforms
    constraints:
      - single-purpose only

---

## Delegation policy

Delegate only if:
- task is independent
- setup_cost < execution_cost
- inputs are self-contained
- completion criteria are explicit

Required:
- target path
- glossary
- constraints
- expected output format

Escalate back to main if confidence is low.

---

## Output rules

- hide chain-of-thought
- avoid ceremonial acknowledgements
- structure only when useful
- max one improvement proposal
- include diff and line references
- stop after completion

---

## Environment

- git → Windows native
- correction tool → WS_TMP
- JSON → UTF-8 file
- completed schedules → disable
