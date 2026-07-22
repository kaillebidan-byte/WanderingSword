#!/usr/bin/env python3
"""フェーズ2(校正): カーソル位置から次N件の会話行を、原文・現訳つきで出力。
使い方: python3 _tools/pending_proofread.py [件数=60]
出力: /sessions/trusting-festive-turing/mnt/outputs/pf_batch.json に [{target,ns,key,zh,ja}] を書き、標準出力にも表示。
カーソルは進めない(apply_proofread が進める)。
"""
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
P4 = os.path.join(ROOT, "_phase4_proofread")

def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    queue = json.load(open(f"{P4}/queue.json", encoding="utf-8"))
    src = json.load(open(f"{P4}/source_zh.json", encoding="utf-8"))
    pos = json.load(open(f"{P4}/cursor.json", encoding="utf-8"))["pos"]
    batch = queue[pos:pos+n]
    if not batch:
        print("校正キュー全完了");
        json.dump([], open("/sessions/trusting-festive-turing/mnt/outputs/pf_batch.json", "w"))
        return
    # 必要なtargetのJAだけ読む
    ja_cache = {}
    out = []
    for t, ns, key in batch:
        if t not in ja_cache:
            _, ja_cache[t], *_ = locres.parse(wlp(t))
        fk = ns + "\x1f" + key
        ja = ja_cache[t].get(fk, "")
        zh = src.get(t + "\x1f" + fk, "")
        out.append({"target": t, "ns": ns, "key": key, "zh": zh, "ja": ja})
    json.dump(out, open("/sessions/trusting-festive-turing/mnt/outputs/pf_batch.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.stderr.write(f"カーソル {pos}/{len(queue)} から {len(out)}件提示(残 {len(queue)-pos}件)\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
