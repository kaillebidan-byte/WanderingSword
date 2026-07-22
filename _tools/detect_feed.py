# -*- coding: utf-8 -*-
"""永続Haikuセッション用 detect 給餌/反映ヘルパ(claude -p の毎回コールド起動を避ける)。

  next [N]   : 未detect行(キャッシュ無し or no_response)を N件 給餌。
               出力 -> $WS_TMP/detect_feed.tsv  (i<TAB>zh<TAB>ja  ※#で残数ヘッダ)
                       $WS_TMP/detect_feed_map.json  (i -> 行キー)
               残り0なら "[feed] 残り0 (完了)" を表示。
  apply <f>  : エージェントの JSONL 採点ファイル f を detect_risk.json にマージ。
               各行 {"i":<番号>,"s":<0-1>,"v":<0-1>,"reason":"..."} 。i は map で行キーに対応。
               反映数と残り未detect数を表示。

行キー = target\x1fns\x1fkey。閾値・zhオンデマンドは pending_char 側で適用するので、ここは生スコアを貯めるだけ。
"""
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
P4 = os.path.join(ROOT, "_phase4_proofread")
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
CACHE = os.path.join(P4, "detect_risk.json")
FEED = os.path.join(TMP, "detect_feed.tsv")
FMAP = os.path.join(TMP, "detect_feed_map.json")
import re

def status_of(n):
    p = os.path.join(ROOT, "10_人物", n + ".md")
    if not os.path.isfile(p): return "X"
    m = re.search(r"status:\s*(\S+)", open(p, encoding="utf-8").read(600))
    return m.group(1) if m else "X"

def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def load_cache():
    return json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}

def needs(risk, key):
    v = risk.get(key)
    return (v is None) or (v.get("reason") == "no_response(safe)")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
    risk = load_cache()

    if cmd == "apply":
        f = sys.argv[2]
        fmap = json.load(open(FMAP, encoding="utf-8"))
        n = 0
        for line in open(f, encoding="utf-8"):
            line = line.strip().strip("`").strip()
            if not line.startswith("{"):
                continue
            try:
                o = json.loads(line)
                key = fmap[str(int(o["i"]))]
            except Exception:
                continue
            s = float(o.get("s", 0)); v = float(o.get("v", 0))
            risk[key] = {"s": round(s, 2), "v": round(v, 2),
                         "risk": round(max(s, v), 2), "reason": str(o.get("reason", ""))}
            n += 1
        json.dump(risk, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        # 残り
        data = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
        order, lines = data["order"], data["lines"]
        rem = 0
        for ch in (order[i] for i in range(724, len(order)) if status_of(order[i]) == "確定"):
            for t, ns, k in lines[ch]:
                if needs(risk, t + "\x1f" + ns + "\x1f" + k): rem += 1
        print(f"[feed] {n}行 反映 -> detect_risk.json  / 残り未detect {rem}行")
        return

    # next
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    data = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    src = json.load(open(f"{P4}/source_zh.json", encoding="utf-8"))
    order, lines = data["order"], data["lines"]
    ja_cache = {}
    def ja_of(t, ns, k):
        if t not in ja_cache:
            _, ja_cache[t], *_ = locres.parse(wlp(t))
        return ja_cache[t].get(ns + "\x1f" + k, "")
    picked, total_rem = [], 0
    for ch in (order[i] for i in range(724, len(order)) if status_of(order[i]) == "確定"):
        for t, ns, k in lines[ch]:
            key = t + "\x1f" + ns + "\x1f" + k
            if needs(risk, key):
                total_rem += 1
                if len(picked) < N:
                    picked.append((key, src.get(key, ""), ja_of(t, ns, k)))
    fmap = {}
    def esc(s): return (s or "").replace("\t", " ").replace("\r", " ").replace("\n", " ")
    with open(FEED, "w", encoding="utf-8") as f:
        f.write(f"# 給餌 {len(picked)}行 / 残り未detect {total_rem}行。各行 i<TAB>zh<TAB>ja。これを採点しJSONLで返す。\n")
        for i, (key, zh, ja) in enumerate(picked):
            fmap[str(i)] = key
            f.write(f"{i}\t{esc(zh)}\t{esc(ja)}\n")
    json.dump(fmap, open(FMAP, "w", encoding="utf-8"), ensure_ascii=False)
    if not picked:
        print("[feed] 残り0 (完了)")
    else:
        print(f"[feed] {len(picked)}行 給餌 -> {FEED}  / 残り未detect {total_rem}行")

if __name__ == "__main__":
    main()
