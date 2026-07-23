# 新チャット再開プロトコル

この文書は、同じChatGPTプロジェクト内で新しいチャットへ移ったときの固定手順です。現在の人物ペア、件数、次場面はここへ書かず、`CURRENT_WORK.json` に置きます。

## 起動文

ユーザーが次の一文を送ったら、再開モードへ入ります。

```text
現状把握して作業の続きを
```

「現状を確認して続けて」「作業の続き」「前の作業を再開して」など、同じ意図の表現も再開モードとして扱います。

## 前提

- 同じプロジェクト内の新チャットでは、対象リポジトリのURLと接続先は既知として扱います。
- URL、リポジトリ名、前回の作業内容をユーザーへ聞き直しません。
- URLや前回作業を聞き直さず、GitHub上の実状態と正本から復元します。
- GitHubへ接続できない、複数リポジトリを区別できないなど、実際に特定不能な場合だけ不足を報告します。
- 過去チャットの要約は補助資料です。GitHub上のmain、未統合PR、GitHub Actions、正本ファイルを優先します。

## 起動時の行動契約

再開モードでは、現状報告だけで応答を終えません。次の順で復元し、短い報告のあと同じ応答内で実作業へ進みます。ユーザーが明示的に「現状だけ」と頼んだ場合だけ作業を開始しません。

### 1. GitHub上の生存状態を確認する

最初に次を確認します。

1. リポジトリのdefault branchとmainの最新状態
2. 未統合PRの有無
3. 未統合PRのhead SHA、変更ファイル、レビュー、未解決スレッド
4. 各head SHAのGitHub Actions
5. 直近のmerged PR
6. `CURRENT_WORK.checkpoint` の状態

### 2. 未統合PRを分類する

未統合PRは、開いているだけで現行作業と決めない。各PRを次のいずれかへ分類します。

- `active`: mainに未統合の有効な作業があり、現在の人物ペア・場面・修正束と連続する
- `superseded`: 後続PRが同じ作業を置換し、既に検証・統合している
- `abandoned`: 作業を破棄しており、再開根拠がない
- `unrelated`: 現在の翻訳作業とは別目的

分類時は、PR本文、branch名、変更ファイル、commit差分、後続merged PR、適用記録、mainへの包含を照合します。

置換PRを作る場合は、旧PRへ置換先をコメントし、その時点で旧PRを閉じます。旧PRを開いたまま残して、新チャットへ判断を委ねません。実地例としてPR #38はPR #39に完全置換されていたため、#39を確認後に#38を閉じました。

`CURRENT_WORK.json.immediate_next` より優先するのは、`active` と判定した未統合PRだけです。

### 3. 正本を読む

次の順序を基本とします。

1. `README.md`
2. `AGENTS.md`
3. 本文書 `SESSION_BOOTSTRAP.md`
4. `CURRENT_WORK.json`
5. `CURRENT_HANDOFF.md`
6. `audit_status.json`
7. 現在工程のRUNBOOKとskill
8. 現在人物のペルソナ、関係資料、一次資料、最新の修正束・監査記録

全ファイルを漫然と通読せず、現在工程と直近作業に必要な箇所を優先します。

### 4. 再開位置を裁定する

状態は次の優先順位で決めます。

1. **active PRがあり、CIが進行中**: そのPRとCIを追跡する
2. **active PRがあり、CIが失敗**: ログを読み、翻訳・構造・状態同期のどこで失敗したかを分けて直す
3. **active PRがあり、CI成功・未マージ**: head SHA、レビュー、スレッド、差分、checkpointを再確認して統合工程を続ける
4. **直近PRはmergedだが状態文書が古い**: 状態文書を実GitHub状態へ合わせてから次へ進む
5. **active PRがない**: `CURRENT_WORK.json.immediate_next` から次束を開始する

`CURRENT_WORK.json` は「確定済みcheckpointと次に何をするか」の正本です。作業途中のPRはmain上の同ファイルへまだ反映されていないことがあるため、起動時はPRとActionsを先に確認します。

### 5. bot書き戻し後のActionsを判定する

apply workflowがlocres、pak、`audit_status.json` をbot commitとしてPR branchへ書き戻すと、そのbot commitを契機とする三本のworkflowが `action_required` になる場合があります。

- `action_required` は翻訳失敗、構造違反、CI失敗を意味しません。
- 直前のapply jobが成功し、bot差分が生成物と監査索引だけであることを確認します。
- 内容に即した人手コミットでcheckpointまたは適用記録を最終化し、最新HEADに三本を再実行します。
- `action_required` のまま完了・統合済みとは報告しません。

### 6. 最初の報告

長い総括は不要です。通常は次の四点を短く報告します。

- 復元した現在ペア・完了束・累計・checkpoint状態
- 未統合PRの分類とCI状態
- 直ちに着手する場面・作業
- 古い資料や矛盾を見つけた場合の扱い

報告後、そのまま調査・修正・PR・CI確認へ進みます。「作業を始めてもよいか」と確認しません。

## checkpointのライフサイクル

`CURRENT_WORK.checkpoint.status` は次の二値です。

### `verified`

mainへ統合可能な確定状態。

- `CURRENT_WORK` と `audit_status` の人物ペア、束数、件数、build状態が一致する
- `checkpoint.applied_record` が実在し、`audit_status.record_index` に収録されている
- `checkpoint.translation_head` と `checkpoint.verified_head` が現在HEADの祖先である
- 最終HEADの関係抽出、register QA、apply・build検証が成功している

### `pending_audit_sync`

翻訳適用後、状態文書を次束へ進めたが、apply workflowによる監査索引同期がまだ完了していない遷移状態。

- 件数、束番号、適用記録索引の一時差は警告として扱う
- 翻訳作業やapply workflowは続行してよい
- mainへは統合しない
- apply workflowの同期後、人手コミットで `verified` に変更し、最終HEADを再検証する

`python _tools/check_handoff_consistency.py` は遷移中の差を警告として表示します。統合前は `python _tools/check_handoff_consistency.py --require-verified` が成功することを確認します。

初回applyで実際の翻訳差分がある間は、PR branch上の `CURRENT_WORK` が前回の `verified` checkpointを指し、作業ツリー上の `audit_status` だけが新件数へ進む。この短い区間ではcheckpoint完全一致検査を延期し、生成物と監査件数を先にbot commitする。これは検証省略ではなく、旧checkpointと新生成物の一時差を確定状態として誤検査しないための順序制御である。

## 束終了時の標準順序

1. 修正束・監査記録を作成してPRを開く。`CURRENT_WORK` は前回の `verified` checkpointのままにする
2. 初回CIで修正適用、locres、pak、ゼロ差分、回帰、LFSを確認する。pending fixがあるrunではcheckpoint完全一致検査を延期する
3. botが生成物と監査件数を書き戻したことを確認する
4. 適用記録、`CURRENT_WORK`、`CURRENT_HANDOFF` を更新し、checkpointを `pending_audit_sync` にする
5. pending fix 0件のapply workflowで `audit_status` の記録索引を同期し、handoff checkerを通す
6. bot書き戻し後の差分を確認する
7. 人手コミットでcheckpointを `verified` にし、`verified_head` をbot書き戻しHEADへ更新する
8. 最新HEADの三本と `--require-verified` を成功させる
9. レビュー、未解決スレッド、変更ファイルを確認してmergeする

## 翻訳判断の最低関門

- 最優先は、その人物がその相手へその時点で実際に発する声として成立すること。
- 中国語構文を移した硬い訳は、意味を保った自然な日本語の語順、長さ、切れ目、助詞省略へ再構成する。
- 笑い、咳、息、叫び、間、反復、文字種を一律表記へ押し込まない。
- 自然さを無難な現代会話と同一視しない。人物固有の古風さ、豪放さ、尊大さ、陰湿さ、幼さ、寡黙さは発声として保持する。
- `ALLUSION_REVIEW` と `FACT_DOUBT` を別々に通す。
- ペルソナ、関係性マップ、完成例、過去の適用記録は作業仮説であり、一次資料の反例があれば資料側を改訂する。
- 悪役・怪人・雑兵・癖の強い端役は、原文と役割に根拠があれば大胆に演出してよい。黒無常・白無常は許容強度の一例であり、具体的な口調の流用元ではない。

## 実装と完了の最低関門

- 既存修正束との同一キー異値競合を適用前に止める。
- 話者接頭辞、タグ、改行、プレースホルダを保持する。
- 修正JSONだけで止めず、原則としてlocres反映、pak再生成、適用後ゼロ差分、register lint、関係抽出、単体テスト、回帰走査、LFS確認まで進める。
- checkpointが `verified` で、最終HEADのCI成功後に統合する。
- Steamゲームフォルダへの配置、ゲーム起動、ゲーム内確認は行わない。

## 終了時の書き戻し契約

新しい束を統合するPRでは、原則として次も同じPR内で更新します。

- `CURRENT_WORK.json`: checkpoint、完了束、件数、build状態、次場面
- `CURRENT_HANDOFF.md`: 人間向け現在地、直近裁定、次場面
- `audit_status.json`: 品質段階、件数、適用記録索引
- 必要なペルソナ、関係資料、典故・設定疑義記録

`_TODO.md` は横断課題用、`_handover.md` は履歴用です。現在地を重複して正本化しません。

## 再開失敗を防ぐ禁止事項

- URLや前回作業を、同じプロジェクトのユーザーへ毎回聞き直す
- 未統合PRを開いているという理由だけでactiveと決める
- `CURRENT_WORK.json` だけを読み、active PRを見落とす
- `pending_audit_sync` のままmergeする
- bot commitの `action_required` を翻訳失敗と断定する
- 初回apply中の旧checkpointと新監査件数の一時差を、確定状態の不整合として停止する
- 現状報告だけで作業を終える
- 過去チャットの要約だけで翻訳判断を再現する
- CI成功を確認せず「完了」「統合済み」と報告する
- 古いTODO、ペルソナ完成例、適用記録を一次資料より優先する