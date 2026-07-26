# 公開CI窓 運用契約

## 目的

翻訳判断、candidate準備、quality audit、encodingはprivateで行う。GitHub-hosted runnerを使う短時間だけrepositoryをpublicにし、公開回数と公開時間を最小化する。

visibilityを変更できるのはユーザーだけである。エージェントは申告ではなくrepository metadataを正本として確認する。

## turn入口のvisibility preflight

- 新規チャット、再開指示、作業継続指示では、利用者向け報告より先にrepository metadataを取得する。
- metadata確認前に翻訳再開や束開始を宣言しない。
- public中にprivate作業状態なら、翻訳を始めずprivate復帰を依頼する。
- 実visibility、PR metadata、Actionsを文書中の古い表記より優先する。

## privateで公開前に完了すること

1. wave preparation、quality audit、encodingを完了する。
2. candidate作成時に全owner snapshotを生成する。
3. encoding後にsnapshotを再生成し、owner移動・新設を反映する。
4. manifest、quality gate、private stage、next packet、handoffを同期する。
5. 翻訳を`translation_frozen`へ進める。
6. 次を成功させる。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

preflightは次を一括検査する。

- operation mode
- wave遷移
- candidate owner全件実測
- manifest
- NEXT_TASK_PACKET
- quality gate
- handoffとcheckpoint
- CI trigger回帰

失敗中は公開CI窓を開かない。

## public化の依頼

```text
公開CI窓を開いてください。
対象: <train_id / 束>
完成HEAD: <SHA>
集計: <束数 / 通読行 / 修正キー>
実行: release-ci → Relation / Cross / Apply → finalize-release → phase2
```

ユーザーの「公開した」だけで進めず、metadataでpublicを確認する。

## public中の正式手順

1. release PRを作る。PR作成だけでは重いCIは起動しない。
2. `release-ci`ラベルを付ける。
3. Relation / Cross / Applyを同じHEADで成功させる。
4. Applyのlocres、pak、audit status書き戻しを確認する。
5. `release-ci`を外す。
6. release evidence、適用記録、CURRENT_WORK、manifest、next packet、handoffを確定する。
7. `finalize-release`ラベルを付ける。
8. phase2 gateを成功させる。
9. 未解決review thread 0件を確認する。
10. private復帰を依頼する。

局所的な制度修正後に重い三本を再走する場合だけ`ci-heavy-rerun`を使う。再利用時はラベルを外して付け直す。

## public中に行わないこと

- 新しい場面のpreparation
- quality auditの再開
- 新しいfix / keep判断
- fix JSON追加
- owner方針の再判断
- FACT_DOUBT、ALLUSION_REVIEW、人物声の再検討
- 正式束追加
- PR作成や通常commitをトリガーにした重いCIの反復
- post-merge状態専用PR

## public中の局所修正

同じPRで許すのは、次をすべて満たす修正だけである。

1. 原文、訳文、fix値を変更しない。
2. quality auditの判断を変更しない。
3. owner重複解消、schema補完、workflow、release evidence、状態同期に限定する。
4. 修正後に必要なラベルを明示的に付けて再検証する。

翻訳再判断へ広がる場合は`public_ci_blocked`としてprivateへ戻す。

## private復帰後

- metadataでprivateを確認する。
- 公開中のphase2成功を再要求しない。
- 未適用0件、未解決thread 0件、verified checkpointを確認する。
- 同じrelease PRをsquash統合する。
- release evidenceを後続の制度・翻訳PRで`squash_merged`へ正規化できるが、その同期だけの専用PRは作らない。
- 次waveはprivateで開始する。

## 終了条件

- Relation / Cross / Apply成功
- 未適用0件
- pak、LFS、lint、回帰成功
- candidate owner snapshot整合
- release evidence整合
- verified checkpoint
- `finalize-release` phase2成功
- 未解決review thread 0件
- private復帰確認
- squash統合
- post-merge状態専用PR 0件

## 禁止事項

- visibility preflight前の開始宣言
- 一packetごとのpublic化
- preflight失敗中の公開依頼
- public中の翻訳判断
- `opened`、`ready_for_review`、`synchronize`による重いCI自動起動
- release evidenceなしの統合
- publicのまま放置
