# private翻訳四段階

## 目的

既存の荒い翻訳を見つけて直す品質判断と、束・所有・修正JSON・CI輸送を同時に処理しない。
作業者が「あと何行」「あと何束」を意識してkeepへ寄せることを防ぎ、判断後にだけ制度化する。

機械契約は`PRIVATE_TRANSLATION_STAGES.json`、現在段階は`PRIVATE_STAGE_STATE.json`、
検査は`python _tools/check_private_translation_stage.py`を正本とする。

## 四段階

### 1. `private_preparation`

翻訳判断をしない準備回。

許可:
- 原文、現訳、前後、話者、相手、時系列、分岐を抽出する。
- 重複familyと既存ownerを調べる。
- 典故候補と設定疑義候補を未確定のまま置く。
- 校正用candidate packetを作る。

禁止:
- fix / keepを確定する。
- 修正JSON、レビュー結論、pair key、cross-register keyを作る。
- 正式な束番号を確定する。
- releaseまでの残り行数や束数を品質判断者へ表示する。

### 2. `private_quality_audit`

読むことと校正判断だけを行う回。

許可:
- 原文の意味、強弱、発話役割、人物声、設定追加、欠落、不自然さを判断する。
- `fix_candidate`、`challenged_keep`、`needs_context`を記録する。
- ownerと重複情報を参照する。

禁止:
- 修正JSONへ書き込む。
- pair / cross-register ownerを新設する。
- 束を完了扱いにする。
- manifest件数、release閾値、残り行数を見ることを前提に判断する。

この段階で必要な構造情報は参照できるが、制度操作はできない。
所有情報を隠し切ると重複分岐やcross-registerを落とすため、情報参照と書込み権限を分ける。

### 3. `private_encoding`

品質監査で確定した判断だけを制度化する回。

許可:
- 確定済み修正をfix JSONへ収録する。
- pair / cross-register所有を決める。
- 重複分岐へ鏡写しする。
- レビュー記録、FACT_DOUBT、ALLUSION_REVIEWを整形する。
- unique rowsとreviewed keysを集計し、最後に束番号を確定する。

禁止:
- 新しい翻訳判断をその場で追加する。
- encoding中に疑義が出た行を便宜的にfixまたはkeepへ決める。

新しい疑義や監査記録との矛盾が出た場合は
`private_quality_audit`へ戻し、判断記録を更新してから再びencodingへ進む。

### 4. `ready_for_public_ci`

翻訳判断と収録を凍結し、public CIへ送る待機状態。

許可:
- 完成HEAD、品質ゲート、未適用キー、CI対象を確認する。
- 利用者へpublic化を依頼する。
- public後にRelation / Cross / Apply / phase2 gateを実行する。

禁止:
- 新しい場面を読む。
- 訳文判断を変更する。
- fix keyや束を追加する。

品質問題が見つかった場合はpublicで直さずprivateへ戻し、
`private_quality_audit`から再開する。

## 遷移

通常:
`private_preparation -> private_quality_audit -> private_encoding -> ready_for_public_ci`

再作業:
- `private_encoding -> private_quality_audit`
- `ready_for_public_ci -> private_quality_audit`

次は禁止:
- preparationからencodingまたはCI待ちへの飛越
- quality auditからCI待ちへの飛越
- public CIから品質判断を再開すること

各遷移は`PRIVATE_STAGE_STATE.json.history`へ証拠とともに記録する。

## 指標の扱い

- preparation / quality auditでは`metrics_snapshot`を持たない。
- quality audit中は束数、行数、修正率、release閾値を判断材料にしない。
- encodingで重複をunique rowsへ正規化した後にだけ集計する。
- ready_for_public_ciでは集計を輸送情報として表示してよい。
- 束数・通読行数・修正数は品質成果ではなくCI輸送指標である。

低収穫ゲートは`TRANSLATION_QUALITY_GATE.md`を併用する。
低収穫時の二巡目監査もquality audit段階で行い、encodingへ持ち込まない。

## 報告

quality audit回の報告順:
1. 修正候補と理由
2. 疑ったが保持した箇所
3. 追加文脈が必要な箇所
4. 件数は原則として表示しない

encoding回の報告順:
1. 監査判断がどのfix / ownerへ収録されたか
2. 重複・所有・FACT_DOUBTの整合
3. 品質ゲート結果
4. 最後に輸送件数

## train-05への適用

train-05は初回public検証後に低収穫再監査を行ったため、
既存記録から四段階の証拠を遡及して`PRIVATE_STAGE_STATE.json`へ固定する。
これは段階飛越を正当化するものではない。次の列車からは各段階を順番に実行し、
状態遷移そのものを往復テストする。
