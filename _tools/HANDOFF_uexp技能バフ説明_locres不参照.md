# 引き継ぎ: 技能/バフ説明の「locres不参照」未訳（uexpパッチ案件）

作成 2026-06-21 / 調査のみ完了・**未着手**（本格対応は別セッション）

## 一行サマリ
技/バフ/図鑑の効果説明テキストは **locresではなく DataTable の uexp に簡体字で内蔵**されており、locresしか書き換えない現行MODでは**ゲーム内で中文のまま**。例として報告された「睡夢羅漢功の特殊効果」がこれ。**locres側は完全に訳済みなのに表示されない**。FText棚卸し報告(`_tools/FTEXT棚卸し報告.md`)のD項「locres不参照」そのもの。

## 確定した事実（調査結果）
- ベースpak: `C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks\Wandering_Sword-WindowsNoEditor.pak`(5.9GB)。
- 該当uexp（ベースpak内、UTF-16LEで簡体字を内蔵）:
  - `Wandering_Sword/Content/JH/Tables/Skills.uexp`(2.74MB)：簡体字概数 **3202**。列名 `SpecialEffectDesc`/`CastEffectDesc` を内包＝技の使用/特殊効果の本文がここ。
  - `Wandering_Sword/Content/JH/Tables/Buffs.uexp`(1.69MB)：簡体字概数 **1301**。バフ効果説明。`睡梦`/`睡生`/`罗汉` をUTF-16で検出済み。
  - `Wandering_Sword/Content/JH/Tables/PictorialBook.uexp`：武学図鑑。睡夢羅漢功は `系统|PictorialBook|1738_PictorialName`。図鑑の説明も要確認。
  - 他に `Items.uexp` `JingMais.uexp` 等も同種の可能性（要確認）。
- 抽出済み（次セッションで再利用可）: `_ws_tmp/_uexp/Wandering_Sword/Content/JH/Tables/Skills.uexp`, `Buffs.uexp`（.uasset は未抽出。要追加抽出）。
- locres側（`_work/jp/.../Localization/Skills技能表`, `Buff与道具`）は **JA訳済み**。例 `Skills|820_SpecialEffectDesc`=「5級効果-睡生夢死：…/10級効果-大夢先覚：…」（全文訳済み）。これがゲームに出ていない＝uexp参照の証拠。

## スコープ（重要）
- 睡夢羅漢功だけの問題ではない。**技/バフ説明が広範に uexp 内蔵**＝これまでの locres バフ/心法/字形の翻訳も**ゲーム内で表示されていない可能性が高い**。
- ⚠ 最初に**実機確認**: 適当なバフ/技の効果説明がゲーム内でJAか中文かを1つ確認。中文なら全面的にuexp対応が必要。

## 対応手順（uexpパッチ）
正系ツール: `_tools/uexp_ftext_patcher_v2.py` の `patch_file2(head_path, uexp_path, out_head, out_uexp, TM, verbose)`。
- 動作: uexp内の keyed FText(`\x21\x00\x00\x00`+32hexGUID)のソース文字列を走査し、`TM[中文ソース]` があればJAへ置換。サイズフィールド/export map/BulkDataStartOffset を全補正（入れ子コンテナ対応）。
- ⚠ `guidance_patcher.py` は旧版でLinuxパス(`/sessions/.../tm.json`)がハードコード。使うなら v2 を使うこと。

### TM(翻訳メモリ {中文ソース: JA}) の作り方
locresは既訳なので、それを中文キーに紐付け直せばよい:
1. ベースpakから**原文(中文)のlocres**を抽出:
   `repak.exe unpack <BASE> -o _ws_tmp/_base -i "Wandering_Sword/Content/Localization/Skills技能表/zh-Hans/Skills技能表.locres"`（Buff与道具も同様）
2. 原文locres `{ns\x1fkey: 中文}` と、`_work/jp`の訳済みlocres `{ns\x1fkey: JA}` を**同じキーで突き合わせ** → `TM[中文]=JA`（中文≠JAのものだけ）。
   - `_tools/locres.py` の `parse()` で両方読める。
3. 注意: uexpのソース文字列＝原文locresのソースと一致するはず（locresはDataTableから生成）。一致しない断片はTM無しでスキップされる。

### 適用フロー
1. ベースpakから `Tables/Skills.uexp` と `Tables/Skills.uasset`（**.uasset必須**＝header補正に要る）を抽出。Buffs/PictorialBook も同様。
2. `patch_file2("Skills.uasset","Skills.uexp", out_uasset, out_uexp, TM, verbose=True)`。
   - 出力先は `_work/jp/Wandering_Sword/Content/JH/Tables/Skills.uasset` と `.uexp`（MODパクに同梱）。
3. `repak.exe pack _work/jp _work/aaWanderingSword_JP_P.pak --version V11 --mount-point ../../../`
4. `python _tools/deploy_to_game.py`（WS_TMP設定）。ゲーム再起動で確認。
5. **検証**: 睡夢羅漢功の特殊効果がJA表示になるか実機確認。

## リスク/未確認
- v2パッチャは Guidance/UI の uexp で実績。**Tables系DataTableのFText形式が同じkeyed FTextか未検証** → まず1ファイル・少数置換で試し、repak後に壊れない（ゲーム起動）ことを確認してから全面適用。
- DataTableのFTextがkey無し/inline FString列だとPAT不一致で拾えない。その場合は別途オフセット直置換が必要。
- .uexp と .uasset は必ずペアで一貫させる。MODパクにTables一式が増える（サイズ増）。
- `Items.uexp`等にも未訳説明があれば同手順で。

## 関連ファイル
- `_tools/uexp_ftext_patcher_v2.py`（正系パッチャ）
- `_tools/FTEXT棚卸し報告.md`（D項=本案件の分類元）
- `_tools/ftext_inventory.json`（UI系のみ。技/バフTablesは棚卸し対象外＝睡夢ヒット0だった）
- `_tools/locres.py`(parse) / `_tools/deploy_to_game.py`
- `_work/jp/.../Localization/Skills技能表`,`Buff与道具`（既訳locres＝TM元）
