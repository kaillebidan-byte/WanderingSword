# 現在の引継ぎ

- active train: `yuwen-mowen-train-51`
- branch: `agent/yuwen-mowen-train-51`
- stage: `private_quality_audit`
- transport: `not_ready`
- wave: `yuwen-mowen-train-51-wave-01` / 1 packet / 69 unique rows
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5224_1_5229_13_2026-07-30.json`
- previous release: `yuwen-mowen-train-50` / PR #207 / `da31a1ea4f663fd2d0442317cf2f457722799103`

## exact next action

`_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5224_1_5229_13_2026-07-30.json`を読み、KEEP/FIX・人物性・事実・典故だけを監査する。
GitHub API、branch、workflow、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。

## quality audit資料還流

candidateの一次資料だけで典故・事実疑義を先に立て、その後に`quality_audit_context.required_documents`を照合する。全人物資料targetへ`keep/revise/create/unresolved`を記録し、人物資料を直接編集しない。
