# 公開CI窓 運用契約

## 目的

翻訳判断、candidate準備、quality audit、encodingはprivateで行う。GitHub-hosted runnerを使う短時間だけrepositoryをpublicにし、公開中は輸送と検証だけを行う。

visibilityを変更できるのはユーザーだけである。エージェントは申告ではなくrepository metadataを正本として確認する。

## turn入口のvisibility preflight

- 新規チャット、再開指示、作業継続指示では、利用者向け報告より先にrepository metadataを取得する。
- metadata確認前に翻訳再開や束開始を宣言しない。
- public中にprivate作業状態なら、翻訳を始めずprivate復帰を依頼する。
- 実visibility、PR metadata、GitHub Actionsを文書中の古い表記より優先する。

## privateで公開前に完了すること

1. wave preparation、quality audit、encodingを完了する。
2. candidate作成時とencoding後に全owner snapshotを生成する。
3. manifest、quality gate、private stage、handoffを同期する。
4. 次waveはschema v6のminimal reservationだけを置く。
5. 翻訳を`translation_frozen`へ進める。
6. 次を成功させる。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

preflightはoperation mode、wave、candidate owner、manifest、minimal reservation、batch planning契約、quality gate、Apply前輸送状態、workflow構造回帰を一括検査する。失敗中は公開CI窓を開かない。

## minimal reservation

公開releaseへ含める次候補は、scene group、artifact指紋、checkpoint、`reserved_only`だけとする。

次はprivate preparation開始時にcandidateへ生成するため、public releaseの予約へ書かない。

- focus key
- scene flowの詳細
- voice questions
- FACT_DOUBT / ALLUSION_REVIEW
- owner snapshot
- batch planningと小束例外
- skill review

これらは校正準備であり、release輸送情報ではない。

## public化の依頼

```text
公開CI窓を開いてください。
対象: <train_id / 束>
完成HEAD: <SHA>
集計: <束数 / 通読行 / 修正キー>
実行: release-ci → Release train orchestrator → finalize-release
```

ユーザーの「公開した」だけで進めず、metadataでpublicを確認する。

## public中の正式手順

1. release PRをreadyにする。PR作成・ready化・通常commitでは重いCIを起動しない。
2. `release-ci`ラベルを付ける。
3. `Release train orchestrator`が固定HEADで完全preflightを行う。
4. preflight成功後、同じrun内で再利用workflowのRelation / Crossを並列実行する。
5. Relation / Cross両方が成功した場合だけApplyを開始する。
6. Applyは開始時にPR branchが固定release HEADから動いていないことを確認する。
7. Applyがlocres、pak、APPLIED_FIXES、audit statusを一度に書き戻す。
8. release evidence、CURRENT_WORK、manifest、private stage、handoffを最終化する。
9. `finalize-release`ラベルを付ける。
10. phase2 gateと未解決review thread 0件を確認する。
11. private復帰を依頼する。

`ci-heavy-rerun`も同じorchestrator全工程を再走する。Relation / Cross / Applyを個別ラベルや別eventで直接起動しない。

## workflow責務

### Release train orchestrator

一つのpull_request run内で次のjob依存を強制する。

```text
preflight
  ├─ relation
  └─ cross
       ↓ 両方成功
      apply
       ↓
    complete
```

再利用workflowはPR branch上の同じcommitから呼び出す。`GITHUB_TOKEN`による別eventの再帰起動へ依存しない。

### release preflight

Apply前に実行する。

- operation mode
- current wave owner
- fix JSONとquality gate
- manifest readiness
- minimal reservation
- batch planningのprivate延期契約
- Apply前輸送状態
- workflow構造回帰

release evidence、audit status、verified checkpointの最終一致は要求しない。

### Relation / Cross

固定release HEADを読み取り専用で検査する。Applyより先に両方成功する。

### Apply

QA成功後だけ実行する。

- 未適用fixを一度適用する
- locresとpakを再構築する
- manifestと実owner件数から`APPLIED_FIXES_*.md`を生成する
- 適用記録生成後に`audit_status.json`を更新する
- 資産、適用記録、audit statusを一つのbot commitへ収録する

Apply中はrelease evidenceやverified checkpointの完成を要求しない。これらはbot commit後のfinalizationで確定する。

### finalize-release

- release evidence
- CURRENT_WORK
- audit status
- applied record
- verified checkpoint
- handoff
- minimal next reservation
- GitHub run evidence

を厳密に検査する。

新releaseではrelease evidence schema v2を使い、Relation / Cross / Apply三runではなく`Release train orchestrator`一runと、その中の三job成功を証跡にする。既存schema v1 releaseは改変しない。

## public中に行わないこと

- 新しい場面のpreparation
- quality auditの再開
- 新しいfix / keep判断
- fix JSON追加
- owner方針の再判断
- FACT_DOUBT、ALLUSION_REVIEW、人物声の再検討
- 正式束追加
- 次候補予約へのprivate preparation情報の復活
- PR作成や通常commitをトリガーにした重いCIの反復
- post-merge状態専用PR

## public中の局所修正

同じPRで許すのは、原文・訳文・fix値・品質判断を変えない輸送修正だけである。翻訳再判断へ広がる場合は`public_ci_blocked`としてprivateへ戻す。

## private復帰後

- metadataでprivateを確認する。
- 未適用0件、未解決thread 0件、verified checkpointを確認する。
- 同じrelease PRをsquash統合する。
- release evidenceを後続の制度・翻訳PRで`squash_merged`へ正規化できるが、その同期だけの専用PRは作らない。
- 次waveはprivateで開始し、minimal reservationからcandidate detailを新規生成する。

## 禁止事項

- visibility preflight前の開始宣言
- 一packetごとのpublic化
- preflight失敗中の公開依頼
- public中の翻訳判断
- Relation / Cross成功前のApply
- `opened`、`ready_for_review`、`synchronize`による重いCI自動起動
- release evidenceなしの統合
- publicのまま放置
