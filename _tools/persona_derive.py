#!/usr/bin/env python3
"""キャラ開始時の「ペルソナ深掘り」用。原文(中国語)から、そのキャラの
自称・二人称マーカーの統計と、長短・話題のばらけた代表セリフ(原文)を出す。
これを読んで `10_人物/<キャラ>.md` を「簡易」→「確定」へ書き上げる。
使い方: python3 _tools/persona_derive.py "話者名" [サンプル数=20]
※素材は必ず原文zh(MT訳ではない)。語格(register)変化の根拠も原文から取る。
"""
import sys, os, json, re, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
P4 = os.path.join(ROOT, "_phase4_proofread")

SELF = ['老夫','老身','贫道','貧道','贫僧','貧僧','老衲','老道','在下','洒家','本座','本督','本帅','本帥',
        '末将','末將','卑职','卑職','微臣','妾身','奴家','小女子','鄙人','晚辈','晚輩','为师','為師',
        '为父','為父','为兄','為兄','本教主','罪者','某','贫尼','小僧','小道','小老儿']
YOU  = ['您','阁下','閣下','足下','汝','尔','爾','尊驾','尊駕','贤侄','賢侄','小友','少侠','少俠',
        '公子','姑娘','道友','施主','兄台','尊兄']

def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    name = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    bc = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    src = json.load(open(f"{P4}/source_zh.json", encoding="utf-8"))
    rows = bc["lines"].get(name, [])
    zh_lines = []
    for t, ns, k in rows:
        z = src.get(t + "\x1f" + ns + "\x1f" + k, "")
        if z:
            body = z.split("$@$", 1)[1] if "$@$" in z else z
            body = re.sub(r'</?[^>]*>|\\r|\\n|[\r\n]', '', body).strip()
            if body:
                zh_lines.append(body)
    text = " ".join(zh_lines)
    self_hit = {w: text.count(w) for w in SELF if w in text}
    you_hit = {w: text.count(w) for w in YOU if w in text}
    # 長短・内容のばらけた代表(重複除外、長さで分散サンプル)
    uniq = list(dict.fromkeys(zh_lines))
    uniq.sort(key=len)
    picks = []
    if uniq:
        step = max(1, len(uniq) // n)
        picks = uniq[::step][:n]
    print(f"# {name} 原文ベース・ペルソナ深掘り素材")
    print(f"総セリフ: {len(rows)} 行 / 異なり原文: {len(uniq)}")
    print(f"\n## 自称マーカー(原文・多い順) ※老/贫等は register 変化の根拠")
    print("、".join(f"{w}×{c}" for w, c in sorted(self_hit.items(), key=lambda x:-x[1])) or "（明確な自称なし＝我のみ）")
    print(f"\n## 二人称・呼称マーカー(原文・多い順)")
    print("、".join(f"{w}×{c}" for w, c in sorted(you_hit.items(), key=lambda x:-x[1])) or "（特記なし）")
    print(f"\n## 代表セリフ(原文・長短ばらけ {len(picks)}本)")
    for p in picks:
        print(f"- {p[:80]}")
    print("\n→ 上記を読み、10_人物/" + name + ".md を確定版へ。一人称は『相手・場面別』に書く"
          "(例: 弟子へ=わし/そなた、道門=貧道、対外=この老いぼれ)。status: 確定 に。")

if __name__ == "__main__":
    main()
