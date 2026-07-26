# 宇文逸↔莫問 train-11 wave-01 private quality audit

- stage: `private_quality_audit`
- train: `yuwen-mowen-train-11`
- status: `complete`

この記録はsealed queue全体の翻訳判断だけを固定する。修正JSON、owner、review record、正式束、輸送集計はquality audit中には作成していない。

## fix candidates

### `5784_9_Dlgs_Index1_Text` — 程钰

- 現訳: `伯父の賀寿に来られたんですよね？ 武当の方々が着いたと聞いて、伯父が私を迎えに寄こしたんです。`
- 判断: `fix_candidate`
- 候補訳: `伯父の賀寿に来られたんですよね？　武当の方々が着いたと聞いて、伯父が皆さんを迎えに行けと私を寄こしたんです。`
- 理由: 迎えられる対象が程鈺へ逆転する曖昧さを解消し、伯父が程鈺を迎え役として派遣した主客を戻す。

### `5784_9_Dlgs_Index4_Text` — 程钰

- 現訳: `（頭をかいて）本当は伯父が父を呼んだんです。でも父は帰ったばかりなのに、玄火教の大侠と話をしに行ってしまって……`
- 判断: `fix_candidate`
- 候補訳: `（頭をかいて）本当は伯父が父を呼んだんです。でも父は家に戻るなり、玄火教の大侠と相談に行ってしまって……`
- 理由: 「帰宅するなり相談へ行った」という時間順を戻し、原文にない逆接を除く。

### `5784_9_Dlgs_Index8_Text` — 程钰

- 現訳: `伯父はいつも、『四海の内、皆兄弟』だ、正邪の違いなんて気にしすぎるなって言ってます……`
- 判断: `fix_candidate`
- 候補訳: `伯父はいつも、「四海の内、皆兄弟。正邪の違いなど気にしすぎるな」って言っています……`
- 理由: 定着句の像を保ちつつ、壊れた引用境界を直して程鈺の口語へつなぐ。

### `5786_15_Dlgs_Index4_Text` — 莫问

- 現訳: `うむ。ただ、ここは門内ではない。何をするにも気をつけろ。`
- 判断: `fix_candidate`
- 候補訳: `ああ。ただ、外では門内と勝手が違う。師弟、万事気をつけろ。`
- 理由: 場所の否定ではなく、門外では勝手が異なるという兄弟子の実務的な注意へ戻す。

### `5786_15_Dlgs_Index5_Text` — 宇文逸

- 現訳: `分かりました。忠告ありがとうございます、師兄。`
- 判断: `fix_candidate`
- 候補訳: `分かりました。お気遣いありがとうございます、師兄。`
- 理由: 硬い翻訳語「忠告」を、師兄の気遣いへ応じる自然な礼へ直す。

### `5789_2_Dlgs_Index0_Text` — 宇文逸

- 現訳: `（頭をかいて）寝過ごしました……待たせてしまって、すみません。`
- 判断: `fix_candidate`
- 候補訳: `（頭をかいて）寝過ごしました。師兄をお待たせしてしまって……`
- 理由: 原文の宛先と関係を戻し、説明的な一般謝罪へ痩せさせない。

### `5790_11_Dlgs_Index2_Text` — 莫问

- 現訳: `（声を潜めて）だが今は各派が集まり、人目も口も多い……まずは動きを見よう。`
- 判断: `fix_candidate`
- 候補訳: `（声を潜めて）だが今は各派が集まり、誰が何を聞いているか分からない……まずは静観しよう。`
- 理由: `人多嘴杂`の直訳臭を除き、衆人環視下で情報漏れを警戒する判断を明確にする。

### `5803_2_Dlgs_Index3_Text` — 宇文逸

- 現訳: `この外道……よくも梧桐村のことを口にできたな！`
- 判断: `fix_candidate`
- 候補訳: `この野郎……よくも梧桐村のことを口にできたな！`
- 理由: `混蛋`を分類語「外道」へ置かず、宇文逸の直接的な怒りへ戻す。

### `5803_2_Dlgs_Index4_Text` — 宇文逸

- 現訳: `江大哥に続いて、今度は程堡主まで……これだけ人を害して、夜ごと悪夢にうなされもしないのか！`
- 判断: `fix_candidate`
- 候補訳: `江大哥に続いて、今度は程堡主まで……これほど多くの人を傷つけて、夜ごと悪夢にうなされもしないのか！`
- 理由: 中国語的な「人を害する」を自然化し、全員死亡と断定せず加害の広がりを保つ。

### `5803_2_Dlgs_Index9_Text` — 莫问

- 現訳: `――師弟、避けろ！`
- 判断: `fix_candidate`
- 候補訳: `――師弟、危ない！`
- 理由: 原文は危険を知らせる短句であり、回避という具体動作を追加しない。

## allusion review

- `四海之内皆兄弟`: 定着した成句として「四海の内、皆兄弟」を保持する。特定典籍の長い引用として膨らませず、程鈺が伯父の教えを口語で伝える機能を優先する。

## keep judgments

### `5784_9`

- `5784_9_Dlgs_Index0_Text` — `keep`
- `5784_9_Dlgs_Index2_Text` — `keep`
- `5784_9_Dlgs_Index3_Text` — `keep`
- `5784_9_Dlgs_Index6_Text` — `keep`
- `5784_9_Dlgs_Index7_Text` — `keep`
- `5784_9_Dlgs_Index10_Text` — `keep`
- `5784_9_Dlgs_Index11_Text` — `keep`
- `5784_9_Dlgs_Index12_Text` — `keep`

### `5786_3 + 5786_15`

- `5786_3_Dlgs_Index0_Text` — `keep`
- `5786_3_Dlgs_Index1_Text` — `keep`
- `5786_3_Dlgs_Index2_Text` — `keep`
- `5786_3_Dlgs_Index3_Text` — `keep`
- `5786_3_Dlgs_Index4_Text` — `keep`
- `5786_3_Dlgs_Index5_Text` — `keep`
- `5786_3_Dlgs_Index6_Text` — `keep`
- `5786_3_Dlgs_Index7_Text` — `keep`
- `5786_3_Dlgs_Index8_Text` — `keep`
- `5786_3_Dlgs_Index9_Text` — `keep`
- `5786_15_Dlgs_Index0_Text` — `keep`
- `5786_15_Dlgs_Index1_Text` — `keep`
- `5786_15_Dlgs_Index2_Text` — `keep`
- `5786_15_Dlgs_Index3_Text` — `keep`

### `5789_2 + 5789_4 + 5790_10 + 5790_11`

- `5789_2_Dlgs_Index1_Text` — `keep`
- `5789_2_Dlgs_Index2_Text` — `keep`
- `5789_2_Dlgs_Index3_Text` — `keep`
- `5789_4_Dlgs_Index0_Text` — `keep`
- `5789_4_Dlgs_Index1_Text` — `keep`
- `5789_4_Dlgs_Index2_Text` — `keep`
- `5790_10_Dlgs_Index0_Text` — `keep`
- `5790_10_Dlgs_Index1_Text` — `keep`
- `5790_10_Dlgs_Index2_Text` — `keep`
- `5790_11_Dlgs_Index0_Text` — `keep`
- `5790_11_Dlgs_Index1_Text` — `keep`
- `5790_11_Dlgs_Index3_Text` — `keep`
- `5790_11_Dlgs_Index4_Text` — `keep`
- `5790_11_Dlgs_Index5_Text` — `keep`

### `5800_1 + 5801_2 + 5803_2`

- `5800_1_Dlgs_Index0_Text` — `keep`
- `5800_1_Dlgs_Index1_Text` — `keep`
- `5800_1_Dlgs_Index2_Text` — `keep`
- `5801_2_Dlgs_Index0_Text` — `keep`
- `5801_2_Dlgs_Index1_Text` — `keep`
- `5803_2_Dlgs_Index0_Text` — `keep`
- `5803_2_Dlgs_Index1_Text` — `keep`
- `5803_2_Dlgs_Index2_Text` — `keep`
- `5803_2_Dlgs_Index5_Text` — `keep`
- `5803_2_Dlgs_Index6_Text` — `keep`
- `5803_2_Dlgs_Index7_Text` — `keep`
- `5803_2_Dlgs_Index8_Text` — `keep`

## fact doubts

- 程鈺の父と玄火教の関係を親交・共謀へ確定しない。
- 程家の家事、霊蛛使、程万清の人物像を場面外から補わない。
- 蒼鷹の来訪目的と、江吟風・程徳明・弟妹に関する中傷を客観事実へしない。
- 依頼人が程二爺だという宇文逸の推測を確定しない。
