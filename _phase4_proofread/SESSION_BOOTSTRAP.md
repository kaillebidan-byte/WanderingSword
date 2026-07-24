# 新チャット再開プロトコル

この文書は、同じChatGPTプロジェクト内で新しいチャットへ移ったときの固定手順です。現在の人物ペア、件数、次場面、作業モードはここへ固定せず、`CURRENT_WORK.json` に置きます。公開CI窓の詳細は `PUBLIC_CI_WINDOW.md` を正本とします。

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
- 過去チャットの要約は補助資料です。GitHub上の実visibility、main、未統合PR、GitHub Actions、正本ファイルを優先します。

## 起動時の行動契約

再開モードでは、現状報告だけで応答を終えません。次の順で復元し、翻訳可能な状態なら短い報告のあと同じ応答内で実作業へ進みます。ユーザーが明示的に「現状だけ」と頼んだ場合だけ作業を開始しません。

visibility操作が必要な状態は例外です。エージェントはvisibilityを変更できないため、必要な操作をユーザーへ依頼し、GitHub metadataで変更を確認するまで翻訳または公開CI工程へ先走りません。

### 1. 実visibilityとoperation modeを確認する

最初にGitHub repository metadataから実visibilityを取得し、`CURRENT_WORK.operation_mode` と `PUBLIC_CI_WINDOW.md` を読む。会話中の申告や状態文書だけでpublic/privateを決めません。

宣言状態と実visibilityから次のように裁定します。

- `private_translation_work` + private: private翻訳作業回。PRを開く前の監査と準備へ進む。
- `private_translation_work` + public: `return_private_required`。private復帰を依頼し、新しい翻訳や追加commitを始めない。
- `ready_for_public_ci` + private: 完成HEADと終了条件を示し、`公開CI窓を開いてください。`と依頼する。
- `ready_for_public_ci` + public: `public_ci_window`。CI、レビュー、squash統合、post-merge状態同期だけを行う。
- `public_ci_blocked` + public: private復帰を依頼し、原因不明の試行を続けない。
- `public_ci_blocked` + private: 深い修正をprivateで完成させる。

ユーザーが`公開した`または`privateに戻した`と述べても、GitHub metadataの実visibilityを再確認してから遷移します。

### 2. GitHub上の生存状態を確認する

次を確認します。

1. リポジトリのdefault branchとmainの最新状態
2. 未統合PRの有無
3. 未統合PRのhead SHA、変更ファイル、レビュー、未解決スレッド
4. 各head SHAのGitHub Actions
5. 直近のmerged PR
6. `CURRENT_WORK.checkpoint` の状態
7. `CURRENT_WORK.operation_mode` の宣言状態

### 3. 未統合PRを分類する

未統合PRは、開いているだけで現行作業と決めない。各PRを次のいずれかへ分類します。

- `active`: mainに未統合の有効な作業があり、現在の人物ペア・場面・修正束または公開CI工程と連続する
- `superseded`: 後続PRが同じ作業を置換し、既に検証・統合している
- `abandoned`: 作業を破棄しており、再開根拠がない
- `unrelated`: 現在の翻訳作業とは別目的

分類時は、PR本文、branch名、変更ファイル、commit差分、後続merged PR、適用記録、mainへの包含を照合します。

置換PRを作る場合は、旧PRへ置換先をコメントし、その時点で旧PRを閉じます。旧PRを開いたまま残して、新チャットへ判断を委ねません。

`CURRENT_WORK.json.immediate_next` より優先するのは、`active` と判定した未統合PRだけです。ただし、実visibilityとoperation modeの裁定はactive PRより先です。

### 4. 正本を読む

次の順序を基本とします。

1. `README.md`
2. `AGENTS.md`
3. 本文書 `SESSION_BOOTSTRAP.md`
4. `PUBLIC_CI_WINDOW.md`
5. `CURRENT_WORK.json`
6. `CURRENT_HANDOFF.md`
7. `NEXT_TASK_PACKET.json`
8. `COLD_START_ACCEPTANCE.md`
9. `audit_status.json`
10. 現在工程のRUNBOOKとskill
11. 現在人物のペルソナ、関係資料、一次資料、最新の修正束・監査記録

全ファイルを漫然と通読せず、現在工程と直近作業に必要な箇所を優先します。

### 5. 再開位置を裁定する

状態は次の優先順位で決めます。

1. **visibility操作が必要**: public/private変更をユーザーへ依頼し、確認まで翻訳またはCIへ進まない
2. **public_ci_window**: active PRとCIを追跡し、公開中に新しい翻訳を始めない
3. **active PRがあり、CIが進行中**: そのPRとCIを追跡する
4. **active PRがあり、CIが失敗**: ログを読み、局所修正か深い修正かを分ける。深い修正ならprivateへ戻す
5. **active PRがあり、CI成功・未マージ**: head SHA、レビュー、スレッド、差分、checkpointを再確認して統合工程を続ける
6. **直近PRはmergedだが状態文書が古い**: 状態文書を実GitHub状態へ合わせてから次へ進む
7. **private_translation_workでactive PRがない**: `CURRENT_WORK.json.immediate_next` から次束を開始する

`CURRENT_WORK.json` は「確定済みcheckpoint、operation mode、次に何をするか」の正本です。作業途中のPRはmain上の同ファイルへまだ反映されていないことがあるため、起動時は実visibility、PR、Actionsを先に確認します。

### 6. bot書き戻し後のActionsを判定する

apply workflowがlocres、pak、`audit_status.json` をbot commitとしてPR branchへ書き戻すと、そのbot commitを契機とする三本のworkflowが `action_required` になる場合があります。

- `action_required` は翻訳失敗、構造違反、CI失敗を意味しません。
- 直前のapply jobが成功し、bot差分が生成物と監査索引だけであることを確認します。
- 内容に即した人手コミットでcheckpointまたは適用記録を最終化し、最新HEADに三本を再実行します。
- `action_required` のまま完了・統合済みとは報告しません。

### 7. 最初の報告

通常は次を短く報告します。

- 復元した現在ペア・完了束・累計・checkpoint状態
- 宣言operation mode、実visibility、導出状態
- 未統合PRの分類とCI状態
- 直ちに着手する場面、またはユーザーに必要なvisibility操作
- 古い資料や矛盾を見つけた場合の扱い

private翻訳作業へ入れる場合は、報告後そのまま調査・修正へ進みます。「作業を始めてもよいか」と確認しません。

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

## 束終了時の標準順序

1. privateで修正束、監査記録、状態文書、テストを完成させる。PRはまだ開かない
2. privateで読み取り検証と所有確認を行う
3. 作業branchの宣言状態を`ready_for_public_ci`へ変更する
4. ユーザーへpublic化を依頼し、GitHub metadataでpublicを確認する
5. PRを開き、初回CIで修正適用、locres、pak、ゼロ差分、回帰、LFSを確認する
6. botが生成物と監査件数を書き戻したことを確認する
7. 適用記録、`CURRENT_WORK`、`CURRENT_HANDOFF` を更新し、checkpointを `pending_audit_sync` にする
8. pending fix 0件のapply workflowで `audit_status` の記録索引を同期する
9. 人手コミットでcheckpointを `verified` にする
10. 最新HEADの三本、operation mode検査、`--require-verified`を成功させる
11. レビュー、未解決スレッド、変更ファイルを確認してsquash mergeする
12. post-merge状態PRでsquash commit参照へ同期し、三本成功後にsquash mergeする
13. mainの宣言状態を`private_translation_work`へ戻し、実visibilityがpublicならprivate復帰を依頼する

## 翻訳判断の最低関門

- 最優先は、その人物がその相手へその時点で実際に発する声として成立すること。
- 中国語構文を移した硬い訳は、意味を保った自然な日本語の語順、長さ、切れ目、助詞省略へ再構成する。
- 笑い、咳、息、叫び、間、反復、文字種を一律表記へ押し込まない。
- 自然さを無難な現代会話と同一視しない。人物固有の古風さ、豪放さ、尊大さ、陰湿さ、幼さ、寡黙さは発声として保持する。
- `ALLUSION_REVIEW` と `FACT_DOUBT` を別々に通す。
- ペルソナ、関係性マップ、完成例、過去の適用記録は作業仮説であり、一次資料の反例があれば資料側を改訂する。

## 実装と完了の最低関門

- 既存修正束との同一キー異値競合を適用前に止める。
- 話者接頭辞、タグ、改行、プレースホルダを保持する。
- 修正JSONだけで止めず、原則としてlocres反映、pak再生成、適用後ゼロ差分、register lint、関係抽出、単体テスト、回帰走査、LFS確認まで進める。
- checkpointが `verified` で、最終HEADのCI成功後に統合する。
- Steamゲームフォルダへの配置、ゲーム起動、ゲーム内確認は行わない。

## 終了時の書き戻し契約

新しい束を統合するPRでは、原則として次も更新します。

- `CURRENT_WORK.json`: checkpoint、完了束、件数、build状態、operation mode、次場面
- `CURRENT_HANDOFF.md`: 人間向け現在地、直近裁定、visibility状態、次場面
- `audit_status.json`: 品質段階、件数、適用記録索引
- 必要なペルソナ、関係資料、典故・設定疑義記録

`_TODO.md` は横断課題用、`_handover.md` は履歴用です。現在地を重複して正本化しません。

## 再開失敗を防ぐ禁止事項

- URLや前回作業を、同じプロジェクトのユーザーへ毎回聞き直す
- GitHub metadataを確認せずvisibilityを決める
- public中に新しい翻訳を始める
- `ready_for_public_ci`前にPRを開く
- 未統合PRを開いているという理由だけでactiveと決める
- `CURRENT_WORK.json` だけを読み、active PRを見落とす
- `pending_audit_sync` のままmergeする
- bot commitの `action_required` を翻訳失敗と断定する
- public中に深い失敗のcommit試行を重ねる
- 現状報告だけで作業を終える
- 過去チャットの要約だけで翻訳判断を再現する
- CI成功を確認せず「完了」「統合済み」と報告する
- 公開CI窓終了後もpublicのまま放置する
