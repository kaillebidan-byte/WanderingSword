# 現在の引継ぎ

- active train: `yuwen-mowen-train-81`
- branch: `agent/yuwen-mowen-train-81`
- stage: `private_quality_audit`
- transport: `not_ready`
- tail: 14 rows / 2 packets
- previous release: `yuwen-mowen-train-80` / PR #237 / `dee19812149e901b6d057cdd48a23e980e5731fb`

## exact next action

2candidateを読み、KEEP/FIX・人物性・事実・典故だけを監査する。
GitHub API、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。

## quality audit資料還流

2candidateをtarget/namespace別に保ち、各candidateの一次資料から典故・事実疑義を先に立てる。その後、各`quality_audit_context.required_documents`を照合し、全人物資料targetへ`keep/revise/create/unresolved`を記録する。人物資料は直接編集しない。
