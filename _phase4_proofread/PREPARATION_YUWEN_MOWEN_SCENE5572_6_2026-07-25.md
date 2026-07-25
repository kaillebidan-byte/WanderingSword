# 宇文逸↔莫問 `5572_6` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-06`
- translation judgment: 未実施
- source: Relation audit extraction run `30149789606`
- artifact: `relation-audit-evidence` / `yuwen_mowen.json`
- artifact id: `8617244568`
- artifact digest: `sha256:48ac3451477c3d865bad8b8e04e4c2526a81ad26df2f40a4517f3bccdfbd9827`
- artifact head: `a568f731dcf419c766dc6a3845461aed1f83d46a`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5572_6_2026-07-25.json`

## 場面境界

直前の`5551_2`では、遼城へ着いた宇文逸が叔父との再会を期待し、叔父を父親同然に思っていることを同行者へ語った。

対象`5572_6`は遼城事件後の会話である。仮面の怪人に襲われた宇文逸と瑶姫へ欧陽雪が駆け寄り、一行は怪人が風雲訣を狙った理由、天龍幇との関係、相手の力量と素性を推測する。莫問は黎城で師父たちへ尋ねる方針を示し、宇文逸は叔父の衣冠塚を建ててから出発すると決める。

後続`5572_9`では遼城を出る直前、宇文逸が上の空の莫問へ声をかけ、黎城への道順が示される。怪人の正体や莫問の内面は対象場面へ先取りしない。

`5572_6_Dlgs`自体に重複locationはない。

## 話者順

欧陽雪 → 瑶姫 → 瑶姫 → 宇文逸 → 瑶姫 → 欧陽雪 → 瑶姫 → 瑶姫 → 莫問 → 莫問 → 宇文逸 → 宇文逸

## 所有境界

全12キーの既存ownerは`_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json`。

- `5572_6_Dlgs_Index0_Text`
- `5572_6_Dlgs_Index1_Text`
- `5572_6_Dlgs_Index2_Text`
- `5572_6_Dlgs_Index3_Text`
- `5572_6_Dlgs_Index4_Text`
- `5572_6_Dlgs_Index5_Text`
- `5572_6_Dlgs_Index6_Text`
- `5572_6_Dlgs_Index7_Text`
- `5572_6_Dlgs_Index8_Text`
- `5572_6_Dlgs_Index9_Text`
- `5572_6_Dlgs_Index10_Text`
- `5572_6_Dlgs_Index11_Text`

この段階ではowner内容を変更しない。

## quality auditへ渡す確認軸

- 欧陽雪の負傷確認が二人への切迫した呼びかけとして自然か
- 瑶姫の軽い伸ばしと事件直後の緊張が、人物声を失わず同居しているか
- `借刀杀人`の推測を天龍幇の確定した計画へ強めていないか
- 怪人の功力と素性について、話者の見立てと未確認情報を確定していないか
- 莫問の江湖経験と次行動の提示が事務説明へ平坦化していないか
- 宇文逸の衣冠塚への決断が、叔父への弔いと黎城行きの優先を自然に結んでいるか

## 未確定ゲート

ALLUSION_REVIEW候補:

- `借刀杀人`: 一般成句として自然に機能している可能性が高いが、典故処理が必要かはquality auditで判定する。

FACT_DOUBT候補:

- 仮面の怪人の正体・所属・目的を確定しない
- 風雲訣が実際に曹煜天の手にあるかを客観的事実へ確定しない
- 天龍幇が怪人を利用したという推測を確定しない
- 怪人の功力が義父と同等以上かを瑶姫の見立て以上に強めない
- 莫問が怪人を知らないことを江湖全体で未知という意味へ広げない
- 衣冠塚から叔父の遺体・死の経緯・葬送状況を補わない

## この段階で行っていないこと

fix / keep判断、修正JSON、owner変更、正式な束完了、件数による品質判断、locres書き戻し、pak再生成は行っていない。
