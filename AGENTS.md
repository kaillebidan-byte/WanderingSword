# AGENTS.md — Wandering Sword 翻訳プロジェクト

> このファイルは**地図**。手順の正本ではない。詳細は各正本へ飛ぶこと。重複を増やさない。

## これは何か
中国製武侠RPG「Wandering Sword」の**日本語翻訳MOD**。ゲームの locres/pak を直接書き換えてビルドする。
2つの顔: (1) Obsidian Vault = 翻訳設定資料、(2) `_tools/` の Python パイプライン(repakで再パック)。

## 正本(まずここを読む)
- **手順の正本**: [_tools/RUNBOOK_翻訳自動実行.md](_tools/RUNBOOK_翻訳自動実行.md)。フェーズ判定・1回の作業量・進め方は**すべてRUNBOOKが上書き不可の正本**。
- **現在地**: `python _tools/status.py`(進捗・現在キャラ・開いてるTODO)。
- **横断TODO**: [_phase4_proofread/_TODO.md](_phase4_proofread/_TODO.md)(開いてる項目のみ)。
- **恒久ルール**: `00_ルール/`(口調・一人称・基本翻訳・世界観口調指針・典故ノート)。
- **キャラ別ペルソナ**: `10_人物/<キャラ>.md`(声の核・校正変換規則・原文根拠)。

## 校正(フェーズ2)の芯 ★最重要
**最優先は「声の非平坦化」＝場面なりきりと文脈理解**。「このキャラがこの場面でどう喋るか」を再現する。
- **一人称修正と誤訳検出は前提条件であって目的ではない**。これだけに痩せると、チェックは通るのにキャラが死ぬ(既知の失敗)。
- 多モードキャラ(例 顧思帰=風雅↔殺意、莫問=3モード)の**モード落差・比喩・相槌を平板に均さない**。
- ペルソナの `声の核`＋`完成例` を**先に読んで**から手を入れる。「直しすぎより触らない」。

## ★ペルソナ確定の関門(モデル分担)
`10_人物/<キャラ>.md` の `status:` を必ず確認:
- `確定` → 継続校正してよい(継続マシン/Sonnet可)。
- `確定でない(仮訳/なし)` → **校正に進まず停止して報告**。ペルソナ確定はメイン(Opus)直轄。
- `保留` → 着手しない。**現状 保留キャラは無し**（宇文逸/主人公16,276行は2026-07-01にペルソナ`確定`。校正本体はregister固定バッチでSonnet委託可＝[[PLAN_宇文逸_別セッション]] Step 3）。

## エージェント編成
main=Opus(計画・決定・統合・デプロイ・難所) / Sonnet(反復校正・提案のみ・デプロイ不可・完了報告必須) / Haiku(計数・整形・決定的変換)。
優先度: `accuracy > source_intent > consistency > efficiency > style`。glossary優先・捏造禁止。

## 実行環境(Windowsネイティブ / 2026-06-15 移行)
- **Python**: `python` / `python3` どちらも 3.12.10(`python3.exe` はシム)。外部パッケージ不要(標準ライブラリのみ)。
- **repak**: `_tools/repak.exe`(0.2.3)。スクリプトは `os.name=="nt"` 分岐で `.exe` を選ぶ。Linux版ELF `_tools/repak` は残置。
- **中間ファイル**: 環境変数 **`WS_TMP`** を作業フォルダ内(`_ws_tmp/`)に設定。素の `/tmp` は同期ラグがあるため避ける。入力JSONは bash heredoc で書く。
- **`PYTHONIOENCODING=utf-8` 必須**: 無いと `pending_char.py` 等が cp932 でcrash(exit 1)・出力文字化け。実行前に設定する。
- **CJKを含むPythonは `python -`(stdin)で渡さない**: PowerShellのパイプがソース中の日本語/中国語リテラルを「??」に化けさせ、検索や置換が静かに誤作動する。**必ず .py ファイルに書いて `python file.py` で実行**(Writeツールは正しいUTF-8で書く)。
- 設定メニュー等のUIラベルは `系统` locres の**hexキー**(例 Audio=7AAFDD7C…)。texture/FTextではなく**通常のlocres編集で短縮・改名できる**。
- **ゲーム**: `C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks`。
- **移行の残**: deploy_to_game の Windows パス分岐(B-2)と `/tmp/_deployverify`(B-3)は未対応。詳細 [_tools/PLAN_Windows移行.md](_tools/PLAN_Windows移行.md)。

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
  - deployment
  - difficult cases

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
- JSON → bash heredoc
- completed schedules → disable
