#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全体監査(機械検出): **キャラの台詞**に紛れた①生英語②時代錯誤カタカナ を洗い出す。
LLMには走査させない=スクリプトの仕事。出力語彙を人/Opusが判断し修正する。
- **話者発話だけ**を対象=値に `$@$` がある行のみ($@$より後ろの本文を見る)。UI/クエスト説明文(=`$@$`無し)は対象外。
  → UIの「チーム」は無視され、台詞の「チーム」だけが出る。
- タグ `<...>`・プレースホルダ `{...}`・`#nl` は除外。笑い/咳/相槌の定訳カタカナ(ゴホ/ハハ/フフ等)も除外。
出力: $WS_TMP/loanword_report.txt。使い方: python _tools/scan_loanwords.py
"""
import os, re, glob, json, collections, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres

LAT = re.compile(r"[A-Za-z][A-Za-z'\-]+")
KAT = re.compile(r"[ァ-ヴ][ァ-ヴー・ｦ-ﾟ]+")
# 台詞でも正当なカタカナ(笑い・咳・相槌・嘆息の定訳)。これは除外。
ONOMAT = re.compile(r"^(ゴホ+ッ?|ゴホ(ゴホ)+|ハハ+|アハ+|ワハ+|フフ+|ウフ+|ヘヘ+|フン|コホン|オホン|エヘン|"
                    r"ケケ+|クク+|ヒヒ+|ニヤ|ニヤニヤ|ハァ+|ふぅ|ウウ+|ウム|フゥ+|キャ+|アァ+|オオ+|ンン+)$")


def clean(body):
    body = re.sub(r"<[^>]*>", "", body)
    body = re.sub(r"\{[^}]*\}", "", body)
    return body.replace("#nl", " ").replace("\\r", " ").replace("\\n", " ")


def main():
    lat = collections.Counter(); lat_s = {}
    kat = collections.Counter(); kat_s = {}
    n_spoken = 0
    for f in glob.glob(f"{ROOT}/_work/jp/**/*.locres", recursive=True):
        m = re.search(r"Localization[\\/]([^\\/]+)[\\/]", f)
        tgt = m.group(1) if m else "?"
        try:
            _, d, *_ = locres.parse(f)
        except Exception:
            continue
        for k, v in d.items():
            if not v or "$@$" not in v:        # ★話者発話のみ
                continue
            n_spoken += 1
            pre, body = v.split("$@$", 1)
            who = pre.split(" - ")[1].strip() if " - " in pre else "?"
            body = clean(body)
            for w in set(LAT.findall(body)):
                if len(w) >= 2:
                    lat[w] += 1; lat_s.setdefault(w, (who, k.replace("\x1f", "|")))
            for w in set(KAT.findall(body)):
                if len(w) >= 2 and not ONOMAT.match(w):
                    kat[w] += 1; kat_s.setdefault(w, (who, k.replace("\x1f", "|")))

    rep = os.path.join(TMP, "loanword_report.txt")
    with open(rep, "w", encoding="utf-8") as f:
        f.write(f"# 話者発話({n_spoken}行)中の 生英語/時代錯誤カタカナ候補\n")
        f.write(f"\n=== 英語 distinct={len(lat)} ===\n")
        for w, c in lat.most_common():
            f.write(f"{c:4}  {w}\t(話者:{lat_s[w][0]} {lat_s[w][1]})\n")
        f.write(f"\n=== カタカナ(笑い/咳/相槌の定訳は除外) distinct={len(kat)} ===\n")
        for w, c in kat.most_common():
            f.write(f"{c:4}  {w}\t(話者:{kat_s[w][0]} {kat_s[w][1]})\n")
    print(f"話者発話 {n_spoken}行 / 英語 distinct={len(lat)} / カタカナ distinct={len(kat)} -> {rep}")
    print("英語:", [w for w, _ in lat.most_common(30)])
    print("カタカナ:", [w for w, _ in kat.most_common(40)])


if __name__ == "__main__":
    main()
