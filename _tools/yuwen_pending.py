#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宇文逸(主人公・別トラック)の register駆動バッチ供給。pending_char.py の宇文逸版。
線形char_progressは888で完了済＝宇文逸は別トラック。本ドライバが register純度の高い順に
バッチを供給し、独立進捗 yuwen_bulk_progress.json {cursor} で続きから再開する。

使い方:
  python _tools/yuwen_pending.py [N]      # 次N本文(ユニーク)を _ws_tmp/yuwen_batch.json に出力＋#META表示
  反映は yuwen_apply.py(out→pf_inbox→apply_char reviewed=0→cursor前進)。
"""
import json, os, sys, re, glob, struct
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres
import locres_write as L
P4 = os.path.join(ROOT, "_phase4_proofread")
WS_TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
PROG = os.path.join(P4, "yuwen_bulk_progress.json")
SRC = os.path.join(ROOT, "_work", "jp", "Wandering_Sword", "Content", "Localization")


def _kim(b):
    o = 16; o += 1; o += 8; o += 4
    (nsc,) = struct.unpack_from('<I', b, o); o += 4
    out = {}
    for _ in range(nsc):
        o += 4; ns, o = locres.rd(b, o)
        (kc,) = struct.unpack_from('<I', b, o); o += 4
        for _ in range(kc):
            o += 4; key, o = locres.rd(b, o); o += 4
            (idx,) = struct.unpack_from('<i', b, o); o += 4
            out[ns + "\x1f" + key] = idx
    return out


def load_live_ja(rows):
    """現在の_work locresから 宇文逸の各keyの最新ja本文を読む(校正前snapshotでなくライブ)。"""
    by_t = {}
    for r in rows:
        by_t.setdefault(r["t"], []).append((r["ns"], r["key"]))
    live = {}
    for t, keys in by_t.items():
        files = glob.glob(f"{SRC}/{t}/zh-Hans/*.locres")
        if not files:
            continue
        b = open(files[0], "rb").read()
        _, ver, _, arr, _ = L.load(files[0])
        km = _kim(b)
        for ns, key in keys:
            i = km.get(ns + "\x1f" + key)
            if i is not None and arr[i][0]:
                live[(t, ns, key)] = arr[i][0]
    return live

# register別 partner集合（B表準拠）。判定優先: M7(全文括弧) > partner群 > その他(混在)。
REG = [
    ("M1武当・師長", {"清虚道長","清霄道長","道玄","道妙","道微","道通"}),
    ("M1武当・兄弟子", {"莫問","元啓","元風","莫棄"}),
    ("M2義兄弟", {"李元興","燕未還","孔亮","葉雲","王天聡","江吟風","冷無情","白錦","葉飛","顧思帰","肖寒光","衛霍","欧陽海"}),
    ("M3後輩・弟分", {"呂仙児","江小彤","司馬鈴","程鈺"}),
    ("M5親密・恋情", {"欧陽雪"}),
    ("M4少林", {"滌罪僧","円悟","円覚","円難","円苦","慧空","慧平","智武","空聞","円真","円澄"}),
    ("M4江湖・対外", {"藍孔雀","瑶姫","商葶苧","歩微月","冷鷹","上官虹","蓮芯","飛蝎使-娜烏","欧陽衡",
                  "殷無矜","左江龍","白惟一","上官雨","司馬鈴","湯統","童安","赫連輔弼","赤鷹"}),
]
# 処理順（register純度の高い→最後に混在の大群）
ORDER = ["M1武当・師長","M1武当・兄弟子","M2義兄弟","M3後輩・弟分","M5親密・恋情","M4少林","M4江湖・対外","M7独白","E混在(要判定)"]
ORDER_IDX = {k: i for i, k in enumerate(ORDER)}


def body(s): return (s.split("$@$", 1)[-1] if "$@$" in s else s).strip()
def fully_paren(b): return b[:1] in ("（","(") and b[-1:] in ("）",")")


def classify(r):
    jb = body(r.get("_ja", r["ja"]))
    if r.get("has_paren") and fully_paren(jb):
        return "M7独白"
    p = r.get("partner_prev")
    for label, s in REG:
        if p in s:
            return label
    return "E混在(要判定)"


def build_order():
    rows = json.load(open(os.path.join(P4, "yuwen_classified.json"), encoding="utf-8"))
    live = load_live_ja(rows)  # 校正後の最新jaを反映
    for r in rows:
        r["_ja"] = live.get((r["t"], r["ns"], r["key"]), r["ja"])
    # ユニーク本文単位（同一本文の別keyは一括。ライブjaでdedup）
    seen = {}
    for r in rows:
        jb = body(r["_ja"])
        seen.setdefault(jb, []).append(r)
    items = []
    for jb, rs in seen.items():
        r0 = rs[0]
        reg = classify(r0)
        items.append({
            "reg": reg, "ja": jb, "zh": body(r0["zh"]), "partner": r0.get("partner_prev"),
            "qid": r0.get("quest_id") or 0, "key": r0["key"],
            "keys": [{"target": r["t"], "ns": r["ns"], "key": r["key"]} for r in rs],
        })
    items.sort(key=lambda it: (ORDER_IDX.get(it["reg"], 99), it["qid"], it["key"]))
    return items


def print_plan(n):
    items = build_order()
    from collections import Counter
    c = Counter(it["reg"] for it in items)
    tot = len(items)
    print(f"# 宇文逸 register校正プラン  総{tot}本文 / 1バッチ{n} / 総バッチ {-(-tot//n)}")
    run = 0
    for k in ORDER:
        if c.get(k):
            print(f"  {k:16s} {c[k]:5d}本文  cursor {run}-{run+c[k]:<6d} ~{-(-c[k]//n)}バッチ")
            run += c[k]
    cur = json.load(open(PROG, encoding="utf-8")).get("cursor", 0) if os.path.exists(PROG) else 0
    print(f"# 現在 cursor={cur}  (batch {cur//n}/{-(-tot//n)} 完了相当)")


def main():
    args = sys.argv[1:]
    if "--plan" in args:
        nn = next((int(a) for a in args if a.isdigit()), 120)
        print_plan(nn); return
    n = next((int(a) for a in args if a.isdigit()), 120)
    items = build_order()
    total = len(items)
    total_batches = -(-total // n)
    cur = 0
    if os.path.exists(PROG):
        cur = json.load(open(PROG, encoding="utf-8")).get("cursor", 0)
    if cur >= total:
        print(f"#DONE 宇文逸 register校正 全{total}本文 完了 (cursor={cur})")
        return
    batch = items[cur:cur+n]
    regs = sorted(set(b["reg"] for b in batch), key=lambda k: ORDER_IDX.get(k,99))
    out = [{"i": i, "reg": b["reg"], "partner": b["partner"], "zh": b["zh"], "ja": b["ja"], "keys": b["keys"]}
           for i, b in enumerate(batch)]
    os.makedirs(WS_TMP, exist_ok=True)
    json.dump(out, open(os.path.join(WS_TMP, "yuwen_batch.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    completes = (cur + len(batch)) >= total
    meta = {"batch_no": cur//n + 1, "batch_total": total_batches,
            "cursor": cur, "emit": len(batch), "next_cursor": cur+len(batch), "total": total,
            "registers": regs, "completes_track": completes, "totalkeys": sum(len(b["keys"]) for b in batch)}
    print("#META " + json.dumps(meta, ensure_ascii=False))
    print(f"batch {meta['batch_no']}/{total_batches}  register:{regs}  本文{len(batch)}(key{meta['totalkeys']})  進捗 {cur}/{total}")
    print(f"-> {os.path.join(WS_TMP,'yuwen_batch.json')}  反映は yuwen_apply.py")


if __name__ == "__main__":
    main()
