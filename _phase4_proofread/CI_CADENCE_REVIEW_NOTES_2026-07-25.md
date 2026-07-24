# 公開CI窓の粒度 観察メモ

- status: `observation_only`
- proposal timing: 第60束の公開CI窓終了後
- current-cycle rule: 現行制度を変更せず、第60束を同じ手順で完了する

## 問題意識

翻訳束が9〜12行程度の小場面で閉じる一方、公開CI窓では翻訳PR、bot書き戻し、最終HEAD再検証、squash統合、post-merge状態PR、再検証、squash統合、visibility復帰が必要になる。翻訳量に対する状態同期・CI・visibility操作の比率が高い。

## 第59束で観測した実作業

- 通読: 12行
- 修正: 12キー
- 人物ペア新規: 2キー
- 翻訳PR: 1本
- post-merge状態PR: 1本
- 成功したworkflow: 翻訳PRで6本、状態PRで3本
- bot書き戻し直後の`action_required`: 3本（既知のno-op）
- visibility操作: public化とprivate復帰
- squash SHA確定後に、checkpoint・次作業パケットの参照付け替えが必要

## 第60束で追加観測する値

- 通読9行、修正予定6キー、人物ペア新規予定1キーに対し、同じ公開工程がどの程度発生するか
- 翻訳判断、資産適用、checkpoint確定、次作業計画、squash参照同期のうち、どこが必須の安全境界で、どこが束ごとの反復であるか
- 失敗時の切り分けと冷間再開精度を保ったまま、公開往復をまとめられる単位

## 次回提案で比較する論点

- `verified checkpoint`を小束ごとではなく複数束をまとめた単位にできるか
- privateで複数の翻訳束を完成させ、一つの公開CI窓でまとめて適用できるか
- squash SHAへの参照付け替えを自動化し、post-merge状態PRをなくせるか
- CURRENT_HANDOFFやCOLD_START_ACCEPTANCEなどの生成・同期を、毎束ではなく確定単位へ寄せられるか
- まとめた場合でも、所有競合、未適用0件、回帰、失敗束の特定、ロールバックを維持できるか

この文書では結論を出さない。第60束の実測を加えた後、候補制度と移行手順を提示する。
