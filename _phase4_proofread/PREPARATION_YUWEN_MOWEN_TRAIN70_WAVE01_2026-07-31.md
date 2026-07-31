# 宇文逸↔莫問 yuwen-mowen-train-70 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30601107348`
- queue: 1 packet / 63 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 6002_5 + 6064_6 + 6151_2 + 6151_3
- rows: 63
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES6002_5_6151_3_2026-07-31.json`
- context: 丐幇分舵事件後。莫問が本来は自分に属する物を取り戻す行動に出たのち、無名が伏龍子であり莫問の父であること、天山派滅亡と風雲訣をめぐる旧事が開示される。後日、宇文逸が残篇を莫問へ返し復讐停止を求めるが、莫問は各派殲滅を正当化し、最後に師兄呼称を拒絶するまで。

## boundary attestation

- 四場面63行で、莫問の奪取行為、伏龍子の正体と父子関係の開示、天山派旧事、残篇返還、復讐継続の論理、師兄関係の明示的拒絶までが閉じる。60行を超えるが、6151_3末尾の関係断絶まで切らずに読む必要があるためcomplete_semantic_unit延長を使用する。
- 6002_5と6064_6は莫問の離反と出自開示へ続く局面、6151_2〜6151_3は清虚死後に残篇を返す後続対峙。発話時点を直列に保ち、6064_6で開示された情報をそれ以前の認識へ遡及させない。6155_1以後の決戦・勝敗・生死分岐は次cycleへ分離する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
