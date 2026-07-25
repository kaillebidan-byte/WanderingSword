# 宇文逸↔莫問 `5551_2` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-06`
- translation judgment: 未実施
- source: Relation audit extraction run `30149789606`
- artifact: `relation-audit-evidence` / `yuwen_mowen.json`
- artifact id: `8617244568`
- artifact digest: `sha256:48ac3451477c3d865bad8b8e04e4c2526a81ad26df2f40a4517f3bccdfbd9827`
- artifact head: `a568f731dcf419c766dc6a3845461aed1f83d46a`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5551_2_2026-07-25.json`

## 場面境界

直前の`5540_4`で宇文逸は黎城へ向かう前に故郷の遼城へ戻る意向を示し、莫問・欧陽雪・瑶姫が同行することになった。

対象`5551_2`は遼城到着時の会話である。宇文逸は叔父との再会を無邪気に期待し、叔父に育てられたこと、心中では父親と思っていることを同行者へ語る。莫問は「父親」という語へ間を置き、真心から接してくれる人に出会えた幸運を自分たち双方へ広げる。宇文逸は叔父の人柄と家の場所を話し、一行を城内へ急がせる。

後続`5572_6`では遼城での事件後の会話へ移る。叔父の実際の状況や事件結果は対象場面へ先取りしない。

`5551_2_Dlgs`自体に重複locationはない。

## 話者順

宇文逸 → 宇文逸 → 欧陽雪 → 宇文逸 → 宇文逸 → 莫問 → 莫問 → 宇文逸 → 宇文逸 → 宇文逸 → 宇文逸

## 所有境界

全11キーの既存ownerは`_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch9.json`。

- `5551_2_Dlgs_Index0_Text`
- `5551_2_Dlgs_Index1_Text`
- `5551_2_Dlgs_Index2_Text`
- `5551_2_Dlgs_Index3_Text`
- `5551_2_Dlgs_Index4_Text`
- `5551_2_Dlgs_Index5_Text`
- `5551_2_Dlgs_Index6_Text`
- `5551_2_Dlgs_Index7_Text`
- `5551_2_Dlgs_Index8_Text`
- `5551_2_Dlgs_Index9_Text`
- `5551_2_Dlgs_Index10_Text`

この段階ではowner内容を変更しない。

## quality auditへ渡す確認軸

- 宇文逸の再会への高揚と、叔父を父親と思う私的な告白が同じ説明調へ均されていないか
- `咳`が照れ隠し・言い直しとして働く流れを、日本語の不自然な咳払いへ固定していないか
- 莫問の`父親、か……`から`我们都很幸运`へ続く間に、原文以上の過去や対象を補っていないか
- 欧陽雪の相槌が宇文逸との親密さを弱めるほど他人行儀になっていないか
- 宇文逸の叔父自慢と城へ急ぐ勢いが、重い身の上説明だけに沈んでいないか

## 未確定ゲート

ALLUSION_REVIEW候補は現時点でない。

FACT_DOUBT候補:

- 叔父が実際に喜ぶか、現在どのような状態かを確定しない
- 宇文逸の両親の死因・時期・経緯を補わない
- 莫問の`如此诚心以待之人`が具体的に誰を指すかを、この場面だけで単一人物へ固定しない
- 莫問の父親観・過去・師父との関係を台詞以上に説明しない
- 叔父が友人へ料理した回数や具体的な料理を補わない

## この段階で行っていないこと

fix / keep判断、修正JSON、owner変更、正式な束完了、件数による品質判断、locres書き戻し、pak再生成は行っていない。
