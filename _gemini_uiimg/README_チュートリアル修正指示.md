# チュートリアル画像 修正指示（第2ラウンド）

前回（第1ラウンド）で 43枚のキャプションを日本語化してもらった。感謝。実機確認で3点の改善要望が出たので、**全43枚を作り直してほしい**（同じ `tutorial_src/`＝英語版・`tutorial_src_簡体字/`＝簡体字版を素材に使用）。

## 変更点（前回からの差分・すべて必須）

### ① 全文を日本語化（キャプションだけでなく画面内パネルも）
- 前回はキャプション（灰色帯の説明文）のみ訳した。今回は**画像内の全テキストを日本語に**する。
- **英語版 `tutorial_src/` が完全な翻訳ソース**：キャプションも、スクショ枠内のUI（スキルバー名・スキル詳細パネル・"Attack Range/Skill Info/Weapon Mastery" 等）も**すべて英語で入っている**。これを全部日本語へ。
- 例（`shuoming20_wuxueshuoming`）: "Basic Palm Technique / Lv.5 / Attack Range / Attack:51 / Skill Info / Use Effects / Special Attributes / Learning or upgrading any move grants Weapon Mastery points…" も日本語に。
- 密なパネル文字も、英語が収まっているので日本語なら十分収まる（日本語の方が短い）。

### ② キャプションは「白文字＋黒縁（約2px）」
- 実ゲームのチュートリアル背景は**灰色**。前回の**灰色文字は埋もれて読めない**。
- キャプション（説明文）は必ず **白 (#FFFFFF) ＋ 黒アウトライン約2px**。灰色地でもくっきり読めること。
- パネル内の文字は元のスタイル（白/色付き）に準じてよいが、灰色地に出る説明文は白＋黒縁。

### ③ 文字被り厳禁（レイアウト調整）
- 前回 `shuoming10_diaoyushuoming` の中央下キャプションが長すぎて右の文と衝突した。
- **各キャプションは自分の列幅内に収める**。はみ出す場合は**簡潔に要約**（意味が通れば短縮可）。隣と重ならないこと。
- 例の短縮: 「左側で魚池のレベルと産出される魚の種類、および対応する確率を確認できます」→「左の魚池でレベル・出現魚・確率を確認できます」。

## 不変（前回同様・厳守）
- パネル枠・アイコン・武器/スキルのサムネ画像・黄色いハイライト枠・背景テクスチャ・ボタングリフ（A/B/LB/RB・十字キー）は**一切変更しない**。位置も維持。
- **出力は元と完全同寸・透過PNG(RGBA)**。リサイズ/トリミング禁止。
- `gamepad__*` はゲームパッド版（内容同じ、画面内の LB/RB 等の表記は変えない）。

## 用語集（本文既訳＝locresと統一）
| 英/中 | 日本語 |
|---|---|
| Normal/Special/Mighty/Unique Move, Lightness Skill, Cultivation Method（普攻/二式/三式/絶式/軽功/心法） | 通常攻撃／二式／三式／絶式／軽功／心法 |
| Martial Arts / Martial Art interface（武学） | 武学 |
| Martial Arts Deployment（招式配置） | 招式配置 |
| Learned Martial Arts | 習得済み武学 |
| Weapon Mastery（武器熟练） | 武器熟練度 |
| Attack Range（攻击范围） | 攻撃範囲 |
| Skill Info / Skill Description（技能描述） | スキル説明 |
| Use Effects（使用效果） | 使用効果 |
| Special Attributes（特殊效果） | 特殊効果 |
| Attack / MP Cost / Cooldown（攻击力/消耗真气/等待回合） | 攻撃力／真気消費／待機ターン |
| Blueprint（图纸） | 設計図 |
| Sword/Saber/Polearm/Fist/Hidden Weapon/Others（剑/刀/棍/拳/暗器/其它） | 剣／刀／棍／拳／暗器／その他 |
| Forging Level / Required Level | 鍛造レベル／必要レベル |
| EXP / deploy / undeploy | 経験値／装填／解除 |
| Basic Palm Technique（基础拳掌） | 基礎拳掌 |
| Side/Back Attack Grid Range | 側面／背面攻撃の範囲 |

※ 迷ったら英語版の意味を優先しつつ自然な日本語。武侠用語（心法/軽功/真気/招式 等）は上記で固定。

## 返却
- **`返却/` に元と同じフラット名で保存**（例 `shuoming20_wuxueshuoming.png`, `gamepad__gamepad_shuoming06.png`）。元と同寸・透過RGBA。
- そろったら開発側で `import_ja_png.py` により注入・pak・deploy。
- （キャプションの白＋黒縁は開発側に後処理ツール `enhance_caption.py` もあるが、**最初から白＋黒縁で作ってほしい**。仕上がりの一貫性のため。）

## 対象
`tutorial_src/` にある全PNG（本命は 1386×789 の解説ページ 41枚。gamepad版含む）。前回作った43枚すべて対象。
