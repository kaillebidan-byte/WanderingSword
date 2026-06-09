#!/usr/bin/env python3
"""キャラ単位の校正: 現在のキャラの次N行を 原文zh・現訳ja つきで出力。"""
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
P4 = os.path.join(ROOT, "_phase4_proofread")
TMP = os.environ.get("WS_TMP", "/tmp")

def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    data = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    src = json.load(open(f"{P4}/source_zh.json", encoding="utf-8"))
    order, lines = data["order"], data["lines"]
    ja_cache = {}
    def ja_of(t, ns, key):
        if t not in ja_cache:
            _, ja_cache[t], *_ = locres.parse(wlp(t))
        return ja_cache[t].get(ns + "\x1f" + key, "")

    if len(sys.argv) > 2 and sys.argv[1] == "--audit":
        ch = sys.argv[2]
        rows = lines.get(ch, [])
        out = [{"target": t, "ns": ns, "key": k, "zh": src.get(t+"\x1f"+ns+"\x1f"+k, ""),
                "ja": ja_of(t, ns, k)} for t, ns, k in rows]
        json.dump(out, open(f"{TMP}/char_audit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        sys.stderr.write(f"[audit] {ch}: {len(out)} -> {TMP}/char_audit.json\n")
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    prog = json.load(open(f"{P4}/char_progress.json", encoding="utf-8"))
    ci, pos = prog["ci"], prog["pos"]
    while ci < len(order) and pos >= len(lines[order[ci]]):
        ci += 1; pos = 0
    if ci >= len(order):
        print("全キャラ校正完了"); json.dump([], open(f"{TMP}/pf_char_batch.json", "w")); return
    ch = order[ci]; rows = lines[ch][pos:pos+n]
    out = [{"target": t, "ns": ns, "key": k, "zh": src.get(t+"\x1f"+ns+"\x1f"+k, ""),
            "ja": ja_of(t, ns, k)} for t, ns, k in rows]
    total = len(lines[ch])
    completes = (pos + len(out)) >= total
    meta = {"character": ch, "pos": pos, "total": total, "completes_character": completes,
            "persona_card": f"10_人物/{ch}.md"}
    json.dump({"meta": meta, "lines": out}, open(f"{TMP}/pf_char_batch.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    sys.stderr.write(f"[{ch}] {pos}-{pos+len(out)}/{total}\n")
    print(json.dumps({"meta": meta, "lines": out}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
