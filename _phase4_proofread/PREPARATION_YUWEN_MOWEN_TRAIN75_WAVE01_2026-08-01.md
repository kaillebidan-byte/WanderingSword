# 宇文逸↔莫問 yuwen-mowen-train-75 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30658392194`
- queue: 1 packet / 43 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 9247_1 + 9250_1 + 9261_1 + 9262_1 + 9267_1 + 9273_1 + 9279_1 + 20515_4 + 20516_3
- rows: 43
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES9247_1_20516_3_2026-08-01.json`
- context: 少林の方丈室で莫問と瑶姫の交戦を目撃し、円覚襲撃後に莫問の消息を案じる局面から、平康・樊城・丐幇総舵の各分岐で襲撃後の状況を調べ、陳長老殺害の背後を推測するまで。末尾は後日、清霄師伯と元啓師兄へ莫問の行方を尋ね、なお消息不明であることを確認する二場面。

## boundary attestation

- 少林異変の前段5行、丐幇各拠点の調査5場面32行、後日の消息確認2場面6行で計43行。予約候補9261_1を含み、分岐差・人物の知識状態・莫問の在不在を監査できる意味単位として閉じる。
- 9247_1と9250_1は少林異変と莫問不在の前段。9261_1と9262_1は平康分舵の同行者・聞き手が異なる分岐、9267_1は樊城分舵、9273_1は総舵、9279_1は陳長老事件として別々に保持する。20515_4と20516_3は後日の消息確認であり、莫問が同行する9261_1〜9279_1と同一時点へ合成しない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
