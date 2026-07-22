# 引き継ぎ: 訳済みなのに中文表示される件 → 真因は「locresソースハッシュ陳腐化」

旧題「技能/バフ説明のlocres不参照（uexpパッチ案件）」。**2026-06-25 全面改訂**: 当初仮説(uexp手術)は誤りと判明。本書が正本。経緯は memory [[uexp-locres-bypass]]、要点は [[locres-srchash-staleness]]。

> **2026-06-25 実施済（全てdeploy済・実機で睡夢羅漢功JA化を確認）**:
> 1. stale 5件を locres-only 修正（ハッシュ更新5＋再訳2: Buff7511・Skills820）。
> 2. 段階プレフィクス正規化 **206エントリ**（Skills技能表）: レベルN効果-→**N級効果-**、レベルごとの効果-→**各級効果-**、パッシブ変種→級形、本文 Nレベルで→N級で。`_ws_tmp/apply_prefix_norm.py`。
> 3. 武学熟練度の称号11段階（系统・hexキーUIラベル＝locres、uexpではない）の半端訳を**意訳称号11種で統一**（計34エントリ）。`_ws_tmp/apply_titles.py`。マップ: 修練の徒/開門の士/技を知る者/自在の手練/一角の達人/万理開眼/極致の境地/傑物無双/天下無敵/群雄の頂/武林宗主。
>
> ツール: `_tools/locres_rw.py`（忠実round-trip writer・バイト一致検証済）。バックアップ `_ws_tmp/_stale_backup/` `_norm_backup/` `_titles_backup/`。**残: 実機で②③の見栄え最終確認のみ。**

## 一行サマリ
「訳済みなのにゲーム内で中文」（例 睡夢羅漢功の特殊効果）の真因は **locresに保存されたソース文字列ハッシュが、実ソース(uexp)のハッシュと食い違う**こと。UEは不一致時に訳を棄却し中文へフォールバックする。**uexp手術は不要。locres-onlyで直る。クラッシュリスク無し。**

## 当初仮説はなぜ誤りだったか
- 旧説「効果説明はlocres参照されずuexp内蔵で常に中文」→ 反証: 同じ技の **820_CastEffectDesc は画面でJA表示**・**820_SpecialEffectDesc だけ中文**。locresは参照されている。
- 実体: 両列とも uexp に `ns="Skills" + key + ソース文字列` のインラインFTextを内蔵。ゲームは (ns,key) でlocresを引く。**ただしlocresエントリの保存ソースハッシュ == FText埋め込みソースのCRC32 の時だけ訳を採用**。ゲームが原文を改修（睡夢羅漢: 棍ダメージ+15%→+30% 等）すると採取時ハッシュが陳腐化し、訳が棄却される。

## 確定事実（2026-06-25 全9ネームスペース走査）
- 照合法: ベースpakの zh-Hans locres（=ゲーム現行のソース＋ハッシュ）と `_work/jp` のlocresを**フルキー(ns+key)**で突合。`zh-Hans` locresの保存ハッシュ＝実行時の真のソースハッシュ（uexpソースのCRC32と一致を実証済み）。
- **真の陳腐化(stale)は全体で5件のみ**:

| # | NS | key | 状態 | 対応 |
|---|---|---|---|---|
| 1 | Buffs | 7511_Description | 原文の数値改修(50%→30%几率＋真気消耗追加) | **再訳**＋ハッシュ更新 |
| 2 | NPCTalks | 71_Dlgs_Index5_Text | 訳良好・原文軽微変更 | ハッシュ更新のみ |
| 3 | Quests | 28226_FinishingDlgs_Index5_Text | 訳良好・原文軽微変更 | ハッシュ更新のみ |
| 4 | Quests | 5225_FinishingDlgs_Index2_Text | 訳良好・原文軽微変更 | ハッシュ更新のみ |
| 5 | Skills | 820_SpecialEffectDesc | 原文の数値改修(+15%→+30%等) | **再訳**＋ハッシュ更新＋表記正規化 |

- それ以外の「中文に見える」もの＝**未訳(JP=原文)2447件は大半が日中同形の漢字語**（一品/三式/少林寺/武当派/中毒/崇敬 等、JAでそのまま正しく表示）と**保留中の宇文逸/主人公会話**。バグではない。missing(キー欠落)=0。

## 重要な落とし穴
- **locresファイル名 ≠ 内部ネームスペース**（例 ファイル「Buff与道具」/ NS「Buffs」、「Skills技能表」/「Skills」）。ベアキーでuexpを引くと別NSの文字列を拾い**偽陽性が大量発生**（一度246件の偽不一致を出した）。必ず ns+key のフルキーで照合。
- **JA本文の編集はハッシュ照合に無影響**（照合は原文ハッシュ基準）。よって表記正規化や再訳は自由。直すのは「保存ソースハッシュ」と必要なら訳文。

## 修正方針（locres-only）
各stale行について:
1. 原文が実質変化 → 現uexpソース(=ベースzh-Hans locresのソース)からJA再訳（glossary準拠）。
2. 当該エントリの**保存ソースハッシュを `CRC32(現ソース)` に更新**。
3. repak（V11）→ deploy → 実機で睡夢羅漢功の特殊効果がJA化するか確認 → 全件展開。

### 付随QA（同パスで実施可・ユーザー裁定2026-06-25）
技能/バフ説明の段階プレフィクス表記ゆれを統一:
- 通常 `N级效果-` → **`N級効果-`**（現「N級効果-」139件＋「レベルN効果-」199件を集約）
- 被动 `N级 被动效果-` → **`N級効果-`**（パッシブ語を出さない）
- `每级效果-` → `各級効果-`（要最終確認）

## 必要ツール（未整備）
- ソースハッシュCRC32: `zlib.crc32`で各UTF-16コードユニットを `<lo><hi>00 00` に展開してCRC（UE `FCrc::StrCrc32`と一致を実証）。
- **locres書き込み**: 既存 `_tools/locres_write.py`（fstr/string-array I/Oのみ）を拡張し、エントリの**ソースハッシュ書換**＋文字列差替を再シリアライズする小ツールが要る。`apply_*.py`がソースハッシュを温存している（Skills 1505/1506一致が証拠）ので、その書込経路に「ハッシュ更新」を足す形が素直。

## 関連ファイル / 再現
- 走査: `_ws_tmp/scan_final.py`（全NS・stale/未訳/簡残を集計）、`_ws_tmp/reconcile2.py`（NS込みでuexpソース=ベースハッシュを実証）。
- ベース抽出: `repak.exe unpack <BASE> -o _ws_tmp/_base -i "Wandering_Sword/Content/Localization/"`。
- `_tools/locres.py`(parse) / `_tools/locres_write.py` / `_tools/deploy_to_game.py`。
- ベースpak: `C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks\Wandering_Sword-WindowsNoEditor.pak`。
