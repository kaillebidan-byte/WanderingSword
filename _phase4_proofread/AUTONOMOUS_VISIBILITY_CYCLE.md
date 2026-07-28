# 自律作業cycle契約

## 目的

手動private/public/private反復と常時public full pipelineを、同じ翻訳段階機械とCI輸送経路で動かす。

実行モードの正本は`EXECUTION_MODES.json`とする。利用者の入力はどちらも`作業の続きを`で変えない。

## mode選択

新しいcycleを始める直前のrepository metadataだけでmodeを選ぶ。

- private: `manual_visibility_cycle`
- public: `always_public_full_pipeline`

```bash
python _tools/select_cycle_execution_mode.py --repository-visibility <private|public> --write
```

選択結果は`CURRENT_WORK.operation_mode`と`PRIVATE_STAGE_STATE.cycle_control`へ固定する。進行中cycleでは変更しない。前cycleのtransportが`merged`になった後だけ次cycleを選べる。

既存のmode fieldを持たない進行中cycleはlegacy manual cycleとして完了させる。途中で常時publicへ付け替えない。

## 共通段階

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen`

`private_*`は認知段階の識別子であり、visibility条件ではない。

- preparation: 候補とowner snapshotを準備する。翻訳判断、fix、owner、正式束は禁止
- quality audit: sealed queue全体を監査する。翻訳判断以外の書込みは禁止
- encoding: 記録済み判断をowner生成器で収録する。新しい翻訳判断は禁止
- translation frozen: 翻訳判断を閉じる。以後はCI輸送だけを進める

owner生成、live owner検査、quality gate、manifest ready、digest証跡は両modeで同一とする。

## manual_visibility_cycle

正常停止地点はvisibility境界またはmerge完了。

1. privateで`ready_for_public_ci`
2. publicで`awaiting_private_merge`
3. privateでsquash mergeし、merge後reconcilerで`merged`

public CI窓では翻訳判断、fix追加、owner変更、次wave準備を行わない。publicのままmergeしない。

## always_public_full_pipeline

repositoryをpublicのまま維持する。

`private_preparation -> private_quality_audit -> private_encoding -> translation_frozen -> release preflight -> orchestrator -> state finalization -> release phase2 -> review thread 0 -> squash merge -> merged-state reconciliation`

`ready_for_public_ci`と`awaiting_private_merge`は内部checkpointとして記録するが、正常停止地点にはしない。visibility変更依頼を出さず、同じcycleで`merged`まで進む。

publicで翻訳段階を実行できるのは、modeがcycle開始時にpublicから選ばれ、二つの状態正本へlockされ、段階権限が一致している場合だけとする。

## CI

通常commit、PR作成、ready化だけでは重いCIを起動しない。

translation freeze、manifest ready、release preflight成功後に既存の`release-ci`を使う。Relation、Cross、Apply、finalization、release phase2の経路はmodeで分岐させない。

## cycle_control

必須項目:

- `status`: `running | paused | target_reached`
- `private_completion_target`: `ready_for_public_ci`
- `public_completion_target`: `awaiting_private_merge`
- `post_public_completion_target`: `merged`
- `continuation_required`
- `stop_reason`
- `exact_next_action`
- `last_safe_checkpoint`

新cycleでは次も必須。

- `execution_mode`
- `cycle_start_visibility`
- `mode_locked_for_cycle=true`
- `normal_completion_target`

manualの`normal_completion_target`は`visibility_boundary_or_merged`。always-publicは`merged`。

## 規定二フェイズ終端シグナル

巨大作業は次の二フェイズで進む。

1. `quality_reaudit`: 関係クラスタ、人物ペア、場面、既訳の順で行う高確度再監査
2. `narrative_readthrough`: 章・事件単位の日本語通読と原文対照による章ごとの通読修正

この二フェイズはvisibility cycleより長い作業単位であり、単一waveや単一mergeをフェイズ完了としない。

終端は次の三正本へ従う。

- `PHASE_COMPLETION_SIGNAL.json`
- `REGULATED_PHASE_STATE.json`
- `FINAL_RESPONSE_GATE.md`

`signal_authorization=null`の間、契約のmarker値は応答本文、引用、説明、例示へ出力禁止とする。

認可済みterminal responseの最終三行は、固定文字列を複製せず、契約値から次の構造で生成する。

```text
<authorization_prefix><signal_authorization.event_id>
<status_prefix><signal_authorization.result>
<marker>
```

通常応答も含め、送信前に次を通す。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

自動化consumerは固定marker単独で停止せず、`regulated_phase_terminal_consumer.js`がlive state照合後に返す`accepted === true`だけをterminalとして扱う。live stateを取得できなければ非受理とする。

## 例外停止

許可理由:

- `user_decision_required`
- `checker_failure`
- `external_dependency_unavailable`
- `turn_capacity_checkpoint`

`paused`は理由と機械実行可能な`exact_next_action`を必須とする。always-publicでは失敗時もmodeを変えず、private復帰を要求しない。

規定フェイズ自体が継続不能なterminal errorで終わり、live authorizationが発行された場合だけterminal responseを生成する。通常の一時停止、visibility境界、単一wave、単一人物ペア、単一章では終端予約語を出さない。

## 禁止

- mode未選択の新cycle開始
- active cycle中のmode変更
- publicであることを理由に段階権限を省略すること
- manual modeでpublic translationを行うこと
- always-public modeでprivateへ切り替えて継続すること
- translation freeze前の重いCI起動
- release phase2成功前のmerge
- merge前の次wave開始
- always-publicで`ready_for_public_ci`または`awaiting_private_merge`を正常停止地点にすること
- 終端予約語を単一waveや単一章の完了に使うこと
- authorizationなしで終端予約語を出すこと
- 固定markerだけ、またはresultとの二行だけで自動化を停止すること
- live stateを取得できないのにterminal扱いすること
