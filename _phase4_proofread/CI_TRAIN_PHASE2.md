# CI列車 第二段階: 単一PR最終化

## 目的

意味境界ごとの小束とmulti-packet waveを維持しつつ、公開CI窓の事務処理を最小化する。

- 翻訳判断はprivateで完了する。
- publicではRelation / Cross / Applyとphase2だけを輸送する。
- PR作成、ready化、通常commitでは重いCIを起動しない。
- bot書き戻し後の状態commitでも重いCIを再起動しない。
- release evidence、verified checkpoint、次候補予約を同じPR内で確定する。
- private復帰後は同じPRをsquash統合し、post-merge状態専用PRを作らない。

## privateで完了させるもの

1. waveの全candidate packetを準備する。
2. 各candidateへ全`fixes_*.json`実測の`ownership_snapshot`を付ける。
3. sealed queue全体をquality auditする。
4. 確定判断だけをencodingする。
5. encoding後にowner snapshotを再生成する。
6. manifest、quality gate、NEXT_TASK_PACKET、handoffを同期する。
7. 翻訳段階を`translation_frozen`、輸送を`ready_for_public_ci`へ進める。
8. 次を成功させる。

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

train-07以前のschema v1 candidateは`PRIVATE_STAGE_STATE.ownership_policy.legacy_candidate_paths`で明示し、履歴を改変しない。

## 重いCIの明示起動

GitHubの`pull_request.paths`はPR全体差分で評価されるため、path条件だけでは中間状態への再起動を防げない。Relation / Cross / Applyは`pull_request:labeled`だけを入口とする。

通常入口:

```text
release-ci
```

局所的な行政・owner修正後の再走:

```text
ci-heavy-rerun
```

どちらもrepositoryがpublicで、actorがbotでない場合だけjobを実行する。PR作成、reopen、ready化、`synchronize`では重い三本を起動しない。

同じラベルを再利用する場合は、一度外してから付け直す。

## public CIの順序

1. repository metadataでpublicを確認する。
2. release PRを作成する。draftのままでよい。
3. `release-ci`ラベルを付ける。
4. Relation / Cross / Applyを同じCI HEADで成功させる。
5. Applyがlocres、pak、audit statusを書き戻す。
6. `release-ci`を外す。
7. 適用記録、release evidence、CURRENT_WORK、manifest、handoff、next packetを最終化する。
8. `finalize-release`ラベルを付ける。
9. `CI train phase2 gate`を成功させる。
10. 未解決review thread 0件を確認する。
11. private復帰を依頼する。
12. metadataでprivateを確認後、同じPRをsquash統合する。

`finalize-release`はphase2専用である。このラベルではRelation / Cross / Applyを実行しない。

## phase2 gate

phase2は`finalize-release`ラベル時だけ実行し、次を検査する。

- operation modeと実visibility
- release evidenceとGitHub Actions実run
- squash前branch lineageまたは過去releaseのsquash lineage
- verified checkpoint、audit status、適用記録
- manifest、wave、quality gate
- candidate owner snapshot
- NEXT_TASK_PACKET
- 冷間再開文書
- 回帰テスト

locresやpakの再生成は行わない。

## bot書き戻し

Applyは未適用fixが0件でも`update_audit_status.py`を実行する。適用記録からaudit status差分が生じた場合は、その状態差分だけをbot commitする。

bot commit、資産commit、最終状態commitでは重い三本を自動起動しない。phase2も`finalize-release`を付けるまで起動しない。

## 失敗時

- owner snapshot不一致、重複owner、状態schema欠落はprivateへ戻して直す。
- public中に許すのは翻訳判断を変えない局所的な行政修正だけ。
- 訳文、人物声、FACT_DOUBT、ALLUSION_REVIEW、owner方針の再判断が必要なら`public_ci_blocked`としてprivateへ戻す。
- run IDを書き換えて通さず、実run、HEAD、PR lineageを確認する。
- private復帰後のrunner未開始をrelease失敗としない。

## 受入条件

- 翻訳PR一つ
- candidate owner snapshotが全fix owner実測と一致
- Relation / Cross / Applyが`release-ci`または明示的なrerunで成功
- Apply後の未適用0件、pak・LFS・lint・回帰成功
- `finalize-release`によるphase2成功
- 未解決thread 0件
- repository metadataでprivate復帰確認
- squash統合
- post-merge状態専用PR 0件
