# Wandering Sword 日本語翻訳MOD

中国製武侠RPG「Wandering Sword」の日本語翻訳MODプロジェクトです。原文・現訳・前後文・話者・相手・時系列を一次資料として、人物の声、関係段階、典故、設定事実、locres、pakを一体で監査します。

## 新しいチャット／エージェントで再開する

過去の会話要約だけで再開しないでください。次の順でリポジトリ内の正本を読み、現在地を復元します。

1. [`AGENTS.md`](AGENTS.md) — プロジェクト全体の地図、資料の優先順位、作業境界
2. [`_phase4_proofread/CURRENT_WORK.json`](_phase4_proofread/CURRENT_WORK.json) — 現在の人物ペア、完了束、累計、直ちに着手する場面
3. [`_phase4_proofread/CURRENT_HANDOFF.md`](_phase4_proofread/CURRENT_HANDOFF.md) — 人間向けの短い申し送りと開始プロンプト
4. [`_phase4_proofread/audit_status.json`](_phase4_proofread/audit_status.json) — 品質段階、累計、監査キューの機械可読正本
5. [`_phase4_proofread/RUNBOOK_人物ペア再監査.md`](_phase4_proofread/RUNBOOK_人物ペア再監査.md) — このプロジェクト固有の再監査入口
6. [`.agents/skills/zhja-game-translation-codex/SKILL.md`](.agents/skills/zhja-game-translation-codex/SKILL.md) — 翻訳・再監査skillの入口
7. 現在ペアの `10_人物/<人物>.md`、関係資料、一次資料抽出、最新の監査・適用記録

着手前に次も確認します。

- `main` の最新コミットと未統合PR
- 最新HEADのGitHub Actions結果
- `_work/aaWanderingSword_JP_P.pak` と `audit_status.json` の適用キー数
- 既存修正束との座標・値競合

## 資料が食い違う場合

優先順位は次です。

1. 原文zh、現訳ja、同一場面の前後、話者、相手、時系列、分岐
2. 設定・用語・デプロイ境界の正本
3. `CURRENT_WORK.json` の現在地と直近作業
4. `audit_status.json` の品質段階・累計
5. ペルソナ、関係性・呼称マップ
6. `_TODO.md`、過去の監査記録、適用記録
7. `_handover.md` の履歴

ペルソナや関係性マップは作業仮説です。一次資料と衝突したら訳文を資料へ押し込まず、資料側を改訂します。

`_phase4_proofread/_handover.md` は履歴アーカイブであり、現在地の正本ではありません。`_TODO.md` は横断課題の一覧であり、件数や次場面が古い場合は `CURRENT_WORK.json` と `audit_status.json` を優先します。

## 新チャットで最初に渡す指示

```text
このリポジトリを正本としてWandering Sword日本語翻訳の続きを行ってください。
README.mdの「新しいチャット／エージェントで再開する」の順番で資料を読み、CURRENT_WORK.jsonとaudit_status.jsonから現在地を復元してください。
過去の完了記録、ペルソナ、関係性マップを正本扱いせず、原文・現訳・前後文・相手・時系列を優先してください。
作業は人物ペア→連続場面→高確度修正束→locres反映→pak再生成→ゼロ差分・lint・関係抽出・回帰・LFS確認まで進め、ゲームフォルダへは配置しないでください。
まず、復元した現在地、直ちに着手する場面、読んだ正本、矛盾や古い資料を短く報告してから作業を続けてください。
```

## 状態確認

```text
python _tools/status.py
python _tools/check_handoff_consistency.py
```

`status.py` は初回校正と品質再監査を分け、`CURRENT_WORK.json` の直近作業を表示します。`check_handoff_consistency.py` は現在ペア、完了束、適用キー数、最新適用記録が `audit_status.json` と一致するか検証します。

## 作業境界

エージェント側は修正案だけで止めず、原則として修正適用、locres書き戻し、pak再生成、構造・lint・回帰・LFS確認まで行います。Steamゲームフォルダへの配置、ゲーム起動、ゲーム内確認はユーザー側の作業です。詳細は [`00_ルール/デプロイ境界.md`](00_ルール/デプロイ境界.md) を優先します。
