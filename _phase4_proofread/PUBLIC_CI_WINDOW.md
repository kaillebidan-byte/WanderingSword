# 公開CI窓 運用契約（manual_visibility_cycle専用）

この文書は`execution_mode=manual_visibility_cycle`のpublic区間だけに適用する。`always_public_full_pipeline`では`ALWAYS_PUBLIC_FULL_PIPELINE.md`を使い、publicであること自体を翻訳禁止条件にしない。

## manual modeの目的

翻訳判断、candidate準備、quality audit、encodingをprivateで完了し、GitHub-hosted runnerを使う区間だけpublicにする。public中はtranslation frozen後の輸送と検証だけを行う。

## 入口

- metadataでpublicを確認する。
- active cycleのmodeがmanualであることを確認する。
- manifest ready、translation frozen、private release preflight成功を確認する。
- `release-ci`でorchestratorを起動する。

## public区間

Relation / Cross成功後だけApplyを開始し、release evidence、state finalization、phase2、review thread 0件まで進める。`awaiting_private_merge`後にprivate復帰を依頼する。追加の「作業の続きを」は要求しない。

public中に新しいpreparation、quality audit、fix判断、owner方針再判断、正式束追加を行わない。深い翻訳判断が必要なら`public_ci_blocked`としてprivateへ戻す。

## merge

metadataでprivateを確認し、verified checkpoint、未適用0件、未解決thread 0件、検証済みHEADを確認して同じPRをsquash mergeする。post-merge状態専用PRは作らず、reconcilerでCURRENT_WORK、PRIVATE_STAGE_STATE、CI_TRAIN_MANIFEST、NEXT_TASK_PACKET、CURRENT_HANDOFFを同期する。

## always-publicとの境界

always-publicでは開始時にmodeをlockし、private_*認知段階からmergeまでpublicのまま進む。manual public CI窓のprivate復帰規則を適用しない。
