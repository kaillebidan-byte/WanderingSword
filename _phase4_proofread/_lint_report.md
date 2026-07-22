# 横断リント報告 (2026-06-11)

## 自動修正済み(本日)
- (不翻译)マーカー除去: 296件+8件(Buff与道具/Skills) ※8件は簡体字込みの内部アイテム名を個別修正
- 簡体字字形→日本語字形(龙→龍, 经→経, 丰→豊 等70字マップ): 157件相当(dedup込み)。「叶」は後続ひらがなで除外
- 猿林→猴児林: 12件 / 公務員→役人・官憲: 3件 / 中華句読点(，；→、): 14件

## 未修正(校正フェーズで対応)
- 生『余』一人称: 14件(キャラ別一人称への置換が必要)
- 中華語彙: 姑娘577件・公子536件・兄台90件・在下2件・高強3件(意図的保持か要判断。glossary方針: 在下→この身/兄台→貴殿/高強→見事)
- 色タグ非平衡: 374件(下記、表示崩れの可能性。優先確認)

  - Quests任务表 Quests/9051_RequestDlgs_Index1_Text open=0 close=1 | 1 - 宇文逸 $@$（今すぐ真武殿首座への昇進任務を完了する必要がありますか？）<qnames_r
  - Quests任务表 Quests/17222_RequestDlgs_Index0_Text open=0 close=1 | 17001 - 船頭 $@$お客様は名剣山荘へ行かれますか？すぐに出航します。<qnames_r i
  - Quests任务表 Quests/12812_RequestDlgs_Index0_Text open=1 close=2 | 2 - 傍白 $@$この先、重要なストーリーが始まります。このストーリーは途中で放棄できず、任務中は
  - Quests任务表 Quests/21501_RequestDlgs_Index0_Text open=1 close=2 | 2 - 傍白 $@$重要なストーリーが始まります。<R>この後、一部の仲間は離脱・加入ができなくなり
  - Quests任务表 Quests/6245_RequestDlgs_Index0_Text open=0 close=1 | 2 - 傍白 $@$重要なストーリーが始まります。少侠、準備をしてください。<qnames_r id
  - Quests任务表 Quests/6241_RequestDlgs_Index0_Text open=0 close=1 | 2 - 傍白 $@$重要なストーリーが始まります。少侠、準備をしてください。<qnames_r id
  - Quests任务表 Quests/6243_RequestDlgs_Index0_Text open=0 close=1 | 2 - 傍白 $@$重要なストーリーが始まります。少侠、準備をしてください。<qnames_r id
  - Quests任务表 Quests/6247_RequestDlgs_Index0_Text open=0 close=1 | 2 - 傍白 $@$重要なストーリーが始まります。少侠、準備をしてください。<qnames_r id
  - Quests任务表 Quests/6291_RequestDlgs_Index0_Text open=0 close=1 | 2 - 傍白 $@$重要なストーリーが始まります。少侠、準備をしてください。<qnames_r id
  - Quests任务表 Quests/5745_RequestDlgs_Index0_Text open=1 close=2 | 5011 - 道通 $@$……今回は五割の力で挑む。もし勝てば<Y>伝功弟子</>に昇格できるぞ！<
  - Quests任务表 Quests/5320_RequestDlgs_Index0_Text open=1 close=2 | 5011 - 道通 $@$……やはりいつもの通りだ。今回は三割の力しか出さない。私に勝てば<Y>エリ
  - Quests任务表 Quests/6266_RequestDlgs_Index1_Text open=1 close=2 | 5011 - 道通 $@$私に<Y>勝てば</>、この真武殿首座の座は、小逸、お前のものだ！<qna
  - Quests任务表 Quests/5314_RequestDlgs_Index2_Text open=0 close=1 | 5011 - 道通 $@$ふふ、難しくはない……私は一割の力しか出さない。もしお前が私の一手でも勝て
  - Quests任务表 Quests/5752_RequestDlgs_Index1_Text open=0 close=1 | 5011 - 道通 $@$五割の力で挑む。もし勝てば試練を突破し、伝功弟子となれるだろう！<qnam
  - Quests任务表 Quests/5859_RequestDlgs_Index1_Text open=0 close=1 | 5011 - 道通 $@$八割の力で挑む。もし勝てば、試練を突破し、執法弟子になれるぞ！<qname
  - Quests任务表 Quests/5325_RequestDlgs_Index1_Text open=0 close=1 | 5011 - 道通 $@$私は一割の力しか出さない。もしお前が勝てば、試練を乗り越え、ベテラン弟子に
  - Quests任务表 Quests/5327_RequestDlgs_Index1_Text open=0 close=1 | 5011 - 道通 $@$私は三割の力しか出さない。もしお前が勝てば、試練を乗り越え、エリート弟子に
  - Quests任务表 Quests/6261_RequestDlgs_Index0_Text open=1 close=2 | 5011 - 道通 $@$さあ来い、この間の進歩をじっくり見せてもらおうか！私に<Y>勝てば</>、
  - Quests任务表 Quests/5855_RequestDlgs_Index0_Text open=1 close=2 | 5011 - 道通 $@$では、いつもの通りだ…今回は八割の力で、私に勝てば<Y>執法弟子</>に昇
  - Skills技能表 Skills/480_CastEffectDesc open=1 close=2 | <B>使用後、対象に青雲印記効果を1層付与し、5ターン持続する。</>-6%、命中を-5%減少させ、
  - Skills技能表 Skills/751_SpecialEffectDesc open=1 close=4 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/724_SpecialEffectDesc open=1 close=4 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/704_SpecialEffectDesc open=1 close=4 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/701_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/752_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/722_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/706_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/702_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/723_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/720_SpecialEffectDesc open=1 close=2 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/753_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/707_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/711_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/709_SpecialEffectDesc open=1 close=2 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/705_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/703_SpecialEffectDesc open=1 close=2 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/700_SpecialEffectDesc open=1 close=2 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/721_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後の次ターン集気値+5%（10レベルで+50%）。</>


  - Skills技能表 Skills/710_SpecialEffectDesc open=1 close=3 | <B>レベルごとの効果-この軽功使用後、次ターンの集気値+5%（10級で+50%）。</>

<
  - Skills技能表 Skills/857_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="3">レベル3効果-四海承風：力道、根骨、身
  - Skills技能表 Skills/852_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="3">レベル3効果-四海承風：この心法を装備
  - Skills技能表 Skills/854_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="3">レベル3効果-四海承風：この心法を装備
  - Skills技能表 Skills/855_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="3">レベル3効果-四海承風：この心法を装備
  - Skills技能表 Skills/856_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="3">レベル3効果-四海承風：この心法を装備
  - Skills技能表 Skills/136_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4-太上虚無：この技の攻撃ごとに
  - Skills技能表 Skills/130_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4-翻雲覆雨：この技を使用すると
  - Skills技能表 Skills/430_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4-翻雲覆雨：この招式使用時、2
  - Skills技能表 Skills/364_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-一式：この招式が1回攻撃
  - Skills技能表 Skills/472_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-万事東流：この技使用時、
  - Skills技能表 Skills/835_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="4">レベル4効果-万象春生：自身の真気が7
  - Skills技能表 Skills/893_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-不争須臾：戦場に入ると自身は
  - Skills技能表 Skills/837_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-雲随風動：太極効果の累積
  - Skills技能表 Skills/882_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-雲龍太極：戦場に入ると自身に
  - Skills技能表 Skills/906_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-五岳定：自身がこのターンに移
  - Skills技能表 Skills/836_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-五霊奇毒：すべての敵ユニ
  - Skills技能表 Skills/403_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-借力打力：太極拳使用時、目標
  - Skills技能表 Skills/442_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-借力打力：太極拳を使用する際
  - Skills技能表 Skills/444_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-借力打力：自身が太極拳を装備
  - Skills技能表 Skills/558_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-八荒殺：流血中の対象に攻
  - Skills技能表 Skills/265_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-八面玲瓏：命中した目標ご
  - Skills技能表 Skills/579_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-凶星入魔：この招式を使用後、
  - Skills技能表 Skills/884_SpecialEffectDesc open=0 close=5 | <skill_flags sufficient_lv="4">4級効果-剣随意動：毎ターン50%の確
  - Skills技能表 Skills/573_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-匹夫一怒：江湖血器効果を
  - Skills技能表 Skills/409_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-千葉如来：この技を使用後、自
  - Skills技能表 Skills/303_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-大日如来：この招式を使用
  - Skills技能表 Skills/879_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-大音希声：目標が絶弦無音効果
  - Skills技能表 Skills/885_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-天地恒常：五恒天経効果期間中
  - Skills技能表 Skills/105_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4レベル効果-太極化勢：太極剣法を使用
  - Skills技能表 Skills/115_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-太極化勢：太極剣法を使用
  - Skills技能表 Skills/137_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-太極化勢：自身が太極剣法
  - Skills技能表 Skills/211_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-娑婆刀：この招式で灼焼効
  - Skills技能表 Skills/905_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-幽濁悪水：毎ターン35%の確
  - Skills技能表 Skills/509_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-弾指神通：毎ターン自身に
  - Skills技能表 Skills/887_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-所見即得：天魔六通効果下で攻
  - Skills技能表 Skills/232_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-放下屠刀：断業効果1層ごとに
  - Skills技能表 Skills/838_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-明鏡菩提：この心法使用後
  - Skills技能表 Skills/807_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-易筋固元：この心法使用後
  - Skills技能表 Skills/368_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-梨花帯雨：毎ターン50%の確
  - Skills技能表 Skills/314_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-棍打双犬：丐帮の全ての棍
  - Skills技能表 Skills/468_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-欲天六重：この技使用後、
  - Skills技能表 Skills/441_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-河漢冱：攻撃を受けた際、目標
  - Skills技能表 Skills/425_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-炎陽似火：この招式が対象
  - Skills技能表 Skills/813_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-玄陽勁：自身は寒霜効果を
  - Skills技能表 Skills/891_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-玉龍化変：自身に玉龍決効果が
  - Skills技能表 Skills/305_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-瘋魔：入魔効果が10層に
  - Skills技能表 Skills/892_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-皓虎顛狂：毎ターン自身に1層
  - Skills技能表 Skills/903_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="4">4級効果-石中求実：ターン終了時、気血
  - Skills技能表 Skills/839_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-納天光：毎ターン50%の
  - Skills技能表 Skills/883_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-芳菲謝尽：芳菲効果の対象を攻
  - Skills技能表 Skills/420_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-躍龍在淵：この招式使用後
  - Skills技能表 Skills/315_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-陰差陽錯：</>


  - Skills技能表 Skills/215_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-飲血刀：悪人谷の全ての刀
  - Skills技能表 Skills/817_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4級効果-鬼蛛赤蛇：毎ターン50%の確
  - Skills技能表 Skills/421_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">レベル4効果-龍戦于野：この招式の攻撃
  - Skills技能表 Skills/7_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="4">4レベル効果-龍戦于野：この招式の攻撃
  - Skills技能表 Skills/201_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級 パッシブ効果-八卦：この招式のク
  - Skills技能表 Skills/153_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5 パッシブ効果-松風穿林：この
  - Skills技能表 Skills/407_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級 被動効果-金剛不壊：この技を使用
  - Skills技能表 Skills/455_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5-氷封三尺：この技を使用する際
  - Skills技能表 Skills/465_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5-化骨為泥：この技は目標の防御
  - Skills技能表 Skills/128_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5-混元護体：この技使用後、自身
  - Skills技能表 Skills/428_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5-混元護体：この招式使用後、自
  - Skills技能表 Skills/512_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5-パッシブ効果-天羅勢：本招式
  - Skills技能表 Skills/507_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級-パッシブ効果-奪命穿心：今回の招
  - Skills技能表 Skills/555_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5-パッシブ効果-如影随行：本招
  - Skills技能表 Skills/302_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-慈航：この招式を使用する
  - Skills技能表 Skills/261_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-一点霊犀：このスキルを所持し
  - Skills技能表 Skills/553_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-一箭双雕：命中した対象1
  - Skills技能表 Skills/466_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-七輪流転：この技で攻撃後
  - Skills技能表 Skills/804_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-万法帰一：毎ターン終了時
  - Skills技能表 Skills/163_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-三仙望月：戦闘開始時、自
  - Skills技能表 Skills/216_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-三才刀法：この招式使用時
  - Skills技能表 Skills/253_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-三環相扣：この技の破防一撃の
  - Skills技能表 Skills/439_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-三絶毒：この招式使用後、自身
  - Skills技能表 Skills/886_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-三脈七輪：1～3式の技を使用
  - Skills技能表 Skills/304_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-不動明王：この招式を使用
  - Skills技能表 Skills/818_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-丐帮心法：丐帮の全ての技のダ
  - Skills技能表 Skills/310_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-丐帮棍法：丐帮の全ての棍
  - Skills技能表 Skills/101_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5レベル効果-両儀連華：この招式を使用
  - Skills技能表 Skills/437_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-九曲：この招式使用後、現在の
  - Skills技能表 Skills/110_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-雲淡風軽：この技を使用す
  - Skills技能表 Skills/469_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-雲煙海霧：対象が青雲印記
  - Skills技能表 Skills/111_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-五仙剣法：この技で攻撃す
  - Skills技能表 Skills/814_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-五仙秘術：五仙教のいかなる技
  - Skills技能表 Skills/500_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-五仙銀針：この招式で攻撃する
  - Skills技能表 Skills/801_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5レベル効果-五気朝元：帰元心法を使用
  - Skills技能表 Skills/502_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-五羅青煙：術の範囲の中心にい
  - Skills技能表 Skills/254_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-五虎断門：この技を使用した後
  - Skills技能表 Skills/412_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-仙人指路：友方目標の真気+2
  - Skills技能表 Skills/117_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-伏虎剣法：この技の命中+
  - Skills技能表 Skills/119_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-仏光普照：この技のダメー
  - Skills技能表 Skills/853_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-この心法を使用すると、4
  - Skills技能表 Skills/501_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-この招式使用時、50%の確率
  - Skills技能表 Skills/503_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-この招式使用時、自身が幻蠱効
  - Skills技能表 Skills/205_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-修羅：この武学使用時、目
  - Skills技能表 Skills/812_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-光明心法：戦闘開始時、自
  - Skills技能表 Skills/402_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-八卦：この武学の会心+30%
  - Skills技能表 Skills/166_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-八風乃朝：自身と範囲内の
  - Skills技能表 Skills/827_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-六扇心法：六扇門の全ての技の
  - Skills技能表 Skills/834_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-冥蠱噬魂：攻撃を受けた際
  - Skills技能表 Skills/413_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-凝血神爪：この技で攻撃する際
  - Skills技能表 Skills/210_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-刀山勢：この招式で灼焼効
  - Skills技能表 Skills/156_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-剣光寒：この技を使用した
  - Skills技能表 Skills/103_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5レベル効果-剣気如虹：真武剣気のダメ
  - Skills技能表 Skills/888_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-剣気訣：戦場に入ると自身に3
  - Skills技能表 Skills/308_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-剔骨：本技は目標に1層の
  - Skills技能表 Skills/458_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-劈荊斬棘：この技で2回連
  - Skills技能表 Skills/898_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-動如脱兔：戦闘開始後、自身に
  - Skills技能表 Skills/896_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-勁随意動：気血が70%より大
  - Skills技能表 Skills/831_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-化法功：悪人谷のいかなる技で
  - Skills技能表 Skills/874_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-千蛇化気：中毒目標を攻撃する
  - Skills技能表 Skills/169_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-卓詭変幻：軽功を使用する
  - Skills技能表 Skills/118_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-衛道：この技がクールダウ
  - Skills技能表 Skills/183_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果 - 去年花開：この技を使
  - Skills技能表 Skills/366_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-変陣：パリィ成功後、自身
  - Skills技能表 Skills/309_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-葉落帰根：自身の気血が5
  - Skills技能表 Skills/267_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-合陣：攻撃後、対象に1層
  - Skills技能表 Skills/106_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5レベル効果-名剣剣法：この招式を使用
  - Skills技能表 Skills/808_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-名剣心法：戦闘開始時、自
  - Skills技能表 Skills/506_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-嗜血寒蝠：この招式で攻撃する
  - Skills技能表 Skills/871_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-四関：目標が摧鋒、縛身、卸勁
  - Skills技能表 Skills/371_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-四夷賓服：ターン中に自身が移
  - Skills技能表 Skills/479_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-四極崩裂：この技は対象に
  - Skills技能表 Skills/477_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-回天扇法：この技で攻撃後
  - Skills技能表 Skills/225_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-天人五衰：この技を使用する際
  - Skills技能表 Skills/133_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-天元列宿：自身の気血と真
  - Skills技能表 Skills/508_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-天女散花：この招式使用時、対
  - Skills技能表 Skills/127_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-天山剣法：天山派の全ての
  - Skills技能表 Skills/427_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-天山掌法：天山派の全ての
  - Skills技能表 Skills/260_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-天罡護体：この技を使用した後
  - Skills技能表 Skills/107_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5レベル効果-天羽勢：この招式を使用し
  - Skills技能表 Skills/816_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-天蚕繭：戦場に入ると自身に天
  - Skills技能表 Skills/861_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-天龍無双：双龍斬のダメー
  - Skills技能表 Skills/840_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-太極円転：戦闘開始時、自
  - Skills技能表 Skills/802_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-太極神功：戦闘開始時、自
  - Skills技能表 Skills/416_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-太祖長拳：この技を使用後、自
  - Skills技能表 Skills/362_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-守而待時：この招式で目標
  - Skills技能表 Skills/471_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-寓虚于実：自身が蔵実于虚
  - Skills技能表 Skills/223_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-小五衰：この技を使用する際、
  - Skills技能表 Skills/204_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-少林刀法：全ての少林寺刀
  - Skills技能表 Skills/806_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-少林寺の全ての技のダメー
  - Skills技能表 Skills/300_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-少林棍法：全ての少林寺槍
  - Skills技能表 Skills/453_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-山峰連綿：この技の連撃確
  - Skills技能表 Skills/165_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-岐黄薬理：「回春」効果期
  - Skills技能表 Skills/815_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-幻蠱心経：戦場に入ると自身に
  - Skills技能表 Skills/904_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-幽濁悪水：毎ターン35%の確
  - Skills技能表 Skills/114_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-引蛇出洞：自身に幻蠱効果
  - Skills技能表 Skills/357_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-弥山棍法：この招式が目標
  - Skills技能表 Skills/202_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-帰元：この招式を使用すると自
  - Skills技能表 Skills/112_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-彩雲剣法：目標を1つ命中
  - Skills技能表 Skills/361_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-御敵式：周囲12マスに敵
  - Skills技能表 Skills/880_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-心如止水：白帝剣心効果中、自
  - Skills技能表 Skills/578_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-心宿巨星：この招式を使用する
  - Skills技能表 Skills/889_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-急如鷹飛：毎ターン終了時、自
  - Skills技能表 Skills/212_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-悪鬼刀法：全ての悪人谷刀
  - Skills技能表 Skills/830_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-悪鬼心法：悪人谷の全ての技の
  - Skills技能表 Skills/306_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-悪鬼棍法：悪人谷の全ての
  - Skills技能表 Skills/571_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-意気動：この技を使用した
  - Skills技能表 Skills/206_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-慈怜：この招式は会心が発
  - Skills技能表 Skills/231_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-慈悲無量：この技がクールダウ
  - Skills技能表 Skills/365_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-戍陣：攻撃を受けた際、攻
  - Skills技能表 Skills/433_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-截脈手：この招式の会心率
  - Skills技能表 Skills/116_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-全ての少林寺剣法招式ダメ
  - Skills技能表 Skills/100_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5レベル効果-全ての武当派剣法招式のダ
  - Skills技能表 Skills/219_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-披星趕月：この技を使用した後
  - Skills技能表 Skills/373_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-抜山扛鼎：自身の気血上限が1
  - Skills技能表 Skills/170_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果 - 掠影浮光：この技で目
  - Skills技能表 Skills/134_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-揺光為始：天機宮の剣法招
  - Skills技能表 Skills/464_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-摔碑手：この技のダメージ
  - Skills技能表 Skills/374_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-撼地：この技が1つの目標に命
  - Skills技能表 Skills/372_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-擂鼓：力道が10点ごとにこの
  - Skills技能表 Skills/363_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-擎天式：反射シールド効果
  - Skills技能表 Skills/482_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-擒拿鎖扣：この招式で攻撃する
  - Skills技能表 Skills/408_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-断筋：この技を使用すると目標
  - Skills技能表 Skills/873_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-無形罡気：無形罡気効果により
  - Skills技能表 Skills/552_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-無影飛箭：本招式使用後、
  - Skills技能表 Skills/870_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-無我無相：戦場に入ると自身に
  - Skills技能表 Skills/224_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-無極而生：調息後、自身がこの
  - Skills技能表 Skills/803_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-無極：この心法使用時、自
  - Skills技能表 Skills/157_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-無辺落木：自身の真気が8
  - Skills技能表 Skills/866_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-日升月恒：この心法を使用
  - Skills技能表 Skills/423_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-日月輪手：この招式使用後
  - Skills技能表 Skills/230_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-明鏡仏心：この技を使用する際
  - Skills技能表 Skills/513_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-昏天地暗：本招式攻撃時に
  - Skills技能表 Skills/132_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-星光乍現：この技を使用し
  - Skills技能表 Skills/424_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-星火燎原：攻撃時、50%
  - Skills技能表 Skills/434_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-春雷始鳴：次回すべての拳掌招
  - Skills技能表 Skills/159_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-春風化雨：この技の連続攻
  - Skills技能表 Skills/833_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-晦日朔月：この心法使用時
  - Skills技能表 Skills/554_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-暴雨梨花：50%の確率で
  - Skills技能表 Skills/222_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-枯木逢春：長生殿刀法を使用す
  - Skills技能表 Skills/359_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-梨花帯雨：攻撃を受けた際
  - Skills技能表 Skills/860_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-梵我合一：毎ターン自身の
  - Skills技能表 Skills/354_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-武岳槍法：攻撃された後、
  - Skills技能表 Skills/200_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-武当刀法：全ての武当派刀法招
  - Skills技能表 Skills/800_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5レベル効果-武当心法：武当派の全ての
  - Skills技能表 Skills/400_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-武当長拳：すべての武当派拳掌
  - Skills技能表 Skills/832_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-気散星辰：この心法使用後
  - Skills技能表 Skills/251_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-江湖刀法：この技を使用した後
  - Skills技能表 Skills/151_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-江湖剣法：この技を使用し
  - Skills技能表 Skills/851_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-江湖心法：1式の通常攻撃
  - Skills技能表 Skills/451_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-江湖拳掌：この招式使用後、次
  - Skills技能表 Skills/551_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-江湖暗器：本招式使用後、
  - Skills技能表 Skills/351_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-江湖棍法：本技使用後、次
  - Skills技能表 Skills/864_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="5">レベル5効果-沂水舞雩：この心法を使用
  - Skills技能表 Skills/104_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5レベル効果-流雲：この招式を使用する
  - Skills技能表 Skills/158_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-流水潺潺：回避時、自身の
  - Skills技能表 Skills/895_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-渾天奥理：自身の移動1点ごと
  - Skills技能表 Skills/572_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-浩然気：浩然正器効果期間
  - Skills技能表 Skills/410_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-淬血指：この技で流血効果のあ
  - Skills技能表 Skills/810_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-混元神剣：毎ターン自身に
  - Skills技能表 Skills/102_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5レベル効果-清風：この招式を使用した
  - Skills技能表 Skills/188_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果 - 湖月照影：この技を使
  - Skills技能表 Skills/181_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果 - 湖月照影：この技を使
  - Skills技能表 Skills/484_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-湖月照影：この招式使用時、自
  - Skills技能表 Skills/358_SpecialEffectDesc open=0 close=5 | <skill_flags sufficient_lv="5">レベル5効果-火焼連営：この招式が会心
  - Skills技能表 Skills/575_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-火矢如瀑：この技を使用し
  - Skills技能表 Skills/872_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-霊枢：毎ターン自身の内傷効果
  - Skills技能表 Skills/890_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-錬体篇：攻撃を受けた際、自身
  - Skills技能表 Skills/443_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-熾陽成劫：この招式を使用する
  - Skills技能表 Skills/865_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-煙波浩渺：自身の回避率1
  - Skills技能表 Skills/160_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-煙霞剣法：この技は35%
  - Skills技能表 Skills/867_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-烽鼓不息：兵烽六要効果状
  - Skills技能表 Skills/876_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-焚筋煅骨：攻撃を受けた際、双
  - Skills技能表 Skills/877_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-焚筋煅骨：根骨+15、この心
  - Skills技能表 Skills/207_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-燃木：この招式使用時、目
  - Skills技能表 Skills/367_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-独縦横：この技使用後、自身は
  - Skills技能表 Skills/828_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-玄元経：内功+5。気血が50
  - Skills技能表 Skills/208_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-玄火刀法：全ての玄火教刀
  - Skills技能表 Skills/811_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-玄火心法：玄火教のいずれ
  - Skills技能表 Skills/422_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-玄火掌法：全ての玄火教拳
  - Skills技能表 Skills/203_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-玄虚刀勢：戦場に入ると自身に
  - Skills技能表 Skills/135_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-玄陽破：全ての剣法招式で
  - Skills技能表 Skills/483_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="5">5級効果-琢玉刀：二式使用後、自身に琢
  - Skills技能表 Skills/213_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-疾風驟雨：この招式は50
  - Skills技能表 Skills/432_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-瘟疱病気：この招式使用時
  - Skills技能表 Skills/269_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-白帝剣陣：この招式を使用
  - Skills技能表 Skills/268_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-白帝剣陣：この招式を使用
  - Skills技能表 Skills/189_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果 - 白帝剣陣：この技を使
  - Skills技能表 Skills/182_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果 - 白帝剣陣：この技を使
  - Skills技能表 Skills/129_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-白虹剣気：この技使用後、
  - Skills技能表 Skills/429_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-白虹掌力：この招式使用後
  - Skills技能表 Skills/418_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-百絲纏身：この技を使用後、目
  - Skills技能表 Skills/435_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-百毒交侵：長生殿の拳掌招式で
  - Skills技能表 Skills/881_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-百花残：凋零効果が毎ターン対
  - Skills技能表 Skills/907_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-百花残：凋零効果が毎ターン目
  - Skills技能表 Skills/577_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-百針斉発：この招式がクールダ
  - Skills技能表 Skills/461_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-百陽匯生：友軍の気血+1
  - Skills技能表 Skills/902_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-百陽匯生：味方の気血+15%
  - Skills技能表 Skills/355_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-百鳥朝鳳：使用後、自身の
  - Skills技能表 Skills/897_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-直搗黄龍：戦闘開始後、自身に
  - Skills技能表 Skills/313_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-睡臥沙場：本技使用時に自
  - Skills技能表 Skills/820_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-睡生夢死：この心法を使用する
  - Skills技能表 Skills/217_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-破軍刀法：この技を使用する際
  - Skills技能表 Skills/436_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-破穴封気：この招式を使用する
  - Skills技能表 Skills/154_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-碧水雲茫：この技を使用し
  - Skills技能表 Skills/823_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-神鷹心法：神鷹門の全ての技の
  - Skills技能表 Skills/863_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-秋月寒江：いかなる技で攻
  - Skills技能表 Skills/228_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-窮陰：この技を使用した後に目
  - Skills技能表 Skills/440_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-窮陰：この招式使用後、目標に
  - Skills技能表 Skills/369_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-穿雲：この技使用時、会心、命
  - Skills技能表 Skills/113_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-穿針引線：この技を使用す
  - Skills技能表 Skills/894_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-築心宮：自身の気血が1%減少
  - Skills技能表 Skills/574_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-箭如雨下：この技を使用し
  - Skills技能表 Skills/301_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-続気：この招式を使用する
  - Skills技能表 Skills/401_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-綿掌：この技使用時、目標に1
  - Skills技能表 Skills/404_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-羅漢拳：すべての少林寺拳掌技
  - Skills技能表 Skills/829_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-聚気凝神：この心法を使用する
  - Skills技能表 Skills/511_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-腐屍毒：本招式で対象を撃
  - Skills技能表 Skills/214_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-腐肌：この招式は目標に3
  - Skills技能表 Skills/878_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-自若不変：会心、回避が発動し
  - Skills技能表 Skills/218_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-捨身刀：この技を使用した後の
  - Skills技能表 Skills/152_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-蒼松剣法：この技を使用し
  - Skills技能表 Skills/417_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-蓮花掌：全ての丐幇拳掌技のダ
  - Skills技能表 Skills/311_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-蓮花棒法：本技が目標を1
  - Skills技能表 Skills/229_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-菩提禅心：この技が気血回復効
  - Skills技能表 Skills/470_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-蔵実于虚：この技使用後、
  - Skills技能表 Skills/168_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-虺蛇吐信：この技を使用時
  - Skills技能表 Skills/567_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-虺蛇吐信：中毒効果を持つ
  - Skills技能表 Skills/566_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-蚊須毒針：対象が既中毒効
  - Skills技能表 Skills/167_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-蛇形剣：この技を使用後、
  - Skills技能表 Skills/576_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-蝎尾針：この技を使用する
  - Skills技能表 Skills/352_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-蟠龍棍法：本技使用後、目
  - Skills技能表 Skills/353_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-蟠龍繞柱：パリィ確率+1
  - Skills技能表 Skills/565_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-血滴金輪：30%（自身の
  - Skills技能表 Skills/824_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-血転乾坤：この心法を使用する
  - Skills技能表 Skills/505_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-血鷹喙：50%の確率で対象に
  - Skills技能表 Skills/419_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="5">5級効果-見龍在田：この技の会心+25
  - Skills技能表 Skills/819_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-戦場に入ると自身に神龍掌法効
  - Skills技能表 Skills/162_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-遠山剣法：この技が1つの
  - Skills技能表 Skills/452_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-連山掌法：この技を使用す
  - Skills技能表 Skills/257_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-追撃：目標が破甲状態の場合、
  - Skills技能表 Skills/463_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-通背猿猴：戦場に入ると自
  - Skills技能表 Skills/312_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-酔仙望月：自身に霊動効果
  - Skills技能表 Skills/209_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-野火不尽：この招式で灼焼
  - Skills技能表 Skills/406_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-金剛不壊：この技を使用すると
  - Skills技能表 Skills/252_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-金環刀法：この技を使用した後
  - Skills技能表 Skills/161_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-金翅玄鳥：この技を使用後
  - Skills技能表 Skills/805_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-金鐘罩：戦闘開始時、自動
  - Skills技能表 Skills/459_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="5">レベル5効果-銅牆鉄壁：招架確率+15
  - Skills技能表 Skills/375_SpecialEffectDesc open=0 close=4 | <skill_flags sufficient_lv="5">5級効果-錚錚鉄衣：会心攻撃を受けた際
  - Skills技能表 Skills/869_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-鎮三山：戦場に入ると自身の防
  - Skills技能表 Skills/266_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-鎮軍：攻撃後、自身に2層
  - Skills技能表 Skills/481_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-鏡湖映月：この招式使用時、自
  - Skills技能表 Skills/473_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-鏡湖映月：この技使用時、
  - Skills技能表 Skills/307_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-閻王槍法：目標を1体攻撃
  - Skills技能表 Skills/438_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-陽勁：孟春九曲を使用する際、
  - Skills技能表 Skills/227_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-陽勁：朽木刀法を使用する際に
  - Skills技能表 Skills/454_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-陰魂不散：この技を使用す
  - Skills技能表 Skills/460_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-雷霆万鈞：この技を使用す
  - Skills技能表 Skills/155_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-雷霆万鈞：施法範囲の中心
  - Skills技能表 Skills/370_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5級効果-雷霆：この技が会心後、目標に
  - Skills技能表 Skills/226_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-霜風：自身から12マス範囲内
  - Skills技能表 Skills/875_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-霹靂心法：任意の通常攻撃技の
  - Skills技能表 Skills/255_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-霹靂斬：この技の会心ダメージ
  - Skills技能表 Skills/560_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-霹靂雷火：この技の会心率
  - Skills技能表 Skills/899_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-青雲心法：扇法技のダメージ+
  - Skills技能表 Skills/480_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">5級効果-青雲扇法：青雲扇法の招式ダメ
  - Skills技能表 Skills/478_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-青冥欲雨：この技で対象を
  - Skills技能表 Skills/475_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-青玉手：この技で攻撃し、
  - Skills技能表 Skills/474_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">レベル5効果-青玉手：この技で攻撃し、
  - Skills技能表 Skills/405_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-韋陀掌：この技を使用すると、
  - Skills技能表 Skills/570_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-韶光開：この技を使用した
  - Skills技能表 Skills/184_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果 - 風巻残雲：自身に猿舞
  - Skills技能表 Skills/270_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-風巻残雲：自身に猿舞効果
  - Skills技能表 Skills/109_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-飛仙九剣：この技を使用す
  - Skills技能表 Skills/568_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-食于九山：中毒効果を持つ
  - Skills技能表 Skills/510_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">レベル5効果-骸骨釘：悪人谷の全ての暗
  - Skills技能表 Skills/809_SpecialEffectDesc open=0 close=2 | <skill_flags sufficient_lv="5">レベル5効果-鯨息浪静：この心法使用後
  - Skills技能表 Skills/411_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-鷹爪功：この技の命中+50%
  - Skills技能表 Skills/259_SpecialEffectDesc open=0 close=1 | <skill_flags sufficient_lv="5">5級効果-黄龍入海：戦場に入った後、自
  - Skills技能表 Skills/108_SpecialEffectDesc open=0 close=3 | <skill_flags sufficient_lv="5">5レベル効果-龍泣：この招式を使用する
  - 系统 /AD28CB424CEFBAF49C56FA9315D43842 open=0 close=1 | あなたはすでに<red>{0}</>を習得しています。ふざけないでください。
  - 门派地图与提示 FullscreenScrollTexts/END_Text open=0 close=1 | <Big2>- 終 -</>
- 色タグ脱落(色装飾が原文より少ない・実害小): 29件