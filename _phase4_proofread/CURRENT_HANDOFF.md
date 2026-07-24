# 現在の申し送り

> 現在地の機械正本は`CURRENT_WORK.json`、CI列車は`CI_TRAIN_MANIFEST.json`、
> 次の小束は`NEXT_TASK_PACKET.json`、公開運用は`PUBLIC_CI_WINDOW.md`と`CI_TRAIN_PHASE1.md`。

## 現在地

- 実visibility: private（GitHub metadataで確認）
- checkpoint: 第60束、人物ペア1166、全1517、`verified`
- 宣言operation mode: `private_translation_work`
- 第60束翻訳PR #103・状態PR #104は統合済み
- 未統合PR: private PR作成APIが502のため未作成。管理Issue #105をactive列車ポインタとして確認
- active branch: `agent/ci-train-phase1-pilot`
- tracking issue: #105 `Active CI train: yuwen-mowen-train-01`
- train: `yuwen-mowen-train-01`
- train status: `accumulating`
- train totals: 0束 / 0行 / 0修正キー
- 次の小束: 第61束 `5452_1` 5行

## 第一段階制度

第61束から小束ごとの公開をやめ、完成小束をprivateで列車へ積む。

通常release:
- 4束
- 40行
- 20修正キー

いずれかへ到達した時点。上限は6束または60行。
workflow/schema/security/緊急build確認だけはmanifestへ理由を記録して早期releaseできる。

小束完了時は修正JSON、レビュー記録、所有・疑義を完成させるが、locres・pak・audit_status件数は更新しない。
`CI_TRAIN_MANIFEST`へ`reviewed_pending_ci`として追加し、次束へ進む。
verified checkpointは第60束のまま維持する。

private PR作成APIが利用できなかったため、Issue #105を列車branchの所在保存用にした。CI開始要求ではない。public release時に同じbranchからPRを一つ作る。
release時は同じPRをready化し、別PRへ束を分散しない。

## 第61束

`5452_1`の宇文逸首位分岐5行。

- 莫問の短い祝福
- 莫棄の笑い、小逸呼び、湛盧剣への興奮
- 宇文逸の短い応答
- 清虚の強行収招・内勁反噬を踏まえた負傷確認
- `5449_2`の莫棄首位分岐とは混ぜない

所有:
- 既存第6束: 莫棄 Index1・2
- 第61束候補: 莫問 Index0、宇文逸 Index3
- 清虚cross-register候補: Index4

## 再開

1. metadataでvisibilityを確認
2. phase1 pilotのdraft PR、なければ管理Issue #105からactive branchを判定
3. active branchの`CURRENT_WORK`、manifest、next packetを読む
4. manifestがaccumulatingなら次小束を同じbranchへ積む
5. release未達ならpublic化を依頼しない
6. release到達後だけreadyへ遷移し、一度の公開CI窓を依頼する
