# 宇文逸↔莫問 第39束 適用記録

- 日付: 2026-07-24
- PR: #59
- 場面: `11962_3 / 11970_3`
- 場面監査: 8キー
- 新規適用: 6キー
  - 宇文逸↔莫問: 2キー
  - 莫棄cross-register: 4キー
- 既存再改訂: 莫問2キー（第26束）
- 宇文逸↔莫問累計: 1103キー
- プロジェクト累計: 1351キー
- 対象: `CG表 / QuestDlgs`
- locres: 反映済み
- pak: `_work/aaWanderingSword_JP_P.pak` 再生成済み
- game verification: 未実施

## 検証

- 同一キー異値競合なし
- 話者接頭辞・心内語括弧・省略記号を保持
- `11962_3 / 11970_3` の同一原文を話者別に同値化
- 全1351キーの適用後差分0
- register lint成功
- 関係抽出成功
- 単体テスト・回帰走査成功
- pak実体・Git LFS確認成功
- `audit_status.json / CURRENT_WORK.json / CURRENT_HANDOFF.md` を第39束の確定値へ同期後、最終HEADを再検証する
