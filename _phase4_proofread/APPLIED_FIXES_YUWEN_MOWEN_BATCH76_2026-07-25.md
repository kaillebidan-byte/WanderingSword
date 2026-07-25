# 宇文逸↔莫問 第74〜76束 適用記録

- 日付: 2026-07-25
- PR: #117
- CI列車: `yuwen-mowen-train-05`
- release: `yuwen-mowen-train-05-r2`
- 品質条件: 低収穫再監査完了 / `quality_passed`
- 場面: `5531_3` / `5531_4` / `5531_7` / `5535_2` / `5536_3` / `5536_4`
- reviewed keys: 53
- unique reviewed rows: 47
- 修正キー: 7
- unique修正行: 6
- 現訳保持キー: 46
- 人物ペア新規: 1
- cross-register新規: 0
- 人物ペア累計: 1171
- プロジェクト全体累計: 1529
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`
- Relation run: `30149789606`
- Cross run: `30149789605`
- Apply run: `30149789594`
- CI HEAD: `a568f731dcf419c766dc6a3845461aed1f83d46a`
- verified asset HEAD: `1b84e1586fa13802525904cfbe192ebd3f4972bc`

## 初回監査で適用した3キー

- `5531_4_Dlgs_Index15_Text` — 腕輪確認を「この腕輪ですか？」へ修正
- `5531_4_Dlgs_Index22_Text` — 徐海の`放心了`を娘の無事への安堵として「安心した」へ戻した
- `5531_7_Dlgs_Index2_Text` — 天龍幇の目的を客観的断定にせず「誰かを捜していた可能性が高い」とした

## 低収穫再監査で追加した4キー

- `5535_2_Dlgs_Index2_Text` — 黄宗政本人の助力を「私の力」と明示した
- `5535_2_Dlgs_Index4_Text` — 見送る側の「失礼する」を「さらばだ」へ直し、発話役割を回復した
- `5536_3_Dlgs_Index5_Text`
- `5536_4_Dlgs_Index5_Text` — 原文`带人`にない「門人」の設定追加を除き、「人を連れて」へ戻した

`5535_2_Dlgs_Index4_Text`は旧第8束ownerに存在しなかったため、今回の新規人物ペア1キーとして同じfix fileへ追加した。ほか6キーは既存ownerの再改訂である。

## 品質・段階制度

- 初回修正率は3 / 47 unique rowsで15%未満だったため、初回keep全44 unique rowsを第二巡で疑い直した
- 第二巡で4キー / 3 unique rowsの見落としを発見した
- `reviewed_keys`と`unique_reviewed_rows`、`fix_keys`と`unique_fix_rows`を分離した
- `private_preparation -> private_quality_audit -> private_encoding -> ready_for_public_ci`をtrain-05の既存証拠から遡及固定した
- RelationとApplyで翻訳品質checkerおよびprivate段階checker・回帰testが成功した
- public中は新しい翻訳判断を行っていない

## 機械検証

- Relation audit extraction run `30149789606` 成功
- Cross register QA run `30149789605` 成功
- Apply curated localization fixes run `30149789594` 成功
- Apply前は4件、Apply後は未適用0件・適用済み1529件
- locres反映、pak再生成、LFS確認成功
- validate、register lint、関係抽出、単体テスト、回帰走査成功
- audit statusは第76束・人物ペア1171・全1529へ更新された

この記録をrelease evidence `yuwen-mowen-train-05-r2`の正本とし、同じPR内でverified checkpointと次束packetを確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
