# 宇文逸↔莫問 yuwen-mowen-train-33 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30435847682`
- queue: 1 packet / 70 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 5508_13 + 5509_4 + 5522_1 + 5523_1 + 5525_3 + 5525_6 + 5528_7 + 5531_3 + 5531_4
- rows: 70
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5508_13_5531_4_2026-07-29.json`
- context: 峋谷関へ入った一行が献書を名目に黄将軍への接触を試み、将軍府での衝突と城内の夜襲を経て徐海を追う。黒白無常を退け、負傷した徐海から娘の手掛かりを聞き、蘭児がその娘だと判明して徐海の最期の言葉を受けるまでを扱う。

## boundary attestation

- 九場面・70行。標準上限60行を越えるが、5531_3と5531_4を分断せず、徐海の娘の真相と最期の言葉まで一つの意味単位として閉じるため、hard max 80行以内の意味延長を使用した。
- 5531_3で徐海の傷を確認する流れに入り、5531_4で娘の正体、蘭児の無事、徐海の悔恨までが閉じる。60行地点で切ると同一会話を分断するため70行へ意味延長した。次の5531_7は徐海の件を黄将軍へ報告し、蘭児の危険を再検討する事後局面なので含めない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
