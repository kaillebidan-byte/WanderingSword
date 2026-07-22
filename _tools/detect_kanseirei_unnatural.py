#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完成例の不自然JA検出器。Claude Haiku で各quoteを「日本語として自然か」判定。
ペルソナは渡さない＝口語/書き言葉/古風いずれでも「日本語として通っているか」だけ見る。

入力: _ws_tmp/all_kanseirei.json (extract_all_kanseirei.py の出力)
出力: _ws_tmp/kanseirei_unnatural.json = [{"char","section","quote","u":0-1,"reason"}]
"""
import sys, os, json, time, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))

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
        if p: return p
    return None

CLAUDE_EXE = _find_claude()

PROMPT_HEAD = (
    "あなたは日本語の文字種・語法の厳密な検査器。中国語武侠RPGの**日本語訳セリフ**群を1行ずつ検査する。\n"
    "各行に【u = 不自然度 0〜1】を付ける。**recall優先**=疑わしきは高めに。**書き換えはしない**。\n"
    "\n"
    "■ 高く（u>=0.7）すべきもの — 日本語として失格 / 中国語残置:\n"
    "  1) 中国語感嘆詞/オノマトペが日本語に置換されず残置: 啧/啧啧/呵/呵呵/呵呵呵/嘿/嘿嘿/嗯/咦/哎/哟/唉/啰/喔/嗨\n"
    "     ※「ふふ（呵呵）」のような原文併記の括弧パターンも**翻訳ではない=高く**（プレイヤーが中国語を見ることになる）\n"
    "     ※「ははは」「ふふ」「ちっ」など日本語化済みは低くてよい\n"
    "  2) 簡体字が日本字形に変換されず残置: 这/没/还/给/让/说/话/见/过/现/从/觉/龙/传/应/务/设/备/听/枫/云/凤/丰/灯/树/桥/边/为/无/东/车/师/双/与/対/产/进/选/区/区区/将/争 等\n"
    "     ※「学/国」など日本語常用字形と同じものはOK\n"
    "  3) 完全に中国語のまま未訳: 「成了」「混账」「百死莫赎」「為将之心」「出尔反尔」「有古怪」「你」「惊讶」「算了算了」「喂」「万不可再収此物」「宁以此心入无间」「秋日香飘云水间」等\n"
    "  4) 中国語成語/4字熟語が直訳されず原文のまま: 「一手交銭一手交貨」「大庭広衆」等\n"
    "  5) 係り受け破綻・意味が通らない: 例『この好敵手が手を離せなくて』『先入観がお有りのようで』『水臭いのはなしです』\n"
    "  6) 敬語誤用・不適切活用: 「お+和語+です/ある」(『お有り』『お大切に』『お納めください＝感謝受領で誤用』)\n"
    "\n"
    "■ 中程度（u=0.4〜0.6）— MT臭強いが意味は通る:\n"
    "  7) 直訳臭の反復: 「〜することができる」「〜ということになっている」「〜とでも？」「〜ところだった」過剰\n"
    "  8) 古語/敬語の三重盛り: 「ともあろう方が、かような〜とはな」3つ以上の古語助詞重ね\n"
    "  9) 中国語の語順を引きずる: 動詞句が日本語の自然語順から外れている\n"
    "\n"
    "■ 低く（u<=0.3）すべきもの — 不自然ではない:\n"
    "  - register選択（古風常体・武侠調・侠客の粗暴口調・敬語・老人口調 等）は全て許容\n"
    "  - 短い相槌・名乗り・固有名詞だけの行\n"
    "  - 中国の固有名詞（人名・地名・武功名）の漢字表記（音訳・意訳どちらでも、訳語として確立してれば許容）\n"
    "  - 古典引用や読み下し（典故）の維持\n"
    "  - （原文併記「ふふ（呵呵）」は許容しない＝高く判定すべき。許容例ではない）\n"
    "\n"
    "出力は**1行1JSON(JSONL)**、入力の i のみ、説明文や```は禁止。**全行必ず出力**:\n"
    '{"i":<番号>,"u":<0〜1>,"reason":"<短く具体的に・該当条文1〜9番号を含めて>"}\n\n'
    "入力(i / ja):\n"
)

def call_claude(prompt, model="haiku", timeout=600):
    if not CLAUDE_EXE:
        raise RuntimeError("claude exe not found")
    try:
        r = subprocess.run(
            [CLAUDE_EXE, "-p", "--model", model, "--output-format", "json",
             "--allowed-tools", ""],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude {model} timed out after {timeout}s")
    raw = r.stdout.decode("utf-8", "replace")
    try:
        return json.loads(raw).get("result", raw)
    except json.JSONDecodeError:
        return raw

# 後方互換
def call_haiku(prompt):
    return call_claude(prompt, "haiku")

def parse_jsonl(text):
    out = {}
    for line in text.splitlines():
        line = line.strip().strip("`").strip()
        if not line.startswith("{"):
            continue
        try:
            o = json.loads(line)
            if "i" not in o: continue
            u = float(o.get("u", o.get("risk", 0)))
            out[int(o["i"])] = (u, str(o.get("reason", "")))
        except Exception:
            continue
    return out

def main():
    args = sys.argv[1:]
    model = args[args.index("--model")+1] if "--model" in args else "haiku"
    chunk = int(args[args.index("--chunk")+1]) if "--chunk" in args else (300 if model == "sonnet" else 40)
    th = float(args[args.index("--th")+1]) if "--th" in args else 0.5
    inp = os.path.join(TMP, "all_kanseirei.json")
    suffix = f"_{model}" if model != "haiku" else ""
    out_json = os.path.join(TMP, f"kanseirei_unnatural{suffix}.json")
    rows = json.load(open(inp, encoding="utf-8"))
    if "--limit" in args:
        rows = rows[:int(args[args.index("--limit")+1])]
    # 再開: 既存結果があれば読み込み、u==0 かつ reason==no_response の行のみ再判定
    results = [None] * len(rows)
    if "--resume" in args and os.path.exists(out_json):
        try:
            prev = json.load(open(out_json, encoding="utf-8"))
            for i in range(min(len(prev), len(rows))):
                if prev[i] and prev[i].get("reason") != "no_response":
                    results[i] = prev[i]
            done_n = sum(1 for r in results if r is not None)
            sys.stderr.write(f"[detect_kr] resume: {done_n}/{len(rows)} already done\n")
        except Exception as e:
            sys.stderr.write(f"[detect_kr] resume failed: {e!r}\n")
    for s in range(0, len(rows), chunk):
        # スキップ: chunk内のすべてが done なら飛ばす
        if all(results[i] is not None for i in range(s, min(s+chunk, len(rows)))):
            sys.stderr.write(f"[detect_kr] skip chunk {s} (all done)\n")
            continue
        block = rows[s:s+chunk]
        lines = "\n".join(f'[{s+j}] ja: {r["quote"]}' for j, r in enumerate(block))
        prompt = PROMPT_HEAD + lines
        got = {}
        for attempt in range(2):
            try:
                got = parse_jsonl(call_claude(prompt, model))
                if got: break
            except Exception as e:
                sys.stderr.write(f"[detect_kr] {model} ERR chunk{s} try{attempt}: {e!r}\n")
                time.sleep(1)
        for j, r in enumerate(block):
            idx = s+j
            if idx in got:
                u, rs = got[idx]
            else:
                u, rs = 0.0, "no_response"
            results[idx] = {"char": r["char"], "section": r["section"], "quote": r["quote"],
                            "u": round(u, 2), "reason": rs}
        sys.stderr.write(f"[detect_kr] {s+len(block)}/{len(rows)} (chunk size {chunk}, model {model})\n")
        # 増分保存: 各チャンク完了ごとに上書き
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    hi = sum(1 for r in results if r["u"] >= th)
    print(f"[detect_kr] {len(rows)} quotes / model={model} chunk={chunk} -> {out_json}")
    print(f"  u>={th}: {hi}件")

if __name__ == "__main__":
    main()
