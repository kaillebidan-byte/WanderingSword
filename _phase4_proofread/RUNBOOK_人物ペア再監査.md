# Wandering Sword 人物ペア再監査RUNBOOK

この文書はプロジェクト固有の薄い入口。判断手順の正本は次。

- skill: `.agents/skills/zhja-game-translation-codex/references/08_pair_reaudit.md`
- QA: `.agents/skills/zhja-game-translation-codex/references/06_qa.md`
- 現在地: `_phase4_proofread/audit_status.json`
- 開いている作業: `_phase4_proofread/_TODO.md`

## 1. 標準作業単位

1. `audit_status.json` の現在クラスタと人物ペアを確認する。
2. `_tools/extract_relation_context.py` で一次資料を抽出する。
3. 人物ペアを関係段階と場面へ分ける。
4. 既訳を `fix / keep / source-doc-fix / unresolved` へ裁定する。
5. 高確度の実変更だけを `_phase4_proofread/fixes_*.json` へ収録する。
6. ペルソナ、関係性マップ、TODO、監査台帳を更新する。
7. PRを作成し、恒久CIで検証・適用・再パックする。
8. 最終HEADのCI成功後にmainへマージする。

人物ペア監査台帳はskillの `templates/pair_audit_template.md` を使う。

## 2. 修正束の命名

推奨:

```text
fixes_relation_<pair-slug>_<YYYYMMDD>_batch<N>.json
fixes_cross_register_<scope>_<YYYYMMDD>.json
```

名前は記録用。workflowへ人物名、日付、バッチ番号をハードコードしない。

一つの束は同じ場面または同じ崩れ方へ限定する。目安は10〜40キー。既一致行、判断保留、好みだけの言い換えは含めない。

## 3. ローカル・読み取り検証

```text
python _tools/test_apply_fixes_json.py
python _tools/validate_fixes_json.py --allow-applied _phase4_proofread/fixes_*.json
python _tools/apply_fixes_json.py _phase4_proofread/fixes_*.json
python _tools/test_lint_register.py
python _tools/test_extract_relation_context.py
```

`apply_fixes_json.py` は複数JSONを統合する。

- 同一キー・同一値: 重複として許容
- 同一キー・異なる値: 書き込み前に停止
- 複数target: 各locresを1回だけ書く
- 複数修正束: pakを1回だけ生成
- 未適用0件: repak省略

## 4. PR上の自動適用

`.github/workflows/apply-curated-fixes.yml` が、同一リポジトリのPRで `fixes_*.json` が変更された場合に動く。

1. PRブランチとLFS資産をcheckout
2. 全修正束を未適用・適用済み込みで検証
3. 未適用分をまとめてlocresへ反映
4. pakを一度だけ再生成
5. 適用後ゼロ差分、lint、関係抽出、単体テストを確認
6. locresとLFS pakをPRブランチへcommit・push
7. bot起因の再実行では書き込みを停止

人物ペアごとの一時apply workflowは作らない。

読み取りCI:

- `.github/workflows/relation-audit.yml`: `fixes_relation_*.json` を動的検出
- `.github/workflows/cross-register-qa.yml`: `fixes_cross_register*.json` を動的検出

## 5. 完了段階

- `initial_pass`: 初回キャラ校正の一巡
- `evidence_inventory`: 一次資料抽出
- `persona_reviewed`: ペルソナ検証
- `relation_reviewed`: 関係・呼称検証
- `translation_reaudited`: 既訳再監査
- `build_verified`: locres反映、pak再生成、機械検証
- `game_verified`: ゲーム内表示・場面適合確認

`build_verified` と `game_verified` を混同しない。

## 6. 作業境界

エージェント側:

- 修正JSON
- locres書き戻し
- `_work/aaWanderingSword_JP_P.pak` 再生成
- CI、lint、抽出、LFS確認
- 記録更新

ユーザー側:

- `_tools/deploy_to_game.py`
- Steamゲームフォルダへのコピー・置換
- ゲーム起動とゲーム内確認

ゲーム内確認前は `game_verified: not_started` のままにする。
