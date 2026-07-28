# 最終応答ゲート

この文書は、規定フェイズ終端予約語を誤って通常応答へ出す事故と、その誤出力で自動化が停止する事故を分離して防ぐ。

実際の予約語、接頭辞、動的状態は次を正本とする。

- `_phase4_proofread/PHASE_COMPLETION_SIGNAL.json`
- `_phase4_proofread/REGULATED_PHASE_STATE.json`

## エージェント側の送信前ゲート

`signal_authorization`がobjectでない間、契約の`marker`値は応答本文、報告、引用、例示、コードブロックを含め出力禁止とする。

通常応答を含む最終文面をUTF-8ファイルへ保存し、送信前に次を通す。

```bash
python _tools/check_phase_completion_signal.py --response-file <draft-response.txt>
```

予約語を含まない通常応答は通る。予約語を含む応答は、live stateと一致する次の三行suffixがなければ失敗する。

```text
<authorization_prefix><signal_authorization.event_id>
<status_prefix><signal_authorization.result>
<marker>
```

train、wave、PR、release phase2、transport merge、cycle target到達は、このauthorizationを発行する根拠ではない。

## 自動化consumer側の受理条件

画面上の最後の一行や固定文字列検索だけで停止してはならない。

`_tools/regulated_phase_terminal_consumer.js`の`validateRegulatedPhaseTerminal(responseText, liveState)`を呼び、`accepted === true`の場合だけ停止する。

consumerは次をすべて確認する。

1. markerが一度だけ最終非空行にある。
2. 直前のresultがlive authorizationと一致する。
3. その直前のevent IDがlive authorizationと一致する。
4. authorization scopeとactive phaseが一致する。
5. successならphase statusが`complete`、errorなら`terminal_error`である。

live stateを取得できない場合、固定文をterminalとして推測せず、必ず非受理にする。

## 禁止

- marker単独で停止する旧実装
- resultとmarkerだけの二行判定
- モデルが生成したevent IDをlive state照合なしで信用すること
- `signal_authorization=null`の間に予約語を説明目的で再掲すること
- checker失敗後に手動でterminal扱いへ上書きすること
