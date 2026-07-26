# 宇文逸↔莫問 train-12 wave-01 private quality audit

- stage: `private_quality_audit`
- train: `yuwen-mowen-train-12`
- status: `complete`

この記録はsealed queue全体の翻訳判断だけを固定する。修正JSON、owner、review record、正式束、輸送集計はquality audit中には作成していない。

## fix candidates

### `5805_3_Dlgs_Index0_Text` — 宇文逸

- 現訳: `くっ……あと一歩だったのに。あれほどの軽功まで身につけていたとは！`
- 判断: `fix_candidate`
- 候補訳: `くっ……あと一歩で捕まえられたのに。まさか、あれほど軽功に長けていたとは！`
- 理由 (meaning): 原文は軽功の腕前への驚きであり、別の技まで身につけたという情報を足さない。

### `5805_4_Dlgs_Index2_Text` — 宇文逸

- 現訳: `分かりました。師兄の読みを信じます！`
- 判断: `fix_candidate`
- 候補訳: `はい、師兄の言うとおりにしましょう！`
- 理由 (meaning/voice): 原文は師兄の案に従う短い応答。読みへの信頼という説明を足さない。

### `5807_1_Dlgs_Index2_Text` — 宇文逸

- 現訳: `分かりました！`
- 判断: `fix_candidate`
- 候補訳: `はい！`
- 理由 (voice): 追跡中の「好」を切迫した短い応答として保つ。

### `5809_11_Dlgs_Index1_Text` — 宇文逸

- 現訳: `今までに、江湖の怖さは嫌というほど見てきました……さっきの瑶姫が本心で言っていないことくらい、私にも分かります。`
- 判断: `fix_candidate`
- 候補訳: `今では、江湖の怖さも十分に見てきました……先ほどの瑶姫の言葉が本心ではないことも分かっています。`
- 理由 (meaning/voice): 原文にない自虐的な強調を除き、言不由衷を自然な自己認識へ戻す。

### `5809_2_Dlgs_Index3_Text` — 宇文逸

- 現訳: `私……分かりません……`
- 判断: `fix_candidate`
- 候補訳: `私……私にも分かりません……`
- 理由 (voice): 原文の言い直しと迷いを残す。

### `5810_7_Dlgs_Index1_Text` — 程钰

- 現訳: `二人とも……`
- 判断: `fix_candidate`
- 候補訳: `お二人だったんですね……`
- 理由 (relation/voice): 是你们は相手を認める反応。弟子入り前の二人への礼を保つ。

### `5810_7_Dlgs_Index2_Text` — 程钰

- 現訳: `……二人とも、見ていただろう。`
- 判断: `fix_candidate`
- 候補訳: `……全部、見ていたんですね。`
- 理由 (relation/voice): 悲嘆の中でも莫問大侠・宇文少侠への敬度を保ち、粗い断定へしない。

### `5810_7_Dlgs_Index4_Text` — 程钰

- 現訳: `うう……父さんは、最初から僕を自分の子だと思っていなかったんだ……`
- 判断: `fix_candidate`
- 候補訳: `うう……父さんは、最初から僕を自分の子だと思っていなかったんだろうな……`
- 理由 (meaning): 原文の推量を残し、程鈺の受け止めを客観事実へ確定しない。

### `5810_7_Dlgs_Index5_Text` — 程钰

- 現訳: `二人も……僕の母さんが、あんな人だっているのか？`
- 判断: `fix_candidate`
- 候補訳: `お二人も……母さんがそんな人だっているんですか？`
- 理由 (relation/voice): 感情の揺れを残しつつ、弟子入り前の二人への呼びかけを自然な敬体へ戻す。

### `5810_7_Dlgs_Index8_Text` — 莫问

- 現訳: `本当に母親を信じるなら、まず武を磨け。力をつけてから戻り、真相を突き止めて、母親の潔白を取り戻すんだ……`
- 判断: `fix_candidate`
- 候補訳: `本当に母親を信じるなら、まず武を磨け。力をつけてから戻り、真相を突き止め、母親の潔白を証明するんだ……`
- 理由 (meaning): 还一个清白を日本語の行動目標として自然化する。

### `5810_9_Dlgs_Index1_Text` — 宇文逸

- 現訳: `分かりました、師兄。`
- 判断: `fix_candidate`
- 候補訳: `はい、師兄。`
- 理由 (voice): 原文の短い承諾を保つ。

### `5811_2_Dlgs_Index6_Text` — 莫问

- 現訳: `よかろう、行こう。`
- 判断: `fix_candidate`
- 候補訳: `そうだな。行こう。`
- 理由 (voice): 弟弟子への短い同意を不要に古風な権威口調へしない。

## keep judgments

### `5805_3 + 5805_4 + 5807_1`

- `5805_3_Dlgs_Index1_Text` — `keep`
- `5805_4_Dlgs_Index0_Text` — `keep`
- `5805_4_Dlgs_Index1_Text` — `keep`
- `5807_1_Dlgs_Index0_Text` — `keep`
- `5807_1_Dlgs_Index1_Text` — `keep`

### `5809_11 + 5809_2`

- `5809_11_Dlgs_Index0_Text` — `keep`
- `5809_11_Dlgs_Index2_Text` — `keep`
- `5809_11_Dlgs_Index3_Text` — `keep`
- `5809_11_Dlgs_Index4_Text` — `keep`
- `5809_11_Dlgs_Index6_Text` — `keep`
- `5809_11_Dlgs_Index7_Text` — `keep`
- `5809_11_Dlgs_Index8_Text` — `keep`
- `5809_11_Dlgs_Index10_Text` — `keep`
- `5809_11_Dlgs_Index11_Text` — `keep`
- `5809_11_Dlgs_Index12_Text` — `keep`
- `5809_2_Dlgs_Index0_Text` — `keep`
- `5809_2_Dlgs_Index1_Text` — `keep`
- `5809_2_Dlgs_Index2_Text` — `keep`
- `5809_2_Dlgs_Index4_Text` — `keep`
- `5809_2_Dlgs_Index5_Text` — `keep`
- `5809_2_Dlgs_Index6_Text` — `keep`

### `5810_7 + 5810_9`

- `5810_7_Dlgs_Index0_Text` — `keep`
- `5810_7_Dlgs_Index3_Text` — `keep`
- `5810_7_Dlgs_Index7_Text` — `keep`
- `5810_7_Dlgs_Index9_Text` — `keep`
- `5810_7_Dlgs_Index10_Text` — `keep`
- `5810_7_Dlgs_Index11_Text` — `keep`
- `5810_7_Dlgs_Index12_Text` — `keep`
- `5810_7_Dlgs_Index13_Text` — `keep`
- `5810_7_Dlgs_Index14_Text` — `keep`
- `5810_7_Dlgs_Index15_Text` — `keep`
- `5810_7_Dlgs_Index16_Text` — `keep`
- `5810_9_Dlgs_Index0_Text` — `keep`

### `5811_2 + 5811_3 + 5821_1`

- `5811_2_Dlgs_Index1_Text` — `keep`
- `5811_2_Dlgs_Index2_Text` — `keep`
- `5811_2_Dlgs_Index3_Text` — `keep`
- `5811_2_Dlgs_Index4_Text` — `keep`
- `5811_3_Dlgs_Index1_Text` — `keep`
- `5811_3_Dlgs_Index2_Text` — `keep`
- `5811_3_Dlgs_Index3_Text` — `keep`
- `5821_1_Dlgs_Index0_Text` — `keep`
- `5821_1_Dlgs_Index1_Text` — `keep`
- `5821_1_Dlgs_Index2_Text` — `keep`
- `5821_1_Dlgs_Index3_Text` — `keep`
- `5821_1_Dlgs_Index4_Text` — `keep`
- `5821_1_Dlgs_Index5_Text` — `keep`

## allusion review

- 対象なし。

## fact doubts

- `5805_4`: 一線天峡谷は莫問の推測として扱い、この時点で確定しない。
- `5809_11 / 5809_2`: 瑶姫の発言内容と将来の敵対を確定しない。
- `5810_7`: 父に拒絶されたという程鈺の受け止めと、父の実際の意思を混同しない。
- `5811_2 / 5811_3`: 程家堡と玄火教の関係へ動機を補わず、程鈺の武当受け入れを決定済みとしない。
