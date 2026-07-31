# 宇文逸↔莫問 yuwen-mowen-train-76 wave-01 preparation

- stage: `private_preparation`
- status: `complete`
- source: Relation artifact run `30660076941`
- queue: 1 packet / 70 unique rows
- semantic extension: `used`

## packet layout

### packet-01 — 22010_7 + 22025_1 + 22029_5 + 22031_1 + 22125_1 + 24057_1 + 24058_1
- rows: 70
- candidate: `_phase4_proofread/CANDIDATE_YUWEN_MOWEN_SCENES22010_7_24058_1_2026-08-01.json`
- context: 少林で六派共議が定まった後、宇文逸が夜に師父襲撃と莫問の所在を追い、莫問と伏龍子の同行・親子関係を知る。復讐の是非を思案したのち、後日の戦時局面で莫問の各派への挑戦状を受け、宇文逸が十五日以内に天山と玄火教へ向かう決意を固める。

## boundary attestation

- 前半五場面30行だけでは品質波の下限40行に届かない。直後の関係進展として、莫問の挑戦状を受け宇文逸が天山行きを引き受ける二分岐40行まで含めると、親子関係の判明から対決決意までの意味単位が完結するため、70行のcomplete_semantic_unitとして封印する。
- 22010_7から22125_1は少林会議後から天仏窟前までの連続局面。24057_1と24058_1は同じ戦時会議の分岐であり、台詞差を保ったまま別場面として監査し、事実や話者発言を合成しない。

## stage boundary

- 意味境界のみを記録し、KEEP/FIX判断・fix・owner・正式束はまだ書かない。
- 次stationは`translation_quality_audit`。
