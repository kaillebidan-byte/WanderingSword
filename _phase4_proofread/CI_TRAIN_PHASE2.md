# CI列車 第二段階: 単一PR最終化

## 目的

第一段階で確立した「意味境界ごとの小束」と「複数小束をまとめるCI列車」は維持する。
第二段階では公開CI窓の事務処理だけを減らし、次を実現する。

- botの生成資産書き戻しでRelation / Cross / Applyを再起動しない
- 最終状態文書の更新で重い三本を再起動しない
- squash後のcommit SHA付け替えを廃止し、post-merge状態PRを作らない
- 翻訳PR一つの中で、生成資産、監査件数、release evidence、次束packet、verified checkpointを確定する

## 第一段階から維持するもの

- 小束は場面・分岐・人物関係・同じ崩れ方で閉じる
- 修正JSON、レビュー、所有、FACT_DOUBT、ALLUSION_REVIEWは小束ごとに分離する
- 通常releaseは4束、40行、20修正キーのOR
- 上限は6束または60行
- privateで翻訳判断を完了し、publicではCI・局所修正・統合だけを行う
- 深い翻訳再判断が必要ならprivateへ戻す

蓄積manifestは第一段階schemaと互換に保つ。第二段階は最終化契約を差し替える。

## 重いCIの起動境界

Relation / Cross / Applyは次の場合だけ起動する。

- `fixes_*.json`が変わった
- 翻訳資産の適用・検査コードが変わった
- 当該workflow自身が変わった

次の変更だけでは起動しない。

- botによるlocres、pak、`audit_status.json`書き戻し
- `CURRENT_WORK`、`CURRENT_HANDOFF`、`NEXT_TASK_PACKET`、適用記録、release evidenceの最終化
- post-merge参照同期

bot actorは重い三本のjob条件でも除外する。

## release evidence

verified checkpointの正本はsquash SHAではなく、`RELEASE_EVIDENCE_*.json`とする。
証跡には次を含める。

- release id、train id、PR番号
- Relation / Cross / Applyの成功run ID、workflow名、検証対象HEAD
- 生成資産を含むHEAD
- 完了束、人物ペア件数、全体件数、未適用0件
- 適用記録
- branch内祖先関係、または移行済みreleaseのsquash merge SHA

`check_release_evidence.py`は構造、件数、run名、run結論、PR対応、HEAD、git lineageを検査する。

## 単一PRの順序

1. privateで複数小束を完成し、manifestをrelease可能にする。
2. public確認後、同じbranchから翻訳PRを一つだけ使う。
3. Relation / Cross / Applyを同じCI HEADで成功させる。
4. Applyがlocres、pak、audit statusを同じbranchへ一度だけ書き戻す。
5. bot書き戻しでは重い三本を再起動しない。
6. 人間作成の最終状態commitで、適用記録、release evidence、CURRENT_WORK、manifest、next packet、handoffを確定する。
7. `CI train phase2 gate`だけを実行し、過去の三本成功runと現在HEADの状態整合を検証する。
8. 未解決thread 0件を確認し、同じ翻訳PRをsquash統合する。
9. mainにはすでにprivate作業状態と次束packetが含まれるため、post-merge状態PRは作らない。
10. private復帰を依頼する。

## checkpoint

`CURRENT_WORK.schema_version >= 7`では、checkpointに`translation_head`と`verified_head`を置かない。
代わりに次を持つ。

- `produced_by_pr`
- `release_identity.kind = pr_release_v1`
- `release_identity.release_id`
- `release_identity.evidence`
- `release_identity.pr`
- `release_identity.validated_head`

`translation_base_commit`と`state_base_commit`は列車開始時のmain祖先を指し、squash後に付け替えない。

## phase2 gate

軽量gateは次を検査する。

- operation modeと実visibility
- release evidenceのGitHub Actions実体
- release HEADと資産HEADのlineage
- verified checkpoint、audit status、適用記録
- manifest、次束番号、所有
- 冷間再開文書
- phase2回帰テスト

このgateは状態文書に反応するが、locresやpakを再生成しない。

## 失敗時

- 三本の失敗は、原因小束または検査コードをprivateで直して再releaseする。
- bot書き戻し後の`action_required`だけを失敗とみなさない。
- release evidenceが不完全なら統合しない。
- phase2 gateが過去runを確認できない場合、run IDを書き換えて通すのではなく実runとHEADを再確認する。
- 深い翻訳判断をpublicで反復しない。

## 第二段階の受入条件

- 翻訳PR一つ
- post-merge状態PR 0件
- Applyの資産書き戻し後、Relation / Cross / Applyの追加起動0回
- 最終状態commit後、重い三本の追加起動0回
- phase2 gate成功
- 未適用0件、pak・LFS・回帰成功
- 未解決thread 0件
- squash後のmainからrelease evidenceと次束を復元可能
