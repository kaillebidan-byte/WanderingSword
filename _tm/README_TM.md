# 参考対訳資産（Legend of Mortal 由来）

別ゲーム「Legend of Mortal（俠之道）」の高品質日本語化modから抽出した
中国語→日本語の対訳資産。Wandering Sword校正の**参考用**。

## ファイル
- `TM_LegendOfMortal_zh-ja.csv` … 対訳TMマスター。列 = key, zh_hans, zh_hant, ja
  - 71,805対（JP総72,977タームの98.4%を被覆）。残りは中国語側が空の系統語。
- `glossary_LegendOfMortal_zh-ja.csv` … 用語辞書候補。列 = namespace, zh_hans, ja
  - 1,276語（武功・書物・装備・施設・能力名など）。短い名詞のみ抽出。

## 抽出元（事実）
- 原文: 本体 `Mortal_Data/level*` ・`resources.assets` のI2Localization（言語別格納）。
- 訳文: `Mods/JP/Stringtable.csv`（key→日本語）。同一キーでJOIN。

## 使い方の指針
- **固有名詞は流用不可。** 飛石帮・唐門・三師兄などはLoM固有でWandering Swordには無い。
- 活きるのは(1)武侠語彙の訳し方の慣例、(2)言い回し・語調の参照。
  例: 一心一意→一途 / 与妳同行→君とともに のような熟れた意訳の型。
- 校正時は「この中国語表現を巧者はどう日本語化したか」の類似検索素材として使う。

## 留保（推測混じり）
- 抽出は長さ前置きUTF-8の素彫り。欠落1,172は中国語値が空のため（取りこぼしではない）。
- 簡体/繁体は言語MBの自動判定。ごく稀に誤判定があり得るので、用語確定時は原文を当たること。
