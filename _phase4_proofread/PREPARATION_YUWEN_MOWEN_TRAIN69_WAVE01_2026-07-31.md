# 宇文逸↔莫問 yuwen-mowen-train-69 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30599694651`
- queue: 1 packet / 67 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 5825_1 + 5828_1 + 5829_5 + 5831_3 + 5831_4 + 5897_6 + 5923_2 + 5926_2 + 5926_3 + 5928_1 + 5928_2 + 5928_6 + 5928_7
- rows: 67
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5825_1_5928_7_2026-07-31.json`
- context: 程家堡事件後。町人による程徳明の死後評、程鈺の弟子入り後の母の手紙と修行決意、別分岐での程鈺離山を経て、武当の次任務で丐幇分舵へ向かい、悪人谷との対峙と瑶姫の青竹杖奪取・烏長老救出優先の判断まで。

## boundary attestation

- 十三場面67行で、程家堡事件後の評価、程鈺の入門後・離山分岐、丐幇分舵での悪人谷戦、瑶姫の警告と救人優先までが完結する。60行を超えるが、二つの短い隣接意味単位を5928系の判断転換まで閉じるためcomplete_semantic_unit延長を使用する。
- 5829_5の程鈺弟子入り継続と5831_3〜5831_4の離山は別分岐として保持する。5928_2と5928_7も烏長老の安否をめぐる分岐差分を直列合成しない。5928系で瑶姫の警告を受け救人優先へ切り替わるところまでを閉じ、6002_5の莫問離反局面は次cycleへ分離する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
