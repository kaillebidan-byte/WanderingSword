# Wandering Sword 日本語翻訳MOD

中国製武侠RPG「Wandering Sword」の日本語翻訳MODプロジェクト。原文、現訳、前後文、話者、相手、時系列を一次資料として、人物声、関係段階、典故、設定事実、locres、pakを一体で監査する。

## 新しいチャットで再開する

同じChatGPTプロジェクトではrepository URLを既知として扱う。利用者は通常、`現状把握して作業の続きを`だけ送ればよい。現状報告だけで終わらず、GitHub実体と正本を照合し、再開controllerが指定した工程を続行する。

## 唯一の再開入口

repository metadataでvisibilityを取得した後、次でwork orderを得る。

```bash
python _tools/resume_work_controller.py --repository-visibility <private|public>
```

`resume_work_controller.py`は`INSTITUTION_WORK_QUEUE.json`を先に読む。`always_public_full_pipeline`で未完の制度タスクがあれば`institution_repair`を返し、そのタスクがsquash mergeされmain上で再検証されるまで翻訳cycleを開始しない。キューが空の場合だけ`translation_factory_controller.py`へ委譲する。

制度タスクはPR作成後、同じ実装PR内で現在タスクを`completed`へ更新し、PR番号を記録する。squash merge SHAは事前には確定できないため必須記録にせず、統合後にGitHub metadataから取得してmain実装とともに検証する。mainへ統合される前は同じタスクが再開され、統合後はtask order上の次の`pending`へ進む。別の起動文や貼付け引継ぎは不要とする。

翻訳work orderが返した一つのaction以外へ進んではならない。machine actionは`FACTORY_FLOW_CONTRACT.json`に登録された恒久adapterだけで実行し、adapterがなければ`factory_adapter_missing`で停止する。別API探索、一時workflow作成、trigger変更、同じ失敗引数の再試行は禁止する。

新cycle初期化は、意味境界を記録した`_factory_requests/*.json`を決定論的な次train branchへ一件だけ置き、恒久workflow `.github/workflows/translation-factory-execute.yml`へ渡す。workflowは固定artifactを取得し、mode lock、candidate、owner snapshot、四状態正本を同じcommitへ生成する。作業者が状態正本を直接編集しない。

翻訳における人間判断は次の二stationだけ。

- `semantic_bundle_boundary`: 意味単位の束境界と40〜80行の閉じ方
- `translation_quality_audit`: KEEP/FIX、修正訳、人物性・事実・典故の監査

## 再開時の順序

1. `PROJECT_SCOPE_LOCK.json`
2. GitHub repository metadata、main、open PR、Actions
3. `INSTITUTION_WORK_QUEUE.json`
4. `CURRENT_WORK.json`、`PRIVATE_STAGE_STATE.json`、`CI_TRAIN_MANIFEST.json`
5. `NEXT_TASK_PACKET.json`、`CURRENT_HANDOFF.md`
6. `resume_work_controller.py`が生成したwork order
7. `institution_repair`、または委譲された恒久adapter・二つのhuman station
8. 指定作業に必要な対象workflow、checker、tests、一次資料だけを読む

人間向け文書の固定値よりGitHub metadataと機械状態正本を優先する。制度キューがpendingなら翻訳状態正本の`immediate_next`より制度work orderを優先する。manual mode用とalways-public用の文書は、active `execution_mode`に合う方だけを実行契約として使う。

## 主要正本

- 再開経路・制度優先順位: `_phase4_proofread/INSTITUTION_WORK_QUEUE.json`
- 現在地・checkpoint・mode: `_phase4_proofread/CURRENT_WORK.json`
- wave・cycle: `_phase4_proofread/PRIVATE_STAGE_STATE.json`
- 正式束・transport: `_phase4_proofread/CI_TRAIN_MANIFEST.json`
- 次候補: `_phase4_proofread/NEXT_TASK_PACKET.json`
- 品質段階: `_phase4_proofread/audit_status.json`
- 実行mode: `_phase4_proofread/EXECUTION_MODES.json`
- 段階権限: `_phase4_proofread/PRIVATE_TRANSLATION_STAGES.json`
- 工場フロー: `_phase4_proofread/FACTORY_FLOW_CONTRACT.json`
- 工場request: `_phase4_proofread/FACTORY_REQUEST_CONTRACT.json`

## 整合検査

```bash
python _tools/resume_work_controller.py --repository-visibility <private|public> --validate-contract-only
python _tools/translation_factory_controller.py --repository-visibility <private|public> --validate-contract-only
python _tools/check_factory_adapters.py
python _tools/check_operational_docs_consistency.py
python _tools/check_handoff_consistency_v2.py --require-verified
python _tools/check_private_release_preflight.py --with-tests --repository-visibility <private|public>
```

merge後reconcilerは三状態正本だけでなく、NEXT_TASK_PACKETとCURRENT_HANDOFFも同じmerge SHAへ同期する。post-merge状態専用PRは作らない。制度キューは制度PRだけが更新し、翻訳reconcilerは変更しない。

## 資料優先順位

一次資料、同一人物・関係の別出現、用語・設定正本、ペルソナ・関係性仮説、過去ログの順で判断する。ペルソナと関係性マップは反例があれば改訂する。

## 作業境界

エージェントは修正適用、locres書戻し、pak再生成、構造・lint・回帰・LFS確認まで行う。Steamゲームフォルダへの配置、ゲーム起動、ゲーム内確認は利用者側。
