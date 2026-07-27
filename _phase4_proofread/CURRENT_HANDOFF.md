# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、GitHub PR metadata、Actionsを文書中の固定値より優先する。

## 現在地

- 実visibility: private
- PR #138: open / ready / mergeable
- train: `yuwen-mowen-train-15`
- verified checkpoint: 第110束
- last reviewed batch: 第112束
- 人物ペア適用済みowner: 1170
- プロジェクト全体適用済み: 1546
- private stage: `translation_frozen`
- train-15 transport: `ready_for_public_ci`
- cycle control: `target_reached / ready_for_public_ci`

## train-15

`6151_2 + 6151_3`と`6155_1 + 6155_3 + 6158_5 + 6171_5`を二packet・50行で連続監査し、8行を修正、42行を意図的保持とした。残篇返却の謝罪と因果、師父の遺言を伝える呼称、罪のない者への懇願、欧陽雪の「いつまでも師兄」、莫問の孤独な羨望、戦闘中の脅し、宇文逸の離別を恐れる決意を原文と関係段階へ戻した。

50行はすべて新規ownerとして二つのfix JSONへ収録した。宇文逸の認識、莫問の将来予測と自己正当化、欧陽雪による宇文逸の心情理解は、場面外の客観事実へ強めていない。

## 次の作業

ユーザーがpublic化した後、PR #138で`release-ci`を起動し、Relation、Cross、Apply、state finalization、phase2、review thread 0件まで同一PRで進める。

## 禁止

- public中に翻訳判断、fix追加、owner変更、正式束追加を行わない。
- privateのままPR #138をmergeしない。
- PR #138統合前に`6195_3`のpreparationを始めない。
- ゲームフォルダへ配置しない。
