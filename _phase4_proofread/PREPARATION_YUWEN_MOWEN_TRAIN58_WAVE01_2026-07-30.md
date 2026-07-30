# 宇文逸↔莫問 yuwen-mowen-train-58 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30514543142`
- queue: 1 packet / 57 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 5388_1 + 5389_2 + 5389_4 + 5452_1 + 5444_2 + 5446_1 + 5501_2 + 5502_5 + 5502_6
- rows: 57
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5388_1_5502_6_2026-07-30.json`
- context: 品剣大会で方闊海に追い詰められた宇文逸を莫問が制止して救う。試合後の二分岐で負傷と翌日の試合を案じ、湛盧獲得後に名剣山荘を発つ。姑蘇で尾行を察知し、峋谷関への道を幽雲沢経由へ変更するまで。

## boundary attestation

- 方闊海戦の危機、試合後の二分岐、湛盧獲得後の出立、姑蘇での尾行対応、幽雲沢への迂回決定を57行で閉じた。別時系列の門内大比・杜彪戦直後・出発前の師命は分離する。
- 5389_2と5389_4は方闊海戦後の別分岐として混同せず併記する。5452_1を湛盧獲得後、5444_2と5446_1を山荘出立、5501_2から5502_6を尾行発覚と迂回判断の連続場面として物語順に並べた。5449_2・5450_3・5455_1は過去時系列の別場面なので今回のpacketへ混ぜない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
