# 物語コンテキスト準備層 — 第1回調査記録

- status: `investigated`
- base main: `0b1945599819731a339453cab5f58ffd87ad72f1`
- scope: 既存規定、原文データ、索引、状態管理、抽出・検証資産のread-only調査
- formal reference: `false`
- phase1 / phase2 progress mutation: `none`
- translation / locres / pak mutation: `none`

この記録は、独立した物語コンテキスト準備層を設計するための調査結果である。原文を一度読んだだけの物語資料ではなく、既存校正から参照可能な正式資料でもない。

## 1. 既存制度との境界

既存の `narrative_readthrough` は、人物ペア高確度パス後に開始し、日本語通読、原文対照、修正適用、build確認まで行う後続工程である。今回の準備層は、その開始条件、進捗、完了状態を動かさない。

調査時点の不変基準は次のとおり。

- current pair: `宇文逸↔莫問`
- latest completed batch: `213`
- pair applied keys: `1438`
- project applied keys: `1814`
- build: `verified_not_deployed`
- game verification: `not_started`
- next pair inventory: `宇文逸↔莫棄 / inventory_ready`
- next-pair translation preparation: `not_started`
- existing narrative readthrough: `queued_after_pair_reaudit`

準備層は `_phase4_proofread/CURRENT_WORK.json`、`PRIVATE_STAGE_STATE.json`、`CI_TRAIN_MANIFEST.json`、`NEXT_TASK_PACKET.json`、`audit_status.json`、翻訳束、locres、pakを所有しない。

## 2. 原文索引の実体

`_phase4_proofread/source_zh.json` は、`target\x1fnamespace\x1fkey` を座標とする平坦なobjectである。

|項目|件数|
|---|---:|
|総entry|51,327|
|`CG表 / QuestDlgs`|37,003|
|`Quests任务表 / Quests`|12,571|
|`Npc / NPCs`|1,060|
|`Npc / NPCTalks`|693|
|不正な複合key|0|
|`QuestDlgs` numeric ID|2,271|
|`Quests` numeric ID|1,989|
|`QuestDlgs` scene family|8,319|

`Quests` の内訳は、少なくとも次を機械的に識別できる。

- request dialogue: 2,176
- processed dialogue: 51
- option dialogue: 2,360
- finishing dialogue: 7,684
- scene dialogue: 100
- その他: 200

ただし、この索引に含まれる値はすべて会話形式である。Quest名、目的、前提条件、遷移先などを完全に表す構造化Quest定義ではない。numeric IDの一致だけで `Quests` と `QuestDlgs` を結び付けてはならない。

## 3. 既存索引の利用可能範囲

### `by_character.json`

- 888人物
- 53,391行
- 人物単位の出現座標検索には使える
- 物語順、Quest所属、分岐順は持たない

### `_phase3_gaps/gaps_*.json`

- `CG表`: 28行
- `Npc`: 123行
- `Quests任务表`: 39行

これらは翻訳差分・残差用の小規模資料であり、全原文の章・事件索引には使えない。

### `relation_audit_queue.json` と人物ペアinventory

人物ペアの証拠抽出順、人物alias、明示呼称、同席会話の抽出には使える。章・事件・場面の物語順を定義する資料ではない。

## 4. 再利用できる実装

`_tools/extract_relation_context.py` から次を再利用できる。

- 複合keyの分解
- `$@$` による話者と本文の分離
- `*_Dlgs_IndexN_Text` の会話family化
- Index順の整列
- 原文行の会話ブロック化
- 同内容ブロックの重複統合
- JSON / Markdown出力

既存回帰には、会話解析、family解析、alias正規化、direct exchange、explicit referenceの正常系がある。

`PAIR_INVENTORY_BOOTSTRAP_CONTRACT.json` のrequest、adapter、workflow、fail-closed検証、artifact lineageは制度設計の型として使える。ただし同contractはフェイズ1状態正本を書き換えるため、準備層から直接呼ばない。

## 5. 現在不足している構造

既存資産には、次を同時に満たす正式な索引がない。

- 章 → 事件・Quest群 → 場面群 → 個別key座標
- `Quests` のrequest / processed / option / finishingと`QuestDlgs` scene familyの対応
- `NPCs` / `NPCTalks`を事件の前後へ配置する根拠
- 分岐と合流を含む物語順
- 場面開始時と終了時の知識状態
- プレイヤーと各人物の知識、信念、誤解、秘匿
- 伏線、真相、初出、示唆、判明、確定、回収先
- 場面時点資料と全ネタバレ資料の分離
- 後続展開確認前の暫定資料を正式参照から隔離する状態遷移
- 既存校正疑義から根拠keyへ逆引きする参照経路

したがって、ファイル種別、numeric ID、人物名検索のいずれか一つだけで事件群を確定する設計は成立しない。

## 6. 最初の候補probe

`26006_`、`27203_`、`大白小逸`を手掛かりに調査した。

取得できたのは、Quest名に相当する二座標と、`CG表 / QuestDlgs / 12010_3_Dlgs_Index4_Text` の一発話だけだった。この結果だけでは、開始、進行、完了、関連場面、分岐、後続回収を持つ一つの事件群を確定できない。

この候補は棄却したのではなく、`name_only_evidence_insufficient` とする。正式な試走対象は、次回以降にQuest lifecycleとscene familyを横断して選ぶ。

## 7. 第2回設計へ渡す制約

準備層は原則として `_story_context/` に独立配置する。

必要な制度要素は次のとおり。

1. 独立したcontractとstate
2. 既存フェイズ状態のread-only baseline snapshotまたはdigest
3. 章、事件、場面、keyのmanifest schema
4. 場面時点資料と全ネタバレ資料の別schema
5. 指定された七段階以上の単調な状態遷移
6. key実在、順序、二層混入、状態遷移、既存状態不変を検査するchecker
7. Quest lifecycleとscene familyの候補を出す抽出adapter
8. 暫定資料を既存校正から参照させない参照gate

正式参照可能へ上げるには、後続展開との整合確認を必須にする。全ネタバレ資料を参照した判定でも、場面時点の人物の誤解や曖昧さを誤りとして扱わない。

## 8. 一時調査物の扱い

`_tools/story_context_probe.py`、`_story_context/bootstrap_request.json`、`.github/workflows/story-context-bootstrap.yml` は調査専用である。恒久的な抽出・検証経路が実装され、同じ情報を回帰可能に取得できた時点で削除する。

## 第1回の確定地点

- 既存規定、データ構造、索引、状態管理、抽出資産、テスト経路を調査済み
- 第一回では制度schema、正式state、物語資料、翻訳修正を作成していない
- 次の作業は、上記制約に基づく独立制度の設計確定
