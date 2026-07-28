# 宇文逸↔莫問 train-23 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: train-22 Relation artifact
- queue: 5 packets / 56 unique rows

## packet layout

### packet-01 — 24341_2
- rows: 3
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE24341_2_2026-07-28.json`
- context: 天山での決戦後、莫問が隠棲の意向を翻し、宇文逸への借りとして次の旅に加わる。

### packet-02 — 5227_4 + 5341_2 + 5341_4
- rows: 12
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5227_4_5341_2_5341_4_2026-07-28.json`
- context: 宇文逸の武当入門直後から門内大比まで。莫問は師兄として稽古の安全を気遣い、元鳴を制し、勝敗を宣告する。

### packet-03 — 6003_4 + 6003_6
- rows: 18
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES6003_4_6003_6_2026-07-28.json`
- context: 莫問が清虚襲撃の罪を宇文逸へ着せた直後。宇文逸は莫棄と欧陽雪に、師父を傷つけたのは莫問だと訴える。

### packet-04 — 6008_2
- rows: 18
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE6008_2_2026-07-28.json`
- context: 冤罪と雪児の五仙蠱発作が重なり、宇文逸が無力感と莫問の変化を理解できない苦悩を語る。

### packet-05 — 6057_12
- rows: 5
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE6057_12_2026-07-28.json`
- context: 邪教勢力との戦闘後、莫問が清霄へ報告し、宇文逸の来訪に気づいて『来るべきではなかった』と告げる。

## boundaries

- preparationでは翻訳判断、fix、owner、正式束を書かない。
- 場面間の時系列を統合せず、明示参照だけの他人物行は文脈参照に留める。
- 既存PRで正式束化済みの5203系・11961系は再収録しない。
