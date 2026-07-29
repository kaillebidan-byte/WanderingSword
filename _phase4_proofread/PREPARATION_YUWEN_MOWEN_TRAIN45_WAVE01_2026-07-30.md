# 宇文逸↔莫問 yuwen-mowen-train-45 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30492452206`
- queue: 1 packet / 55 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 9016_1 + 9150_3 + 9150_4 + 9154_2 + 9209_2 + 9210_1 + 9223_6 + 9228_2 + 9229_2 + 9230_2
- rows: 55
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES9016_1_9230_2_2026-07-30.json`
- context: 五仙教の介入を察する場面、莫問を救出して帰還を促す分岐、大戦前の再同行、蒼鷹追跡・程鈺への気遣い・森での救援、悪人谷残党との対峙までを含む後期再同行群。各場面は分岐・事件別に裁定し、一本の連続時系列へ合成しない。

## boundary attestation

- 十場面・55行。予約9016_1から、莫問の救出・再同行と悪人谷残党への対峙を閉じ、無名登場直前で意味境界を切る。
- 9016_1、9150_3〜9154_2、9209_2〜9223_6は別事件・分岐を含む。9228_2、9229_2、9230_2は同行者構成が異なる相互排他的な対峙分岐であり、発話者・同席者・討伐対象を合成しない。次の9231_3以降は無名登場と風雲訣・天山の核心へ移るため別packetとする。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
