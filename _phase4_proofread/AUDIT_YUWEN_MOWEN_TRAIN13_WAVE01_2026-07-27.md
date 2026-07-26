# 宇文逸↔莫問 train-13 wave-01 private quality audit

- stage: `private_quality_audit`
- train: `yuwen-mowen-train-13`
- status: `complete`

この記録はsealed queue全体の翻訳判断だけを固定する。修正JSON、owner、review record、正式束、輸送集計はquality audit中には作成していない。

## fix candidates

### `5825_1_Dlgs_Index7_Text` — 宇文逸

- 現訳: `程堡主はあれだけ人のために尽くし、この人たちだって恩を受けたはずなのに……亡くなったばかりの方を、よくここまで悪く言えるな！`
- 判断: `fix_candidate`
- 候補訳: `程堡主はあれだけ人のために尽くし、この人たちだって恩を受けたはずなのに……亡くなったばかりだというのに、よくここまで悪く言えるな！`
- 理由 (relation/voice): 亡くなった相手を「方」と名詞化した硬い言い回しを避け、程堡主への怒りを直接の発話へ戻す。

### `5829_5_Dlgs_Index0_Text` — 宇文逸

- 現訳: `……母上が、私に宛てた手紙だって？`
- 判断: `fix_candidate`
- 候補訳: `……君の母上が、私に宛てた手紙？`
- 理由 (meaning/relation): 原文の「你娘」を落とさず、母が程鈺の母であることと宇文逸が宛先であることを明確にする。

### `5829_5_Dlgs_Index3_Text` — 程钰

- 現訳: `母さんは、きっと前から何かを感じていたんです。そうでなければ、どうして急にあんなことを……`
- 判断: `fix_candidate`
- 候補訳: `母さんは、きっと前から何かを予感していたんです。そうでなければ、どうして急にあんなことを……`
- 理由 (meaning): 「预感」を曖昧な「感じていた」へ弱めず、程鈺自身の推測として予感を保つ。

### `5829_5_Dlgs_Index4_Text` — 宇文逸

- 現訳: `師弟、あまり思い詰めるな……`
- 判断: `fix_candidate`
- 候補訳: `師弟、あまり気を落とすな……`
- 理由 (meaning/voice): 悲嘆への慰めを、考え込みを禁じる「思い詰めるな」へずらさない。

### `5897_6_Dlgs_Index2_Text` — 宇文逸

- 現訳: `大丈夫です、師父。私と師兄にお任せください！`
- 判断: `fix_candidate`
- 候補訳: `承知しました、師父。私と師兄にお任せください！`
- 理由 (relation/voice): 師父から任務を受ける場面で、直訳的な「大丈夫です」ではなく武当弟子の自然な受諾へ戻す。

### `5926_2_Dlgs_Index0_Text` — 宇文逸

- 現訳: `貴様ら……烏長老を殺したのか！`
- 判断: `fix_candidate`
- 候補訳: `貴様ら……よくも烏長老を殺したな！`
- 理由 (meaning/voice): 原文は殺害を目の前の事実として断罪しており、疑問形へ弱めない。

### `5926_2_Dlgs_Index2_Text` — 包闵

- 現訳: `あの老いぼれが聞き分けねえから、ちょいと早く閻魔様のところへ送ってやっただけだ……どうした、お前も連れが欲しいか？`
- 判断: `fix_candidate`
- 候補訳: `あの老いぼれが聞き分けねえから、ちょいと早く閻魔様のところへ送ってやっただけだ……どうした、お前もあの世で奴の連れになりてえのか？`
- 理由 (meaning): 「跟他做个伴」は烏長老の連れとして死ぬ脅し。相手が連れを欲しがる意味へ主客を逆転させない。

### `5926_3_Dlgs_Index3_Text` — 莫问

- 現訳: `長年、悪事の限りを尽くしてきた貴様らだ。どの罪一つ取っても、書き尽くせぬほどだ！　今こそ命で償え！`
- 判断: `fix_candidate`
- 候補訳: `長年、悪事の限りを尽くしてきた貴様らだ。罪を挙げればきりがない！　今こそ命で償え！`
- 理由 (allusion/voice): 「罄竹难书」を一件ごとの罪が書き切れないという不自然な逐語訳にせず、罪状の多さを断罪する発話へ戻す。

### `5928_1_Dlgs_Index2_Text` — 宇文逸

- 現訳: `何だと！？`
- 判断: `fix_candidate`
- 候補訳: `何だって！？`
- 理由 (voice/relation): 師兄の警告への驚きを、敵へ返すような攻撃的な「何だと」へ寄せない。

## keep judgments

### `5825_1 + 5828_1 + 5829_5`

- `5825_1_Dlgs_Index0_Text` — `keep`
- `5825_1_Dlgs_Index1_Text` — `keep`
- `5825_1_Dlgs_Index2_Text` — `keep`
- `5825_1_Dlgs_Index3_Text` — `keep`
- `5825_1_Dlgs_Index4_Text` — `keep`
- `5825_1_Dlgs_Index5_Text` — `keep`
- `5825_1_Dlgs_Index6_Text` — `keep`
- `5825_1_Dlgs_Index8_Text` — `keep`
- `5828_1_Dlgs_Index0_Text` — `keep`
- `5828_1_Dlgs_Index1_Text` — `keep`
- `5829_5_Dlgs_Index1_Text` — `keep`
- `5829_5_Dlgs_Index2_Text` — `keep`
- `5829_5_Dlgs_Index5_Text` — `keep`
- `5829_5_Dlgs_Index6_Text` — `keep`
- `5829_5_Dlgs_Index7_Text` — `keep`

### `5831_3 + 5831_4 + 5897_6 + 5923_2`

- `5831_3_Dlgs_Index0_Text` — `keep`
- `5831_3_Dlgs_Index1_Text` — `keep`
- `5831_4_Dlgs_Index0_Text` — `keep`
- `5831_4_Dlgs_Index2_Text` — `keep`
- `5831_4_Dlgs_Index3_Text` — `keep`
- `5831_4_Dlgs_Index4_Text` — `keep`
- `5897_6_Dlgs_Index0_Text` — `keep`
- `5897_6_Dlgs_Index1_Text` — `keep`
- `5897_6_Dlgs_Index3_Text` — `keep`
- `5923_2_Dlgs_Index0_Text` — `keep`
- `5923_2_Dlgs_Index1_Text` — `keep`
- `5923_2_Dlgs_Index2_Text` — `keep`

### `5926_2 + 5926_3 + 5928_1`

- `5926_2_Dlgs_Index1_Text` — `keep`
- `5926_2_Dlgs_Index3_Text` — `keep`
- `5926_2_Dlgs_Index4_Text` — `keep`
- `5926_2_Dlgs_Index5_Text` — `keep`
- `5926_2_Dlgs_Index6_Text` — `keep`
- `5926_2_Dlgs_Index7_Text` — `keep`
- `5926_2_Dlgs_Index8_Text` — `keep`
- `5926_2_Dlgs_Index9_Text` — `keep`
- `5926_3_Dlgs_Index0_Text` — `keep`
- `5926_3_Dlgs_Index1_Text` — `keep`
- `5926_3_Dlgs_Index2_Text` — `keep`
- `5926_3_Dlgs_Index4_Text` — `keep`
- `5928_1_Dlgs_Index0_Text` — `keep`
- `5928_1_Dlgs_Index1_Text` — `keep`

### `5928_2`

- `5928_2_Dlgs_Index0_Text` — `keep`
- `5928_2_Dlgs_Index1_Text` — `keep`
- `5928_2_Dlgs_Index2_Text` — `keep`
- `5928_2_Dlgs_Index3_Text` — `keep`
- `5928_2_Dlgs_Index4_Text` — `keep`
- `5928_2_Dlgs_Index5_Text` — `keep`
- `5928_2_Dlgs_Index6_Text` — `keep`
- `5928_2_Dlgs_Index7_Text` — `keep`

## allusion review

- `入土为安`: 埋葬して死者を安んじる定着表現として現訳の「土に還してやる」を保持した。
- `人各有志`: 人にはそれぞれ志があるという定着句として現訳を保持した。
- `罄竹难书`: 罪状が多く書き尽くせない意として解し、「罪を挙げればきりがない」へ自然化する。

## fact doubts

- `5825_1`: 程堡主の埋葬場所、程二爺の関与、街の噂の真偽を確定しない。
- `5829_5`: 程鈺の母が将来を予感していたという程鈺の推測を客観事実へしない。
- `5831_3 / 5831_4`: 程鈺が去った理由と行き先を補わない。
- `5926_2 / 5926_3`: 悪人谷の親分が宇文逸を必要とする目的と、莫問が言いかけた天山の過去を確定しない。
- `5928_1 / 5928_2`: 瑶姫が青竹杖を得た経緯、烏長老の現在の生死、別の襲撃者の正体を補わない。
