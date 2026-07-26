# 宇文逸↔莫問 train-13 wave-01 private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-13`
- translation judgment: 未実施
- source run: `30219687084`
- artifact id: `8636842358`
- artifact digest: `sha256:5c421e8d6ada65adb77cff8a24d0b1a5e40bf5c8712e49c580d1b68061f6d57b`

## packet 1 — `5825_1 + 5828_1 + 5829_5`

程堡主の死後をめぐる街の噂、青渓の所在、程鈺が母から託された手紙を扱う。

- 境界: 街の噂と程鈺の推測を客観事実へせず、母の所属と手紙の宛先を取り違えない。

## packet 2 — `5831_3 + 5831_4 + 5897_6 + 5923_2`

程鈺の失踪への反応から、清虚の任務指示、莫棄の同行願い、丐幇分舵への移動までを扱う。

- 境界: 程鈺が去った理由を補わず、清虚への礼、莫棄の粗さ、莫問の案内役の声を均さない。

## packet 3 — `5926_2 + 5926_3 + 5928_1`

烏長老を殺した悪人谷の一団との対峙、莫問が天山の過去に触れかける場面、瑶姫と青竹杖の出現を扱う。

- 境界: 悪人谷の親分の目的、莫問の天山での過去、瑶姫が青竹杖を得た経緯を補わない。

## packet 4 — `5928_2`

瑶姫の挑発と、烏長老の救出を優先する莫問の判断を扱う。

- 境界: 瑶姫の説明を敵対者の主張として保ち、烏長老の現在の生死や別の襲撃者を確定しない。

## owner snapshot

encoding後、全candidateの`schema_version: 2` `ownership_snapshot`を全fix owner実測へ同期した。58行中54行は既存ownerに属し、4行は意図的保持のためunownedのまま残した。9修正は既存owner更新8、新規owner1として収録し、複数ownerはない。

queueは四packet・58行でsealした。preparationではfix / keep判断、修正JSON、正式束番号を作らず、sealed queue全体をquality auditへ渡した。
