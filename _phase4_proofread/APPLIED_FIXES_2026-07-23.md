# 検証済み修正70キーの反映記録

日付: 2026-07-23  
状態: locres反映・pak再生成・機械検証済み／ゲーム未配置・未確認

## 適用範囲

|修正セット|対象|キー数|
|---|---|---:|
|`fixes_cross_register_20260723.json`|絶無心の対道長・対宇文逸register|24|
|`fixes_cross_register_coldhawk_20260723.json`|冷鷹の対主人公二人称|32|
|`fixes_relation_yuwen_qingxu_20260723_batch1.json`|宇文逸↔清虚道長の初回関係監査|14|
|合計||70|

## 生成物

- 更新locres:
  - `_work/jp/Wandering_Sword/Content/Localization/CG表/zh-Hans/CG表.locres`
  - `_work/jp/Wandering_Sword/Content/Localization/Npc/zh-Hans/Npc.locres`
- 更新pak:
  - `_work/aaWanderingSword_JP_P.pak`
- pakはGit LFS管理。

## 実行した検証

適用前:

- 全70複合キーの存在
- 新旧値の実差分
- `$@$` 前の話者接頭辞不変
- タグ、改行、プレースホルダの並び不変

適用後:

- 3修正JSONすべてのプレビューが `計0件`
- `test_lint_register.py` 成功
- `test_extract_relation_context.py` 成功
- `lint_register.py` 完走
- `extract_relation_context.py` 完走
- pakが空でなく、LFS対象として認識されることを確認

修正JSONは適用後も回帰仕様として保持する。`validate_fixes_json.py --allow-applied` により、未適用候補と適用済み値の両方を検査できる。

## デプロイ境界

次は実行していない。

- `_tools/deploy_to_game.py`
- Steamゲームフォルダへのコピー・置換
- ゲーム起動とゲーム内表示確認

したがって `game_verified` は未完了。人物ペア単位の残候補再監査も継続する。
