# 宇文逸↔莫問 train-25 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: train-24 Relation artifact
- queue: 4 packets / 57 unique rows
- reservation: `5234_1` verified in the latest Relation artifact; adjacent source-backed scenes were grouped by narrative boundary.

## packet layout

### packet-01 — 5234_1 + 5237_2 + 5237_3
- rows: 17
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5234_1_5237_2_5237_3_2026-07-28.json`
- context: 清河村の初任務で、宇文逸が山賊の所在と戦力を推理し、莫問が推論を補う。討伐後、事件の全貌を追えなくても侠義と良心を基準にせよと教え、村へ戻る。

### packet-02 — 5238_1 + 5240_1
- rows: 17
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5238_1_5240_1_2026-07-28.json`
- context: 山賊討伐を清河村へ報告し、村人の謝意を受けて辞去する。その後、莫問が道通へ任務結果を復命し、宇文逸は初任務の働きを評価される。

### packet-03 — 5240_4 + 5244_3
- rows: 17
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5240_4_5244_3_2026-07-28.json`
- context: 莫問が日常任務・緊急任務・門派貢献の仕組みを説明し、宇文逸の独り立ちを促す。後日、平康城へ向かう宇文逸へ危険を告げ、丹薬を渡す。

### packet-04 — 5245_1
- rows: 6
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5245_1_2026-07-28.json`
- context: 宇文逸が資深弟子へ昇格し、莫問へ感謝する。莫問は自分の手柄へせず、宇文逸本人の勤勉を認めて師父のもとへ送り出す。
- small-packet exception: 六行で自己完結し、次の`5274_1`は平康城帰還後の別事件へ移るため分離する。

## boundaries

- preparationでは翻訳判断、fix、owner、正式束を書かない。
- 村長・蘭児・道通の発話は文脈参照とし、明白な疑義はcross-register候補へ分離する。
- 山賊の背後関係、平康城の不穏、昇格の因果を場面以上に補わない。
