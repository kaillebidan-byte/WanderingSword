# 宇文逸↔莫問 第77〜80束 適用記録

- 日付: 2026-07-26
- PR: #118
- CI列車: `yuwen-mowen-train-06`
- release: `yuwen-mowen-train-06-r1`
- release evidence: `_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_06.json`
- 品質条件: `quality_passed` / low yieldなし
- 場面: `5540_4` / `5551_2` / `5572_6` / `5572_9` / `5581_5`
- reviewed keys: 50
- unique reviewed rows: 50
- 修正キー: 16
- unique修正行: 16
- 現訳保持キー: 34
- 人物ペア新規: 0
- cross-register新規: 0
- 人物ペア累計: 1171
- プロジェクト全体累計: 1529
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`

CI run ID・CI HEAD・asset HEADの機械正本はrelease evidenceとする。この適用記録は、適用した翻訳判断・所有・件数の正本であり、CI識別子を重複管理しない。

## 第77束 `5540_4`

4キーを既存ownerへ再収録し、9キーを疑ったうえで保持した。

- 宇文逸が叔父から知らせを受けた経緯を原文の範囲へ戻した
- 叔父の心配を客観的事実へ確定しなかった
- 師父の指示を護衛・監視命令へ拡張しなかった
- 瑶姫が伏せた遼城の事情を先取りしなかった

## 第78束 `5551_2`

4キーを既存ownerへ再収録し、7キーを保持した。

- 宇文逸と叔父の自然な親しさを回復した
- 欧陽雪の柔らかな礼を保った
- 宇文逸の父親同然という感情を説明しすぎず発話へ戻した
- 家の位置と移動の促しを自然にした

## 第79束 `5572_6`

3キーを既存ownerへ再収録し、9キーを保持した。

- 瑶姫の怪人への力量評価と天龍幇への仮定を断定から戻した
- 莫問が黎城で師父たちへ尋ねる次行動を回復した
- 黎城の件と叔父の衣冠塚を建ててから出発する順序を両立させた
- `借刀杀人`は一般成句として現訳を保持した

## 第80束 `5572_9 + 5581_5`

5キーを既存ownerへ再収録し、9キーを保持した。

- 宇文逸の師兄への案じ方を自然な連続した問いへ戻した
- 瑶姫の不自然な復命表現を整理した
- `出手太狠`の暴力強度を回復した
- 欧陽雪の短い否定を柔らかな言いさしへ戻した
- `太想我`を恋愛感情へ固定せず別れの軽口へ戻した

未所有の`5572_9_Dlgs_Index0_Text`は保持のためownerを新設していない。

## 所有と件数

16修正キーはすべて既存の人物ペアowner内の再改訂である。新規人物ペアキーとcross-registerキーは0。そのため適用済みキー累計は人物ペア1171・プロジェクト全体1529から増えない。

## 機械検証

release evidenceが固定する最終成功run:

- Relation audit extraction run `30166311919`
- Cross register QA run `30166311912`
- Apply curated localization fixes run `30166311917`
- 同一CI HEAD `2b994888eae0929af76ddb886efe2c911362fcdf`
- verified asset HEAD `39f3248e9333460e2c35e110f40e944ba3bf9927`
- state-only phase2 gate run `30166513929`
- 未解決review thread 0件
- Applyで未適用差分0件を確認
- locres、pak、LFS、validate、register lint、関係抽出、単体テスト、回帰走査成功
- audit statusは第80束・人物ペア1171・全1529へ同期
- public中に新しい翻訳判断、owner変更、次小束監査は行っていない

この記録とrelease evidenceを使って第80束checkpointを確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
