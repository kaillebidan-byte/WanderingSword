#!/usr/bin/env python3
"""翻訳漏れ抽出パイプライン。
原文(本体pakのzh-Hans locres)と訳(MOD pakのzh-Hans locres)をキー単位で突き合わせ、
「訳が原文の中国語のまま＝未翻訳」の行を洗い出す。

使い方(sandbox bash):
  python3 _tools/build_gaps.py \
    --base "/path/to/Wandering_Sword-WindowsNoEditor.pak" \
    --mod  "/path/to/aaWanderingSword_JP_P.pak" \
    --out  "_phase3_gaps"
repak バイナリは同じ _tools/ 内を使用。
"""
import argparse, glob, json, os, re, subprocess, sys, tempfile
import locres  # 同ディレクトリの locres.py

TARGETS = ["Buff与道具","CG表","Npc","Quests任务表","Skills技能表","系统","门派地图与提示"]
KANA = re.compile(r'[぀-ヿ]')
CJK  = re.compile(r'[一-鿿]')
TAGS = re.compile(r'</?[A-Za-z][^>]*>|\{[0-9]+\}|#nl|\\[rn]|[\r\n]')

def body(s):
    if '$@$' in s:
        s = s.split('$@$', 1)[1]
    return TAGS.sub('', s).strip()

def unpack(repak, pak, outdir):
    inc = []
    for t in TARGETS:
        inc += ["-i", f"Wandering_Sword/Content/Localization/{t}/zh-Hans/{t}.locres"]
    subprocess.run([repak, "unpack", pak, "-o", outdir, *inc], check=True)

def lp(root, t):
    g = glob.glob(f"{root}/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")
    return g[0] if g else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--mod", required=True)
    ap.add_argument("--out", default="_phase3_gaps")
    ap.add_argument("--repak", default=os.path.join(os.path.dirname(__file__), "repak"))
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()
    base_dir, mod_dir = os.path.join(tmp,"base"), os.path.join(tmp,"mod")
    unpack(a.repak, a.base, base_dir)
    unpack(a.repak, a.mod, mod_dir)
    os.makedirs(a.out, exist_ok=True)
    grand = []
    for t in TARGETS:
        bp, mp = lp(base_dir, t), lp(mod_dir, t)
        if not (bp and mp):
            continue
        _, zh, *_ = locres.parse(bp)
        _, jp, *_ = locres.parse(mp)
        rows = []
        for k, jv in jp.items():
            zv = zh.get(k)
            if jv is None or zv is None or jv != zv:
                continue
            bd = body(jv)
            if len(CJK.findall(bd)) >= 4 and not KANA.search(bd):
                ns, key = k.split('\x1f', 1)
                rows.append({"namespace": ns, "key": key, "source_zh": zv, "target_ja": ""})
        json.dump(rows, open(f"{a.out}/gaps_{t}.json","w"), ensure_ascii=False, indent=1)
        grand += rows
    # ユニーク原文
    uniq = {}
    for r in grand:
        u = uniq.setdefault(r["source_zh"], {"source_zh": r["source_zh"], "occurrences": 0, "target_ja": ""})
        u["occurrences"] += 1
    ul = sorted(uniq.values(), key=lambda x: -x["occurrences"])
    json.dump(ul, open(f"{a.out}/_unique_to_translate.json","w"), ensure_ascii=False, indent=1)
    print(f"漏れ(キー単位): {len(grand)} / ユニーク原文: {len(ul)} -> {a.out}")

if __name__ == "__main__":
    main()
