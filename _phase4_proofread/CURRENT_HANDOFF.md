# 現在の引継ぎ

- active train: `yuwen-mowen-train-79`
- branch: `agent/yuwen-mowen-train-79`
- stage: `private_quality_audit`
- transport: `not_ready`
- wave: `yuwen-mowen-train-79-wave-01` / 1 packet / 45 unique rows
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5689_1_6008_2_2026-08-01.json`
- previous release: `yuwen-mowen-train-78` / PR #235 / `f4c92c238fd9b06ebba89d8ec39d23086bc1dc39`

## exact next action

`_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES5689_1_6008_2_2026-08-01.json`を読み、KEEP/FIX・人物性・事実・典故だけを監査する。
GitHub API、branch、workflow、owner、正式束、encoding、CI、mergeはこのstationでは操作しない。

## quality audit資料還流

candidateの一次資料だけで典故・事実疑義を先に立て、その後に`quality_audit_context.required_documents`を照合する。全人物資料targetへ`keep/revise/create/unresolved`を記録し、人物資料を直接編集しない。
