# 最終応答ゲート

この文書は、通常cycle完了と規定フェイズ終端を混同して予約tokenを誤送信する事故を、送信前に機械的に遮断する。

routine正本は`_phase4_proofread/FINAL_RESPONSE_POLICY.json`とする。生の終端契約・live認可state・予約tokenの字面はvalidator／controller／renderer専用であり、通常応答を作るモデルの読書対象にしない。

## 唯一の再開入口

```bash
python _tools/resume_work_entrypoint.py --repository-visibility <private|public>
```

返された`final_response_gate.mode`に従う。

### normal_response

- `safe_completion_label`で通常作業の完了を報告する。
- 予約token、認可ID、result行を本文・引用・説明・例示・コードブロックへ出さない。
- terminal rendererを実行しない。
- train、wave、PR、release phase2、transport merge、cycle target到達を規定フェイズ終端へ昇格しない。

### authorized_terminal

- モデルは終端suffixを手入力・復元・推測しない。
- 次の専用rendererだけを実行する。

```bash
python _tools/render_phase_completion_suffix.py --output <terminal-suffix.txt>
```

- renderer出力を改変せず、応答の最終suffixとして一度だけ付ける。
- rendererが失敗した場合は終端suffixを出さない。

## 送信前検査

通常応答を含む最終文面をUTF-8ファイルへ保存し、送信前に必ず次を通す。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

checker失敗後に手動で送信・terminal扱いへ上書きしない。

## 自動化consumer側

画面上の最後の一行や固定文字列検索だけで停止しない。`_tools/regulated_phase_terminal_consumer.js`のlive state照合が`accepted === true`の場合だけ停止する。

consumerは、suffixの一意性、event ID、result、authorization scope、active phase、terminal statusをすべて検証する。live stateを取得できない場合は非受理とする。

## 禁止

- 通常応答から生の終端契約・live認可stateを読むこと
- marker単独または二行形式で停止する旧実装
- モデルが認可ID・result・予約tokenを生成すること
- consumer側の非受理だけに依存し、誤送信自体を許容すること
- checkerまたはrenderer失敗後の手動上書き
