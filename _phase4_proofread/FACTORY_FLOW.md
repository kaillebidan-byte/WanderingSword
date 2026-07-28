# 翻訳工場フロー

翻訳者へ残す判断は、意味単位の束境界と訳文品質監査の二つだけとする。GitHub、branch、PR、workflow、artifact、owner、状態正本、encoding、CI、phase2、mergeは搬送設備の担当であり、作業者が代替手段を考案しない。

## 唯一の進行入口

```bash
python _tools/translation_factory_controller.py --repository-visibility <private|public>
```

controllerは四状態正本とminimal reservationを読み、一つのwork orderだけを返す。返されたaction以外へ進んではならない。

## 人間判断station

### semantic_bundle_boundary

機械が原文・現訳・話者・場面ID・前後文・行数を搬送した後、翻訳者は意味単位の境界だけを決める。標準40〜60行、意味単位完結時のみ最大80行。branch、workflow、owner、正式束、状態正本は触らない。

### translation_quality_audit

翻訳者はKEEPまたはFIX、修正訳、人物性・事実・典故メモだけを判断する。encoding、GitHub、CI、mergeは触らない。

## 異常時

既知の一時障害だけ一回再試行する。未知の失敗は再試行せず、固定エラーコードと失敗stepを保存する。web検索、別API探索、一時workflow作成、trigger変更、同一引数再試行は禁止する。

controllerに対応actionがなければ`factory_unknown_state`、状態正本が不一致なら`factory_state_mismatch`で停止する。この停止は翻訳作業の終了ではなく、搬送設備の安全停止である。
