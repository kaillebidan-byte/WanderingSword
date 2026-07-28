# 翻訳工場フロー

翻訳者へ残す判断は、意味単位の束境界と訳文品質監査の二つだけとする。GitHub、branch、PR、workflow、artifact、owner、状態正本、encoding、CI、phase2、mergeは搬送設備の担当であり、作業者が代替手段を考案しない。

## work order

```bash
python _tools/translation_factory_controller.py --repository-visibility <private|public>
```

controllerは四状態正本とminimal reservationを読み、一つのwork orderだけを返す。返されたaction以外へ進んではならない。

machine actionは`FACTORY_FLOW_CONTRACT.json`の`adapter`または固定executorへ接続されていなければならない。接続を`check_factory_adapters.py`で検査し、欠落時は`factory_adapter_missing`で停止する。

## 恒久request搬送

新cycle初期化と意味境界記録は`FACTORY_REQUEST_CONTRACT.json`に従う。

1. controllerが`initialize_next_cycle_from_reservation`を返す。
2. `semantic_bundle_boundary`で場面境界だけを決める。
3. 決定内容と予約済みartifact identityを `_factory_requests/*.json` に一件だけ記録する。
4. 恒久workflow `translation-factory-execute.yml`が固定run/nameのartifactを取得する。
5. `factory_request_executor.py`がcontroller actionを再検証し、`fixed_cycle_initializer.py`だけを呼ぶ。
6. mode lock、candidate、owner snapshot、preparation、四状態正本を同じcommitへ生成する。
7. requestを生成commitから削除し、次stationを`translation_quality_audit`へ固定する。

一時workflow、別trigger、手動状態編集は使わない。

## 恒久encoding搬送

quality audit完了後は、監査決定を手作業でowner・正式束へ転記しない。

1. `AUDIT_DECISIONS_*.json`がcandidate全行をKEEP/FIXへ完全分割し、status=`complete`になる。
2. 恒久workflow `translation-factory-encode.yml`が同一trainの監査記録を一件に解決する。
3. `fixed_encoding_pipeline.py`がcandidateの現訳、FIX前後、KEEP集合、scene順序を再検証する。
4. 40〜60行を標準semantic wave、意味単位完結時のみ61〜80行を`complete_semantic_unit` extensionとして正式束へ収録する。
5. `apply_owner_assignment_v2.py`を固定生成器として呼び、既存owner更新、新規owner、owner digest、manifest集計を生成する。
6. review、owner plan/result、正式束、四状態正本を同じbot commitへ収録し、`translation_frozen`・`ready_for_public_ci`へ遷移する。
7. 以後は`release-ci` labelから既存`Release train orchestrator`だけを起動する。

encoding中に翻訳判断を再開したり、Contents APIで状態正本を一つずつ変更したり、一時apply workflowを作ったりしてはならない。

## 人間判断station

### semantic_bundle_boundary

機械が原文・現訳・話者・場面ID・前後文・行数を搬送した後、翻訳者は意味単位の境界だけを決める。標準40〜60行、意味単位完結時のみ最大80行。branch、workflow、owner、正式束、状態正本は触らない。

### translation_quality_audit

翻訳者はKEEPまたはFIX、修正訳、人物性・事実・典故メモだけを判断する。encoding、GitHub、CI、mergeは触らない。

## 異常時

既知の一時障害だけ一回再試行する。未知の失敗は再試行せず、固定エラーコードと失敗stepを保存する。web検索、別API探索、一時workflow作成、trigger変更、同一引数再試行は禁止する。

controllerに対応actionがなければ`factory_unknown_state`、状態正本が不一致なら`factory_state_mismatch`、恒久adapterがなければ`factory_adapter_missing`で停止する。この停止は翻訳作業の終了ではなく、搬送設備の安全停止である。
