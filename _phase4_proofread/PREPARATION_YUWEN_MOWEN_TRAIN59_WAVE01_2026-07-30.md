# 宇文逸↔莫問 yuwen-mowen-train-59 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30515671572`
- queue: 1 packet / 51 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 5449_2 + 5455_1 + 5450_3 + 5504_3 + 5506_3 + 5508_13 + 5509_4
- rows: 51
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5449_2_5509_4_2026-07-30.json`
- context: 二つの時系列ブロックを同じwaveで監査する。前半は武当の門内大比決着、清虚による名剣山荘行きの師命、姑蘇での杜彪戦後に船で山荘へ向かう判断。後半は幽雲沢で追手の狙いを分析し、徐海の待ち伏せを疑い、峋谷関へ入城して献書による将軍面会を試みるが失敗し、黄将軍重傷の噂を検討するまで。

## boundary attestation

- 門内大比後から名剣山荘行きへ至る過去時系列19行と、幽雲沢から峋谷関の献書失敗までの現行時系列32行を、二ブロック51行で閉じた。両ブロック間の出来事を補完せず、黄将軍との直接対面と将軍府衝突は次束へ残す。
- 5449_2・5455_1・5450_3は既監査の名剣山荘本編より前に位置する未監査場面で、5504_3以降へ直結させない。5504_3・5506_3・5508_13・5509_4は5502_6の幽雲沢迂回決定後の連続場面として扱い、5522_1の将軍府衝突は次束へ分ける。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
