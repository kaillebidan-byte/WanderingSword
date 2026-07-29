# 宇文逸↔莫問 yuwen-mowen-train-46 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30494673142`
- queue: 1 packet / 53 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 9231_3 + 9232_3 + 9233_2 + 9233_4
- rows: 53
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES9231_3_9233_4_2026-07-30.json`
- context: 悪人谷残党との戦闘末尾、沙権賈の敗北と莫問の処断、同行者構成が異なる三つの分岐における無名の出現、宇文逸の内力への評価、悪人谷主としての正体開示、莫問への挑発と不倶戴天の宣言までを含む。各出現場面は相互排他的な分岐として扱い、同席者や発話を一本の時系列へ合成しない。

## boundary attestation

- 四場面・53行。悪人谷残党の敗北から、分岐別の無名出現・正体開示・莫問への挑発と不倶戴天の宣言までを閉じ、円覚による後始末直前で意味境界を切る。
- 9231_3・9232_3・9233_4は無名出現時の同行者構成が異なる分岐であり、李元興・燕未還・荀杳杳の同席や発話を他分岐へ拡張しない。9233_2は悪人谷残党の敗北と莫問による処断を示す別の戦闘末尾で、全分岐に共通する出来事とは断定しない。次の9234_6以降は円覚の介入、烏長老の遺体・青竹杖の処置、少林への移動という後始末へ移るため別packetとする。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
