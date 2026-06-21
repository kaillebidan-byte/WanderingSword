#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フェーズ2校正の自動ループ(headless Sonnet)。

1バッチ=1新claudeプロセス(文脈肥大なし)。char_progress.jsonで再開可。
未確定/保留に当たる or 進捗停滞で自動停止。トークン枯渇は sleep して再開。

PowerShell版(loop_proofread.ps1)はPS5.1のJSON parse・cmdクォート・$env:APPDATA・
Start-Processの癖で環境依存に壊れる。本Python版はそれらを一切踏まない。
どこで実行してもよい(cmd / VSCode / PowerShell / どれでも):

    python _tools/loop_proofread.py [--max 500] [--sleep-on-limit 1800]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta

PROJ = r"C:\Users\kaill\Claude\Projects\Wandering Sword翻訳"
P4 = os.path.join(PROJ, "_phase4_proofread")
WS_TMP = os.path.join(PROJ, "_ws_tmp")
LOG = os.path.join(WS_TMP, "loop_proofread.log")
PROMPT_FILE = os.path.join(WS_TMP, "loop_prompt.txt")  # 校正指示(UTF-8)。stdinから生バイト投入=CJK化け回避


def find_claude():
    """claude実体を解決。$env:APPDATAに依存せず複数候補+PATHから探す。
    .cmdではなく実PE(bin/claude.exe)を優先(subprocessで直接起動できる)。"""
    cands = [
        r"C:\Users\kaill\.local\bin\claude.exe",  # ネイティブインストール(主)
        os.path.expanduser(r"~\.local\bin\claude.exe"),
        os.path.expandvars(r"%APPDATA%\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"),
        r"C:\Users\kaill\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe",
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    # PATHからのフォールバック(.exe優先)
    for name in ("claude.exe", "claude.cmd"):
        p = shutil.which(name)
        if p:
            return p
    return None


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"{ts} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_prog():
    """char_progress.json -> dict(ci,pos) or None"""
    try:
        with open(os.path.join(P4, "char_progress.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def run_batch(claude_exe):
    """claudeを1バッチ起動。--output-format jsonでトークン使用量も取得。
    戻り値: (text, usage, model_usage, stderr_text)
      usage       = top-level usage(=Sonnet本体のみ。Haiku補助は含まない)
      model_usage = modelUsage(モデル別。costUSD等。Haikuもここに別計上)"""
    with open(PROMPT_FILE, "rb") as stdin_f:
        r = subprocess.run(
            [claude_exe, "-p", "--model", "sonnet", "--dangerously-skip-permissions",
             "--output-format", "json"],
            stdin=stdin_f,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # stderr分離: CLIの警告がJSONに混入しないよう
            cwd=PROJ,
        )
    raw = r.stdout.decode("utf-8", errors="replace")
    stderr_text = r.stderr.decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
        text = data.get("result", raw)
        usage = data.get("usage", {})
        model_usage = data.get("modelUsage", {})
    except json.JSONDecodeError:
        text = raw
        usage = {}
        model_usage = {}
    return text, usage, model_usage, stderr_text


LIMIT_RE = re.compile(
    r"session limit|usage limit|rate limit|quota|too many requests|"
    r"hit your (session|usage)|resets?\s+\d|利用上限|上限",
    re.IGNORECASE,
)
RESET_RE = re.compile(r"resets?\s+(\d{1,2}):(\d{2})\s*(am|pm)?", re.IGNORECASE)
STOP_RE = re.compile(r"未確定|保留|status:\s*確定 でない")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=500, help="最大イテレーション(暴走止め)")
    ap.add_argument("--sleep-on-limit", type=int, default=1800, help="トークン枯渇時の待機秒(既定30分)")
    args = ap.parse_args()

    # コンソールがcp932だと日本語printでcrashするのでUTF-8に固定。
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    os.environ["WS_TMP"] = WS_TMP
    os.environ["PYTHONIOENCODING"] = "utf-8"

    claude_exe = find_claude()
    if not claude_exe:
        log("✗ claude実体が見つからない。`where claude` で場所を確認して find_claude() の候補に追加して。")
        sys.exit(1)

    with open(os.path.join(P4, "by_character.json"), encoding="utf-8") as f:
        order = json.load(f)["order"]
    total = len(order)

    log(f"=== loop開始 total={total} claude={claude_exe} ===")
    stall = 0
    total_in = total_out = total_cache = 0
    total_cost = 0.0
    for i in range(1, args.max + 1):
        p = get_prog()
        if p is None or p["ci"] >= total:
            ci = p["ci"] if p else "?"
            log(f"全キャラ完了(ci={ci}/{total})。終了。")
            break
        cur = order[p["ci"]]
        log(f"[{i}] 開始 ci={p['ci']} pos={p['pos']} キャラ={cur}")

        text, usage, model_usage, stderr_text = run_batch(claude_exe)

        # トークン集計・表示(top-level usage = Sonnet本体のみ)
        in_tok  = usage.get("input_tokens", 0)
        out_tok = usage.get("output_tokens", 0)
        cache_tok = (usage.get("cache_read_input_tokens", 0)
                     + usage.get("cache_creation_input_tokens", 0))
        total_in  += in_tok
        total_out += out_tok
        total_cache += cache_tok
        # コスト = 全モデル合算(Sonnet本体 + Haiku補助)。止め時判断の主指標。
        batch_cost = sum(m.get("costUSD", 0.0) for m in model_usage.values())
        total_cost += batch_cost
        if in_tok or out_tok or batch_cost:
            log(f"  tokens(Sonnet): in={in_tok:,} out={out_tok:,} cache={cache_tok:,}"
                f"  |  cost ${batch_cost:.4f} (累計 ${total_cost:.2f})"
                f"  |  累計tok in={total_in:,} out={total_out:,} cache={total_cache:,}")

        with open(LOG, "a", encoding="utf-8") as f:
            f.write(text + "\n")
            if stderr_text:
                f.write("[stderr]\n" + stderr_text + "\n")

        # limit/stopの判定はtext+stderr両方を対象に
        combined = text + "\n" + stderr_text

        # 結果判定: 未確定/保留 → Opus介入が必要なので停止
        if STOP_RE.search(combined):
            log(f"→ 未確定/保留に到達({cur})。Opus介入が必要。停止。")
            break

        # セッション/トークン上限 → リセット時刻まで(拾えれば)待機して再試行
        if LIMIT_RE.search(combined):
            wait = args.sleep_on_limit
            m = RESET_RE.search(combined)
            if m:
                h, mn, ap_ = int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()
                if ap_ == "pm" and h < 12:
                    h += 12
                if ap_ == "am" and h == 12:
                    h = 0
                now = datetime.now()
                target = now.replace(hour=h, minute=mn, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                wait = int((target - now).total_seconds()) + 120
            log(f"→ セッション/トークン上限に到達。{wait // 60}分待機してリセット後に再試行。")
            time.sleep(wait)
            continue

        # 進捗が進んだか(停滞検知)
        p2 = get_prog()
        if p2 and p2["ci"] == p["ci"] and p2["pos"] == p["pos"]:
            stall += 1
            log(f"→ 進捗が動かず(stall={stall})。応答末尾: {text[-200:]}")
            if stall >= 2:
                log("→ 2回連続で停滞。異常とみて停止。")
                break
        else:
            stall = 0
            log(f"→ 前進 ci={p2['ci']} pos={p2['pos']}")
        time.sleep(3)

    log(f"=== loop終了  累計cost ${total_cost:.2f}  "
        f"tok(Sonnet) in={total_in:,} out={total_out:,} cache={total_cache:,} ===")


if __name__ == "__main__":
    main()
