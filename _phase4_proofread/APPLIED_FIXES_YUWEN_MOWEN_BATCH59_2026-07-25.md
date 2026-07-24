# 宇文逸↔莫問 第59束 適用記録

- 日付: 2026-07-25
- PR: #101
- 場面: `5444_2`・`5446_1`
- 通読行数: 12
- 修正キー: 12
- 現訳保持: 0
- 既存第6束の再改訂: 10
- 人物ペア新規: 2
- 人物ペア累計: 1165
- プロジェクト全体累計: 1516
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`
- applied assets head: `9cc0bc0e8538520b0e91cebed9cf9a7212f029a2`

## 適用した修正束

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch6.json` — 既存所有10キーを再改訂
- `_phase4_proofread/fixes_relation_yuwen_mowen_20260725_batch59.json` — 未所有の莫問2キーを新規追加

## 主な校正判断

- 莫問の起床確認、出立判断、道案内、短い同意を、古風な威厳ではなく旅を取りまとめる兄弟子の地声へ戻した
- 宇文逸の`欧陽姑娘`をこの時点の距離に合う`欧陽さん`へし、瑶姫への不要な`殿`を外した
- 寝坊後の宇文逸を復命調・謝罪文から、同行者へ砕けて詫びる発話へ戻した
- 瑶姫の美人二人という自負、待ちぼうけの誇張、語尾の伸ばしを地モードのからかいとして残した
- 欧陽雪の取りなしと出発提案を、対宇文逸の柔らかさと同行者への礼が同居する声へした
- 桟橋と進路の表示タグ、姑蘇から北西という方角、推測の強度を保持した

## 機械検証

- Relation audit extraction成功
- Cross register QA成功
- Apply curated localization fixes成功
- locres反映済み
- pak再生成済み
- 全1516キー差分0
- register lint成功
- 関係抽出・単体テスト・回帰走査成功
- pak実体・LFS確認成功
- 未解決レビューthread 0件
- bot書き戻し後の`action_required`はbot起因runを開始しない既知の挙動で、失敗ではない

ゲームフォルダへの配置とゲーム内確認は行っていない。