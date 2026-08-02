# Event selection evidence — Quest 13511

## Accepted event

- Event ID: `quest_13511_fengming_staff`
- Quest lifecycle root: `13511`
- QuestDlgs scene family: `13511_1`
- State after this round: `event_manifest_ready`
- Formal reference: disabled

## Source-supported continuity

The Quest lifecycle and scene family form one causal chain.

1. In `RequestDlgs`, 王道明 asks what happened to 王天聪 and learns that he has become dejected after the encounter in 天水城.
2. 王道明 proposes a new weapon to help 王天聪 recover.
3. In `OptionDlgs1`, 宇文逸 accepts the task and 王道明 requests three pieces of `寒铁矿`.
4. In `FinishingDlgs`, 王道明 receives the cold iron and says the artisans can finish the weapon after the remaining material is supplied.
5. In QuestDlgs family `13511_1`, 王道明 states that the `凤鸣棍` has been completed and asks 宇文逸 to deliver it to 王天聪.

The same participants, intended recipient, material, weapon objective, and completion-to-delivery transition are preserved. The shared numeric root is therefore used as a locator, while the source-content continuity is the verification basis.

## Internal placement

`13511_1` is placed after the `finishing` lifecycle block because the lifecycle block records delivery of the final cold iron and predicts imminent completion, while the scene opens by declaring the weapon complete.

No ordering relative to other Quests or chapters is asserted.

## Rejected candidate links

The following shared-dialogue links were reviewed and rejected as event-membership evidence because their only shared text was a generic response used in unrelated contexts.

- Quest `11006` ↔ family `9016_2`: `嗯，你说得对。`
- Quest `11696` ↔ family `17402_3`: `只是……`
- Quest `11241` ↔ family `5300_1`: `这样吗……`
- Quest `11776` ↔ family `9245_1`: `原来是这件事……`

These links remain candidate inventory records but are not promoted into the verified event manifest.

## Limits

- The source index has no `13511_RequestDlgs_Index10_Text`; no missing line is synthesized.
- Chapter placement and global story order remain unresolved.
- The later delivery result and any branch outcome are outside this manifest.
- Scene-time knowledge, beliefs, misunderstandings, secrets, and full-spoiler truths are not recorded here.
- Existing proofreading and translation consumers remain blocked until the reference gate reaches `reference_ready`.
