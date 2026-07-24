# 新チャット再開プロトコル

現在値は`CURRENT_WORK.json`、CI列車は`CI_TRAIN_MANIFEST.json`、次小束は`NEXT_TASK_PACKET.json`を正本とする。
公開制度は`PUBLIC_CI_WINDOW.md`、第一段階の詳細は`CI_TRAIN_PHASE1.md`。

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の表現も再開モードとして扱い、URLや前回内容を聞き直さない。

## 起動順

1. GitHub metadataで実visibilityを確認する。
2. mainとopen PRを確認し、active / superseded / abandoned / unrelatedへ分類する。
3. phase1 pilotのdraft PRがあれば、mainの次場面よりそのPR headを優先する。
4. PR headの`CURRENT_WORK`、manifest、next packetを照合する。
5. Actions、review、未解決threadを確認する。
6. visibilityとoperation modeとmanifest statusから作業を裁定する。

## phase1の裁定

- private_translation_work + private + manifest accumulating:
  active train branchで次小束を監査する。release未達ならpublic化しない。
- private_translation_work + public:
  return_private_required。翻訳・commitを始めない。
- ready_for_public_ci + private + manifest ready:
  完成HEAD、束数、行数、修正キーを示してpublic化を依頼する。
- ready_for_public_ci + public + manifest ready:
  public_ci_window。CI、review、統合だけを行う。
- public_ci_blocked:
  publicならprivate復帰を依頼し、privateなら深い修正を行う。

## 正本の読順

1. README.md
2. AGENTS.md
3. SESSION_BOOTSTRAP.md
4. PUBLIC_CI_WINDOW.md
5. CI_TRAIN_PHASE1.md
6. CURRENT_WORK.json
7. CI_TRAIN_MANIFEST.json
8. CURRENT_HANDOFF.md
9. NEXT_TASK_PACKET.json
10. COLD_START_ACCEPTANCE.md
11. audit_status.json
12. RUNBOOK、skill、人物資料、一次資料

## verified checkpointと蓄積束

- `CURRENT_WORK.checkpoint`は公開CIで適用済みの最後の確定点。
- `CI_TRAIN_MANIFEST.bundles`は翻訳判断済みだが未適用の小束。
- private蓄積中はlast_completed_batchと適用件数を進めない。
- 小束完了時はlast_reviewed_batch、manifest totals、next packetを進める。
- locres、pak、audit_status件数はreleaseまで更新しない。

## 小束終了順

1. 原文、現訳、前後、人物声、分岐、所有、FACT_DOUBT、ALLUSION_REVIEWを確認。
2. 修正JSONとレビュー記録を個別ファイルで完成。
3. 同一キー異値競合がないことを確認。
4. manifestへbundleを追加しtotalsを再計算。
5. next packetを次の意味境界へ更新。
6. release条件を判定。
7. 未達ならprivateの同じbranchで次小束へ進む。
8. 到達ならmanifestとCURRENT_WORKをreadyへし、public化を依頼する。

## release条件

通常は次のOR:
- 4束
- 40行
- 20修正キー

上限:
- 6束
- 60行

早期releaseは許可された理由をmanifestへ記録した場合だけ。

## draft PR

private中に一つのdraft CI列車PRを開いてよい。private PR作成APIが利用できない場合は管理Issueを一つ開く。どちらも所在保存用でありCI開始要求ではない。
release時は同じPRをready化する。別PRへ小束を分散しない。

## public中

新しい翻訳や小束追加をしない。
第一段階ではRelation / Cross / Apply、bot書き戻し後の最終検証、squash統合、post-merge状態PRを維持する。
深い判断が必要ならprivateへ戻す。

## 最初の報告

- verified checkpoint
- active train id、branch、draft PR
- manifest statusとtotals
- operation modeと実visibility
- 次に着手する小束または必要なvisibility操作

privateでaccumulatingなら報告だけで止まらず、同じ応答内で次小束へ進む。

## 禁止事項

- 小束一つごとのpublic化
- 件数合わせで別場面を混ぜる
- verified checkpointと未適用小束を混同する
- release未達で理由なくreadyへする
- active trainを無視してmainから別branchを作る
- public中に新しい小束を追加する
- manifest totalsを手計算だけで信用する
- CI成功前に完了と報告する
