# 宇文逸↔莫問 第71束レビュー

## 対象

- 日付: 2026-07-25
- scenes: `5523_1` / `5525_3`
- 行数: 8
- 修正: 1
- 保持: 7
- source workflow: Relation audit extraction
- source run: `30140191768`
- source artifact: `8614192158`
- digest: `sha256:7a38ab3e453d2544fdefd886f8dcc50467b59df1c9d3088547c32297128056ad`
- source HEAD: `1bf29e39de33d22c52291123f64474935adb8eca`

対象8キーはtrain-03の修正対象に含まれず、release後もzh・ja本文は変化していないため、この成功CI artifactを一次資料として使用する。

## 意味境界

- `5523_1`: 灯りのついた書斎を見つけ、中の人物が黄将軍かもしれないと考えて入室する。
- `5525_3`: 城外の戦闘が始まる中、莫問が黄将軍の指示を優先し、徐海捜索を続ける。
- `5525_6`は徐海の偽傷・天龍幇の目的に関する推測が集中するため別束へ分離する。

## 行別判断

### 5523_1 Index0 宇文逸 — keep

- zh: `这里应该就是书房了吧？`
- ja: `ここが書斎だよな？`
- 場所を確かめる短い独り言寄りの確認として自然。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### 5523_1 Index1 莫問 — keep

- zh: `灯还亮着，证明里面有人。`
- ja: `まだ灯りがついている。中に誰かいるな。`
- 観察から推論へ短く進み、人数や人物を補っていない。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### 5523_1 Index2 宇文逸 — keep

- zh: `啊，那我们进去看看吧，说不定里面的人就是将军呢！`
- ja: `なら、入ってみましょう。中にいるのが将軍かもしれません！`
- 最初の確認は地の常体、同行者全体への提案は敬体という場面内切替として成立する。将軍と確定せず可能性を保っている。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### 5525_3 Index0 宇文逸 — keep

- zh: `城外已经打起来了，我们……`
- ja: `城外ではもう戦いが始まっています。私たちは……`
- 城外への懸念を言いさしで残し、戦況や参加者を説明し切っていない。黄将軍との会話直後の敬体も許容範囲。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### 5525_3 Index1 莫問 — fix

- zh: `师弟，城外的战斗绝非一人之力所能改变。`
- before: `師弟、城外の戦いは一人の力で覆せるものではない。`
- after: `師弟、城外の戦いは一人の力でどうにかできるものではない。`
- `改变`を勝敗の「覆し」に限定せず、個人では戦況を変えられないという実務的判断へ戻す。敗北宣言や諦観にはしない。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260725_batch71.json`

### 5525_3 Index2 莫問 — keep

- zh: `我们还是尽快按照黄将军的吩咐，找到徐海要紧！`
- ja: `まずは黄将軍に言われたとおり、急いで徐海を探すんだ！`
- 任務優先の短い指示として自然。黄将軍の指示内容を追加していない。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### 5525_3 Index3 宇文逸 — keep

- zh: `嗯，我明白。`
- ja: `はい、分かりました。`
- 莫問への応答として簡潔な敬体が自然。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### 5525_3 Index4 宇文逸 — keep

- zh: `不过刚才那士兵说徐海就在城西的医馆，也不知道医馆到底在哪……`
- ja: `ただ、さっきの兵士は徐海が城西の医館にいると言っていました。肝心の医館がどこにあるのか……`
- 徐海の所在を兵士の発言として保持し、確認済み事実へ強めていない。医館の具体的な場所や経路も追加していない。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

## 所有境界

- 既存第7束所有を維持: 7キー
- 新規人物ペア所有: `5525_3_Dlgs_Index1_Text`
- cross-register新規: 0

## FACT_DOUBT

- 灯りから書斎内の人物・人数を確定しない。
- 書斎内の人物を黄将軍と保証しない。
- 城外の戦闘の参加者、規模、戦況、結果を追加しない。
- 莫問の判断を敗北宣言や撤退命令へ変えない。
- 黄将軍の指示内容を徐海捜索以上に補わない。
- 兵士の徐海所在情報を確認済みの現在地へ強めない。

## ALLUSION_REVIEW

- 該当なし。

## skill review

- 変更なし。
- `改变`を文脈に応じて「どうにかする」とする判断は既存の意味優先規則で扱える。

## 結論

第71束は1修正・7保持で`reviewed_pending_ci`とする。train-04累計は2束・15行・3修正・人物ペア新規1キー。release条件到達までlocres、pak、audit_status、適用件数は更新しない。
