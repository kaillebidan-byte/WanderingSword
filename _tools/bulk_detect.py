# -*- coding: utf-8 -*-
"""全(確定)キャラの誤訳/演技リスクを Haiku で事前一括 detect → detect_risk.json にキャッシュ。
校正ループはこのキャッシュを pending_char 経由で読む(inline detect 不要・バッチ出力が上限内に収まる)。

使い方:
  python _tools/bulk_detect.py [--from-ci 724] [--max-chars N] [--workers 8] [--chunk 40] [--reason-th 0.4] [--th 0.3]
- 対象: order[from_ci:] のうち persona status:確定 のキャラ(保留/未確定は自動スキップ)。
- 再開可: detect_risk.json に既存の行キーはスキップ。Ctrl-C しても途中まで保存済み。
- 出力: _phase4_proofread/detect_risk.json  = { "target\x1fns\x1fkey": {"s":..,"v":..,"risk":..,"reason":".."} }
"""
import sys, os, json, glob, time, re, subprocess, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
# サブスクの5h利用上限/レート上限を検知して綺麗に停止するためのパターン(loop_proofreadと同系)。
LIMIT_RE = re.compile(r"usage limit|rate limit|session limit|quota|too many requests|"
                      r"resets?\s+\d|hit your (session|usage)|利用上限|上限に達", re.IGNORECASE)
STOP = threading.Event()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
import detect_mistrans as dm   # call_haiku/parse_jsonl/PROMPT_HEAD/CLAUDE_EXE を再利用
P4 = os.path.join(ROOT, "_phase4_proofread")
CACHE = os.path.join(P4, "detect_risk.json")
GROQ_KEY = dm.SEC.get("groq", "")
GROQ_MODEL = "openai/gpt-oss-120b"   # 理由が的確。速度優先なら llama-3.3-70b-versatile
GROQ_MAXTOK = 4000   # main で chunk に応じ再設定。gpt-oss free の TPM=8000 を超えないこと(入力+これ<8000)。


def call_groq(prompt, model=None):
    """Groq(OpenAI互換・無料枠・超高速)。CFのbot遮断を避けるため User-Agent を付ける。429はsleep再試行。"""
    model = model or GROQ_MODEL
    # max_tokens は TPM(=8000 free) を超えないよう chunk連動(GROQ_MAXTOK)。入力+max_tokens<8000 が必須。
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "max_tokens": GROQ_MAXTOK}).encode()
    # 無料枠のRPM/TPMは毎分リセット。429は辛抱強く待てば通る → 長めのバックオフで粘る(Haikuに落とさない)。
    for attempt in range(7):
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions", data=body,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json",
                     "User-Agent": "curl/8.4.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Retry-After ヘッダがあれば尊重、無ければ漸増(最大45s)
                ra = e.headers.get("retry-after")
                time.sleep(min(float(ra), 60) if ra and ra.replace('.', '').isdigit() else min(8 + attempt * 7, 45))
                continue
            raise
    raise RuntimeError("groq 429 retries exhausted")


def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]


def arg(name, default, cast=str):
    a = sys.argv
    return cast(a[a.index(name) + 1]) if name in a else default


def status_of(name):
    p = os.path.join(ROOT, "10_人物", name + ".md")
    if not os.path.isfile(p):
        return "NOFILE"
    m = re.search(r"status:\s*(\S+)", open(p, encoding="utf-8").read(600))
    return m.group(1) if m else "NONE"


# claude -p の起動コスト(=毎回まっさらエージェント)を軽くするため、プロジェクトCLAUDE.mdを読まない空dirから起動。
HAIKU_CWD = os.path.join(os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp")), "_haiku_cwd")
os.makedirs(HAIKU_CWD, exist_ok=True)


def call_haiku_cost(prompt):
    """call_haiku と同じ呼び出しだが total_cost_usd も返す(計測用)。権限不要(ツール無効)。
    cwd=空dir でプロジェクトCLAUDE.md/メモリのロードを避け、1起動あたりの土台トークンを削る。"""
    r = subprocess.run(
        [dm.CLAUDE_EXE, "-p", "--model", "haiku", "--output-format", "json", "--allowed-tools", ""],
        input=prompt.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=HAIKU_CWD,
    )
    raw = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    # 上限メッセージは stderr 側に出ることがある。LIMIT_RE 検知のため text に併合(parse_jsonlは{始まり行だけ拾うので無害)。
    try:
        d = json.loads(raw)
        return (d.get("result", raw) + "\n" + err), float(d.get("total_cost_usd", 0) or 0)
    except json.JSONDecodeError:
        return (raw + "\n" + err), 0.0


def main():
    from_ci = arg("--from-ci", 724, int)
    max_chars = arg("--max-chars", 0, int)
    workers = arg("--workers", 8, int)
    chunk = arg("--chunk", 40, int)
    reason_th = arg("--reason-th", 0.4, float)
    backend = arg("--backend", "auto")   # auto=Groq優先+Haikuフォールバック(既定) | groq | haiku
    # Groq gpt-oss free の TPM=8000 を超えないよう出力上限を chunk連動に(入力+max_tokens<8000)。
    global GROQ_MAXTOK
    GROQ_MAXTOK = arg("--groq-maxtok", min(chunk * 150 + 800, 6000), int)

    data = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    src = json.load(open(f"{P4}/source_zh.json", encoding="utf-8"))
    order, lines = data["order"], data["lines"]

    chars = [order[i] for i in range(from_ci, len(order)) if status_of(order[i]) == "確定"]
    if max_chars:
        chars = chars[:max_chars]

    ja_cache = {}
    def ja_of(t, ns, k):
        if t not in ja_cache:
            _, ja_cache[t], *_ = locres.parse(wlp(t))
        return ja_cache[t].get(ns + "\x1f" + k, "")

    risk = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    # mop-up: 取りこぼし(no_response=安全側1.0)をキャッシュから外し、再detect対象に戻す。
    # 使い方: --redo-failed --chunk 25 (truncationしない小チャンクで埋め直す)
    if "--redo-failed" in sys.argv:
        before = len(risk)
        risk = {k: v for k, v in risk.items() if v.get("reason") != "no_response(safe)"}
        print(f"[bulk] redo-failed: no_response {before - len(risk)}行を除去 → 再detect対象", flush=True)

    # reason を高リスク行だけに絞って Haiku 出力を圧縮(速度)。フォーマットは detect_mistrans と同一。
    HEAD = dm.PROMPT_HEAD.replace(
        "入力(行ごと i / zh / ja):\n",
        f"※reason は s>={reason_th} か v>={reason_th} の行だけ簡潔に。それ以外は \"reason\":\"\" にせよ。\n"
        "入力(行ごと i / zh / ja):\n")

    tasks = []
    total_lines = 0
    for ch in chars:
        items = [(t + "\x1f" + ns + "\x1f" + k, src.get(t + "\x1f" + ns + "\x1f" + k, ""), ja_of(t, ns, k))
                 for t, ns, k in lines[ch]]
        total_lines += len(items)
        for s in range(0, len(items), chunk):
            block = items[s:s + chunk]
            if all(lk in risk for lk, _, _ in block):
                continue
            tasks.append(block)

    print(f"[bulk] backend={backend}(groq={GROQ_MODEL}) / 対象 {len(chars)}キャラ / {total_lines}行 / 未処理チャンク {len(tasks)} / workers={workers} chunk={chunk}", flush=True)
    if not tasks:
        print("[bulk] 未処理なし(全キャッシュ済み)")
        return

    # 試行順: auto=Groq(無料)→失敗チャンクだけHaiku(Claude枠少々) / groq=Groqのみ / haiku=Haikuのみ
    TRY_ORDER = {"auto": ["groq", "haiku"], "groq": ["groq"], "haiku": ["haiku"]}.get(backend, ["groq", "haiku"])

    def do_block(block):
        # 既に上限検知で停止指示が出ていれば即スキップ(キャッシュ汚染しない)。
        if STOP.is_set():
            return "skip", None, 0.0
        lines_txt = "\n".join(f'[{j}] zh: {zh}\n     ja: {ja}' for j, (lk, zh, ja) in enumerate(block))
        prompt = HEAD + lines_txt
        got, cost = {}, 0.0
        for bk in TRY_ORDER:
            for attempt in range(2):
                try:
                    if bk == "groq":
                        text = call_groq(prompt)
                    else:
                        text, c = call_haiku_cost(prompt); cost += c
                    if LIMIT_RE.search(text or ""):   # Haikuの5h利用上限に到達
                        STOP.set()
                        return "limit", None, cost
                    got = dm.parse_jsonl(text)
                    if got:
                        break
                except Exception:
                    time.sleep(1)
            if got:
                break   # このバックエンドで取れたら次のフォールバックには行かない
        if not got:
            # 全バックエンド失敗。キャッシュせず次回再開でリトライさせる。
            return "fail", None, cost
        res = {}
        for j, (lk, zh, ja) in enumerate(block):
            s, v, rs = got.get(j, (1.0, 1.0, "no_response(safe)"))
            res[lk] = {"s": round(s, 2), "v": round(v, 2), "risk": round(max(s, v), 2), "reason": rs}
        return "ok", res, cost

    t0 = time.time(); done = 0; ok = 0; failed = 0; total_cost = 0.0; limit_hit = False
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(do_block, b) for b in tasks]
        try:
            for f in as_completed(futs):
                status, res, cost = f.result()
                total_cost += cost; done += 1
                if status == "ok":
                    risk.update(res); ok += 1
                elif status == "limit":
                    limit_hit = True
                elif status == "fail":
                    failed += 1
                if ok and (ok % 5 == 0 or done == len(futs)):
                    json.dump(risk, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
                    el = time.time() - t0
                    print(f"  ok{ok}/未{len(futs)} 経過{el:.0f}s  {el/max(ok,1):.1f}s/ok  "
                          f"cost ${total_cost:.4f}  cache={len(risk)}行", flush=True)
        finally:
            json.dump(risk, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    el = time.time() - t0
    json.dump(risk, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[bulk] 終了 ok={ok} fail={failed} {el:.0f}s  総cost ${total_cost:.4f}  cache={len(risk)}行 -> {CACHE}")
    if limit_hit:
        print("[bulk] ⚠ 利用上限/レート上限を検知して停止。未処理分はキャッシュ未書込なので、"
              "上限リセット後に**同じコマンドを再実行**すれば続きから自動再開する。")
    elif failed:
        print(f"[bulk] ⚠ {failed}チャンクが上限以外で失敗(未キャッシュ)。再実行でリトライされる。")
    else:
        print("[bulk] 全チャンク完了。")
    if ok:
        print(f"[bulk] 概算: {el/ok:.1f}s/ok・${total_cost/ok:.4f}/ok")


if __name__ == "__main__":
    main()
