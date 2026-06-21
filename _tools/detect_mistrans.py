#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""誤訳疑い検出器(外部API)。コスト削減の前処理。主=Google AI Studio(gemini-2.5-flash-lite)、
失敗時=OpenRouter無料モデル(gemma-4-26b/qwen3-next/gpt-oss-20b/llama-3.3 を順に試行)へ自動フォールバック。両方ダメなら安全側(risk=1.0)。
役割分離: ここは**意味の誤訳だけ**を recall 優先で抽出する。**口調・キャラ性は一切見ない**(=ペルソナを渡さない)。
LLM(Claude)はこの結果で zh の添付要否を決め、声校正＋最終修正に集中する。

入力: `$WS_TMP/pf_char_batch.tsv`(pending_char の出力。target⇥ns⇥key⇥zh⇥ja)
出力: `$WS_TMP/mistrans_risk.json` = { "<行index>": {"risk":0-1, "reason":"...", "key":"..."} }
使い方: python _tools/detect_mistrans.py [batch.tsv] [--model gemma-4-26b-a4b-it] [--chunk 25]
APIエラー時は該当行を risk=1.0(=zh必須・安全側)にして誤訳網を絶対に落とさない。
"""
import sys, os, json, time, shutil, subprocess, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
SEC = json.load(open(os.path.join(ROOT, "_tools", ".secrets.json"), encoding="utf-8"))
KEY = SEC["google_ai_studio"]


# --- backend=haiku(既定): 無料枠APIに依存せず Claude Haiku を headless で叩く ---
def _find_claude():
    cands = [
        r"C:\Users\kaill\.local\bin\claude.exe",
        os.path.expanduser(r"~\.local\bin\claude.exe"),
        os.path.expandvars(r"%APPDATA%\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    for name in ("claude.exe", "claude.cmd", "claude"):
        p = shutil.which(name)
        if p:
            return p
    return None


CLAUDE_EXE = _find_claude()


def call_haiku(prompt):
    """Claude Haiku を headless(-p)で呼び s/v 判定。Gemini/OpenRouter の無料枠に依存しない。"""
    if not CLAUDE_EXE:
        raise RuntimeError("claude 実体が見つからない(_find_claude)")
    # 検出器はツールを使わない純テキスト分類(JSONL出力のみ)なので権限は不要。
    # --dangerously-skip-permissions は付けない(不要かつ安全側)。
    r = subprocess.run(
        [CLAUDE_EXE, "-p", "--model", "haiku", "--output-format", "json",
         "--allowed-tools", ""],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT,
    )
    raw = r.stdout.decode("utf-8", "replace")
    try:
        return json.loads(raw).get("result", raw)
    except json.JSONDecodeError:
        return raw

PROMPT_HEAD = (
    "あなたは中日翻訳の検査器。各行の zh(中国語原文)と ja(日本語訳)を比べ、2軸で0〜1を付ける。\n"
    "【s = 意味リスク】意味の脱落/付加・否定の反転・数量や数値の違い・固有名詞のズレ・"
    "『誰が誰に何をするか(主体/客体/敬意の向き)』の取り違え・長文の省略。\n"
    "【v = 演技リスク】原文zhが**字義どおりでない含み**(皮肉・反語・煽り・言外の含意・強い感情や感嘆・"
    "古風な言い回し・敬意/register の含み)を持ち、平板な逐語訳では**その含みが失われやすい**度合い。"
    "=校正者が声を作るのに原文を見るべき行ほど高く。※キャラ設定は見ない。原文zhのトーンの有無だけ。\n"
    "**日本語は書き換えない・訳は作らない**。recall優先=どちらも疑わしきは高めに。\n"
    "出力は**1行1JSON(JSONL)**、入力の i だけ、説明文や```は禁止:\n"
    '{"i":<番号>,"s":<0〜1>,"v":<0〜1>,"reason":"<短く。無ければ空>"}\n\n'
    "入力(行ごと i / zh / ja):\n"
)


def call_gemma(prompt, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 4096},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    return d["candidates"][0]["content"]["parts"][0]["text"]


# --- フォールバック: OpenRouter(無料モデルを順に試行)---
ORKEY = SEC.get("openrouter")
OR_MODELS = [
    "google/gemma-4-26b-a4b-it:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]


def call_openrouter(prompt, model):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0, "max_tokens": 4096,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {ORKEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def parse_jsonl(text):
    out = {}
    for line in text.splitlines():
        line = line.strip().strip("`").strip()
        if not line.startswith("{"):
            continue
        try:
            o = json.loads(line)
            if "i" not in o:
                continue
            s = float(o.get("s", o.get("risk", 0)))   # s=意味, v=演技(後方互換でriskをsに)
            v = float(o.get("v", 0))
            out[int(o["i"])] = (s, v, str(o.get("reason", "")))
        except Exception:
            continue
    return out


def load_tsv(tsv):
    meta_lines, rows = [], []
    for ln in open(tsv, encoding="utf-8"):
        if ln.startswith("#"):
            meta_lines.append(ln.rstrip("\n")); continue
        if not ln.strip():
            continue
        parts = ln.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        rows.append({"target": parts[0], "ns": parts[1], "key": parts[2], "zh": parts[3], "ja": parts[4]})
    return meta_lines, rows


def main():
    args = sys.argv[1:]
    backend = args[args.index("--backend") + 1] if "--backend" in args else "haiku"
    model = "gemini-2.5-flash-lite"   # backend=gemini時のみ。gemma-4-31b-it も --model で可(26bは500故障/2.0-lyteは429)
    chunk = 40 if backend == "haiku" else 25   # haikuはCLI起動コストが乗るので大きめチャンクで呼び出し数を削減
    if "--model" in args:
        model = args[args.index("--model") + 1]
    if "--chunk" in args:
        chunk = int(args[args.index("--chunk") + 1])
    th = 0.3
    if "--th" in args:
        th = float(args[args.index("--th") + 1])
    no_rewrite = "--no-rewrite" in args
    inp = next((a for a in args if not a.startswith("--") and (a.endswith(".tsv") or a.endswith(".json"))), os.path.join(TMP, "pf_char_batch.tsv"))
    # 完走監査モード: char_audit.json(全行・full zh)を入力すると、書き換えず「誤訳疑い一覧」を報告。
    audit_mode = inp.endswith(".json")
    if audit_mode:
        data = json.load(open(inp, encoding="utf-8"))
        rows = [{"target": r["target"], "ns": r["ns"], "key": r["key"], "zh": r.get("zh", ""), "ja": r.get("ja", "")} for r in data]
        meta_lines = []
        no_rewrite = True
    else:
        meta_lines, rows = load_tsv(inp)
    # 無料枠のレート制限対策: チャンク間に待機。完走監査(多チャンク)は既定4秒、バッチ(1チャンク)は0。
    sleep = float(args[args.index("--sleep") + 1]) if "--sleep" in args else (4.0 if audit_mode else 0.0)
    risk = {}
    for s in range(0, len(rows), chunk):
        block = rows[s:s + chunk]
        lines = "\n".join(f'[{s+j}] zh: {r["zh"]}\n     ja: {r["ja"]}' for j, r in enumerate(block))
        prompt = PROMPT_HEAD + lines
        got = {}
        if backend == "haiku":
            # 既定: Claude Haiku(無料枠APIに依存しない)を2回試行
            for attempt in range(2):
                try:
                    got = parse_jsonl(call_haiku(prompt))
                    if got:
                        break
                except Exception as e:
                    sys.stderr.write(f"[detect] haiku ERR (chunk {s}) try{attempt}: {e!r}\n")
                    time.sleep(1)
        else:
            # backend=gemini: Google AI Studio(主) を2回試行
            for attempt in range(2):
                try:
                    got = parse_jsonl(call_gemma(prompt, model))
                    if got:
                        break
                except urllib.error.HTTPError as e:
                    sys.stderr.write(f"[detect] google HTTP {e.code} (chunk {s}) try{attempt}: {e.read()[:120]}\n")
                    time.sleep(2)
                except Exception as e:
                    sys.stderr.write(f"[detect] google ERR (chunk {s}) try{attempt}: {e!r}\n")
                    time.sleep(2)
        # 2) ダメなら OpenRouter 無料モデルを順にフォールバック(gemini backend時のみ)
        if not got and backend != "haiku" and ORKEY:
            for orm in OR_MODELS:
                try:
                    got = parse_jsonl(call_openrouter(prompt, orm))
                    if got:
                        sys.stderr.write(f"[detect] fallback OpenRouter={orm} (chunk {s})\n")
                        break
                except Exception as e:
                    sys.stderr.write(f"[detect] OR {orm} ERR (chunk {s}): {e!r}\n")
                    continue
        for j, r in enumerate(block):
            idx = s + j
            if idx in got:
                sv, vv, rs = got[idx]
            else:
                sv, vv, rs = 1.0, 1.0, "no_response(safe)"   # 取りこぼし=安全側でzh必須
            # 注: スコアを `s` に入れると外側ループの「チャンク開始オフセット s」を壊す(idxが小数化する)。必ず別名で受ける。
            risk[str(idx)] = {"s": round(sv, 2), "v": round(vv, 2),
                              "risk": round(max(sv, vv), 2), "reason": rs, "key": r["key"]}
        if sleep:
            time.sleep(sleep)

    out = os.path.join(TMP, "mistrans_risk.json")
    json.dump(risk, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    hi = sum(1 for v in risk.values() if v["risk"] >= 0.7)
    mid = sum(1 for v in risk.values() if 0.3 <= v["risk"] < 0.7)
    lo = len(risk) - hi - mid

    # zhオンデマンド化: バッチTSVを書き換え。risk<th の行は zh を空に(声校正はja＋ペルソナで足りる)。
    # risk>=th の行は zh＋[risk/理由] を残す(Claudeが意味を確認すべき行)。
    kept = 0
    if not no_rewrite:
        with open(inp, "w", encoding="utf-8") as f:
            for ml in meta_lines:
                f.write(ml + "\n")
            for j, r in enumerate(rows):
                v = risk.get(str(j), {"risk": 1.0, "s": 1.0, "v": 1.0, "reason": "?"})
                if v["risk"] >= th:
                    # s=意味リスク, v=演技リスク。校正者はどちらが高いかで読み方を変える。
                    zh = f'[s{v.get("s","?")}/v{v.get("v","?")} {v.get("reason","")}] {r["zh"]}'; kept += 1
                else:
                    zh = ""   # 両軸とも低=意味も演技もOK→zh不要(トークン削減)
                f.write("\t".join([r["target"], r["ns"], r["key"], zh, r["ja"]]) + "\n")

    v_only = sum(1 for v in risk.values() if v.get("v", 0) >= th and v.get("s", 0) < th)
    print(f"[detect] {len(rows)}行 backend={backend}{'/'+model if backend!='haiku' else ''} th={th} -> {out}")
    print(f"  zh復元 risk>=0.7={hi} / 0.3-0.7={mid} / 低={lo}  (うち演技リスク主導の復元={v_only}件=意味OKだが声に原文が要る行)")
    if audit_mode:
        # 完走監査: 疑い(s/v いずれか>=th)を一覧報告。これだけ Claude が zh と突き合わせて確認する。
        sus = sorted(((float(v["risk"]), str(k)) for k, v in risk.items() if float(v["risk"]) >= th), reverse=True)
        rep = os.path.join(TMP, "mistrans_audit.txt")
        with open(rep, "w", encoding="utf-8") as f:
            for rk, k in sus:
                r = rows[int(k)]; v = risk[k]
                f.write(f'[s{v.get("s","?")}/v{v.get("v","?")} {v.get("reason","")}] {r["key"]}\n  zh: {r["zh"]}\n  ja: {r["ja"]}\n')
        print(f"  【完走監査】疑い {len(sus)}件 -> {rep}(Claudeはこの件だけzh突合)")
    elif not no_rewrite:
        print(f"  バッチTSV書換: zh残し {kept}行 / zh削除 {len(rows)-kept}行(=入力削減) -> {inp}")


if __name__ == "__main__":
    main()
