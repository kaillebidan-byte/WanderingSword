# 宇文逸↔莫問 第73束レビュー

## 対象

- 日付: 2026-07-25
- scenes: `5528_7` / 完全重複分岐 `5529_5`
- unique rows: 7
- reviewed keys: 14
- 修正: 0
- 保持: 14
- source workflow: Relation audit extraction
- source run: `30140191768`
- source artifact: `8614192158`
- digest: `sha256:7a38ab3e453d2544fdefd886f8dcc50467b59df1c9d3088547c32297128056ad`
- source HEAD: `1bf29e39de33d22c52291123f64474935adb8eca`

artifactは`5529_5_Dlgs`を`5528_7_Dlgs`の完全重複分岐として記録している。7行の意味判断を共有し、両family計14キーの文面一致を確認した。

## 行別判断

### Index0 宇文逸 — keep

- zh: `等等，曹煜天你站住——`
- ja: `待て、曹煜天！`
- 原文末尾の中断線は省かれているが、直後に白無常が割り込む場面順によって制止が遮られた機能は保持されている。句読点だけの再改訂は高確度変更としない。
- primary owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json`
- duplicate `5529_5`は未所有のまま保持。

### Index1 白無常 — keep

- zh: `小家伙，你现在的对手，可是我们。`
- ja: `小僧ォ、今のお前の相手は――この白と黒だよ。`
- `小家伙`を挑発的な`小僧ォ`へ寄せ、白黒の名乗りを芝居がかった間で示している。黒白無常に許容された過剰演出の範囲で、能力や階級は追加していない。
- primary owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json`

### Index2 黒無常 — keep

- zh: `桀桀，不小心点，会丧命的。`
- ja: `ケヒヒィ……油断すりゃ、命を落とすぞォ。`
- 笑いと伸ばしを含む端役固有の誇張が機能している。脅しを戦闘結果の確定へは変えていない。
- primary owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json`

### Index3 宇文逸 — keep

- zh: `可恶！`
- ja: `くそっ！`
- 追跡を遮られた短い苛立ちとして自然。
- primary / duplicateとも未所有。変更しないためownerを作らない。

### Index4 莫問 — keep

- zh: `师弟！这两人气息内敛，绝非易于之辈！`
- ja: `師弟！　二人とも気配を深く隠している。侮れる相手ではない！`
- 観察から実力評価へ進む兄弟子の警告として明瞭。`気息内敛`を具体的な技法名へ変えていない。
- primary owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json`

### Index5 莫問 — keep

- zh: `我们得小心应对！`
- ja: `油断するな！`
- 包括的な注意喚起を危機時の短い命令へ圧縮している。直前の実力評価と合わせて応戦の慎重さが伝わる。
- primary owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json`

### Index6 宇文逸 — keep

- zh: `我知道了！`
- ja: `分かりました！`
- 莫問の警告を受ける短い応答として自然。
- primary / duplicateとも未所有。変更しないためownerを作らない。

## 重複分岐

- `5528_7`と`5529_5`はzh・ja・話者順が完全一致。
- 片側だけの修正は行っていない。
- 今後いずれかを再改訂する場合は、同じIndexを両familyへ鏡写しする。

## 所有境界

- 既存第8束所有: primary Index0 / 1 / 2 / 4 / 5
- 未所有keep: primary Index3 / 6、duplicate全7キー
- 新規ownerなし
- fix fileなしのkeep-only束

## FACT_DOUBT

- 曹煜天の逃走先、目的、戦況を追加しない。
- 黒白無常の能力、階級、過去、相互関係を台詞以上に確定しない。
- `気息内敛`を具体的な術・技・変身へ変えない。
- 命を落とすという脅しから戦闘結果を先取りしない。
- 莫問の実力評価を客観的順位や数値へ変えない。

## ALLUSION_REVIEW

- 該当なし。

## skill review

- 変更なし。
- 黒白無常の誇張は既存の端役・過剰演出許容で扱える。

## 結論

第73束は0修正・14保持で`reviewed_pending_ci`とする。fix fileは作成しない。train-04累計は4束・34行・3修正・人物ペア新規1キー。通常release条件`bundle_count=4`へ到達したため、新しい第74束の翻訳判断は開始せずpublic CI準備へ移る。
