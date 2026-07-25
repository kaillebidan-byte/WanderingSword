# 新チャット冷間再開 受入基準

## 起動文

```text
現状把握して作業の続きを
```

同じ意図の「作業を続けて」「再開して」も対象とする。

## 最初の無言ゲート

1. 最初の外部確認としてGitHub repository metadataを取得する。
2. metadata結果前に、利用者向けの計画、開始宣言、途中報告を出さない。
3. 利用者のvisibility申告を実状態の正本として扱わない。
4. metadata取得後、実visibilityと有効operation modeを確定してから最初の報告または作業へ進む。
5. metadata取得失敗時は、作業開始を主張しない。

## 合格条件

1. `VISIBILITY_PREFLIGHT_CONTRACT.json`が機械検査を通る。
2. main、未統合PR、GitHub Actionsを確認し、開いているだけで現行作業と決めない。
3. active Issue、active branch、open PRをCURRENT_WORK・manifest・GitHub実体から復元する。
4. verified checkpointをCURRENT_WORK.checkpointとrelease evidenceから復元する。
5. active trainの状態・集計・review済み束をCI_TRAIN_MANIFESTから復元する。
6. NEXT_TASK_PACKETから、次に許可された作業と所有境界を復元する。
7. visibility、declared state、manifest statusの組合せから裁定する。
8. private_translation_work + privateなら、状態報告だけで止まらず同じ応答内で許可されたprivate作業へ進む。
9. ready_for_public_ci + publicなら、新規翻訳をせずpublic CI・単一PR最終化へ進む。
10. private_translation_work + publicなら、翻訳を開始せずprivate復帰を依頼する。
11. ready_for_public_ci + privateなら、完成HEADと集計を確認してpublic化を依頼する。
12. verified checkpointと未適用小束を混同しない。
13. 小束ではlocresとpakを更新せず、release時だけ適用する。
14. post-merge状態PRを作らない。

## 動的期待値

固定のbatch番号、件数、Issue番号、branch名をこの文書へ複製しない。各値は次の正本から毎回取得する。

- 実visibility: GitHub repository metadata
- declared state、checkpoint、active train、active branch: `CURRENT_WORK.json`
- 列車集計、review済み束、release readiness: `CI_TRAIN_MANIFEST.json`
- 次作業と所有境界: `NEXT_TASK_PACKET.json`
- active Issue / PR / Actions: GitHub実体
- 確定release: checkpointが指す`RELEASE_EVIDENCE_*.json`

この文書の固定値が現在地を上書きしてはならない。

## 機械検査

```bash
python _tools/check_visibility_preflight_contract.py
python _tools/check_operation_mode.py --repository-visibility <private|public>
python _tools/check_release_evidence.py --verify-git-lineage
python _tools/check_handoff_consistency_v2.py --require-verified
python _tools/check_ci_train_manifest.py
python _tools/check_next_task_packet.py
python _tools/test_check_visibility_preflight_contract.py
python _tools/test_check_operation_mode.py
python _tools/test_check_release_evidence.py
python _tools/test_check_release_evidence_github.py
python _tools/test_check_handoff_consistency_v2.py
python _tools/test_check_ci_train_manifest.py
python _tools/test_check_next_task_packet_ownership.py
```

すべてが成功しない状態を確定状態として扱わない。
