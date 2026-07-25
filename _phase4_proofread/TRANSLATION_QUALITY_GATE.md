# 翻訳品質ゲート

## 目的

この工程の目的は、既存日本語の意味ずれ、不自然さ、人物声の崩れ、原文にない追加・原文からの欠落を見つけて直すことにある。

束数、通読行数、修正キー数はCI輸送と作業上限を決めるための指標であり、成果そのものではない。指標を満たすために束を細分化したり、重複分岐を別行として水増ししたり、疑わしい訳をkeepへ寄せてはならない。

## 集計

- `reviewed_keys`: 実際に確認したlocresキー数。重複分岐を含む。
- `unique_reviewed_rows`: 同一原文・同一訳文の重複を一度だけ数えた実質通読行数。
- `fix_keys`: 修正するlocresキー数。重複分岐の鏡写しを含む。
- `unique_fix_rows`: 同じ判断を共有する重複修正を一度だけ数えた実質修正行数。
- manifestの`totals.reviewed_rows`は`unique_reviewed_rows`と一致させる。
- 4束、40行、20修正キーのORはpublic CIへ送れる輸送候補条件であり、品質合格条件ではない。
- keep-only束は意味境界の記録として許可するが、keep-only束の個数だけで品質合格にしない。

## 低収穫ゲート

release候補時点で`unique_fix_rows / unique_reviewed_rows < 15%`なら低収穫とする。低収穫は失敗ではないが、既訳が本当に良いのか、通読を進めることが目的化したのかを区別するため、次を必須にする。

1. 初回keepとなった全unique rowsを、原文・現訳・話者・相手・前後・分岐・所有から二巡目で疑い直す。
2. 二巡目では少なくとも、意味の強弱、発話役割、人物声、原文にない設定追加、情報の欠落、直訳由来の不自然さを別々に確認する。
3. 発見した見落としと、疑ったが保持した近接候補を品質記録へ残す。
4. 二巡目後の`unique_fix_rows`と`fix_keys`をmanifestへ反映する。
5. 品質記録とmanifestの整合をcheckerで検査する。

## release条件

public CIへ出すには、輸送候補条件に加えて`quality_gate.release_decision = quality_passed`が必要。

低収穫時は次も必要。

- `challenge_pass.status = complete`
- `challenge_pass.scope = all_initial_keep_unique_rows`
- 初回keep unique rowsを全件再監査した件数
- 二巡目で見つけたunique findingsとkey findings
- repository内に存在する品質記録

## 禁止

- 同一内容の重複分岐を通読行数へ二重計上する。
- FACT_DOUBTで「補わない」と書きながら、訳文では原文にない人物・身分・因果を補う。
- 表記上の些細な候補だけを拾い、意味・役割・人物声の粗さを見ない。
- 低修正率を「既訳が良かった」と説明するだけで二巡目を省く。
- 行数や束数の達成を進捗の主成果として報告する。

## 報告の優先順位

作業報告は次の順にする。

1. 何を直したか、なぜ直したか。
2. 重大なkeep判断と、何を疑って保持したか。
3. 見落とし防止の品質ゲート結果。
4. 束数・unique rows・reviewed keysなどの輸送情報。
