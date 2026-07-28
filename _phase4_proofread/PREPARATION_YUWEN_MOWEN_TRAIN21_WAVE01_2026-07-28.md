# 宇文逸↔莫問 train-21 wave-01 private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-21`
- status: `complete`
- execution mode: `always_public_full_pipeline`
- source artifact: Release train orchestrator run `30316600608` / artifact `8672377081`
- source digest: `sha256:39325a39bf84b31eb3c431eafec39c8cc40a99693f5e3deac8146e4aa5eb3af2`

この記録では文脈、時系列、重複、既存ownerだけを固定する。翻訳のfix/keep判断、正式束、manifest totalsは作らない。

## 予約候補の無効化

`5803_AttachDlgs_Index0` は関係抽出artifactには残っているが、過去の一次資料監査で現行 `source_zh` に存在しない疑似座標と確認済みだった。新cycleの先頭packetには採用せず、`packet_invalidated` として実在する次の明示参照群へ補充した。

## sealed queue

### packet 1 — 不在期の情報状態

- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES13297_2_20515_4_20516_3_2026-07-28.json`
- scenes: `13297_2 / 20515_4 / 20516_3`
- rows: 8
- boundary: 程鈺探索期と莫問自身の失踪後を分ける。元啓、程鈺、清霄の所有行は別人物ペアへ残す。

### packet 2 — 行方探索から伏龍子との同行確認へ

- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES22010_7_22025_1_2026-07-28.json`
- scenes: `22010_7 / 22025_1`
- rows: 10
- boundary: 師父襲撃と莫問の所在を未確定のまま保ち、同行という行動事実を思想的一致へ広げない。

### packet 3 — 血縁開示と復讐手段への疑問

- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES22029_5_22031_1_22125_1_2026-07-28.json`
- scenes: `22029_5 / 22031_1 / 22125_1`
- rows: 20
- boundary: 実子という説明、親子として認め合ったという推測、復讐手段への賛同疑義を分ける。清霄、瑶姫、欧陽雪の所有行は取り込まない。

### packet 4 — 天山行きと恩讐の決着

- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE24057_1_2026-07-28.json`
- scene: `24057_1`
- rows: 20
- boundary: 宇文逸の現在形の師兄認識と、自分が恩讐を決着させる責任を保つ。`24058_1` は鏡写し同期の照合だけに使い、今回のunique rowsへ重ねて数えない。

## seal

- packet count: 4
- unique reviewed rows: 58
- seal reason: `packet_threshold`
- cap check: 4 packets / 58 rowsで、6 packets / 60 rowsの上限内
- queue status: `sealed`

次段階では四packetを分割せず、sealed queue全体を連続監査する。
