#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""クエスト会話(ns=Quests / target=Quests任务表)の全行を zh+ja つきで抽出し、
detect_mistrans.py の監査モードに渡す audit JSON を作る。
出力: $WS_TMP/quests_audit.json  (= [{target,ns,key,zh,ja}, ...])
使い方:
  PYTHONIOENCODING=utf-8 python _tools/audit_quests.py
  PYTHONIOENCODING=utf-8 python _tools/detect_mistrans.py $WS_TMP/quests_audit.json --backend haiku
  -> $WS_TMP/mistrans_audit.txt に疑い一覧(s/v>=0.3)
オプション:
  --limit N   先頭N行だけ(スモークテスト用)
  --qid 12345 特定クエストIDのみ(keyの数値接頭辞で絞る)
"""
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
TARGET = "Quests任务表"
NS = "Quests"

def wlp(t):
    return glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")[0]

def main():
    args = sys.argv[1:]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    qid = args[args.index("--qid") + 1] if "--qid" in args else None

    src = json.load(open(f"{ROOT}/_phase4_proofread/source_zh.json", encoding="utf-8"))
    _, ja_map, *_ = locres.parse(wlp(TARGET))

    rows = []
    for full, zh in src.items():
        t, ns, key = full.split("\x1f", 2)
        if t != TARGET or ns != NS:
            continue
        if qid and not key.startswith(qid + "_"):
            continue
        ja = ja_map.get(ns + "\x1f" + key, "")
        rows.append({"target": t, "ns": ns, "key": key, "zh": zh, "ja": ja})

    rows.sort(key=lambda r: r["key"])
    if limit:
        rows = rows[:limit]

    out = os.path.join(TMP, "quests_audit.json")
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[audit_quests] {len(rows)}行 -> {out}")
    print("次: PYTHONIOENCODING=utf-8 python _tools/detect_mistrans.py "
          f"{out} --backend haiku")

if __name__ == "__main__":
    main()
