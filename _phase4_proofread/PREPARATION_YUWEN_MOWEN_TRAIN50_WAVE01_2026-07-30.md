# 宇文逸↔莫問 yuwen-mowen-train-50 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30503591974`
- queue: 1 packet / 60 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 5203_4 + 5203_6 + 5203_7 + 5203_14 + 5211_4 + 5211_5 + 5212_1 + 5214_6 + 5215_1 + 5215_2 + 5217_2 + 5220_1 + 5222_1 + 5222_3
- rows: 60
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5203_4_5222_3_2026-07-30.json`
- context: 宇文逸が武当を訪れ、莫問が二人の師弟の非礼を詫びて江吟風の訃報と救援依頼を聞き、清虚へ取り次ぐ。清虚が宇文逸を弟子に迎えた後、莫問が大師兄として弟子部屋へ案内し、翌日の入門を経て武当の主要施設を巡る前半まで。

## boundary attestation

- 初対面の謝罪と身元確認、江吟風の訃報、清虚への取次ぎ、入門決定、弟子部屋への案内、拝師後の武当施設巡り前半まで、14場面・60行で入門前から兄弟子関係成立までを閉じる。次の5224系は錬丹房後の会話と清霄面会へ進むため別packetとする。
- 5203_4・5203_6・5203_7・5203_14は入門前で、宇文逸は莫問を『莫問大哥』と呼び、莫問は少侠・閣下・宇文少侠を使う。5211_4で師兄弟呼称へ切り替わるため遡及しない。5214_6以降の施設案内は兄弟子の常体と、師父・師叔への敬意を別軸で扱う。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
