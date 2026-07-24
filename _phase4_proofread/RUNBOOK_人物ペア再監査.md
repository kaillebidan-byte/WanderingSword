# Wandering Sword 人物ペア再監査RUNBOOK

この文書はプロジェクト固有の薄い入口。判断手順の正本は次。

- skill: `.agents/skills/zhja-game-translation-codex/references/08_pair_reaudit.md`
- QA: `.agents/skills/zhja-game-translation-codex/references/06_qa.md`
- 公開CI窓: `_phase4_proofread/PUBLIC_CI_WINDOW.md`
- 現在地: `_phase4_proofread/audit_status.json`
- 開いている作業: `_phase4_proofread/_TODO.md`

## 1. 標準作業単位

### private翻訳作業回

1. GitHub metadataでリポジトリがprivateであることを確認する。
2. `CURRENT_WORK.operation_mode.declared_state` が `private_translation_work` またはprivate上の `public_ci_blocked` であることを確認する。
3. `audit_status.json` の現在クラスタと人物ペアを確認する。
4. `_tools/extract_relation_context.py` で一次資料を抽出する。
5. 人物ペアを関係段階と場面へ分ける。
6. 既訳を `fix / keep / source-doc-fix / unresolved` へ裁定する。
7. 高確度の実変更だけを `_phase4_proofread/fixes_*.json` へ収録する。
8. ペルソナ、関係性マップ、TODO、監査台帳、状態文書、必要なテストを更新する。
9. PRを開く前に、翻訳判断と準備物を可能な限り一つのatomic commitへまとめる。
10. 深い判断が残っていないことを確認し、作業branch上の宣言状態を `ready_for_public_ci` へ変更する。
11. ユーザーへ公開CI窓を開くよう依頼する。

### 公開CI窓

1. ユーザーの報告だけでなくGitHub metadataでpublicを確認する。
2. 完成HEADからPRを作成する。
3. Relation、Cross、Applyを一回実行する。
4. job log、artifact、所有表、未適用差分を確認する。
5. 局所修正だけで済む場合はまとめて一回更新する。
6. 最終HEADの三本成功、未適用0件、verified checkpoint、未解決thread 0件を確認する。
7. 翻訳PRをsquash mergeする。
8. squash commitへ参照を付け替えるpost-merge状態PRを作成する。
9. 状態PRの三本成功と未解決thread 0件を確認し、squash mergeする。
10. mainの宣言状態を `private_translation_work` とし、実visibilityがpublicならユーザーへprivate復帰を依頼する。

public中に新しい場面の翻訳、人物声の大幅な再検討、複数commitの試行を始めない。深い修正が必要なら `public_ci_blocked` とし、privateへ戻してから続ける。

人物ペア監査台帳はskillの `templates/pair_audit_template.md` を使う。

## 2. 修正束の命名と監査量

推奨:

```text
fixes_relation_<pair-slug>_<YYYYMMDD>_batch<N>.json
fixes_cross_register_<scope>_<YYYYMMDD>.json
```

名前は記録用。workflowへ人物名、日付、バッチ番号をハードコードしない。

一つの束は、同じ場面だけでなく、時系列・事件・関係段階が連続する隣接場面群をまとめてよい。**通読対象は原則15〜30行**とし、一場面が短い場合は次の隣接場面を確認して、意味上の境界を壊さない範囲で併合する。

15行未満または30行超の束は例外扱いとし、`NEXT_TASK_PACKET.batch_planning` に次を記録する。

- 実際の通読行数
- 確認した隣接候補
- 併合または分離の判断理由
- 分岐境界、高リスク場面、対象範囲内の隣接場面なし、不可分な重複群などの例外理由

**通読行数と修正JSONのキー数を混同しない。** 修正JSONには高確度の実変更だけを収録するため、通読15〜30行でも変更0件または少数でよい。件数を満たすための言い換え、既一致行、判断保留、好みだけの変更は含めない。逆に、同一場面や不可分な重複群で変更が多い場合は、人物声と事実状態を一続きで判断できる範囲を優先する。

`_tools/check_batch_planning.py` は、通読目標、focus key数との一致、小束例外の根拠を機械検査する。

## 3. private中の読み取り検証

```text
python _tools/test_apply_fixes_json.py
python _tools/validate_fixes_json.py --allow-applied _phase4_proofread/fixes_*.json
python _tools/apply_fixes_json.py _phase4_proofread/fixes_*.json
python _tools/test_lint_register.py
python _tools/test_extract_relation_context.py
python _tools/test_check_batch_planning.py
python _tools/check_batch_planning.py
python _tools/test_check_operation_mode.py
python _tools/check_operation_mode.py --repository-visibility private
```

`apply_fixes_json.py` は複数JSONを統合する。

- 同一キー・同一値: 重複として許容
- 同一キー・異なる値: 書き込み前に停止
- 複数target: 各locresを1回だけ書く
- 複数修正束: pakを1回だけ生成
- 未適用0件: repak省略
- 未適用が残る場合: key、所有ファイル、期待値、実値をプレビューへ表示

## 4. PR上の自動適用

`.github/workflows/apply-curated-fixes.yml` が、同一リポジトリのPRで `fixes_*.json` が変更された場合に動く。

1. PRブランチとLFS資産をcheckout
2. 全修正束を未適用・適用済み込みで検証
3. 未適用分をまとめてlocresへ反映
4. pakを一度だけ再生成
5. 適用後ゼロ差分、lint、関係抽出、単体テストを確認
6. locresとLFS pakをPRブランチへcommit・push
7. bot起因の再実行では書き込みを停止

人物ペアごとの一時apply workflowは作らない。

読み取りCI:

- `.github/workflows/relation-audit.yml`: `fixes_relation_*.json` を動的検出し、公開CI窓の状態構造も検査する
- `.github/workflows/cross-register-qa.yml`: `fixes_cross_register*.json` を動的検出

### PR更新とActions使用量

GitHubの`paths`判定は最新commitだけでなくPR全体の差分を対象にする。修正JSONを含むPRでは、後から記録ファイルだけを一件ずつ更新しても、PRの`synchronize`ごとにApply・Relation・Cross-registerが再実行される。

- private中に修正JSON、レビュー、適用記録、必要な資料修正、テスト、状態文書を可能な限り一つの原子commitへまとめる。
- `ready_for_public_ci`へ進むまでPRを開かない。
- 複数ファイルを更新できるツールでは、tree/commitを使い、一つの論理状態をファイルごとの連続commitへ分割しない。
- botの生成資産commit後に行う`CURRENT_WORK`、`NEXT_TASK_PACKET`、`CURRENT_HANDOFF`、review statusの確定も、一つの人手commitへまとめる。
- squash後の状態PRは参照付け替えだけを一つの原子commitで行う。
- 診断のためのcommit・再実行を重ねる前に、既存artifactとjob logを読む。runner開始前の失敗を翻訳失敗として扱わない。
- public中に二回以上の追加commitが見込まれるなら、`public_ci_blocked`としてprivateへ戻す。
- Actions使用枠やrunnerが止まっても、三本成功というmerge条件を弱めない。

## 5. 完了段階

- `initial_pass`: 初回キャラ校正の一巡
- `evidence_inventory`: 一次資料抽出
- `persona_reviewed`: ペルソナ検証
- `relation_reviewed`: 関係・呼称検証
- `translation_reaudited`: 既訳再監査
- `build_verified`: locres反映、pak再生成、機械検証
- `game_verified`: ゲーム内表示・場面適合確認

`build_verified` と `game_verified` を混同しない。

## 6. 作業境界

エージェント側:

- private中の翻訳監査と準備
- 公開が必要な時点の明示依頼
- public確認後のPR、CI、artifact確認、squash統合、状態同期
- 修正JSON
- locres書き戻し
- `_work/aaWanderingSword_JP_P.pak` 再生成
- CI、lint、抽出、LFS確認
- 記録更新

ユーザー側:

- GitHub repository visibilityのpublic/private変更
- `_tools/deploy_to_game.py`
- Steamゲームフォルダへのコピー・置換
- ゲーム起動とゲーム内確認

ゲーム内確認前は `game_verified: not_started` のままにする。
