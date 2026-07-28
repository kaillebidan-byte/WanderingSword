# 宇文逸↔莫問 train-26 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: train-25 Relation artifact
- queue: 4 packets / 40 unique rows
- reservation: `5274_1`を最新Relation artifactで再確認し、後続の意味単位を四packetへまとめた。

## packet layout

### packet-01 — 5274_1
- rows: 7
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5274_1_2026-07-28.json`
- context: 宇文逸が平康城から武当へ戻り、莫問へ事件を報告する。莫問は丐幇幇主が同件で来訪中だと伝え、宇文逸を殿内へ促す。

### packet-02 — 5278_1
- rows: 14
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5278_1_2026-07-28.json`
- context: 宇文逸・莫問・莫棄が平康城で李員外の居所と悪事を探るため、宿屋・医館・富商から聞き込みを始める。

### packet-03 — 5291_1 + 5292_3
- rows: 12
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5291_1_5292_3_2026-07-28.json`
- context: 李府で怯える人々と泣き声を手掛かりに救出を決める。陳麻子が蘭児を連れ去ったため、莫問が先行して救出へ向かい、宇文逸と莫棄が李天宝を足止めする。

### packet-04 — 5293_6 + 5293_7
- rows: 7
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5293_6_5293_7_2026-07-28.json`
- context: 絶無心が官憲への敵対をちらつかせるが、莫問は武当弟子として公道を守ると明言する。直後、莫問が宇文逸のもとへ戻る。

## boundaries

- preparationでは翻訳判断、fix、owner、正式束を書かない。
- 莫棄・李天宝・絶無心など別人物の発話は文脈参照とし、明白な疑義はcross-register候補へ分離する。
- 李員外の悪事、柴房の泣き声、官憲の反応を場面以上に確定しない。
