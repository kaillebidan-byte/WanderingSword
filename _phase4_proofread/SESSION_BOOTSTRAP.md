# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、CI列車は`CI_TRAIN_MANIFEST.json`、次小束は`NEXT_TASK_PACKET.json`、確定releaseは`RELEASE_EVIDENCE_*.json`を正本とする。
公開制度は`PUBLIC_CI_WINDOW.md`、小束蓄積は`CI_TRAIN_PHASE1.md`、単一PR最終化は`CI_TRAIN_PHASE2.md`。

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の表現も再開モードとして扱い、URLや前回作業を聞き直さず、可能なら同じ応答内で実作業へ進む。

## 起動順

1. GitHub metadataで実visibilityを確認する。
2. main、未統合PR、GitHub Actionsを確認し、active / superseded / abandoned / unrelatedへ分類する。
3. PRは開いているだけで現行作業と決めない。CURRENT_WORK、manifest、release evidence、next packetを照合する。
4. phase2制度改修branchまたはactive列車branchがあれば、mainの古い次場面より優先する。
5. review、未解決thread、bot書き戻し後の`action_required`を確認する。
6. visibility、operation mode、manifest statusから作業を裁定する。

## 裁定

- private_translation_work + private:
  制度改修中なら制度改修を先に進める。accumulating列車なら次小束を監査する。
- private_translation_work + public:
  return_private_required。翻訳を始めない。
- ready_for_public_ci + private:
  完成HEADと集計を示してpublic化を依頼する。
- ready_for_public_ci + public:
  public_ci_window。CI、release evidence、単一PR最終化、統合だけを行う。
- public_ci_blocked:
  publicならprivate復帰を依頼し、privateなら深い修正を行う。

## 正本の読順

1. README.md
2. AGENTS.md
3. SESSION_BOOTSTRAP.md
4. PUBLIC_CI_WINDOW.md
5. CI_TRAIN_PHASE1.md
6. CI_TRAIN_PHASE2.md
7. CURRENT_WORK.json
8. CI_TRAIN_MANIFEST.json
9. CURRENT_HANDOFF.md
10. NEXT_TASK_PACKET.json
11. checkpointが指すrelease evidence
12. COLD_START_ACCEPTANCE.md
13. audit_status.json
14. RUNBOOK、skill、人物資料、一次資料

## verified checkpointとrelease evidence

- `CURRENT_WORK.checkpoint`は適用済みの最後の確定点。
- schema 7以降はsquash SHAではなくrelease evidenceでPR、成功run、検証HEAD、件数を固定する。
- `translation_head`と`verified_head`へ依存しない。
- `CI_TRAIN_MANIFEST.bundles`は翻訳判断済みだが未適用の小束。
- private蓄積中はlast_completed_batchと適用件数を進めない。

## public中の第二段階

- Relation / Cross / Applyは修正JSONまたは検査コード変更時だけ起動する。
- botのlocres、pak、audit status書き戻しでは重い三本を再起動しない。
- 最終状態文書ではphase2 gateだけを起動する。
- 同じPR内でrelease evidenceとverified checkpointを確定する。
- squash後のpost-merge状態PRは作らない。

## 再開互換

- `pending_audit_sync`はApply後、release evidence確定前の遷移状態として残す。
- `verified`はrelease evidenceとaudit statusが一致した状態。
- action_requiredはbot起因runを開始しない既知の挙動なら失敗ではない。
- 新チャットはstatus報告だけで止まらず、privateで作業可能なら同じ応答内で実作業へ進む。

## 禁止事項

- 小束一つごとのpublic化
- 件数合わせで別場面を混ぜる
- verified checkpointと未適用小束を混同する
- active branchを無視してmainから別branchを作る
- public中に新しい小束を追加する
- release evidenceのrun IDを実確認せず書く
- post-merge状態PRを第二段階で復活させる
