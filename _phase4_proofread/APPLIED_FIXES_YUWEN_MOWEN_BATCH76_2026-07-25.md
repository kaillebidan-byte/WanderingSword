# 宇文逸↔莫問 第74〜76束 適用記録

- 日付: 2026-07-25
- PR: #117
- CI列車: `yuwen-mowen-train-05`
- release: 通常条件 `reviewed_rows=53 >= 40`
- 場面: `5531_3` / `5531_4` / `5531_7` / `5535_2` / `5536_3` / `5536_4`
- 通読行数: 53
- 修正キー: 3
- 現訳保持: 50
- 人物ペア新規: 0
- cross-register新規: 0
- 人物ペア累計: 1170
- プロジェクト全体累計: 1528
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`
- Relation run: `30148094728`
- Cross run: `30148094731`
- Apply run: `30148094737`
- CI HEAD: `9e767dbd85895fff5b298d605954b0aec91fee22`
- verified asset HEAD: `9e767dbd85895fff5b298d605954b0aec91fee22`

## 適用した再改訂

既存所有 `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json` の3キーを更新した。新規所有キーはない。

- `5531_4_Dlgs_Index15_Text` — 腕輪確認を「この腕輪ですか？」へ修正
- `5531_4_Dlgs_Index22_Text` — 徐海の`放心了`を娘の無事への安堵として「安心した」へ戻した
- `5531_7_Dlgs_Index2_Text` — 天龍幇の目的を客観的断定にせず「誰かを捜していた可能性が高い」とした

第76束はkeep-only束であり、修正JSONを新設せず`fix_files=[]`を正規状態として保持した。

## 主な校正判断

- `穷寇莫追`は故事説明を加えず、戦闘時の深追い禁止として維持した
- 徐海の負傷・余命・死亡、投河後の経緯、処分、父娘再会を台詞以上に確定していない
- 天龍幇の目的と各門派の準備・一掃計画を推測・意図の範囲に留めた
- `5536_3`と`5536_4`で、清霄師伯を待つ指示の有無だけを分岐差として維持した
- 第77束`5540_4`は13行の意味境界を守り、標準下限未満の例外を機械契約へ記録した

## 機械検証

- Relation audit extraction run `30148094728` 成功
- Cross register QA run `30148094731` 成功
- Apply curated localization fixes run `30148094737` 成功
- locres反映、pak再生成、LFS確認成功
- 全修正束の未適用0件
- validate、register lint、関係抽出、単体テスト、回帰走査成功
- visibility preflight、keep-only束、release後packet、batch planning例外の契約検査成功
- 適用キーは既存所有の再改訂のみのため、人物ペア1170・全1528を維持

この記録をaudit_status索引へ同期した後、第76束のverified checkpointを同じPR内で確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
