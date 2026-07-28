# Wandering Sword 日本語翻訳MOD

中国製武侠RPG「Wandering Sword」の日本語翻訳MODプロジェクト。原文、現訳、前後文、話者、相手、時系列を一次資料として、人物声、関係段階、典故、設定事実、locres、pakを一体で監査する。

## 新しいチャットで再開する

同じChatGPTプロジェクトではrepository URLを既知として扱う。利用者は通常、`現状把握して作業の続きを`だけ送ればよい。現状報告だけで終わらず、GitHub実体と正本を照合して有効modeの正常完了地点まで作業を続ける。

## 再開時の順序

1. `PROJECT_SCOPE_LOCK.json`
2. GitHub repository metadata、main、open PR、Actions
3. `VISIBILITY_PREFLIGHT_CONTRACT.json`
4. `EXECUTION_MODES.json`
5. `CURRENT_WORK.json`、`PRIVATE_STAGE_STATE.json`、`CI_TRAIN_MANIFEST.json`
6. `NEXT_TASK_PACKET.json`、`CURRENT_HANDOFF.md`
7. `SESSION_BOOTSTRAP.md`、`AUTONOMOUS_VISIBILITY_CYCLE.md`
8. `PRIVATE_TRANSLATION_STAGES.json`と対応文書
9. 現在ペアの一次資料、人物資料、skill

人間向け文書の固定値よりGitHub metadataと機械状態正本を優先する。manual mode用とalways-public用の文書は、active `execution_mode`に合う方だけを実行契約として使う。

## 主要正本

- 現在地・checkpoint・mode: `_phase4_proofread/CURRENT_WORK.json`
- wave・cycle: `_phase4_proofread/PRIVATE_STAGE_STATE.json`
- 正式束・transport: `_phase4_proofread/CI_TRAIN_MANIFEST.json`
- 次候補: `_phase4_proofread/NEXT_TASK_PACKET.json`
- 品質段階: `_phase4_proofread/audit_status.json`
- 実行mode: `_phase4_proofread/EXECUTION_MODES.json`
- 段階権限: `_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json`

## 整合検査

```bash
python _tools/check_operational_docs_consistency.py
python _tools/check_handoff_consistency_v2.py --require-verified
python _tools/check_private_release_preflight.py --with-tests --repository-visibility <private|public>
```

merge後reconcilerは三状態正本だけでなく、NEXT_TASK_PACKETとCURRENT_HANDOFFも同じmerge SHAへ同期する。post-merge状態専用PRは作らない。

## 資料優先順位

一次資料、同一人物・関係の別出現、用語・設定正本、ペルソナ・関係性仮説、過去ログの順で判断する。ペルソナと関係性マップは反例があれば改訂する。

## 作業境界

エージェントは修正適用、locres書戻し、pak再生成、構造・lint・回帰・LFS確認まで行う。Steamゲームフォルダへの配置、ゲーム起動、ゲーム内確認は利用者側。
