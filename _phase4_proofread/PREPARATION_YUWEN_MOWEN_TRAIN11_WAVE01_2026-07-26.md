# 宇文逸↔莫問 train-11 wave-01 private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-11`
- translation judgment: 未実施
- source run: `30199134621`
- artifact id: `8631091129`
- artifact digest: `sha256:2b86d47476ecdb1093bbda900c4f6b8487192e64bf751d8bd837635418a04339`

## packet 1 — `5784_9`

程鈺の自己紹介、迎えの事情、父と玄火教の話、莫問による話題の切り上げまでを連続して読む。

- 境界: 伯父の懸念、父と玄火教の関係、後続の家内事情を確定しない。
- 典故候補: `四海之内皆兄弟`。定着句として像を保ち、程鈺の口語へ接続する。

## packet 2 — `5786_3 + 5786_15`

程徳明との正式対面と、その後の兄弟子同士の私的な相談を分けて読む。

- 境界: 程家の家事、霊蛛使、程万清の人物像を先取りしない。

## packet 3 — `5789_2 + 5789_4 + 5790_10 + 5790_11`

寝坊の軽いやり取りから寿宴、蒼鷹発見後の低声の制止までを読む。

- 境界: 蒼鷹の目的と宴席で起きる事件を確定しない。

## packet 4 — `5800_1 + 5801_2 + 5803_2`

追跡から城壁での対峙までを読み、敵の中傷と客観事実を分ける。

- 境界: 江吟風、程徳明、程万清に関する蒼鷹の発言を事実へ昇格しない。

## owner snapshot

全candidateに`schema_version: 2`の`ownership_snapshot`を付与した。四packet・58行はすべて既存ownerに属していた。quality audit後の10修正は既存owner値の更新として収録し、新規ownerと複数ownerはない。

queueは四packetでsealした。preparationではfix / keep判断、修正JSON、正式束番号を作らず、sealed queue全体をquality auditへ渡した。
