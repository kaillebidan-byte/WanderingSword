#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""未翻訳検出: ja に中国語が残っている話者発話を機械的に洗い出す(改良版)。
誤検出対策: **zh原文が空の行は除外**(念仏「南無阿弥陀仏」・禅詩・固有名詞など、漢字のみでも正当な日本語を弾く)。
信号: ①ja に**簡体字/中国語専用字**が残存 ②**ja≈zh**(中国語をそのままコピー=丸ごと未訳・高一致＆仮名ほぼ無)。
使い方:
  WS_CHAR=<キャラ> python _tools/scan_untranslated.py   # 1キャラ
  python _tools/scan_untranslated.py --all              # 全話者発話
出力: $WS_TMP/untranslated.txt (+ stdout 件数)
"""
import os, re, glob, json, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres

src = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))
bychar = json.load(open(f"{ROOT}/_phase4_proofread/by_character.json", encoding="utf-8"))
# 中国語専用のみ(日本語でも使う字は入れない)。簡体字や中国語助詞/代名詞。
CN = set("你们們吗嗎呢咱啥咋哪怎麼么什谁这个说见觉让时实战经过风门问间关应现认识论议张长车东书还进远连边难飞习样类节义乐买卖语读变丽华虽")

JCACHE = {}
def ja_of(t, ns, k):
    if t not in JCACHE:
        JCACHE[t] = locres.parse(glob.glob(f"{ROOT}/_work/jp/**/{t}/zh-Hans/*.locres", recursive=True)[0])[1]
    return JCACHE[t].get(ns + "\x1f" + k, "")

def body(v):
    if "$@$" in v:
        v = v.split("$@$", 1)[1]
    v = re.sub(r"<[^>]*>", "", v)
    v = re.sub(r"\{[^}]*\}", "", v)
    return v.replace("#nl", "").strip()

def flags(ja_b, zh_b):
    r = []
    cn = sorted(set(c for c in ja_b if c in CN))
    if cn:
        r.append("簡体/中国語字:" + "".join(cn))
    if zh_b:  # zhがある行だけ「丸ごと未訳」を見る(念仏・固有名詞=zh空は除外)
        jcjk = [c for c in ja_b if 0x4E00 <= ord(c) <= 0x9FFF]
        kana = sum(1 for c in ja_b if 0x3041 <= ord(c) <= 0x30FA)
        if ja_b == zh_b:
            r.append("ja==zh(丸ごと未訳)")
        elif jcjk:
            ratio = sum(1 for c in jcjk if c in zh_b) / len(jcjk)
            if ratio >= 0.78 and kana <= 1:
                r.append(f"zhと高一致{int(ratio*100)}%・仮名ほぼ無(未訳疑い)")
    return r

def main():
    allmode = "--all" in sys.argv
    ch = os.environ.get("WS_CHAR")
    chars = list(bychar["lines"].keys()) if allmode else ([ch] if ch else [])
    if not chars:
        print("WS_CHAR でキャラ指定 か --all を付けてください"); return
    hits = []
    for c in chars:
        for t, ns, k in bychar["lines"].get(c, []):
            ja = ja_of(t, ns, k)
            if not ja or "$@$" not in ja:
                continue
            jb = body(ja); zb = body(src.get(t + "\x1f" + ns + "\x1f" + k, ""))
            r = flags(jb, zb)
            if r:
                hits.append((c, t, ns, k, "/".join(r), zb, ja))
    rep = os.path.join(TMP, "untranslated.txt")
    with open(rep, "w", encoding="utf-8") as f:
        for c, t, ns, k, r, zh, ja in hits:
            f.write(f"[{r}] {c} {t}|{ns}|{k}\n  zh: {zh}\n  ja: {ja}\n")
    print(f"対象 {len(chars)}キャラ / 未翻訳疑い {len(hits)}行 -> {rep}")
    from collections import Counter
    print("話者別:", Counter(h[0] for h in hits).most_common(15))

if __name__ == "__main__":
    main()
