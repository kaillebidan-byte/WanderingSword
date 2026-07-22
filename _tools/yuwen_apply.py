#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宇文逸 register校正バッチの反映＋進捗前進。yuwen_pending.py と対。
yuwen_out.json(変更行のみ [{i,new_body,conf,reason}]) と yuwen_batch.json(keys) を突合し、
pf_inbox.json(reviewed=0) を生成→ apply_char.py で反映(線形char_progressは動かさない)→
yuwen_bulk_progress.json の cursor を「今回emitした本文数」だけ前進させる。

使い方:
  python _tools/yuwen_apply.py    # Sonnetが yuwen_out.json を書いた後に実行
"""
import json, os, sys, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "_phase4_proofread")
WS_TMP = os.environ.get("WS_TMP", os.path.join(ROOT, "_ws_tmp"))
PROG = os.path.join(P4, "yuwen_bulk_progress.json")
LOG = os.path.join(P4, "yuwen_prooflog.md")            # バッチ毎の進捗記録(レート上限で中断しても残る)
QUEUE = os.path.join(P4, "yuwen_review_queue.jsonl")   # conf:low/mid のOpus検証キュー(理由付き・永続)


def main():
    batch = json.load(open(os.path.join(WS_TMP, "yuwen_batch.json"), encoding="utf-8"))
    by_i = {b["i"]: b for b in batch}
    out_path = os.path.join(WS_TMP, "yuwen_out.json")
    if not os.path.exists(out_path):
        # 安全弁: Sonnet出力が無いのにcursorを進めない(空進行＝校正漏れ防止)
        print("[yuwen_apply] 中断: yuwen_out.json が無い。Sonnet校正の出力を先に書くこと(cursor据え置き)。")
        sys.exit(1)
    out = json.load(open(out_path, encoding="utf-8"))
    fixes = []
    for o in out:
        b = by_i.get(o["i"])
        if not b or not o.get("new_body"):
            continue
        for k in b["keys"]:
            fixes.append({"target": k["target"], "ns": k["ns"], "key": k["key"], "new_body": o["new_body"]})
    inbox = os.path.join(WS_TMP, "pf_inbox.json")
    json.dump({"reviewed": 0, "fixes": fixes}, open(inbox, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[yuwen_apply] 変更本文 {len(out)} / 展開key {len(fixes)} -> apply_char(reviewed=0)")
    if fixes:
        subprocess.run([sys.executable, os.path.join(ROOT, "_tools", "apply_char.py"), inbox], check=True)
    else:
        print("[yuwen_apply] 変更なし(apply_charスキップ・再パック不要)")
    # 進捗前進: 今回のバッチ本文数ぶん cursor を進める
    cur = json.load(open(PROG, encoding="utf-8")).get("cursor", 0) if os.path.exists(PROG) else 0
    new_cur = cur + len(batch)
    json.dump({"cursor": new_cur}, open(PROG, "w", encoding="utf-8"), ensure_ascii=False)

    # ---- 記録(レート上限で中断しても残る) ----
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conf = {"high": 0, "mid": 0, "low": 0}
    for o in out:
        conf[o.get("conf", "high") if o.get("conf") in conf else "high"] += 1
    # 修正の種別内訳(声優先の逸脱監視: 呼称/笑いばかりなら声を見落としている)
    KINDS = ["voice", "誤訳", "呼称", "笑い", "他"]
    kind = {k: 0 for k in KINDS}
    for o in out:
        kind[o.get("kind") if o.get("kind") in kind else "他"] += 1
    regs = sorted({b.get("reg") for b in batch})
    total = 13491
    surf = kind["呼称"] + kind["笑い"]
    flag = " ⚠声薄い" if (len(out) >= 4 and kind["voice"] * 2 < surf) else ""
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- {ts}  cursor {cur}→{new_cur}/{total} (batch~{new_cur//len(batch) if len(batch) else '?'})  "
                f"{regs}  変更 {len(out)}本文/{len(fixes)}key  "
                f"種別 声{kind['voice']}/誤訳{kind['誤訳']}/呼称{kind['呼称']}/笑{kind['笑い']}/他{kind['他']}  "
                f"conf h{conf['high']}/m{conf['mid']}/l{conf['low']}{flag}\n")
    # conf:low/mid を検証キューへ(理由付き=後でOpusが重点点検)
    flagged = [o for o in out if o.get("conf") in ("low", "mid")]
    if flagged:
        with open(QUEUE, "a", encoding="utf-8") as f:
            for o in flagged:
                b = by_i.get(o["i"], {})
                rec = {"ts": ts, "cursor": cur, "conf": o.get("conf"), "reg": b.get("reg"),
                       "key": (b.get("keys") or [{}])[0].get("key"), "zh": b.get("zh"),
                       "new_body": o.get("new_body"), "reason": o.get("reason")}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 使い終えた out を消す(次バッチのWrite制約回避)
    try: os.remove(out_path)
    except OSError: pass
    print(f"[yuwen_apply] cursor {cur} -> {new_cur}  (log: yuwen_prooflog.md, conf低mid: {len(flagged)}件をqueueへ)")


if __name__ == "__main__":
    main()
