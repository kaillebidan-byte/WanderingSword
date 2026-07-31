# 現在の引継ぎ

- active train: `yuwen-mowen-train-68`
- branch: `agent/yuwen-mowen-train-68`
- stage: `private_quality_audit`
- transport: `not_ready`
- wave: `yuwen-mowen-train-68-wave-01` / 1 packet / 53 unique rows
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5807_1_5821_1_2026-07-31.json`
- previous release: `yuwen-mowen-train-67` / PR #224 / `dc882f8b994f46ed082a21ebc9a08cc0ae9beb69`

## exact next action

`_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5807_1_5821_1_2026-07-31.json`を読み、KEEP/FIX・人物性・事実・典故だけを監査する。
GitHub API、branch、workflow、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。

## quality audit資料還流

candidateの一次資料だけで典故・事実疑義を先に立て、その後に`quality_audit_context.required_documents`を照合する。全人物資料targetへ`keep/revise/create/unresolved`を記録し、人物資料を直接編集しない。
