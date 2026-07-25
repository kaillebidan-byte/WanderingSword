# 宇文逸↔莫問 第70束レビュー

## 対象

- 日付: 2026-07-25
- scene: `5522_1`
- 行数: 7
- 修正: 2
- 保持: 5
- source workflow: Relation audit extraction
- source run: `30140191768`
- source artifact: `8614192158`
- digest: `sha256:7a38ab3e453d2544fdefd886f8dcc50467b59df1c9d3088547c32297128056ad`
- source HEAD: `1bf29e39de33d22c52291123f64474935adb8eca`

source HEADはtrain-03の成功CI HEADである。第70束の7キーはtrain-03の修正対象に含まれず、asset writeback後も当該zh・ja本文は変化していないため、この束の一次資料として使用する。

## 場面

将軍府内で徐海側に包囲された一行が、数的不利から離脱を図る。徐海が捕縛を命じ、瑶姫が挑発で応じた直後、黄宗政が戦闘を止める。

## 行別判断

### Index0 宇文逸 — keep

- zh: `可恶，他们人太多了。`
- ja: `くそ、数が多すぎる。`
- 数的不利への短い焦りとして自然。人数を具体化せず、宇文逸の戦闘時の切迫を保っている。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### Index1 欧陽雪 — keep

- zh: `宇文公子，我们不能继续硬拼了……`
- ja: `宇文公子、これ以上無理に戦うのは……`
- 言いさしを完成させず、制止と危惧を残している。負傷・敗北の確定を追加していない。
- ownership: unowned。変更しないため新規ownerを作らない。

### Index2 莫問 — keep

- zh: `不错，师弟，我们得赶紧找机会离开。`
- ja: `そうだ、師弟。隙を見て離脱しよう。`
- 兄弟子として欧陽雪の判断を受け、短く離脱方針を示す。説明的な戦況報告へ膨らませていない。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### Index3 副将-徐海 — fix

- zh: `放肆！你们这些小贼，将军府岂是你们想来就来、想走就走的地方！`
- before: `生意気な！貴様ら小賊ども、将軍府は貴様らが好き勝手に出入りできる場所ではない！`
- after: `無礼者め！　小賊ども、将軍府を好き勝手に出入りできると思うな！`
- 「貴様ら」の重複を除き、`放肆`の叱責と将軍府側の威圧を自然な命令調へ戻す。原文以上の残虐さや処罰内容は追加しない。
- owner: `_phase4_proofread/fixes_cross_register_xuhai_5522_1_20260725.json`

### Index4 副将-徐海 — keep

- zh: `给我把他们拿下！`
- ja: `こいつらを捕らえろ！`
- 捕縛命令として短く明確。命令先、人数、捕縛後の処遇を補っていない。
- ownership: unowned。変更しないため新規ownerを作らない。

### Index5 瑶姫 — keep

- zh: `口气倒不小～那就要看看，你到底有没有本事拿下我们了！`
- ja: `大きく出たわね～　なら、私たちを捕らえるだけの腕があるか、見せてもらいましょう！`
- 伸ばし、挑発、余裕、強さが同時に出ており、丁寧な社交辞令へ弱めていない。
- owner: `_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch7.json`

### Index6 黄宗政 — fix

- zh: `都住手！咳咳……`
- before: `皆、やめろ！げほげほ……`
- after: `全員、手を止めろ！　ゴホッ、ゴホッ……`
- 将軍として場を止める命令を強め、咳を台詞の切迫に合う表記へ整える。登場経緯、病名、重傷の程度は確定しない。
- owner: `_phase4_proofread/fixes_cross_register_huangzongzheng_5522_1_20260725.json`

## 所有境界

- 既存第7束所有を維持: Index0 / Index2 / Index5
- 新規cross-register所有: Index3 / Index6
- keep-onlyで未所有のまま: Index1 / Index4
- pair新規キー: 0
- cross-register新規キー: 2

## FACT_DOUBT

- 包囲人数や具体的な戦力差を台詞以上に追加しない。
- 欧陽雪の言いさしを負傷・敗北の確定へ変えない。
- 徐海の権限、命令先、捕縛後の処遇を補わない。
- 黄宗政が現れた経緯、病名、容体をこの七行だけで確定しない。

## ALLUSION_REVIEW

- 該当なし。

## skill review

- 変更なし。
- 徐海と黄宗政の修正は人物・場面固有のregister調整であり、翻訳一般則への新規昇格は不要。

## 結論

第70束`5522_1`は2修正・5保持で`reviewed_pending_ci`とする。release条件到達までlocres、pak、audit_status、適用件数は更新しない。
