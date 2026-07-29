# 翻訳工場フロー

翻訳者へ残す人間判断stationは、意味単位の束境界とquality auditの二つだけとする。quality auditは訳文だけでなく、一次資料と既存ペルソナの相互再検証を含む。GitHub、branch、PR、workflow、artifact、owner、状態正本、encoding、人物資料への決定的書込み、CI、phase2、mergeは搬送設備の担当であり、作業者が代替手段を考案しない。

## work order

```bash
python _tools/translation_factory_controller.py --repository-visibility <private|public>
```

controllerは四状態正本とminimal reservationを読み、一つのwork orderだけを返す。machine actionは`FACTORY_FLOW_CONTRACT.json`の恒久adapterへ接続し、欠落時は`factory_adapter_missing`で停止する。quality auditは`QUALITY_AUDIT_SOURCE_FEEDBACK_CONTRACT.json`も検証する。

## 新cycle初期化

1. controllerが`initialize_next_cycle_from_reservation`を返す。
2. `semantic_bundle_boundary`で場面境界だけを決める。
3. 決定内容と予約済みartifact identityを`_factory_requests/*.json`へ一件だけ記録する。
4. `translation-factory-execute.yml`が固定artifactを取得する。
5. `factory_request_executor.py`がcontroller actionを再検証し、`fixed_cycle_initializer.py`だけを呼ぶ。
6. mode lock、candidate、owner snapshot、preparation、四状態正本を同じcommitへ生成する。
7. candidate schema 3へ、一次資料、digest付き必須skill・人物資料、人物資料target、未解決話者を収録する。
8. requestを削除し、次stationを`translation_quality_audit`へ固定する。

## quality auditの順序

1. candidateの原文・現訳・前後文・話者・時系列だけで典故疑義と設定事実疑義を立てる。
2. `quality_audit_context.required_documents`のskill、RUNBOOK、人物資料を読む。
3. KEEP/FIXと修正訳を決める。
4. 各`source_document_target`へ`keep/revise/create/unresolved`を決める。
5. `revise/create`には一次資料key、適用scope、high confidence、一意な置換文または追記headingを記録する。
6. 人物資料に反例がある場合は訳文を資料へ押し込まない。証拠不足なら`unresolved`に残す。
7. human stationでは人物資料を直接書き換えない。

## 記録済み監査のencoding

1. schema 2の`AUDIT_DECISIONS_*.json`がcandidate全行をKEEP/FIXへ完全分割する。
2. `reading_attestation`がcandidateのdigest付き読書manifestと完全一致する。
3. `source_document_decisions`が全source targetを被覆する。
4. `translation-factory-encode.yml`が同一trainの監査記録を一件に解決する。
5. `check_quality_audit_source_feedback.py`が読書証跡、証拠key、scope、digest、mutation条件を事前検査する。
6. `factory_encoding_executor.py`から`fixed_encoding_pipeline.py`を実行する。
7. `source_document_feedback.py`が高確度・digest一致・一意anchorの人物資料修正だけを決定的に適用する。
8. 40〜60行を標準semantic wave、意味単位完結時のみ61〜80行を`complete_semantic_unit`として正式束へ収録する。
9. `apply_owner_assignment_v2.py`で既存owner更新、新規owner、digest、manifest集計を生成する。
10. 人物資料修正記録、review record、owner結果、正式束、状態正本を同じencoding commitへ収録する。
11. `translation_frozen`・`ready_for_public_ci`へ遷移し、`release-ci` labelから既存orchestratorを起動する。

## release finalization

1. `Release train orchestrator`成功後、固定`release-finalization-inputs-*` artifactを使用する。
2. `_factory_requests/finalize-release-*.json`へPR、orchestrator run、CI HEAD、Apply HEAD、次Relation reservationを一件だけ記録する。
3. `translation-factory-finalize.yml`がartifactをrun IDとnameで取得する。
4. `fixed_release_finalizer.py`がrequestとartifactを完全照合する。
5. release evidence、第N束verified checkpoint、manifest、private state、handoff、次sceneのminimal reservationを同じcommitへ生成する。
6. transportを`awaiting_private_merge`へ進め、controllerの次actionを`verify_phase2_and_merge`へ固定する。
7. phase2成功と未解決review thread 0件を確認してsquash mergeし、`reconcile_merged_cycle.py`で`merged`へ確定する。

Apply HEADはrelease evidenceの`asset_head`として最終HEADの祖先でなければならない。履歴圧縮でApply commitを外したり、release evidenceを手入力したりしてはならない。

## 人間判断station

### semantic_bundle_boundary

原文・現訳・話者・場面ID・前後文・行数を受け取り、意味単位の境界だけを決める。標準40〜60行、意味単位完結時のみ最大80行。branch、workflow、owner、正式束、状態正本は触らない。

### translation_quality_audit

KEEP/FIX、修正訳、人物性・事実・典故、既存ペルソナの維持・修正・追加・保留を判断する。`reading_attestation`と`source_document_decisions`を必須とし、encoding、人物資料への直接書込み、GitHub、CI、mergeは触らない。

## 異常時

既知の一時障害だけ一回再試行する。未知の失敗は再試行せず、固定エラーコードと失敗stepを保存する。web検索、別API探索、一時workflow作成、trigger変更、同一失敗引数再試行は禁止する。安全停止は作業終了ではなく、搬送設備の停止である。
