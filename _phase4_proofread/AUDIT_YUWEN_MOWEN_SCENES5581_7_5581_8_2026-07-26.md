# 宇文逸↔莫問 `5581_7` / `5581_8` private quality audit

- stage: `private_quality_audit`
- train: `yuwen-mowen-train-07`
- input: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5581_7_5581_8_2026-07-26.json`
- preparation: `_phase4_proofread/PREPARATION_YUWEN_MOWEN_SCENES5581_7_5581_8_2026-07-26.md`
- status: `complete`

この記録はquality audit段階の翻訳判断だけを固定する。修正JSON、owner、review record、正式束、輸送集計は作らない。

## fix candidates

### `5581_7_Dlgs_Index0_Text` — 莫問

- 原文: `师弟，走吧，我们也该去前面的法场，向清霄师伯复命了。`
- 現訳: `師弟、行こう。わたしたちも、前の法場で清霄師伯に復命しよう。`
- 判断: `fix_candidate`
- 候補訳: `師弟、行こう。わたしたちも、この先の法場で清霄師伯に復命しよう。`
- 理由: `前面的法场`は以前の法場ではなく前方の法場を指す。`前の法場`では時間的な「前」に読めるため、移動先を明確にする。復命相手と兄弟子の簡潔な促しは変えない。

### `5581_8_Dlgs_Index0_Text` — 莫問

- 原文: `师弟，走吧，我们也该去前面的法场，向师父复命了。`
- 現訳: `師弟、行こう。わたしたちも、前の法場で師父に復命しよう。`
- 判断: `fix_candidate`
- 候補訳: `師弟、行こう。わたしたちも、この先の法場で師父に復命しよう。`
- 理由: 分岐鏡写しとして同じ方向語の誤読を直す。清霄師伯ではなく師父へ復命する差はそのまま保持する。

## challenged keeps

### `5581_7_Dlgs_Index1_Text`

`ああ、行こう。`を保持する。短い同意として自然で、儀礼的な返答や説明を足していない。

### `5581_8_Dlgs_Index1_Text`

`ああ、行こう。`を保持する。分岐間で同一の返答を保つことに意味があり、復命相手の差を宇文逸の行へ持ち込まない。

## needs context

なし。二分岐の差と移動先は対象行内で確定できる。

## FACT_DOUBT

- 二分岐を同時発生として結合しない。
- 法場の用途、状態、そこで起きた出来事を補わない。
- 復命内容と復命後の反応を先取りしない。

## ALLUSION_REVIEW

候補なし。

## 次段階への固定事項

private encodingでは上記二行だけを収録候補とする。表示タグが実値に存在する場合は位置と内容を保持する。新しい疑義が出た場合はquality auditへ戻す。
