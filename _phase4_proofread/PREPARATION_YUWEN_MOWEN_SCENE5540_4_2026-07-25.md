# 宇文逸↔莫問 `5540_4` private preparation

- stage: `private_preparation`
- train: `yuwen-mowen-train-06`
- translation judgment: 未実施
- source: Relation audit extraction run `30149789606`
- artifact: `relation-audit-evidence` / `yuwen_mowen.json`
- artifact id: `8617244568`
- artifact digest: `sha256:48ac3451477c3d865bad8b8e04e4c2526a81ad26df2f40a4517f3bccdfbd9827`
- artifact head: `a568f731dcf419c766dc6a3845461aed1f83d46a`
- candidate packet: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENE5540_4_2026-07-25.json`

## 場面境界

直前は`5536_3` / `5536_4`。武当へ戻らず、半月後に黎城へ集まるよう師父から知らせが届く分岐場面である。

対象`5540_4`では、瑶姫が一行へ合流し、宇文逸が黎城へ向かう前に遼城へ戻る意向を示す。莫問と欧陽雪が同行を申し出る。瑶姫は遼城の状況へ言及しかけるが、説明せずに出発する。

後続`5551_2`では遼城到着後、宇文逸が叔父との関係を語る。さらに後の`5572_6` / `5572_9`は遼城での事件後に位置する。これらの後続事実を対象場面へ先取りしない。

`5540_4_Dlgs`自体に重複locationはない。直前の`5536_3` / `5536_4`は分岐familyとして文脈だけを参照する。

## 話者順

瑶姫 → 瑶姫 → 宇文逸 → 宇文逸 → 宇文逸 → 宇文逸 → 莫問 → 莫問 → 欧陽雪 → 瑶姫 → 宇文逸 → 瑶姫 → 宇文逸

## 所有境界

既存ownerは`_phase4_proofread/fixes_relation_yuwen_mowen_20260723_batch8.json`。

既存ownerに含まれるキー:

- `5540_4_Dlgs_Index0_Text`
- `5540_4_Dlgs_Index1_Text`
- `5540_4_Dlgs_Index3_Text`
- `5540_4_Dlgs_Index4_Text`
- `5540_4_Dlgs_Index5_Text`
- `5540_4_Dlgs_Index6_Text`
- `5540_4_Dlgs_Index7_Text`
- `5540_4_Dlgs_Index8_Text`
- `5540_4_Dlgs_Index9_Text`
- `5540_4_Dlgs_Index12_Text`

未所有として確認したキー:

- `5540_4_Dlgs_Index2_Text`
- `5540_4_Dlgs_Index10_Text`
- `5540_4_Dlgs_Index13_Text`

未所有キーのownerはこの段階では決めない。quality auditで修正判断が確定した場合だけ、encoding段階で所有を決める。

## quality auditへ渡す確認軸

- 瑶姫の軽い笑いと、遼城への含みを同じ平板な調子へ潰していないか
- 宇文逸の叔父への心配を、本人の推測を越えた客観事実へ強めていないか
- 宇文逸の先行提案が莫問に遮られる流れを、説明追加で変えていないか
- 莫問の保護責任を、支配・監視・父親的な調子へ強めていないか
- 欧陽雪の同行意思を、弱い追従へ落としていないか

## 未確定ゲート

ALLUSION_REVIEW候補は現時点でない。

FACT_DOUBT候補:

- 宇文逸と瑶姫が知らせを受け取った経緯を補わない
- 叔父が実際にどの程度心配しているかを確定しない
- 師父の指示を護衛命令・監視命令へ拡張しない
- 半月の期限と移動可能性を保証へ強めない
- 瑶姫が知る遼城の状況をこの場面で先取りしない

## この段階で行っていないこと

fix / keep判断、修正JSON、owner新設、正式な束完了、件数集計、locres書き戻し、pak再生成は行っていない。
