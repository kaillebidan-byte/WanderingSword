# 宇文逸↔莫問 第213束 review

- scenes: `12406_OptionDlgs3_Index0_Text, 12406_RequestDlgs_Index0_Text, 12409_FinishingDlgs_Index8_Text, 12436_RequestDlgs_Index0_Text, 14201_FinishingDlgs_Index2_Text, 20004_FinishingDlgs_Index3_Text, 22576_FinishingDlgs_Index1_Text, 23021_FinishingDlgs_Index0_Text, 5371_FinishingDlgs_Index0_Text, 5371_FinishingDlgs_Index3_Text, 5944_RequestDlgs_Index1_Text, 6252_FinishingDlgs_Index0_Text`
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_TAIL_QUESTS_12406_6252_2026-08-01.json`
- source artifact: run `30668426155` / artifact `8807875827`

## 実変更

- key: `5371_FinishingDlgs_Index0_Text`
- before: `5015 - 莫問 $@$宇文師弟！体の具合はもう大丈夫か？`
- after: `5015 - 莫問 $@$宇文師弟！　まだどこか具合の悪いところはないか？`
- reason: meaning/voice: 原文は身体にまだ不調箇所が残っていないかを具体的に確かめる問い。現訳の『もう大丈夫か』は状態を総括する問いへ弱めているため、兄弟子が傷を観察して世話する声のまま、不調の残存を尋ねる機能を戻す。

## 保持判断

同一packetの残り11行は、原文の意味、話者register、時系列、制御タグを再確認し、実質的な欠陥がないため保持した。
好みだけの言い換え、場面以上の事実補完、別人物の声の一括変更は行っていない。

## 典故監査

- `12406_OptionDlgs3_Index0_Text`: 定着した成語 — 『言之凿凿』は言葉を確かな事実のように言い切る機能。現訳の『断言していた』が、莫棄の発言を根拠に宇文逸が推測する構造を保つためKEEP。
- `20004_FinishingDlgs_Index3_Text`: 通常の追跡動作語 — 『追蹑』は足取りを追って追跡する意味で、特定典籍の引用ではない。現訳『追って行き』が瑶姫を追跡した事実を保つためKEEP。
