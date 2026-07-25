# 翻訳品質ゲート

## 目的

既存日本語の意味ずれ、不自然さ、人物声の崩れ、原文にない追加、原文からの欠落を見つけて直す。束数、通読行数、修正数は輸送設計であり、品質成果ではない。

## wave段階分離

品質判断は`PRIVATE_TRANSLATION_STAGES.md`のwave v2に従う。

1. `private_preparation`: 複数packetの文脈・重複・既存ownerを固定する。翻訳判断をしない。
2. `private_quality_audit`: sealed queueの全packetを続けて監査する。修正JSON・owner・正式束を作らない。
3. `private_encoding`: 全監査済みpacketの確定判断だけを収録する。新しい翻訳判断をしない。
4. `translation_frozen`: 全packet収録後に翻訳判断を閉じる。CI輸送は別軸で進める。

quality auditへは、packet数、行数、修正率、release閾値、残量、manifest totalsを渡さない。

機械契約は`PRIVATE_TRANSLATION_STAGES.json`、現在状態は`PRIVATE_STAGE_STATE.json`、検査は`check_private_translation_stage.py`とする。`check_translation_quality_gate.py`はこのcheckerを通常入口から必ず呼ぶ。

## preparation seal

通常sealは4 packet以上または40 unique reviewed rows相当以上とする。意味境界上追加候補がない場合は`scope_exhausted`と具体的attestationを使える。上限は6 packet / 60 rows。

この閾値はpreparationとencodingの輸送設計にだけ使う。quality auditの判断材料にしない。

## 集計

- `reviewed_keys`: 実際に確認したlocresキー数。重複分岐を含む。
- `unique_reviewed_rows`: 同一原文・同一訳文の重複を一度だけ数えた実質通読行数。
- `fix_keys`: 修正するlocresキー数。重複分岐の鏡写しを含む。
- `unique_fix_rows`: 同じ判断を共有する重複修正を一度だけ数えた実質修正行数。
- manifestにはencoding済み正式束だけを置く。
- bundle状態は`review_status`と`apply_status`へ分ける。

## 低収穫ゲート

release候補時点で`unique_fix_rows / unique_reviewed_rows < 15%`なら低収穫とする。低収穫時は初回keepとなった全unique rowsをquality audit内で再監査する。

二巡目でも件数やrelease残量を判断材料にしない。二巡目完了後、encodingで集計を更新する。

## release条件

public CIへ出すには、輸送候補条件と`quality_gate.release_decision = quality_passed`が必要となる。

全packetがencodedになり、翻訳段階が`translation_frozen`になった後、輸送を`ready_for_public_ci`へ進める。輸送中は翻訳段階を凍結したまま維持する。

## 禁止

- 一packet単位でpreparation、quality audit、encodingをloopする。
- quality audit中に修正JSON、owner、正式束番号、metricsを作る。
- encoding中に新しい翻訳判断を追加する。
- candidate packetをmanifestへ置く。
- `reviewed_pending_ci`一項目へreview完了とapply未完了を混在させる。
- public CI中に品質判断を再開する。
