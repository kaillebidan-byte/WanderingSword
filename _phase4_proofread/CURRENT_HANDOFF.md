# 現在の引継ぎ

- active train: `yuwen-mowen-train-59`
- branch: `agent/yuwen-mowen-train-59`
- stage: `private_quality_audit`
- transport: `not_ready`
- wave: `yuwen-mowen-train-59-wave-01` / 1 packet / 51 unique rows
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5449_2_5509_4_2026-07-30.json`
- previous release: `yuwen-mowen-train-58` / PR #215 / `4f508e5dccf98559ae93c734699f2b66e2ec75d9`

## exact next action

`_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5449_2_5509_4_2026-07-30.json`を読み、KEEP/FIX・人物性・事実・典故だけを監査する。
GitHub API、branch、workflow、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。

## quality audit資料還流

candidateの一次資料だけで典故・事実疑義を先に立て、その後に`quality_audit_context.required_documents`を照合する。全人物資料targetへ`keep/revise/create/unresolved`を記録し、人物資料を直接編集しない。
