# 宇文逸↔莫問 train-14 wave-01 private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-14`
- translation judgment: 未実施
- source run: `30223353373`
- artifact id: `8637871805`
- artifact digest: `sha256:f294e61bbf2eb315a3b9d648ecdd298e60a89ccdf4cca9563b5f6123e29ea0d6`

## packet 1 — `5928_6 + 5928_7 + 6002_5`

瑶姫と青竹杖の分岐鏡写し、烏長老救出の判断、莫問が風雲訣を取り戻す場面を扱う。

- 境界: 5928系の既存裁定を分岐間で揃えつつ、6002_5で莫問が取り戻す物と権利関係を補わない。
- 小束理由: 11行。後続の6064_6は36行の不可分な告発・推論場面であり、併合すると60行上限を越えるため分離する。

## packet 2 — `6064_6`

無名＝伏龍子と莫問の出自が明かされた直後、天山事件から江小彤の両親までの因果を伏龍子と清虚が語る。

- 境界: 伏龍子の告発、清虚の推論、伏龍子の自認を分け、長い因果を一括して客観事実へしない。
- 大束理由: 36行。告発と推論が連鎖する単一場面で、途中分割すると主客・因果・知識状態を壊すため不可分とする。

## owner snapshot

全`fixes_*.json`のlive ownerを照合した。packet 1の8行は既存owner `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch15.json` に属し、残る3行は未所有。packet 2の36行は未所有。複数ownerはない。

queueは二packet・47行で`unique_reviewed_rows_threshold`によりsealした。preparationではfix / keep判断、修正JSON、正式束番号を作らず、sealed queue全体をquality auditへ渡した。
