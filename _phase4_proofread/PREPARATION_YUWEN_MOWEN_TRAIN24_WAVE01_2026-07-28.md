# 宇文逸↔莫問 train-24 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: train-23 Relation artifact
- queue: 4 packets / 54 unique rows
- reservation correction: `11996_1` was absent from the latest Relation artifact and primary source; replaced with real source-backed scenes.

## packet layout

### packet-01 — 5227_3 + 5227_5
- rows: 21
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5227_3_5227_5_2026-07-28.json`
- context: 宇文逸が莫棄・元啓と対面し、莫問から武林各派と武学の基礎を教わる。

### packet-02 — 5229_1 + 5229_2 + 5229_3
- rows: 11
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5229_1_5229_2_5229_3_2026-07-28.json`
- context: 莫問が入門祝いの剣を宇文逸へ譲り、師父から預かった師弟を世話する立場を語る。

### packet-03 — 5215_1 + 5215_2 + 5217_2 + 5220_1
- rows: 15
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5215_1_5215_2_5217_2_5220_1_2026-07-28.json`
- context: 入門直後、莫問が宇文逸へ武当の主要施設と新弟子の手続きを案内する。

### packet-04 — 5230_6
- rows: 7
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5230_6_2026-07-28.json`
- context: 最初の門派任務へ出る直前、莫問が二師兄・莫離の病状を説明し、清河村へ向かう。

## boundaries

- preparationでは翻訳判断、fix、owner、正式束を書かない。
- 莫棄の発話は文脈参照とし、明白な疑義が見つかった場合もcross-register候補へ分離する。
- 場面内で明言されない玄火教の善悪、莫離の病状、天龍幇対応の詳細を補わない。
