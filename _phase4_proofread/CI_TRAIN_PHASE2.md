# CI列車 第二段階: 直列releaseと単一PR最終化

## 目的

意味境界ごとの小束とmulti-packet waveを維持しつつ、公開CI窓の事務処理を校正作業から切り離す。

- 翻訳判断はprivateで完了する。
- publicでは固定HEADのpreflight、Relation / Cross、Apply、phase2だけを輸送する。
- ApplyはRelation / Cross両方の成功前に開始しない。
- PR作成、ready化、通常commitでは重いCIを起動しない。
- bot書き戻し後の状態commitでも重いCIを再起動しない。
- release evidence、verified checkpoint、minimal次候補予約を同じPR内で確定する。
- private復帰後は同じPRをsquash統合し、post-merge状態専用PRを作らない。

## privateで完了させるもの

1. waveの全candidate packetを準備する。
2. 各candidateへ全`fixes_*.json`実測の`ownership_snapshot`を付ける。
3. sealed queue全体をquality auditする。
4. 確定判断だけをencodingする。
5. encoding後にowner snapshotを再生成する。
6. manifest、quality gate、private stage、handoffを同期する。
7. NEXT_TASK_PACKETはschema v6 minimal reservationへ縮小する。
8. 翻訳段階を`translation_frozen`、輸送を`ready_for_public_ci`へ進める。
9. 次を成功させる。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

このpreflightが失敗している間はpublic化を依頼しない。

## candidate owner契約

candidate作成時とencoding後に次を実行する。

```bash
python _tools/check_candidate_ownership.py --write \
  _phase4_proofread/CANDIDATE_....json
```

snapshotは`_phase4_proofread/fixes_*.json`全件を走査して生成する。特定の人物ペアownerだけを見て「未所有」と判断してはならない。

次を失敗とする。

- snapshotと実ownerが一致しない
- 一つのキーに複数ownerがある
- 新規candidateにsnapshotがない
- encodingでownerを更新した後もpreparation時snapshotのまま

## minimal next reservation

release PRへ含めるNEXT_TASK_PACKETはschema v6とする。次だけを保持する。

- verified checkpoint
- current pair
- reserved scene groups
- `reserved_only`と未開始フラグ
- Relation artifactの名前、digest、HEAD、freshness rule
- release candidate
- 次のplanned batch
- public中の禁止事項

focus key、voice question、FACT_DOUBT、ALLUSION_REVIEW、owner、batch planningはprivate preparation開始時にcandidateへ生成する。予約だけの段階でこれらを要求しない。

## release-ci入口

通常起動:

```text
release-ci
```

局所的な制度修正後の全工程再走:

```text
ci-heavy-rerun
```

どちらも`Release train orchestrator`一つだけを起動する。Relation / Cross / Applyは再利用workflowであり、個別eventや内部ラベルを持たない。

## 一run内の順序

```text
preflight
  ├─ relation
  └─ cross
       ↓ 両方成功
      apply
       ↓
    complete
```

1. repository metadataでpublicを確認する。
2. release PRをreadyにする。
3. `release-ci`を付ける。
4. orchestratorがPR HEADを固定し、完全preflightを実行する。
5. preflight成功後、Relation / Cross再利用workflowを同じHEADで並列実行する。
6. 両方成功後だけApply再利用workflowを開始する。
7. Apply開始時にPR branchが固定HEADから動いていないことを確認する。
8. Applyがlocres、pak、APPLIED_FIXES、audit statusを一度に書き戻す。
9. release evidence、CURRENT_WORK、manifest、private stage、handoffを最終化する。
10. `finalize-release`を付ける。
11. phase2 gateと未解決review thread 0件を確認する。
12. private復帰を依頼し、同じPRをsquash統合する。

`finalize-release`はphase2専用であり、orchestratorを再起動しない。

## Apply前preflight

Apply前には次を検査する。

- operation mode
- current wave owner
- fix JSONとquality gate
- manifest readiness
- minimal reservation
- batch planningのprivate延期契約
- restart契約と輸送状態
- workflow構造回帰

release evidence、audit status、verified checkpointの最終一致は要求しない。これらはApply後のphase2責務である。

## Applyの責務

ApplyはQA成功後だけ開始する。

1. PR branchがorchestratorの固定HEADと一致することを確認する。
2. 未適用fixを適用し、locresとpakを一度だけ再構築する。
3. 未適用0件を確認する。
4. manifestと実owner件数から`APPLIED_FIXES_*.md`を自動生成する。
5. 適用記録が存在する状態で`update_audit_status.py`を実行する。
6. 資産、適用記録、audit statusを一つのbot commitにする。

既にverified済みのreleaseで既存適用記録がある場合は上書きしない。

## release evidence

既存releaseのschema v1はRelation / Cross / Apply三runを保持する。

次回以降はschema v2を使用する。

```json
{
  "schema_version": 2,
  "orchestrator": {
    "id": 123456,
    "workflow": "Release train orchestrator",
    "head_sha": "<ci_head>",
    "event": "pull_request",
    "conclusion": "success"
  }
}
```

GitHub checkerはorchestrator runの中に、成功したRelation、Cross、Apply jobが存在することを検証する。checkpoint identityは`pr_release_v2`を使う。

## phase2 gate

phase2は`finalize-release`ラベル時だけ実行し、次を検査する。

- operation modeと実visibility
- release evidenceとGitHub Actions実run/job
- squash前branch lineageまたは過去releaseのsquash lineage
- verified checkpoint、audit status、自動生成済み適用記録
- manifest、wave、quality gate
- candidate owner snapshot
- minimal NEXT_TASK_PACKET
- batch planningのprivate延期契約
- orchestrator job順序とtrigger回帰
- 冷間再開文書

locresやpakの再生成は行わない。

## 失敗時

- preflight失敗ではRelation / Cross / Applyを開始しない。
- RelationまたはCross失敗ではApplyを開始しない。
- QA後にPR HEADが動いた場合はApplyを開始せず失敗する。
- owner snapshot不一致、状態schema欠落はprivateへ戻して直す。
- public中に許すのは翻訳判断を変えない局所的な輸送修正だけ。
- 訳文、人物声、FACT_DOUBT、ALLUSION_REVIEW、owner方針の再判断が必要なら`public_ci_blocked`としてprivateへ戻す。
- run IDを書き換えて通さず、実run、job、HEAD、PR lineageを確認する。

## 受入条件

- 翻訳PR一つ
- candidate owner snapshotが全fix owner実測と一致
- orchestrator preflight成功
- Relation / Cross成功後にApply成功
- Apply後の未適用0件、pak・LFS・lint・回帰成功
- APPLIED_FIXESとaudit statusが同じbot commitで同期
- schema v2 orchestrator evidenceまたは既存schema v1 evidenceが検証済み
- `finalize-release`によるphase2成功
- 未解決thread 0件
- repository metadataでprivate復帰確認
- squash統合
- post-merge状態専用PR 0件
