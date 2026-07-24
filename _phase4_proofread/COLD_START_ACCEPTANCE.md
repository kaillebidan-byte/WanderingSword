# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

## 合格条件

1. GitHub metadataで実visibilityを確認する。
2. 未統合PRとGitHub Actionsを確認し、開いているだけで現行作業と決めない。
3. privateならIssue #110と`agent/yuwen-mowen-train-02`を照合する。
4. 第61束・人物ペア1166・全1518・release `yuwen-mowen-train-01-r1`を復元する。
5. review済み第62〜65束、4束30行8修正を復元する。
6. operation mode `ready_for_public_ci`と通常release理由`bundle_count`を復元する。
7. privateなら公開CI窓を依頼し、追加の翻訳判断を行わない。
8. publicなら単一PRでCI、bot書き戻し観測、release evidence最終化、統合だけを行う。
9. bot書き戻し後のRelation / Cross / Apply追加起動0件を確認する。
10. 最終状態commitではphase2 gateだけを確認する。
11. post-merge状態PRを作らない。
12. private復帰後、第66束`5504_3`へ進む。

## 現在の期待値

- completed batch: 61
- reviewed batch: 65
- pair applied: 1166
- project applied: 1518
- train: `yuwen-mowen-train-02`
- totals: 4 bundles / 30 rows / 8 fixes / 4 new pair keys
- tracking issue: #110
- active branch: `agent/yuwen-mowen-train-02`
- queued translation after release: batch66 / `5504_3`
- actual visibility: GitHubで毎回確認
