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

    if len(sys.argv) > 1 and sys.argv[1] == "--audit":
        ch = os.environ.get("WS_CHAR") or (sys.argv[2] if len(sys.argv) > 2 else "")
        rows = lines.get(ch, [])
        out = [{"target": t, "ns": ns, "key": k, "zh": src.get(t+"\x1f"+ns+"\x1f"+k, ""),
                "ja": ja_of(t, ns, k)} for t, ns, k in rows]
        json.dump(out, open(f"{TMP}/char_audit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # NG語grep用に ja本文だけのテキストも出す(zh混入を避け、grepが軽い)。stdout全文ダンプはしない。
        open(f"{TMP}/char_audit.txt", "w", encoding="utf-8").write("\n".join(r["ja"] for r in out))
        sys.stderr.write(f"[audit] {ch}: {len(out)} -> {TMP}/char_audit.json (+.txt)\n")
        print(f"[audit] {ch}: {len(out)}行 -> {TMP}/char_audit.json / .txt(NG語grep用)")
        return

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    prog = json.load(open(f"{P4}/char_progress.json", encoding="utf-8"))
    ci, pos = prog["ci"], prog["pos"]
    while ci < len(order) and pos >= len(lines[order[ci]]):
        ci += 1; pos = 0
    if ci >= len(order):
        print("全キャラ校正完了"); open(f"{TMP}/pf_char_batch.tsv", "w", encoding="utf-8").write("#DONE\n"); return
    ch = order[ci]; rows = lines[ch][pos:pos+n]
    out = [{"target": t, "ns": ns, "key": k, "zh": src.get(t+"\x1f"+ns+"\x1f"+k, ""),
            "ja": ja_of(t, ns, k)} for t, ns, k in rows]
    # detectキャッシュ(bulk_detect の detect_risk.json)があれば zhオンデマンド化:
    # 低リスク行の zh を空にして校正バッチの出力を絞る(32K出力上限対策)。未detect行は安全側でzh保持。
    rp = f"{P4}/detect_risk.json"
    if os.path.exists(rp):
        risk = json.load(open(rp, encoding="utf-8"))
        TH = 0.3
        for r in out:
            v = risk.get(r["target"] + "\x1f" + r["ns"] + "\x1f" + r["key"])
            if v is None:
                continue
            if v["risk"] < TH:
                r["zh"] = ""
            else:
                r["zh"] = f'[s{v["s"]}/v{v["v"]} {v["reason"]}] {r["zh"]}'

    total = len(lines[ch])
    completes = (pos + len(out)) >= total
    meta = {"character": ch, "pos": pos, "total": total, "completes_character": completes,
            "persona_card": f"10_人物/{ch}.md"}
    # TSV出力(コスト削減): フィールド名・JSON整形を排し1行1レコード。LLMはこの .tsv を読む。
    # stdoutには要約1行だけ(全文の二重読み込みを避ける)。
    def esc(s): return (s or "").replace("\t", " ").replace("\r", " ").replace("\n", " ")
    tsv = f"{TMP}/pf_char_batch.tsv"
    with open(tsv, "w", encoding="utf-8") as fp:
        fp.write("#META\t" + json.dumps(meta, ensure_ascii=False) + "\n")
        fp.write("#COLS\ttarget\tns\tkey\tzh\tja\n")
        for r in out:
            fp.write("\t".join([r["target"], r["ns"], r["key"], esc(r["zh"]), esc(r["ja"])]) + "\n")
    sys.stderr.write(f"[{ch}] {pos}-{pos+len(out)}/{total} -> {tsv}\n")
    print(f"[{ch}] {pos}-{pos+len(out)}/{total} {len(out)}行 完走={completes} -> {tsv}")

if __name__ == "__main__":
    main()
