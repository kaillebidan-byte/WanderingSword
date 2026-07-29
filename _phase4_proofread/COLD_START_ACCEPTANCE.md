# 新チャット冷間再開 受入基準

## 起動文

`現状把握して作業の続きを`、または同じ意図の表現を再開指示として扱う。

## 最初の無言ゲート

1. `PROJECT_SCOPE_LOCK.json`で対象を`kaillebidan-byte/WanderingSword`へ固定する。
2. 最初の外部確認としてrepository metadataを取得する。
3. metadata前に開始宣言、計画、翻訳再開報告を出さない。
4. main、open PR、Actions、三状態正本を照合する。
5. merge済みPRと状態がずれていればreconcilerを先に実行する。
6. `FINAL_RESPONSE_POLICY.json`をroutine正本として読み、生の終端契約とlive認可stateは直接読まない。

## 唯一の再開入口

```bash
python _tools/resume_work_entrypoint.py --repository-visibility <private|public>
```

work orderと`final_response_gate`を同じ呼出しから取得する。旧controllerを新チャットから直接呼ばない。

## mode裁定

前cycleのtransportが`merged`の場合だけ、cycle開始時visibilityからmodeを選ぶ。

- private: `manual_visibility_cycle`
- public: `always_public_full_pipeline`

選択結果は`CURRENT_WORK.operation_mode`と`PRIVATE_STAGE_STATE.cycle_control`へ同時にlockする。active cycle中はmodeを変更しない。

- public + `private_translation_work` + `always_public_full_pipeline`: 段階権限に従ってpreparationを開始できる。
- public + manual modeのprivate段階: 翻訳を開始せずprivate復帰を依頼する。
- always-publicでは`ready_for_public_ci`と`awaiting_private_merge`を内部checkpointとして通過し、正常時は`merged`まで進む。

## 状態正本

- 現在地・checkpoint・mode: `CURRENT_WORK.json`
- wave・cycle: `PRIVATE_STAGE_STATE.json`
- 正式束・transport: `CI_TRAIN_MANIFEST.json`
- 次候補予約: `NEXT_TASK_PACKET.json`
- 人間向け要約: `CURRENT_HANDOFF.md`
- routine最終応答: `FINAL_RESPONSE_POLICY.json`

`CURRENT_HANDOFF.md`と`NEXT_TASK_PACKET.json`は三状態正本に従属し、merge後に同じreconcilerで同期されなければならない。`CURRENT_WORK.mandatory_read_order`は`sanitize_final_response_read_order.py`で安全policyへ補正する。

## owner契約

candidate作成時のownership snapshotはquality auditへ渡した時点の監査記録として固定する。encoding後はsnapshotを上書きせず、`--release-live`とowner delta検査で現在ownerを確認する。

## 最終応答mode

- `normal_response`: safe completion labelだけで通常作業完了を報告し、予約token・認可ID・resultを出さない。rendererは実行禁止。
- `authorized_terminal`: `render_phase_completion_suffix.py`だけがsuffixを生成する。モデルは手入力・復元・推測しない。
- どちらも送信前draftを`check_phase_completion_signal.py --response-file`へ通す。

train merge、release phase2、transport merged、cycle target reachedはauthorized terminalの根拠ではない。

## 合格条件

- active PRをactive / superseded / abandoned / unrelatedへ分類した。
- merged transportではhandoffとnext reservationもmerged状態に一致する。
- schema v6 minimal reservationへfocus key、voice question、owner snapshot、batch planningを戻していない。
- modeとvisibilityの組合せが`EXECUTION_MODES.json`に一致する。
- stage境界だけで会話を終了せず、modeの正常完了地点まで進む。
- post-merge状態専用PRを作らない。
- routine read orderが`FINAL_RESPONSE_POLICY.json`を含み、生の終端契約とlive認可stateを含まない。
- 最終応答がentrypointの`final_response_gate`に一致する。

## 機械検査

```bash
python _tools/resume_work_entrypoint.py --repository-visibility <private|public> --validate-contract-only
python _tools/sanitize_final_response_read_order.py
python _tools/check_operational_docs_consistency.py
python _tools/check_visibility_preflight_contract.py
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_private_translation_stage.py
python _tools/check_autonomous_cycle.py
python _tools/check_next_task_packet.py
python _tools/check_phase_completion_signal.py
python _tools/test_final_response_policy.py
```

通常応答の送信前には最終応答gateも通す。すべてが成功しない状態を確定状態として扱わない。
