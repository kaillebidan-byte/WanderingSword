# 宇文逸↔莫問 yuwen-mowen-train-74 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30656638354`
- queue: 1 packet / 46 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 9234_6 + 9236_6 + 9238_6 + 9245_1 + 9245_3
- rows: 46
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES9234_6_9245_3_2026-08-01.json`
- context: 悪人谷残党戦の直後、円覚が一行を少林へ招き、同行者分岐ごとに青竹杖と烏長老の遺体の処置を決める。少林到着後、莫問が《風雲訣》の来歴を問い、宇文逸が《五霊心経》残篇から会得した経緯を明かし、莫問が先に退出するまで。

## boundary attestation

- 三つの少林招待分岐と、到着後の《風雲訣》説明・師兄退出までの五場面46行で意味単位が完結する。9261_1は場所・事件・同行者が切り替わるため含めない。
- 9234_6は円覚の門弟が遺体を送る分岐、9236_6は李元興が青竹杖と遺体を送る分岐、9238_6は李元興を燕未還・荀杳杳が護衛する分岐として別々に保持する。9245_1と9245_3は少林到着後の共通局面として続け、平康の丐幇分舵事件が始まる9261_1は次packetへ分離する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
