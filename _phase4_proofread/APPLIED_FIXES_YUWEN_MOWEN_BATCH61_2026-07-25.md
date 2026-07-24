# 宇文逸↔莫問 第61束 適用記録

- 日付: 2026-07-25
- PR: #106
- CI列車: `yuwen-mowen-train-01`
- release: `schema_change`による第一段階パイロット早期release
- 場面: `5452_1`
- 通読行数: 5
- 修正キー: 3
- 現訳保持: 2
- 既存第6束の再改訂: 2
- 清虚cross-register新規: 1
- 人物ペア新規: 0
- 人物ペア累計: 1166
- プロジェクト全体累計: 1518
- status: `applied_and_pak_built_pending_audit_sync`
- build: `verified_not_deployed`
- game verification: `not_started`
- Apply run: `30122728746`
- applied assetsを含むHEAD: `239a0aaa9a6ed7d27d7dc3642065529b6f50970e`

## 適用した修正束

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch6.json` — 莫棄の既存所有2キーを再改訂
- `_phase4_proofread/fixes_cross_register_qingxu_tournament_result_20260725.json` — 清虚1キーを新規追加

## 主な校正判断

- 莫棄の明るい笑い、小逸への直接的な賞賛、湛盧剣を早く見たがる勢いを戻した
- 清虚の強行収招と内勁反噬の因果を推測へ弱めず、傷の重さや回復時期は追加しなかった
- 莫問の短い祝福と宇文逸の短い応答は現訳を保持した
- 宇文逸首位分岐を莫棄首位分岐へ遡及させていない

## 機械検証

- Apply curated localization fixes run `30122728746` 成功
- locres反映済み
- pak再生成済み
- 全修正束の未適用0件
- validate、register lint、関係抽出、単体テスト、回帰走査成功
- pak実体・LFS確認成功
- audit_statusは全1518キーへ更新済み
- 適用記録索引と最終verified checkpointは次の同期runで確定する

ゲームフォルダへの配置とゲーム内確認は行っていない。
