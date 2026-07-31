# 宇文逸↔莫問 yuwen-mowen-train-72 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30629731498`
- queue: 1 packet / 55 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 9016_1 + 9150_3 + 9150_4 + 9154_2 + 9209_2 + 9210_1 + 9223_6 + 9228_2 + 9229_2 + 9230_2
- rows: 55
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES9016_1_9230_2_2026-08-01.json`
- context: 莫問救出局面から、救出拒否／再同行の分岐、蒼鷹追跡後の帰路、悪人谷残党との共闘開始まで。

## boundary attestation

- 十場面55行で、莫問の救出拒否と再同行、師弟呼称の復帰、蒼鷹追跡後の判断、悪人谷残党との共闘開始までが分岐別に閉じる。無名登場後の真相対立を混ぜない。
- 9150_4の帰還拒否と9154_2以後の再同行を直列合成しない。9228_2・9229_2・9230_2は同行者構成の異なる戦闘開始分岐として保持し、無名が現れる9231_3は次cycleへ分離する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
