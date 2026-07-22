# チュートリアル画像 日本語化 — 委託指示書

生成 2026-07-02。ゲーム内「新手教程（チュートリアル）」詳細ページの画像を日本語化する。
※操作バー/ボタン画像(`src/`)とは別件。こちらは **1386×789 の解説ページ画像**が主対象。

## 対象と素材
- **`tutorial_src/`** … 英語版PNG。**意味の参照（全文が英語で読める）**。キャプションも画面内UIも英語。
- **`tutorial_src_簡体字/`** … 簡体字版PNG（同名）。**レイアウト/文字サイズの参照**（日本語も漢字なので配置はこれが最適な手本）。
- 各ページ 1386×789（一部異寸あり=manifest的に元寸厳守）。透過RGBA。

## 何を訳すか
各ページは「**スクショ枠パネル** ＋ その下の **白文字キャプション**（透過背景＝ゲーム内では灰色地に見える）」で構成。
1. **最優先: キャプション文**（例 英 "Select the type of the weapon to be forged" → 「鍛造する武器の種類を選択」）。
2. **できれば: パネル内の画面文字**（Blueprint/Sword/Forging Level 0 等）も日本語に。英語版に全部あるので訳せる。フル日本語になり公開水準が上がる。
   - 難しければキャプションだけでも可（ユーザー方針: 灰色帯のキャプションが訳せていれば公開に耐える）。

## 作り方（前回のバー翻訳と同方式）
- **簡体字版を土台**にし、中文テキストのみ消去→日本語をフォント描画（前回同様: 通常文字=Noto Sans CJK JP Bold＋黒縁、見出しの毛筆調は Yuji Boku 等）。**英語版で意味を取る**。
- **パネル枠・アイコン・武器サムネ・黄色いハイライト枠・背景テクスチャは一切変更しない**。位置も維持。
- キャプションの**文字色(白)・サイズ・中央揃え**は元（簡体字版）に合わせる。長い訳は簡潔化可。
- **出力は元と完全同寸・透過PNG(RGBA)**。リサイズ/トリミング禁止。

## 用語集（本文と統一・ゲーム既訳準拠）
チュートリアル項目名（左リスト＝確定訳）:
| 中/英 | 日本語 |
|---|---|
| 织衣 / Tailoring | 裁縫 |
| 钓鱼 / Fishing | 釣り |
| 操作 / Controls | 操作 |
| 装备・锻造 / Equipment・Forging | 装備・鍛造 |
| 心法 / Heart Method | 心法 |
| 经脉 / Meridians | 経脈 |
| 切磋 / Sparring | 手合わせ |
| 战斗 / Battle | 戦闘 |
| 武学 / Martial Arts | 武学（スキル） |
| 驿站 / Station | 宿駅 |
| 坐骑 / Mount | 騎乗 |
| 河图 / HeTu | 河図 |
| 洛书 / LuoShu | 洛書 |
| 猿舞 / YuanWu | 猿舞 |
| 好感 / Favorability | 好感度 |

頻出語:
| 英 | 日本語 |
|---|---|
| Blueprint | 設計図 |
| Sword / Saber / Polearm / Fist Weapon / Hidden Weapon / Others | 剣／刀／棍／拳／暗器／その他 |
| Steel Sword | 純鋼剣 |
| Required Level | 必要レベル |
| Forging Level | 鍛造レベル |
| EXP / Current EXP / Required EXP | 経験値／現在の経験値／必要経験値 |
| Level up | レベルアップ |
| Select | 選択 |
| Current | 現在の |

※ 迷ったら英語版の直訳＋自然な日本語。武侠用語は既訳（心法/経脈/武学 等）を優先。

## ファイル→トピック対応（文脈把握用）
- `shuoming05_haogan` 好感度 / `shuoming06_07_duanzao` 鍛造 / `shuoming08_09_zhiyi` 裁縫 / `shuoming10_diaoyu` 釣り
- `shuoming11_12_zhandou` 戦闘 / `shuoming13_zhuangbei` 装備 / `shuoming14_yaoqing` 招待 / `shuoming15_caozuo` 操作
- `shuoming16_qiecuo` 手合わせ / `shuoming17_xinfa` 心法 / `shuoming18_19_jingmai` 経脈 / `shuoming20_wuxue` 武学
- `shuoming21_shoubing` 兵の配置 / `shuoming22_huiheji` ターン計 / `shuoming23_yizhan` 宿駅 / `shuoming24_zuoqi` 騎乗
- `shuoming25_HeTu` 河図 / `shuoming26_LuoShu` 洛書 / `shuoming27_YuanWu` 猿舞
- `gamepad__*` … 上記のゲームパッド版（内容同じ。画面内のボタン表記 LB/RB 等は変更しない）

## 返却方法
- 日本語版PNGを **`返却/` に元と同じファイル名**で保存（サブフォルダは `__` 区切りのまま。例 `gamepad__gamepad_shuoming06.png`）。
- 元と同寸・透過必須。そろったら「再インポートして」→ こちらで `import_ja_png.py`（Tutorial対応済）で注入・pak・deploy。

## 備考
- DXT5圧縮の装飾（`shuoming00_biaoti/dadiban/diban` 等の底板・タイトル）は文字が無い/装飾なので対象外。
- 再インポートは同寸ピクセル差し戻し（ロスレス・クラッシュ無し）。1386×789も検証済。
