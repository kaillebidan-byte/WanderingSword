# 宇文逸↔莫問 train-12 wave-01 private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-12`
- translation judgment: 未実施
- source run: `30213262353`
- artifact id: `8635079552`
- artifact digest: `sha256:3ee23cff26556950fa23b68a69c1f334b85d90b696395a8051834c6c062b0760`

## packet 1 — `5805_3 + 5805_4 + 5807_1`

蒼鷹を叐c��逃がした直後、宇文逸と莫問が負傷と逃走方向から一線天峡谷を追う。

- 境界: 宇文逸の悔しさへ原文にない能力獲得を足さず、莫問の逃走先推測を確定事実へしない。

## packet 2 — `5809_11 + 5809_2`

瑶姫の発言と蒼鷹討伐後、宇文逸が将来瑶姫へ刃を向けられるか迷い、莫問が目前の危機へ意識を戻す。二場面は分岐差分。

- 境界: 分岐間の重複行を揃えつつ、瑶姫の言葉を真実へ確定せず、宇文逸の迷いと言いさしを残す。

## packet 3 — `5810_7 + 5810_9`

程家堡で母の死と家族の疑念に直面した程鈺が、莫問の叱咤を受け、武を学ぶ決意をして武当へ同行する。

- 境界: 弟子入り前の程鈺は莫問大侠・宇文少侠へ礼を保つ。父から拒絶されたという受け止めを客観事実へしない。

## packet 4 — `5811_2 + 5811_3 + 5821_1`

程家堡を離れる二つの分岐と、程鈺を武当正殿へ連れてきた直後を読む。莫問は判断を示し、宇文逸は程鈺を気遣う。

- 境界: 5811_2と5811_3は分岐差分。程家堡と玄火教の関係へ動機を補わず、程鈺の受け入れは清虚らの判断前として保つ。

## owner snapshot

encoding後の全candidate㑫`schema_version: 2`の`ownership_snapshot`を付与した。58行中54行はownerに属し、4行は意図的保持のためunownedのまま残した。12修正の内訳は既存owner更新9、新規owner3。複数ownerはない。

queueは四packet・58行でsealした。preparationではfix / keep判断、修正JSON、正式束番号を作らず、sealed queue全体をquality auditへ渡した。
