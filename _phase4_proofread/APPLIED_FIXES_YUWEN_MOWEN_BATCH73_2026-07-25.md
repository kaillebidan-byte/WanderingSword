# 宇文逸↔莫問 第70〜73束 適用記録

- 日付: 2026-07-25
- PR: #115
- CI列車: `yuwen-mowen-train-04`
- release: 通常条件 `bundle_count=4`
- 場面: `5522_1` / `5523_1` / `5525_3` / `5525_6` / `5528_7` / `5529_5`
- 通読キー数: 34
- 実質通読行数: 27（第73束の重複分岐7行を一度として数える場合）
- 修正キー: 3
- 現訳保持: 31
- 人物ペア新規: 1
- cross-register新規: 2
- 人物ペア累計: 1170
- プロジェクト全体累計: 1528
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`
- Relation run: `30145143325`
- Cross run: `30145143326`
- Apply run: `30145143320`
- CI HEAD: `abda35f9d742d71e1562c8cdebdf2fdc07643210`
- applied assetsを含むHEAD: `9707bc23aa37054e868aa8d05c21b5f7e263c900`

## 適用した修正束

- `_phase4_proofread/fixes_cross_register_xuhai_5522_1_20260725.json` — 徐海の重複罵倒を整理する1キー
- `_phase4_proofread/fixes_cross_register_huangzongzheng_5522_1_20260725.json` — 黄宗政の制止と咳を戻す1キー
- `_phase4_proofread/fixes_relation_yuwen_mowen_20260725_batch71.json` — 莫問の戦況判断を自然な兄弟子口調へ戻す1キー

第72束と第73束はkeep-only束であり、修正JSONを作らず`fix_files=[]`を正規状態として保持した。第73束は`5528_7`と完全重複する`5529_5`も同時監査し、分岐差を作っていない。

## 主な校正判断

- 包囲人数、捕縛後の処遇、黄宗政の容体を台詞以上に補っていない
- 徐海の偽傷、天龍幇の目的、受制関係を推測強度のまま保持した
- 黒白無常の「小僧ォ」「ケヒヒィ」「ぞォ」を端役固有の過剰registerとして保持した
- 書斎内の人物、城外戦闘の規模、徐海の現在地を確認済み事実へ強めていない
- FACT_DOUBTとALLUSION_REVIEWを分離した

## 機械検証

- Relation audit extraction run `30145143325` 成功
- Cross register QA run `30145143326` 成功
- Apply curated localization fixes run `30145143320` 成功
- locres反映、pak再生成、LFS確認成功
- 全修正束の未適用0件
- validate、register lint、関係抽出、単体テスト、回帰走査成功
- audit_statusは全1528キー、人物ペア1170キーへ更新済み

この記録をaudit_status索引へ同期した後、第73束のverified checkpointを同じPR内で確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
