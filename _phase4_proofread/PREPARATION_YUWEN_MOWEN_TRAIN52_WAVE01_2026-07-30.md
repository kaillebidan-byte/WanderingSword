# 宇文逸↔莫問 yuwen-mowen-train-52 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30506264279`
- queue: 1 packet / 54 unique rows
- semantic extension: `not_used`

## packet layout

### packet-01 — 5230_6 + 5234_1 + 5237_2 + 5237_3 + 5238_1 + 5240_1 + 5240_4
- rows: 54
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5230_6_5240_4_2026-07-30.json`
- context: 宇文逸が莫問と初めての門派任務へ出発し、清河村で山賊被害を聞き取る。莫問の推理を受けて猿の森へ向かい、討伐後に侠義と問心無愧の考えを教わる。村への報告、武当への帰還報告と報酬受領を経て、日常任務・緊急任務・門派貢献の仕組みを学び、弟子部屋へ戻るところまで進む。

## boundary attestation

- 初任務の出発から清河村調査、山賊討伐後の侠義の教え、村と門派への報告、報酬と門派任務制度の説明、一日の終了まで、7場面54行で一つの導線を閉じる。
- 5230_6は初任務の出発、5234_1は清河村での状況分析、5237_2・5237_3は山賊討伐後の教えと帰村、5238_1は村への報告、5240_1は道通への帰還報告、5240_4は任務制度の説明と一日の終了。次の5244_3は丹砂を巡る別任務の導入なので分離する。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
