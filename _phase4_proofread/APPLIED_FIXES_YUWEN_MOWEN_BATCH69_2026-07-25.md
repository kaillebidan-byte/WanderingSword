# 宇文逸↔莫問 第66〜69束 適用記録

- 日付: 2026-07-25
- PR: #113
- CI列車: `yuwen-mowen-train-03`
- release: 通常条件 `bundle_count=4`
- 場面: `5504_3` / `5506_3` / `5508_13` / `5509_4`
- 通読行数: 32
- 修正キー: 4
- 現訳保持: 28
- 人物ペア新規: 2
- cross-register新規: 2
- 人物ペア累計: 1169
- プロジェクト全体累計: 1525
- status: `applied_and_pak_built`
- build: `verified_not_deployed`
- game verification: `not_started`
- Relation run: `30140191768`
- Cross run: `30140191816`
- Apply run: `30140191802`
- CI HEAD: `1bf29e39de33d22c52291123f64474935adb8eca`
- applied assetsを含むHEAD: `12de4b6c7c882e7837e1af96109e992882d7716e`

## 適用した修正束

- `_phase4_proofread/fixes_relation_yuwen_mowen_20260725_batch66.json` — 宇文逸の峋谷関急行判断1キー
- `_phase4_proofread/fixes_cross_register_yaoji_boatman_20260725.json` — 瑶姫の呼びかけと船頭探し2キー
- `_phase4_proofread/fixes_relation_yuwen_mowen_20260725_batch68.json` — 欧陽雪の父から聞いた黄将軍の嗜好1キー

第67束と第69束はkeep-only束であり、修正JSONを作らず`fix_files=[]`を正規状態として保持した。

## 主な校正判断

- 悪人谷・杜彪・徐海の関与を会話以上の客観事実へ強めていない
- 峋谷関の悪化、船頭の逃亡、黄将軍の重傷を推測・伝聞の範囲に留めた
- 瑶姫のからかいと地モードを汎用敬体へ平板化していない
- 莫問の危機判断を簡潔に保ち、人数・手段・目的を追加していない
- 欧陽雪の献書案を知的な補佐として保ち、成功を保証していない

## 制度修正

- repository metadata確認を最初の無言ゲートへ固定した
- metadata verdict前の計画・開始宣言・途中報告を禁止した
- keep-only束の`fix_files=[]`を受理するmanifest v2検査を追加した
- release作業とrelease後のNEXT_TASK_PACKETを分離するnext-task v2検査を追加した
- visibility preflightと列車状態v2の回帰testをphase2へ組み込んだ
- 制度修正は訳文、修正JSON値、人物声、所有境界を変更していない

## 機械検証

- Relation audit extraction run `30140191768` 成功
- Cross register QA run `30140191816` 成功
- Apply curated localization fixes run `30140191802` 成功
- locres反映、pak再生成、LFS確認成功
- 全修正束の未適用0件
- validate、register lint、関係抽出、単体テスト、回帰走査成功
- visibility preflight契約検査成功
- keep-only束とrelease/next packet分離のv2検査成功
- audit_statusは全1525キー、人物ペア1169キーへ更新済み

この記録をaudit_status索引へ同期した後、第69束のverified checkpointを同じPR内で確定する。ゲームフォルダへの配置とゲーム内確認は行っていない。
