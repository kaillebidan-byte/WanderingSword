# Wandering Sword 日本語翻訳MOD

中国製武侠RPG「Wandering Sword」の日本語翻訳MODプロジェクトです。原文・現訳・前後文・話者・相手・時系列を一次資料として、人物の声、関係段階、典故、設定事実、locres、pakを一体で監査します。

## 新しいチャットで再開する

同じChatGPTプロジェクト内の新しいチャットでは、リポジトリURLは既知として扱います。ユーザーは基本的に次の一文だけ送れば足ります。

```text
現状把握して作業の続きを
```

この一文を受けた側は、URLや前回作業を聞き直さず、[`_phase4_proofread/SESSION_BOOTSTRAP.md`](_phase4_proofread/SESSION_BOOTSTRAP.md) の再開プロトコルを実行します。

重要なのは、**現状報告だけで終わらず、未統合PR・CI・main・状態文書を照合したあと、そのまま作業を続けること**です。ユーザーが「現状だけ」と明示した場合のみ作業を開始しません。

## 再開時に読む順番

1. [`AGENTS.md`](AGENTS.md) — プロジェクト全体の地図、資料の優先順位、作業境界
2. [`_phase4_proofread/SESSION_BOOTSTRAP.md`](_phase4_proofread/SESSION_BOOTSTRAP.md) — 起動文を受けたときの固定行動契約
3. [`_phase4_proofread/CURRENT_WORK.json`](_phase4_proofread/CURRENT_WORK.json) — 現在の人物ペア、完了束、累計、直ちに着手する場面
4. [`_phase4_proofread/CURRENT_HANDOFF.md`](_phase4_proofread/CURRENT_HANDOFF.md) — 人間向けの短い申し送り
5. [`_phase4_proofread/audit_status.json`](_phase4_proofread/audit_status.json) — 品質段階、累計、監査キューの機械可読正本
6. [`_phase4_proofread/RUNBOOK_人物ペア再監査.md`](_phase4_proofread/RUNBOOK_人物ペア再監査.md) — このプロジェクト固有の再監査入口
7. [`.agents/skills/zhja-game-translation-codex/SKILL.md`](.agents/skills/zhja-game-translation-codex/SKILL.md) — 翻訳・再監査skillの入口
8. 現在ペアの `10_人物/<人物>.md`、関係資料、一次資料抽出、最新の修正束・監査記録

ただし、文書を読む前後に必ずGitHub上の生存状態を確認します。

- `main` の最新状態
- 未統合PR
- PRのhead SHA、変更ファイル、レビュー、未解決スレッド
- head SHAのGitHub Actions
- 直近のmerged PR

未統合PRが前チャットの続きなら、`CURRENT_WORK.json.immediate_next` よりそのPRを優先します。

## 資料が食い違う場合

優先順位は次です。

1. 原文zh、現訳ja、同一場面の前後、話者、相手、時系列、分岐
2. GitHub上の未統合PR、最新HEAD、Actionsの実状態
3. 設定・用語・デプロイ境界の正本
4. `CURRENT_WORK.json` の現在地と直近作業
5. `audit_status.json` の品質段階・累計
6. ペルソナ、関係性・呼称マップ
7. `_TODO.md`、過去の監査記録、適用記録
8. `_handover.md` の履歴

ペルソナや関係性マップは作業仮説です。一次資料と衝突したら訳文を資料へ押し込まず、資料側を改訂します。

`_phase4_proofread/_handover.md` は履歴アーカイブであり、現在地の正本ではありません。`_TODO.md` は横断課題の一覧であり、件数や次場面が古い場合は `CURRENT_WORK.json` と `audit_status.json` を優先します。

## 再開時の最初の報告

通常は次の四点だけを短く報告し、そのまま作業へ入ります。

- 復元した現在ペア・完了束・累計
- 未統合PRまたはCIの状態
- 直ちに着手する場面・作業
- 古い資料や矛盾の扱い

「作業を始めてもよいか」とは聞きません。

## 状態確認

```text
python _tools/status.py
python _tools/check_handoff_consistency.py
```

`status.py` は起動文、現在地、即時作業を表示します。`check_handoff_consistency.py` は再開プロトコルの存在、起動文、現在ペア、完了束、適用キー数、最新適用記録が状態文書間で一致するか検証します。

## 作業境界

エージェント側は修正案だけで止めず、原則として修正適用、locres書き戻し、pak再生成、構造・lint・回帰・LFS確認まで行います。Steamゲームフォルダへの配置、ゲーム起動、ゲーム内確認はユーザー側の作業です。詳細は [`00_ルール/デプロイ境界.md`](00_ルール/デプロイ境界.md) を優先します。
