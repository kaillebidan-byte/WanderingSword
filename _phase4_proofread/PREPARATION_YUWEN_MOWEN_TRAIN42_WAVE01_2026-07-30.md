# 宇文逸↔莫問 yuwen-mowen-train-42 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30486391758`
- queue: 1 packet / 73 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 5821_1 + 5825_1 + 5828_1 + 5829_5 + 5831_3 + 5831_4 + 5897_6 + 5923_2 + 5926_2 + 5926_3 + 5928_1 + 5928_2 + 5928_6 + 5928_7
- rows: 73
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5821_1_5928_7_2026-07-30.json`
- context: 程家堡事件後、程鈺が武当で受入れを待ち、弟子入りまたは離脱へ分岐する。その後、宇文逸と莫問が次任務で丐幇分舵へ向かい、敵対者との対峙と瑶姫の青竹杖を巡る情報を経て、烏長老救出を優先する。

## boundary attestation

- 十四場面・73行。標準60行を超えるが、程鈺の分岐を閉じた後の次任務で、丐幇分舵の対峙と瑶姫からの情報提示を途中で切らず、救出優先の判断まで含めて意味単位を完結させるため延長した。
- 5821_1から5831_4は程鈺の受入れ・弟子入り・離脱分岐、5897_6から5928_7は武当の次任務から丐幇分舵で救出優先を決めるまでの連続単位。5928_1/5928_2と5928_6/5928_7は選択分岐として別々に監査し、次の6002_5以降の莫問に関する別局面は含めない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
