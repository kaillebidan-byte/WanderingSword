# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、CI列車は`CI_TRAIN_MANIFEST.json`、次小束は`NEXT_TASK_PACKET.json`、確定releaseは`RELEASE_EVIDENCE_*.json`を正本とする。
private作業の段階契約は`PRIVATE_TRANSLATION_STAGES.json`、現在段階は`PRIVATE_STAGE_STATE.json`を正本とする。
公開制度は`PUBLIC_CI_WINDOW.md`、小束蓄積は`CI_TRAIN_PHASE1.md`、単一PR最終化は`CI_TRAIN_PHASE2.md`。
turn入口の最優先契約は`VISIBILITY_PREFLIGHT_CONTRACT.json`とする。

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の表現も再開モードとして扱い、URLや前回作業を聞き直さず、可能なら同じ応答内で実作業へ進む。

## visibility preflight（最初の無言ゲート）

新規チャット・再開指示・作業継続指示では、ほかのGitHub照合や利用者向け進捗報告より先に、GitHub repository metadataから実visibilityを取得する。

1. 最初の外部確認をrepository metadata取得にする。
2. 結果が返るまで、利用者向けの計画、開始宣言、途中報告を出さない。
3. 「再開する」「第N束から進める」「branchを確認する」など、作業開始済みと読める表現も禁止する。
4. 利用者の「公開した」「戻した」はvisibility変更の意図・申告として受け取るが、実状態の正本にはしない。
5. metadata取得後の最初の利用者向け報告で、実visibilityと有効なoperation modeを確定してから作業または依頼へ進む。
6. metadata取得に失敗した場合は、作業開始を主張せず、visibility未確定として停止する。

このゲートは通常の進捗報告より優先する。ツール呼び出しだけを先に行い、結果後に必要な報告を出してよい。
機械契約は`python _tools/check_visibility_preflight_contract.py`で検査する。

## 起動順

1. visibility preflightを完了する。
2. GitHub metadataで実visibilityを確定する。
3. main、未統合PR、GitHub Actionsを確認し、active / superseded / abandoned / unrelatedへ分類する。
4. PRは開いているだけで現行作業と決めない。CURRENT_WORK、manifest、release evidence、next packetを照合する。
5. `PRIVATE_STAGE_STATE.json`を読み、private作業で許可された操作を確定する。
6. phase2制度改修branchまたはactive列車branchがあれば、mainの古い次場面より優先する。
7. review、未解決thread、bot書き戻し後の`action_required`を確認する。
8. visibility、operation mode、private stage、manifest statusから作業を裁定する。

## private四段階の裁定

- `private_preparation`:
  文脈・重複・所有・candidate packetだけを準備する。fix / keep判断、修正JSON、owner新設、正式な束番号は禁止。
- `private_quality_audit`:
  読むことと校正判断だけを行う。ownerは参照できるが、修正JSON・pair key・cross-register key・manifest件数は書かない。件数やrelease閾値を判断材料として表示しない。
- `private_encoding`:
  監査記録で確定済みの判断だけをJSON・所有・レビュー・束へ収録する。新しい疑義が出た場合はその場で決めず`private_quality_audit`へ戻す。release条件未達で列車を蓄積する場合は、現在束のencoding完成後にだけ次束の`private_preparation`へ戻る。
- `ready_for_public_ci`:
  翻訳判断と収録を凍結し、public化依頼とCI輸送だけを行う。

releaseへ進む通常遷移は`private_preparation -> private_quality_audit -> private_encoding -> ready_for_public_ci`。
蓄積を続ける通常ループは`private_encoding -> private_preparation -> private_quality_audit -> private_encoding`。
機械検査は`python _tools/check_private_translation_stage.py`で行う。

## visibilityとoperation modeの裁定

- private_translation_work + private:
  private stageが許可する作業だけを行う。制度改修中でも翻訳判断と制度操作を混ぜない。
- private_translation_work + public:
  return_private_required。翻訳を始めない。
- ready_for_public_ci + private:
  完成HEAD、品質ゲート、段階履歴、集計を示してpublic化を依頼する。
- ready_for_public_ci + public:
  public_ci_window。CI、release evidence、単一PR最終化、統合だけを行う。翻訳判断を変えないCI制度修正は`PUBLIC_CI_WINDOW.md`の行政修正条件に従う。
- public_ci_blocked:
  publicならprivate復帰を依頼し、privateなら`private_quality_audit`へ戻して深い修正を行う。

## 正本の読順

1. README.md
2. AGENTS.md
3. VISIBILITY_PREFLIGHT_CONTRACT.json
4. SESSION_BOOTSTRAP.md
5. PRIVATE_TRANSLATION_STAGES.json
6. PRIVATE_TRANSLATION_STAGES.md
7. PRIVATE_STAGE_STATE.json
8. TRANSLATION_QUALITY_GATE.md
9. PUBLIC_CI_WINDOW.md
10. CI_TRAIN_PHASE1.md
11. CI_TRAIN_PHASE2.md
12. CURRENT_WORK.json
13. CI_TRAIN_MANIFEST.json
14. CURRENT_HANDOFF.md
15. NEXT_TASK_PACKET.json
16. checkpointが指すrelease evidence
17. COLD_START_ACCEPTANCE.md
18. audit_status.json
19. RUNBOOK、skill、人物資料、一次資料

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
- public中は`PRIVATE_STAGE_STATE.stage=ready_for_public_ci`を要求し、品質判断を再開しない。

## 再開互換

- `pending_audit_sync`はApply後、release evidence確定前の遷移状態として残す。
- `verified`はrelease evidenceとaudit statusが一致した状態。
- action_requiredはbot起因runを開始しない既知の挙動なら失敗ではない。
- 新チャットはstatus報告だけで止まらず、privateで作業可能なら同じ応答内で実作業へ進む。
- ただしvisibility preflight前には、status報告も実作業開始宣言も行わない。
- train-05は四段階導入前の記録を遡及固定した移行列車。
- train-06第77束で四段階を実走し、release条件未達時の`private_encoding -> private_preparation`を追加した。新チャットはhistoryの繰り返しを合法な蓄積ループとして復元する。

## 禁止事項

- visibility preflight前の計画・開始宣言・途中報告
- 小束一つごとのpublic化
- 件数合わせで別場面を混ぜる
- verified checkpointと未適用小束を混同する
- active branchを無視してmainから別branchを作る
- public中に新しい小束を追加する
- release evidenceのrun IDを実確認せず書く
- post-merge状態PRを第二段階で復活させる
- quality audit中に修正JSON・owner・束番号を作る
- encoding中に新しい翻訳判断を追加する
- encoding完成前に次束のpreparationへ移る
- preparation / quality audit中にmetrics snapshotを表示する
- private段階を飛び越えてready_for_public_ciへ進む
