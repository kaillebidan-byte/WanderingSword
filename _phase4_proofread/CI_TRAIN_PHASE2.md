# CI列車 第二段階: mode-neutral releaseと単一PR最終化

## 目的

翻訳段階とCI輸送を分離し、`manual_visibility_cycle`と`always_public_full_pipeline`で同じorchestrator、Apply、phase2、squash mergeを再利用する。

## 共通の前提

1. wave全packetのpreparation、quality audit、encodingを完了する。
2. candidate作成時snapshotは監査記録として固定し、encoding後に上書きしない。
3. encoding後はlive owner、複数owner、fix owner delta、candidate範囲を再実測する。
4. manifest、quality gate、private stage、handoff、minimal reservationを同期する。
5. `translation_frozen`、manifest ready、release preflight成功後だけ重いCIへ進む。

## mode別の輸送

### manual_visibility_cycle

privateで`ready_for_public_ci`まで進み、public CI窓でorchestrator、state finalization、phase2、review thread確認を行う。`awaiting_private_merge`後にprivateへ戻り、同じPRをsquash mergeする。

### always_public_full_pipeline

repositoryをpublicのまま維持し、private_*認知段階からsquash merge、merged-state reconciliationまで一cycleで進む。visibility変更依頼を出さない。

## candidate owner契約

snapshotは全`fixes_*.json`を走査してcandidate作成時に生成する。release時の正本はlive owner検査であり、snapshot差だけを理由に修復commitを作らない。複数owner、candidate外変更、owner・修正集計不一致は失敗とする。

## minimal next reservation

release PRの`NEXT_TASK_PACKET.json`はschema v6 minimal reservationとし、checkpoint、current pair、scene groups、artifact指紋、未開始フラグ、release candidate、planned batchだけを保持する。focus key、voice question、FACT_DOUBT、ALLUSION_REVIEW、owner snapshot、batch planningは次cycleのpreparationで生成する。

## release-ciとphase2

`release-ci`または`ci-heavy-rerun`は`Release train orchestrator`一runだけを起動する。preflight後にRelation / Crossを並列実行し、両方成功後だけApplyを開始する。Apply後にrelease evidence、CURRENT_WORK、manifest、private stage、handoff、minimal reservationを同じPRで最終化し、`finalize-release`でphase2を実行する。

phase2はverified checkpoint、release evidence、actual run/job、owner安全性、manifest、wave、minimal reservation、review thread 0件を検査する。locresやpakは再生成しない。

## merge後

post-merge状態専用PRは作らない。`.github/workflows/reconcile-merged-cycle.yml`が次を同じmerge SHAへ同期する。

- `CURRENT_WORK.json`
- `PRIVATE_STAGE_STATE.json`
- `CI_TRAIN_MANIFEST.json`
- `NEXT_TASK_PACKET.json`
- `CURRENT_HANDOFF.md`

次cycleはreconciliation完了後に開始visibilityを再確認してmodeを選ぶ。

## 失敗時

checker failure、外部依存停止、判断要求、turn容量停止は`paused`として理由と`exact_next_action`を残す。always-publicでは失敗を理由にprivateへ戻さない。翻訳判断が必要な場合も、active modeとstage権限の範囲で再開する。
