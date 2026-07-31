# 宇文逸↔莫問 yuwen-mowen-train-68 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30598602893`
- queue: 1 packet / 53 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 5807_1 + 5809_11 + 5809_2 + 5810_7 + 5810_9 + 5811_2 + 5811_3 + 5821_1
- rows: 53
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5807_1_5821_1_2026-07-31.json`
- context: 一線天峡谷で蒼鷹を追跡した後。蒼鷹討伐後の瑶姫をめぐる葛藤、程家堡への帰還、程鈺の絶望と武当での救済方針、分岐ごとの帰山判断を経て、程鈺を伴い武当正殿へ到着するまで。

## boundary attestation

- 八場面53行で、蒼鷹追跡の決着、瑶姫への葛藤、程鈺の救済判断、武当帰還、正殿到着までが完結する。40行以上60行以下の標準範囲で閉じるため延長は使わない。
- 5809_11と5809_2、5811_2と5811_3は分岐差分を含む。重複台詞を一つの直列場面として合成せず、各分岐で宇文逸の応答、程鈺救済の有無、帰山経路を個別に保つ。5821_1で程鈺を武当へ連れ帰った経路の到着と正殿前の待機までが閉じる。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
