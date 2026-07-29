# 常時public full pipeline

## 対象と選択

最初に`PROJECT_SCOPE_LOCK.json`で対象を`kaillebidan-byte/WanderingSword`へ固定する。別repositoryを探索、参照、変更してから戻る運用は禁止する。

新しいcycleを始める直前にWanderingSword repository metadataを確認する。

- privateなら`manual_visibility_cycle`
- publicなら`always_public_full_pipeline`

選択は次で二つの状態正本へ固定する。

```bash
python _tools/select_cycle_execution_mode.py --repository-visibility public --write
```

入力文は従来と同じ`作業の続きを`を使う。モード専用の起動文は設けない。

進行中cycleの`execution_mode`と`cycle_start_visibility`は変更しない。前cycleのtransportが`merged`になった後だけ次cycleのモードを選べる。

## 定型再開と制度優先

常時public modeの再開入口は次とする。

```bash
python _tools/resume_work_controller.py --repository-visibility public
```

`INSTITUTION_WORK_QUEUE.json`にpending taskがある間は、翻訳状態正本の次候補より制度work orderを優先する。現在taskの実装PRを作成後、同じPR内でstatusを`completed`へ更新しPR番号を記録する。squash merge SHAは統合前に確定しないため事前記録を要求せず、統合後にGitHub metadataで検証する。squash mergeとmain再検証が済むまでは同じtaskを再開する。task orderが空になった場合だけ`translation_factory_controller.py`へ委譲する。

利用者は`現状把握して作業の続きを`または同じ意図の定型文だけを使う。制度改修用の別起動文、長文引継ぎ、次タスクの手選択を要求しない。

## 実行順

常時publicでも段階機械は変えない。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> orchestrator -> state finalization -> release phase2 -> review thread 0 -> squash merge -> merged-state reconciliation`

`private_*`は認知段階の名前であり、repository visibilityを意味しない。

## 権限

- `private_preparation`: 翻訳判断、fix書込み、owner書込みを行わない
- `private_quality_audit`: 翻訳判断だけを行う。fix、owner、正式束を書かない
- `private_encoding`: 記録済み判断だけを収録する。新しい翻訳判断を行わない
- `translation_frozen`以後: 翻訳判断、fix追加、owner変更、次wave準備を行わない

publicであることを理由に段階権限を広げない。

## CI境界

通常commit、PR作成、ready化だけでは重いCIを起動しない。

manifest ready、translation freeze、release preflight成功後に既存の`release-ci`入口を使う。Relation、Cross、Apply、finalization、release phase2は既存経路をそのまま使う。

orchestrator開始時にevent HEADとlive PR HEAD、`translation_frozen`、`ready_for_public_ci`、train・branch・PR lineageを照合する。どれかが古い場合は失敗にせず`stale_noop`としてreleaseラベルを外し、Relation以降を開始しない。

activeなreleaseラベルを持つbranchへ`synchronize`が発生した場合もguardだけを走らせ、ラベルを外して成功NOOPにする。修復後の最新HEADでreleaseを再開するには、人間が`release-ci`または`ci-heavy-rerun`を明示的に付け直す。botによるstation遷移も同じcleanupを通す。

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointとして記録する。ただし常時public modeでは正常停止地点にしない。追加のvisibility操作を求めず、同じcycleでsquash mergeまで進む。

merge後は`.github/workflows/reconcile-merged-cycle.yml`が次を同じmerge SHAへ確定する。

- `CURRENT_WORK.json`
- `PRIVATE_STAGE_STATE.json`
- `CI_TRAIN_MANIFEST.json`

次チャットがmerge済みPRを見つけて補正する状態を正常完了としない。

## 二フェイズ終端出力

巨大作業の第一フェイズ`quality_reaudit`と、第二フェイズ`narrative_readthrough`（章ごとの通読修正）は、visibility modeと独立して次へ従う。

- `_phase4_proofread/PHASE_COMPLETION_SIGNAL.json`
- `_phase4_proofread/REGULATED_PHASE_STATE.json`
- `_phase4_proofread/FINAL_RESPONSE_GATE.md`

終端予約語を使用できるのは、active phaseが`complete`または`terminal_error`になり、live `signal_authorization.scope=regulated_phase_terminal`が発行された場合だけである。

認可済みterminal responseは、契約値による次の三行suffixを使う。

```text
<authorization_prefix><signal_authorization.event_id>
<status_prefix><signal_authorization.result>
<marker>
```

`signal_authorization=null`の間は、契約のmarker値を報告、説明、引用、例示へ出力しない。

次は規定フェイズ終端ではない。

- train、wave、PR、squash merge、transportの完了
- `CI_TRAIN_PHASE2`または`finalization_phase=phase2`
- Relation、Cross、Apply、pak再生成、release evidenceの成功・失敗
- 単一人物ペア、単一章
- 再開可能なchecker failure、外部依存停止、turn容量停止

通常応答を含む最終文面は、送信前に次へ通す。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

自動化側は固定marker単独で停止せず、`_tools/regulated_phase_terminal_consumer.js`の返す`accepted === true`だけをterminalとして扱う。live stateを取得できなければ非受理とする。

## 失敗

checker failure、外部依存停止、判断要求、turn容量停止だけを`paused`として許す。

常時public modeの失敗を理由にprivate復帰を要求しない。状態正本へ失敗分類とexact next actionを残し、同じlocked modeで再開する。通常の`paused`では終端予約語を出さない。

## merge

release phase2成功、未解決review thread 0、検証済みHEAD一致を確認してpublicのままsquash mergeする。

merge前に次waveを始めない。merge後reconcilerが三状態正本を`merged`へ確定した後、次cycleの開始visibilityを再確認してmodeを選ぶ。
