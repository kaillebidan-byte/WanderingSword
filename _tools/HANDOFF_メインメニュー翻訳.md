# 引き継ぎ: メインメニュー等「locres外」UIの日本語化(別チャット/高性能モデル向け)

## ✅ 解決済 (2026-06-11)
- 正体: ESCメニューは **BPMV_JHSystem** (JHNeoUI/Modules/System)。ボタン文字は全て**テクスチャ焼き込み**
  (`JH/JHNeoUI/UIAssets/System/xitong01〜22`、PF_B8G8R8A8 無圧縮・mip1・各ボタン3状態)。
- 対応: cv2インペイントで中国語を消去 → Yuji Syuku(OFL)で日本語を再描画 → UE4-DDS-Tools(UE4.26)で
  uassetへ再注入 → MOD pakへ加算(計58ファイル、locres14は温存)。タイトル「系统」→「システム」、
  7ボタン全部(設定/タイトルへ戻る含む)を日本語化。ゲームフォルダへ配備済み。
- 素材・原本: `_uassets_menu/`(original_uasset / original_png / jp_png / フォント)。
- 残り(未対応・別件): タイトル画面 `JH/UI/MasterMenu/Textures/T_BTN*`(新規ゲーム/ロード/設定/終了、3状態ずつ)も
  画像焼き込み。同じ手順で対応可能。
- 注意: 本体pakのrepak listは**全289,441エントリ**。途中で切れた60,378行のリストを信用しないこと。

## ✅ 追加解決 (2026-06-11): チュートリアル説明文(キャプション)
- 正体: `Modules/Guidance/Steps(+_Gamepad)/**/BP_Guidance_*.uexp` 内のFTextリテラル(146ファイル/179箇所)。
- **重要な発見**: これら179キーはlocresに存在し既に翻訳済み(srcHashも一致)なのに、ゲームはlocresを引かず
  ソース文字列を直接表示する(理由不明・この画面特有)。**locres追加では直らない**。
- 対応: uexp内のFTextソース文字列を直接日本語に置換(訳はlocres既訳をTMとして再利用、新規翻訳ゼロ)。
  文字列長変更に伴い、(1) **FPropertyTagのSize int32(FText値の9バイト前)**、(2) uassetのexport map
  (SerialSize/SerialOffset, stride104)、(3) BulkDataStartOffset(0xa9, int64=uasset+uexp-4)の3点を補正。
  ※(1)を忘れると起動時 "Serial size mismatch" でクラッシュする(一度やらかした)。ツール: `_tools/guidance_patcher.py`、
  抽出データ: `_tools/guidance_ftext.json`。146ファイル全てexportチェーン検証済み。
- チュートリアル内の「画面スクリーンショット画像」(图纸・锻造等级0等が写り込んだもの)は画像のため未対応(コスト大、ユーザー了承済み)。

## ✅ 追加解決 (2026-06-11): FText全棚卸し+locres外テキスト24件
- 全UI/Core/Maps/Tables系BPをスキャンし `_tools/ftext_inventory.json` に分類保存(報告: `_tools/FTEXT棚卸し報告.md`)。
- locres外で表示される24件をuexpパッチ: **OPナレーション(LS_CG-5001)**、NPC交流メニュー、採集/釣り/観察/休む、
  ミニゲームUI、未知地域、世界地図、WuDangのumap(喝粥)等。umap/LevelSequenceにも同パッチ手法が通用することを確認。
- locres内未訳のうち不自然な11件を更新(力道→力量、普攻→通常攻撃、口才:→弁舌: 等)。
- 今後ゲーム内で中文を見つけたら: ftext_inventory.json をgrep→repak getで原本取得→**uexp_ftext_patcher_v2.py**で差し替え。

## ⚠️ 重要な教訓 (2026-06-11): FTextが配列/構造体に入れ子の場合
- v1パッチ(guidance_patcher.py)は**TextPropertyタグのSizeしか直さない**。FTextがTArray<struct>内にあると
  外側のArrayProperty/StructPropertyのSize未補正で"Serial size mismatch"起動クラッシュ(BP_MonkeyDanceで発生)。
- v2(`_tools/uexp_ftext_patcher_v2.py`)は名前テーブルを読みプロパティツリーを歩いて**入れ子の全Size(最大5階層確認)を補正**+
  パッチ後にトップレベル全タグ列の整合検証付き。**今後のuexpパッチは必ずv2を使う**。
- WidgetのTextBlock直下(Guidance系)はチェーン長1なのでv1でも安全だった(179箇所全数確認済み)。
- 原本バックアップ: 対象20アセットは sandbox消滅に備え `_uassets_menu/ftext_b_originals/` に保存。

## ゴール
locresに存在せず、現行MODで翻訳できない**メインメニュー5ボタン**を日本語化する:
`继续游戏`(ゲームを続ける)/`保存进度`(セーブ)/`读取进度`(ロード)/`新手教程`(チュートリアル)/`退出游戏`(ゲームを終了)
※ `游戏设置`→ゲーム設定、`返回标题`→タイトルへ戻る は locres(系统)にあり翻訳済。残るは上記5つ。

## 確認済みの事実(調査の出発点)
1. 上記5文字列は、**全9ローカライズ対象 × 全文化(zh-Hans/zh-Hant/en)のlocresのどれにも存在しない**(総当たり確認済)。
   → テキスト翻訳(locres)の層には無い。**.uasset(Widget Blueprint / DataTable)か、テクスチャ画像に焼き込み**のいずれか。
2. base pak内に **`BP_ImageLocalization.uasset/.uexp`** が存在(画像ローカライズ用BP)。メニュー文字列が画像で差し替えられている可能性の有力な手がかり。
3. pak形式: **UE4 pak V11 / mount-point `../../../` / 暗号化なし**。

## 環境・パス
- ゲーム本体pak(原本): `C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks\Wandering_Sword-WindowsNoEditor.pak` (約5.9GB)
- 現行MOD pak(我々の成果・展開ツリー): プロジェクトの `_work/jp/`(全9対象のlocres) → `_work/aaWanderingSword_JP_P.pak`
- ゲームへの設置先: 上記Paksフォルダの `aaWanderingSword_JP_P.pak`(MODはここを差し替え。**この.pakにファイルを追加すれば上書きが効く**)
- pakツール: `_tools/repak`(Linux版, v0.2.3)。Windowsは repak_cli か UnrealPak。
- locres解析/書込: `_tools/locres.py` / `locres_write.py`(自作・検証済)

## 調査手順(別チャットでやること)
1. **文字列の所在特定**: base pakを展開し、`.uasset/.uexp` を **UTF-16LE の "继续游戏"** でバイナリ検索。
   どのアセット(例 `WBP_MainMenu` 等のWidget BP、または `DT_*` DataTable)に在るか特定する。
2. **アセット種別の判定**:
   - **DataTable / BP内のFTextリテラル** → 編集可能(下記3へ)。
   - **Texture2D(画像に焼き込み)** → テキスト編集不可。画像の描き直し＋差し替えが必要(難度高)。
3. **編集と再パック**(DataTable/FTextの場合):
   - `FModel`(閲覧)＋ **`UAssetGUI` / `UAssetAPI`**(.uasset編集)、または Unreal Editor で該当FTextを日本語へ。
   - 編集した.uassetを、**既存MOD pakに追加**して再パック(repak)。locresの14ファイルは温存し、.uassetを足すだけ。
   - mount-point `../../../`、V11 を厳守。ゲームが読む**正確なアセットパス**で上書きすること。

## リスク・注意
- .uassetはシリアライズが厳密。import/name/export テーブルの整合を崩すと**起動クラッシュ**。必ずバックアップ。
- 現行のlocres翻訳(全9対象)を壊さないこと。.uasset追加は**加算**で行う。
- 画像焼き込みだった場合は、テクスチャ差し替え(同名・同フォーマット・mip)になり、別物の作業量。
- 復元用: `_backup/aaWanderingSword_JP_P.original.pak`(MOD原本)。本体pakは無改変。

## 既に終わっていること(重複しないため)
- locresで翻訳可能なUIは全て対応済: 設定画面、戦闘モード切替ダイアログ、セーブ/ロード確認、卡関ツールチップ、
  好感度ランク、ステータス名、`游戏设置`/`返回标题`、騎乗名 等。全9ローカライズ対象をMOD pakに収録済(14ファイル)。
- 残課題は**本ドキュメントの5ボタン(locres外)のみ**。
