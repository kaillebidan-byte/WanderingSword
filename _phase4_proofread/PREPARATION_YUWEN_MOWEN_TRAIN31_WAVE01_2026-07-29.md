# 宇文逸↔莫問 yuwen-mowen-train-31 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30432296591`
- queue: 1 packet / 44 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 5370_1 + 5388_1 + 5389_2 + 5389_4 + 5444_2 + 5446_1 + 5449_2 + 5450_3
- rows: 44
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5370_1_5450_3_2026-07-29.json`
- context: 品剣大会の開始と方闊海戦、負傷後の分岐会話を確認した後、各派の出立、姑蘇から峋谷関への旅程、門内大比の決着、杜彪の再襲撃を警戒して名剣山荘へ急ぐ判断までを扱う。

## boundary attestation

- 八場面・44行でrelation artifact上の連続範囲が意味境界を持って閉じ、標準40〜60行の範囲内で封印した。
- 5389_2と5389_4は試合結果に応じた分岐会話として併記し、同時発生する一続きの会話へ統合しない。5450_3で杜彪への警戒と渡し場へ向かう方針が確定して場面が閉じる。5452_1からは湛盧剣授与後の別場面が始まるため含めない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
