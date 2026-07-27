# owner assignment生成手順

## 目的

`fixes_*.json`の保存先を作業者が目視で選ばない。private encodingでは翻訳判断を構造化planへ記録し、既存owner更新、新規owner作成、manifest・private state・CURRENT_WORK集計、生成証跡を一命令で確定する。

## 正規入口

1. sealed waveのcandidate順と同じ順で`_phase4_proofread/OWNER_ASSIGNMENT_PLAN.json`を作る。
2. 次を一度実行する。

```bash
python _tools/apply_owner_assignment.py
```

3. 生成された`_phase4_proofread/OWNER_ASSIGNMENT_RESULT.json`を含めてcommitする。
4. public化前に通常の完全preflightを実行する。

```bash
python _tools/check_private_release_preflight.py --with-tests
```

## plan schema

```json
{
  "schema_version": 1,
  "packets": [
    {
      "candidate": "_phase4_proofread/CANDIDATE_....json",
      "new_owner_file": "_phase4_proofread/fixes_relation_....json",
      "values": {
        "short_key": "speaker-id - 話者 $@$最終訳"
      },
      "fix_keys": ["short_key"]
    }
  ]
}
```

- `candidate`は`PRIVATE_STAGE_STATE.wave.packets`と同じ順・同じpathでなければならない。
- `values`は、既存ownerへ反映する値と、新規ownerとして収録する値だけを持つ。
- `fix_keys`は実際に基準訳から変更するkeyで、必ず`values`の部分集合とする。
- `new_owner_file`は未所有keyだけへ使用される。既存owner keyはツールが元のownerファイルへ戻す。
- 同じkeyに複数ownerがある場合、生成前に停止する。

## 自動更新範囲

生成器は次を同じ実行で更新する。

- 全`fixes_*.json`の既存owner値
- packetごとの新規ownerファイル
- `CI_TRAIN_MANIFEST.json`のowner・fix集計と`fix_files`
- `PRIVATE_STAGE_STATE.json.wave.encoding_summary`
- `CURRENT_WORK.json.ci_train.totals`
- `OWNER_ASSIGNMENT_RESULT.json`のcandidate、plan、全owner、三状態正本のdigest

## 禁止

- candidate snapshotだけを見て新規ownerファイルを手書きすること
- 既存owner keyを別名の`fixes_*.json`へ複製すること
- ownerファイル更新後にmanifest件数を手で転記すること
- `OWNER_ASSIGNMENT_RESULT.json`生成後にowner、candidate、manifest、private state、CURRENT_WORKを個別編集すること

変更が必要ならplanを直して生成器を再実行する。preflightはdigest差、複数owner、集計ミラー差を拒否する。

## train-15回帰

`6151_2`から`6171_5`までの50行について、既存owner 38・新規owner 12を回帰テストへ固定している。日付違いの新規batchへ50行すべてを重複収録する旧挙動はテスト失敗になる。
