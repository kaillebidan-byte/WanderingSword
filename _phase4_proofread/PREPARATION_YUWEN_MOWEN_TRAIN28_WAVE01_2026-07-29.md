# 宇文逸↔莫問 yuwen-mowen-train-28 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30391224493`
- queue: 1 packet / 62 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 5331_2 + 5337_2 + 5339_2 + 5340_1 + 5340_2 + 5342_2 + 5342_3 + 5343_1 + 5345_1 + 5347_1
- rows: 62
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5331_2_5347_1_2026-07-29.json`
- context: 品剣大会前倒しの報を受け、宇文逸が門内大比へ参加する。予選突破後は元鳴戦の敗北分岐と莫棄戦の優勝分岐が併存し、いずれも品剣大会参加資格を得る。その後、莫問が一行を率いるよう命じられ、出発時に江吟風の墓参りのため梧桐村へ寄ることを決める。

## boundary attestation

- 5331_2から5343_1まででは39行で大比の勝敗分岐だけが閉じ、5345_1を加えた46行では旅程指示の途中で切れる。5347_1までの62行で、大比参加資格の確定から名剣山荘行きの編成・出発判断までが完結する。
- 5342_2・5342_3と5343_1は相互排他的な勝敗分岐であり、一つの直線時系列として接続しない。両分岐で共通する参加資格と、後続の名剣山荘行きへの合流を別々に監査する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
