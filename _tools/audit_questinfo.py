#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""クエスト『情報』(会話ではない UI 文言)の誤訳監査セットを作る。
対象 = Quests任务表 / ns=Quests の非会話キー:
  _Name(クエスト名 ~1774) / _Descript(説明・目標/道案内 ~1706) / _OptionText(選択肢 ~1501)
これらは source_zh.json に無い(＝phase4校正の対象外)。zh 原文は基底ゲーム pak から取る。

zh 原文の取得: 基底 pak の Quests任务表.locres を repak get で 1 ファイルだけ吸い出す。
  base pak 既定: Steam の Wandering_Sword-WindowsNoEditor.pak
出力: $WS_TMP/questinfo_audit.json  = [{target,ns,key,zh,ja}, ...]
      標準出力に「機械フラグ」(未訳/ゴミ/タグ欠落)の集計＋例。
次段: python _tools/detect_mistrans.py $WS_TMP/questinfo_audit.json --backend haiku
      -> $WS_TMP/mistrans_audit.txt に意味リスク s>=0.3 の疑いだけ列挙(Claudeが zh 突合)。

使い方:
  PYTHONIOENCODING=utf-8 WS_TMP=$PWD/_ws_tmp python _tools/audit_questinfo.py [--kind descript|name|option|all] [--flags-only]
"""
import sys, os, re, json, glob, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")
BASE_PAK = os.environ.get("WS_BASE_PAK",
    r"C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks\Wandering_Sword-WindowsNoEditor.pak")
QPATH = "Wandering_Sword/Content/Localization/Quests任务表/zh-Hans/Quests任务表.locres"
KIND_RE = re.compile(r"^\d+_(Name|Descript|OptionText)")

def ja_map():
    f = glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/Quests任务表/zh-Hans/*.locres")[0]
    return locres.parse(f)[1]

def zh_map():
    """基底 pak から原文中国語 locres を取り出してパース(キャッシュ)。"""
    cache = os.path.join(TMP, "quests_zh_orig.locres")
    if not os.path.exists(cache) or os.path.getsize(cache) == 0:
        with open(cache, "wb") as out:
            subprocess.run([REPAK, "get", BASE_PAK, QPATH], stdout=out, check=True)
    return locres.parse(cache)[1]

def main():
    args = sys.argv[1:]
    kind = args[args.index("--kind") + 1] if "--kind" in args else "all"
    flags_only = "--flags-only" in args
    want = {"descript": ("Descript",), "name": ("Name",),
            "option": ("OptionText",), "all": ("Name", "Descript", "OptionText")}[kind]

    ja, zh = ja_map(), zh_map()
    rows = []
    for k, jav in ja.items():
        ns, key = k.split("\x1f", 1)
        m = KIND_RE.match(key)
        if not m or m.group(1) not in want:
            continue
        rows.append({"target": "Quests任务表", "ns": ns, "key": key,
                     "zh": zh.get(k, ""), "ja": jav, "_kind": m.group(1)})
    rows.sort(key=lambda r: r["key"])

    # 機械フラグ(LLM前の安価な網): 空/未訳(zh==ja)/かな無し/ラテン片/タグ欠落
    def kana(s): return bool(re.search(r"[ぁ-んァ-ヶ]", s))
    flagged = []
    for r in rows:
        z, j = r["zh"], r["ja"]
        f = None
        if not j.strip(): f = "空JA"
        elif z and j == z and re.search(r"[一-鿿]", z): f = "未訳(zh==ja)"
        elif re.fullmatch(r"[A-Za-z0-9 \W]{1,4}", j or "") and re.search(r"[A-Za-z]", j or ""): f = "ラテン片/ゴミ"
        elif z.count("{") != j.count("{"): f = "placeholder{}不一致"
        elif z.count("<") != j.count("<"): f = "色タグ<>欠落/不一致"
        # 注: かな無し漢字のみは quest 名で正常(漢文調)が多く誤検出が多いので既定では出さない
        if f:
            r["_flag"] = f; flagged.append(r)

    from collections import Counter
    print(f"[questinfo] 対象 {len(rows)}行 kind={kind}  内訳={dict(Counter(r['_kind'] for r in rows))}")
    print(f"[questinfo] 機械フラグ {len(flagged)}件 -> {dict(Counter(r['_flag'] for r in flagged))}")
    for r in flagged[:30]:
        print(f'  [{r["_flag"]}][{r["_kind"]}] {r["key"]}')
        print(f'     zh: {r["zh"]!r}'[:100]); print(f'     ja: {r["ja"]!r}'[:100])

    if not flags_only:
        out = os.path.join(TMP, "questinfo_audit.json")
        json.dump([{k: r[k] for k in ("target", "ns", "key", "zh", "ja")} for r in rows],
                  open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[questinfo] audit -> {out}")
        print(f"  次: PYTHONIOENCODING=utf-8 python _tools/detect_mistrans.py {out} --backend haiku")

if __name__ == "__main__":
    main()
