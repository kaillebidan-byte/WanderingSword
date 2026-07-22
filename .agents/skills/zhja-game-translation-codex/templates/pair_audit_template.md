# 人物ペア監査台帳: <人物A> ↔ <人物B>

- cluster: `<関係クラスタ>`
- status: `evidence_inventory | persona_reviewed | relation_reviewed | translation_reaudited | build_verified | game_verified`
- updated_at: `YYYY-MM-DD`
- evidence_source: `<抽出物・コーパス・locres>`
- auditor: `<担当>`

## 1. 監査範囲

- 対象人物:
- 対象時系列:
- 対象場面:
- 除外範囲:
- 抽出ブロック数:
- 固有行数:
- 重複・分岐の扱い:

## 2. 関係段階

|段階|開始根拠キー|人物A→人物B|人物B→人物A|register / 公私|確度|備考|
|---|---|---|---|---|---|---|
|関係成立前|||||high / medium / low||
|関係成立|||||high / medium / low||
|変化後|||||high / medium / low||

## 3. ペルソナ主張の検証

|人物|主張|根拠キー・場面|反例|裁定|確度|
|---|---|---|---|---|---|
|||||keep / revise / unresolved|high / medium / low|

## 4. 場面台帳

### `<scene-id / 会話ブロック>`

- 時点:
- 場所・状況:
- 同席者:
- 関係機能: `平時 / 公的 / 私的 / 緊張 / 病床 / 儀礼 / 戦闘 / 告白 / 継承`
- 主要原文機能:
- 現訳の問題:
- 連続発話上の注意:

|複合キー|話者|原文要旨|現訳要旨|裁定|理由軸|確度|
|---|---|---|---|---|---|---|
|||||fix / keep / source-doc-fix / unresolved|meaning / voice / relation / implementation|high / medium / low|

## 5. 意図的保持

|複合キー|保持理由|確認した前後文・場面|
|---|---|---|
||||

## 6. 未確定

|複合キー / 論点|不足情報|次の確認|
|---|---|---|
||||

## 7. 修正束

|path|keys|場面・崩れ方|status|検証|
|---|---:|---|---|---|
|`fixes_....json`||同一場面または同一機能|draft / validated / applied_and_pak_built|key・接頭辞・制御トークン・回帰走査|

修正束へ含めないもの:

- 既に正しい行
- 好みだけの言い換え
- 宛先・時系列が不明な行
- ゲーム表示なしでは決められない行

## 8. 資料改訂

- ペルソナ:
- 関係性マップ:
- 用語・典故:
- ワーカープロンプト:
- lint例外・設定:

## 9. ビルド検証

- applied_keys:
- locres_targets:
- pak:
- fix preview zero: `yes / no`
- unit tests: `pass / fail`
- register scan: `pass / fail`
- relation extraction: `pass / fail`
- LFS object: `confirmed / not confirmed`
- game deployment: `not performed / performed by user`
- game verification: `not_started / passed / failed`

## 10. 次の行動

- 次の場面・人物ペア:
- 終了条件:
