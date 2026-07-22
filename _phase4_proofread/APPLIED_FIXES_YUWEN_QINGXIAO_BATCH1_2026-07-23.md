# 宇文逸↔清霄道長 第1修正束 適用記録

## 対象

`_phase4_proofread/fixes_relation_yuwen_qingxiao_20260723_batch1.json`

- 19キー
- 対象locres: `CG表`
- 対象場面:
  - 祖師殿での問い
  - 無名・清虚襲撃の真相を知った反応
  - `6118_1_Dlgs` の病身・天山決着・宇文逸への託し
  - 終盤の掌門令牌と武当の未来の託宣
  - 副掌門任命時の功績評価
  - 峋谷援軍をためらう宇文逸への訓戒

## 修正方針

- 弟子への全面敬体を、関係段階と感情に合う常体へ戻す。
- 初期叱責の `お前` は保持し、後期の信頼・病身・託宣では `そなた／逸児／省略` を使う。
- `老夫` を軸にするが、言いさしへ機械的に補充しない。
- 咳、短句、沈黙、感情の上昇を連続場面として揃える。
- `逸よ` の誤変換を `逸児` へ修正する。
- 話者接頭辞、タグ、改行、プレースホルダを変更しない。

## 適用・検証

恒久workflow `.github/workflows/apply-curated-fixes.yml` で実行。

- 既存161キーと新規19キーを一括検証。
- 修正束間の競合なし。
- 全19キーの存在と実差分を確認。
- 話者接頭辞、タグ、改行、プレースホルダ不変。
- locresへ反映。
- pakを一度だけ再生成。
- 適用後、全180キーのプレビューがゼロ差分。
- `test_apply_fixes_json.py`、`test_lint_register.py`、`test_extract_relation_context.py` 成功。
- register lintと人物ペア一次資料再抽出に成功。
- `_work/aaWanderingSword_JP_P.pak` の実体とGit LFS管理を確認。
- locresとpakをPRブランチへ自動コミット。

## 状態

- `evidence_inventory`: complete
- `persona_reviewed`: in_progress
- `relation_reviewed`: in_progress
- `translation_reaudited`: batch1_in_progress
- `build_verified`: batch1_complete
- `game_verified`: not_started

## 境界

Steamゲームフォルダへの配置とゲーム内確認は行っていない。
