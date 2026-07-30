# 宇文逸↔莫問 yuwen-mowen-train-49 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30501996757`
- queue: 1 packet / 56 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 22020_8 + 24221_2 + 24221_3 + 24221_5 + 24221_6 + 24223_3 + 24230_1 + 24232_3 + 24341_2 + 30821_1 + 32001_2 + 32001_5 + 32004_1 + 32007_1
- rows: 56
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES22020_8_32007_1_2026-07-30.json`
- context: 莫問が無名とともに天山側へ立ったことを明かした後。宇文逸が天山残篇を返す、または謝罪する分岐から対決へ進み、戦後に殺さず何度でも止めると告げる。その後、莫問が借りを返すため助力し、再び調査・稽古・日常会話を共にするまで。

## boundary attestation

- 天山側への離反開示、対決前後の分岐、宇文逸の不殺と反復制止、後日の助力、再び師兄弟として調査・稽古・日常を共にするところまで、14場面・56行で関係の崩壊から回復までを閉じる。次の5203系は両者の初対面へ時系列が戻るため別packetとする。
- 24221_2・24221_3は残篇返却、24221_5・24221_6は謝罪と江小彤への使用説明へ分岐するため合成しない。24223_3と24230_1・24232_3も戦後の応答が異なる分岐として扱う。24341_2以降は後日の助力と関係回復を示す別時点であり、対決直後の連続場面へ畳み込まない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
