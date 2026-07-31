# 宇文逸↔莫問 yuwen-mowen-train-71 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30628360400`
- queue: 1 packet / 65 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 6155_1 + 6155_3 + 6158_5 + 6171_5 + 6195_3 + 6198_3 + 6206_3 + 6213_1 + 6214_4 + 6229_1
- rows: 65
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES6155_1_6229_1_2026-07-31.json`
- context: 莫問が師兄関係を拒絶した直後の決戦分岐。宇文逸が情を断ち切れず敗れる局面、欧陽雪への攻撃を契機に戦意を戻す局面、莫問を倒して処断を拒む局面、莫問が死を受け入れる局面、瑶姫が介入する局面、宇文逸が敗北して悔恨を背負わされる局面まで。

## boundary attestation

- 十場面65行で、宇文逸のためらい、欧陽雪・瑶姫の介入、双方の勝敗、莫問の処断要求と死への受容、宇文逸の処断拒否、敗北後の脅しまで、決戦分岐群が閉じる。60行を超えるが、分岐結果を途中で切ると同型台詞の帰属と生死条件を誤るためcomplete_semantic_unit延長を使用する。
- 6155_1〜6229_1は同一決戦から派生する複数の勝敗・介入・生死分岐。重複に見える台詞を直列の一場面へ合成せず、各分岐内の前後関係を保持する。6206_3の莫問の死は一分岐の結果であり、6213_1・6214_4・6229_1へ遡及させない。9016_1以後は別事件として次cycleへ分離する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
