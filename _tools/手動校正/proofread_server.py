#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手動校正Webツール（全行/キャラ別/非対話タブ・編集保存）。
配置: _tools/手動校正/ 。SPEC: _tools/手動校正/SPEC_手動校正Web.md 。運用: 同フォルダ 手順書_手動校正サーバ.md

起動:  set PYTHONIOENCODING=utf-8 && python _tools/手動校正/proofread_server.py
       （またはエクスプローラで proofread_start.ps1 を右クリック→PowerShellで実行）
       → http://127.0.0.1:8765 をブラウザで開く

書き戻し先: _phase4_proofread/manual_edits.json（locres直書きはしない）
進行ログ:   _phase4_proofread/manual_review.json
反映:       apply_manual.py --deploy（検証→適用+再パック→ゲームへ配置。本サーバはオーバーレイを書くだけ）
"""
import os, sys, json, glob, re, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# このファイルは _tools/手動校正/ にある → プロジェクトrootは3階層上
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres

P4 = os.path.join(ROOT, "_phase4_proofread")
PERSONA_DIR = os.path.join(ROOT, "10_人物")
UI_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proofread_ui.html")
EDITS = os.path.join(P4, "manual_edits.json")
REVIEW = os.path.join(P4, "manual_review.json")
SEP = "\x1f"
PORT = 8765

# ---- 起動時ロード（メモリ展開） -------------------------------------------
def wlp(t):
    g = glob.glob(f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization/{t}/zh-Hans/*.locres")
    return g[0] if g else None

def load_state():
    st = {}
    st["queue"] = json.load(open(f"{P4}/queue.json", encoding="utf-8"))
    st["src"]   = json.load(open(f"{P4}/source_zh.json", encoding="utf-8"))
    bc = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))["lines"]
    # フルキー(target,ns,key) -> JP話者名
    k2c = {}
    for ch, keys in bc.items():
        for t, ns, key in keys:
            k2c[(t, ns, key)] = ch
    st["k2c"] = k2c
    # locres JA を全 target 展開 → fullkey(target\x1fns\x1fkey) -> ja
    ja = {}
    loc_dir = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
    all_targets = sorted(os.path.basename(d) for d in glob.glob(loc_dir + "/*")
                         if os.path.isdir(d))
    for t in all_targets:
        p = wlp(t)
        if not p:
            continue
        _, d, *_ = locres.parse(p)
        for nskey, val in d.items():
            ja[t + SEP + nskey] = val
    st["ja"] = ja
    # カバレッジ補完: locres に在るが queue.json に無い対話行を取り込む。
    # 話者は値の接頭辞 "id - 名前 $@$" からも拾う（by_character 漏れ対策）。
    qset = set((t, ns, key) for t, ns, key in st["queue"])
    added = 0
    for fk, val in ja.items():
        if not val or "$@$" not in val:
            continue
        t, ns, key = fk.split(SEP)
        if (t, ns, key) in qset:
            continue
        st["queue"].append([t, ns, key]); added += 1
        if (t, ns, key) not in k2c:
            sp = speaker_of(val)
            if sp:
                k2c[(t, ns, key)] = sp
    if added:
        sys.stderr.write(f"カバレッジ補完: queue外の対話 {added}件を取り込み\n")
    st["edits"]  = json.load(open(EDITS, encoding="utf-8")) if os.path.exists(EDITS) else {}
    st["review"] = json.load(open(REVIEW, encoding="utf-8")) if os.path.exists(REVIEW) else {}
    # 会話グループ（末尾 _Index<n>_Text を除いた接頭辞で連続行を束ねる）。
    # rows は (t,ns,key,idx) の参照。idx は queue 行番号、合成行は None。
    groups = []
    last = None
    for i, (t, ns, key) in enumerate(st["queue"]):
        gk = (t, ns, gkey(key))
        if gk != last:
            groups.append({"target": t, "gid": gkey(key), "rows": []})
            last = gk
        groups[-1]["rows"].append((t, ns, key, i))
    # 選択肢(OptionText)を会話へ挟む：target+先頭ID ごとに合成グループ
    opt = {}
    for fk in ja:
        t, ns, key = fk.split(SEP)
        if OPT_RE.search(key):
            opt.setdefault((t, lead_id(key)), []).append((t, ns, key))
    for (t, lid), rows in opt.items():
        rows.sort(key=lambda r: nat_tuple(r[2]))
        groups.append({"target": t, "gid": f"{lid}_OptionText（選択肢）",
                       "rows": [(rt, rns, rk, None) for rt, rns, rk in rows]})
    # 同一クエスト/シーン番号でまとめ、受注→中間→完了の順に並べ替え
    def gsort(g):
        idxs = [r[3] for r in g["rows"] if r[3] is not None]
        return (g["target"], lead_id(g["gid"]), block_pri(g["gid"]),
                nat_tuple(g["gid"]), idxs[0] if idxs else -1)
    groups.sort(key=gsort)
    st["groups"] = groups
    # 行index(queue) -> グループindex
    g_of_row = [0] * len(st["queue"])
    for gi, g in enumerate(groups):
        for (_, _, _, i) in g["rows"]:
            if i is not None:
                g_of_row[i] = gi
    st["g_of_row"] = g_of_row
    # キャラ別行数（補完後の実到達行から再集計）
    cc = {}
    for t, ns, key in st["queue"]:
        ch = k2c.get((t, ns, key))
        if ch:
            cc[ch] = cc.get(ch, 0) + 1
    st["char_count"] = cc
    # キャラ -> そのキャラを含むグループindex（並べ替え後の順）
    cg = {}
    for gi, g in enumerate(groups):
        seen = set()
        for (t, ns, key, _) in g["rows"]:
            ch = k2c.get((t, ns, key))
            if ch and ch not in seen:
                cg.setdefault(ch, []).append(gi); seen.add(ch)
    st["char_groups"] = cg
    # 非対話索引（カテゴリ別）。OptionText は会話側へ回すため除外。
    nd = {c: [] for c in ND_CATS}
    for fk, val in ja.items():
        if "$@$" in val or OPT_RE.search(fk):
            continue
        t = fk.split(SEP)[0]
        cat = ND_CAT_OF.get(t)
        if cat:
            nd[cat].append(tuple(fk.split(SEP)))
    for c in nd:
        nd[c].sort(key=lambda x: (x[0], nat_tuple(x[2]), x[2]))
    st["nd"] = nd
    return st

GIDX_RE = re.compile(r"_Index\d+_Text$")
OPT_RE  = re.compile(r"_OptionText\d+$")
def gkey(key):
    return GIDX_RE.sub("", key)

# 非対話タブのカテゴリ（target → カテゴリ）
ND_CATS = ["用語", "クエスト", "UI", "その他"]
ND_CAT_OF = {
    "Buff与道具": "用語", "Skills技能表": "用語", "Npc": "用語",
    "Quests任务表": "クエスト",
    "系统": "UI",
    "程序_导出": "その他", "门派地图与提示": "その他", "坐骑": "その他",
}

def lead_id(gid):
    m = re.match(r"(\d+)", gid)
    return int(m.group(1)) if m else 0

def speaker_of(val):
    # "id - 名前 $@$本文" の "名前" を返す。話者prefixが無ければ None。
    if "$@$" not in val:
        return None
    pre = val.split("$@$", 1)[0]
    m = re.match(r"\s*\S+\s*-\s*(.+?)\s*$", pre)
    return m.group(1).strip() if m else None

def nat_tuple(gid):
    return tuple(int(x) for x in re.findall(r"\d+", gid))

def block_pri(gid):
    if "RequestDlgs" in gid:   return 0   # 受注
    if "FinishingDlgs" in gid: return 8   # 完了
    return 4                              # 中間（Option/Processing/Attach/UnFinished等）

STATE = load_state()

def fullkey(t, ns, key):
    return t + SEP + ns + SEP + key

def effective_ja(fk):
    e = STATE["edits"].get(fk)
    if e and "new_ja" in e:
        return e["new_ja"]
    return STATE["ja"].get(fk, "")

# ---- タグ／接頭辞バリデーション -------------------------------------------
TAG_RE = re.compile(r"<[^>]+>")
PH_RE  = re.compile(r"\{\d+\}")

def tag_multiset(s):
    # 色タグ・プレースホルダ・改行記号の出現数（順不同の多重集合）
    from collections import Counter
    c = Counter()
    for m in TAG_RE.findall(s):
        c["TAG" + m] += 1
    for m in PH_RE.findall(s):
        c["PH" + m] += 1
    c["#nl"]  += s.count("#nl")
    c["\\r\\n"] += s.count("\\r\\n")
    c["CRLF"] += s.count("\r\n")
    return c

def split_prefix(s):
    # "$@$" より前（ID・話者名）は不変。無ければ非対話扱いで全文可変。
    if "$@$" in s:
        pre, body = s.split("$@$", 1)
        return pre + "$@$", body
    return "", s

def validate(orig, new):
    errs = []
    o_pre, o_body = split_prefix(orig)
    n_pre, n_body = split_prefix(new)
    if o_pre != n_pre:
        errs.append(f"接頭辞(ID・話者名/$@$)が変更されています")
    co, cn = tag_multiset(o_body), tag_multiset(n_body)
    if co != cn:
        diff = []
        for k in set(co) | set(cn):
            if co.get(k, 0) != cn.get(k, 0):
                label = k.replace("TAG", "").replace("PH", "")
                diff.append(f"{label}({co.get(k,0)}→{cn.get(k,0)})")
        errs.append("タグ/改行/プレースホルダ不一致: " + ", ".join(diff))
    return errs

# ---- 行データ生成 ----------------------------------------------------------
def row_key(t, ns, key, idx=None):
    fk = fullkey(t, ns, key)
    e = STATE["edits"].get(fk, {})
    rv = STATE["review"].get(fk, {})
    return {
        "idx": idx, "target": t, "ns": ns, "key": key, "fk": fk,
        "zh": STATE["src"].get(fk, ""),
        "ja": effective_ja(fk),
        "orig_ja": STATE["ja"].get(fk, ""),
        "char": STATE["k2c"].get((t, ns, key), ""),
        "edited": "new_ja" in e,
        "state": rv.get("state", "未"),
        "note": rv.get("note", ""),
    }

def row(idx):
    t, ns, key = STATE["queue"][idx]
    return row_key(t, ns, key, idx)

def grp_rows(g):
    return [row_key(t, ns, key, i) for (t, ns, key, i) in g["rows"]]

def save_edit(fk, new_ja, state, note):
    orig = STATE["ja"].get(fk, "")
    errs = validate(orig, new_ja)
    if errs:
        return {"ok": False, "errors": errs}
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    if new_ja != orig:
        # 既存の orig_ja があれば保持（適用後の再編集で baseline が動くため）
        prev = STATE["edits"].get(fk, {})
        STATE["edits"][fk] = {"orig_ja": prev.get("orig_ja", orig),
                              "new_ja": new_ja, "ts": ts}
    else:
        STATE["edits"].pop(fk, None)  # 元に戻したらオーバーレイから除去
    STATE["review"][fk] = {"state": state or "OK", "note": note or "", "ts": ts}
    json.dump(STATE["edits"], open(EDITS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(STATE["review"], open(REVIEW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"ok": True}

# ---- ペルソナ／キャラ -------------------------------------------------------
def parse_persona(char):
    p = os.path.join(PERSONA_DIR, char + ".md")
    if not os.path.exists(p):
        return {"exists": False, "status": "なし",
                "core": "（ペルソナ未作成 — 00_ルールの基本翻訳・口調指針に従う）",
                "examples": ""}
    txt = open(p, encoding="utf-8").read()
    m = re.search(r"^status:\s*(.+)$", txt, re.M)
    status = m.group(1).strip() if m else "不明"
    def section(name):
        mm = re.search(r"^##\s*" + name + r"[^\n]*\n(.*?)(?=^##\s|\Z)", txt, re.M | re.S)
        return mm.group(1).strip() if mm else ""
    return {"exists": True, "status": status,
            "core": section("声の核"), "examples": section("完成例")}

def bucket_of(c):
    if c < 100:  return "lt100"
    if c < 400:  return "mid"
    return "gte400"

def reviewed_by_char():
    # フルキー -> char は k2c を使う。レビュー済(state!=未)をキャラ別に集計
    cnt = {}
    for fk, rv in STATE["review"].items():
        if rv.get("state", "未") == "未":
            continue
        parts = fk.split(SEP)
        if len(parts) == 3:
            ch = STATE["k2c"].get((parts[0], parts[1], parts[2]))
            if ch:
                cnt[ch] = cnt.get(ch, 0) + 1
    return cnt

def char_list(bucket):
    rbc = reviewed_by_char()
    out = []
    for ch, cnt in STATE["char_count"].items():
        if bucket_of(cnt) != bucket:
            continue
        out.append({"char": ch, "count": cnt,
                    "reviewed": rbc.get(ch, 0),
                    "status": parse_persona(ch)["status"]})
    out.sort(key=lambda x: -x["count"])
    return out

# ---- HTTP ------------------------------------------------------------------
class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/" or u.path == "/index.html":
            self._send(200, open(UI_HTML, encoding="utf-8").read(),
                       "text/html; charset=utf-8")
        elif u.path == "/api/groups":
            q = parse_qs(u.query)
            groups = STATE["groups"]
            ng = len(groups)
            if "row" in q:                       # 行番号→その行を含むグループ
                r = max(0, min(int(q["row"][0]), len(STATE["queue"]) - 1))
                goff = STATE["g_of_row"][r]
            else:
                goff = max(0, min(int(q.get("goff", ["0"])[0]), ng))
            target = int(q.get("rows", ["40"])[0])   # 目安行数
            out, acc, gi = [], 0, goff
            while gi < ng and (acc < target or not out):
                g = groups[gi]
                rows = grp_rows(g)
                out.append({"gid": g["gid"], "target": g["target"],
                            "count": len(rows), "rows": rows})
                acc += len(rows); gi += 1
            next_goff = gi if gi < ng else goff
            pg, pacc = goff, 0
            while pg > 0 and pacc < target:
                pg -= 1; pacc += len(groups[pg]["rows"])
            first_idx = next((r[3] for r in groups[goff]["rows"]
                              if r[3] is not None), 0) if goff < ng else 0
            self._send(200, json.dumps({
                "total_rows": len(STATE["queue"]), "total_groups": ng,
                "goff": goff, "next_goff": next_goff, "prev_goff": pg,
                "row_start": first_idx,
                "groups": out}, ensure_ascii=False))
        elif u.path == "/api/chars":
            q = parse_qs(u.query)
            bucket = q.get("bucket", ["gte400"])[0]
            lst = char_list(bucket)
            self._send(200, json.dumps({"bucket": bucket, "chars": lst},
                                       ensure_ascii=False))
        elif u.path == "/api/char_view":
            q = parse_qs(u.query)
            ch = q.get("char", [""])[0]
            gis = STATE["char_groups"].get(ch, [])
            ng = len(gis)
            goff = max(0, min(int(q.get("goff", ["0"])[0]), ng))
            target = int(q.get("rows", ["40"])[0])
            out, acc, gi = [], 0, goff
            while gi < ng and (acc < target or not out):
                g = STATE["groups"][gis[gi]]
                rows = grp_rows(g)
                for r in rows:
                    r["focal"] = (r["char"] == ch)
                out.append({"gid": g["gid"], "target": g["target"],
                            "count": len(rows), "rows": rows})
                acc += len(rows); gi += 1
            next_goff = gi if gi < ng else goff
            pg, pacc = goff, 0
            while pg > 0 and pacc < target:
                pg -= 1; pacc += len(STATE["groups"][gis[pg]]["rows"])
            self._send(200, json.dumps({
                "char": ch, "total_groups": ng, "goff": goff,
                "next_goff": next_goff, "prev_goff": pg,
                "persona": parse_persona(ch), "groups": out}, ensure_ascii=False))
        elif u.path == "/api/nd":
            q = parse_qs(u.query)
            cat = q.get("cat", ["用語"])[0]
            keys = STATE["nd"].get(cat, [])
            n = len(keys)
            off = max(0, min(int(q.get("offset", ["0"])[0]), n))
            lim = int(q.get("limit", ["60"])[0])
            rows = [row_key(t, ns, k) for (t, ns, k) in keys[off:off + lim]]
            self._send(200, json.dumps({"cat": cat, "total": n, "offset": off,
                                        "counts": {c: len(STATE["nd"][c]) for c in ND_CATS},
                                        "rows": rows}, ensure_ascii=False))
        elif u.path == "/api/stats":
            n = len(STATE["queue"])
            reviewed = sum(1 for fk in STATE["review"]
                           if STATE["review"][fk].get("state", "未") != "未")
            self._send(200, json.dumps({"total": n, "edited": len(STATE["edits"]),
                                        "reviewed": reviewed}, ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        u = urlparse(self.path)
        try:
            ln = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(ln) if ln else b""
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception as e:
            self._send(400, json.dumps({"ok": False, "errors": [f"不正なリクエスト本文: {e}"]},
                                       ensure_ascii=False))
            return
        if u.path == "/api/save":
            res = save_edit(data["fk"], data.get("new_ja", ""),
                            data.get("state", "OK"), data.get("note", ""))
            self._send(200 if res["ok"] else 422, json.dumps(res, ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error": "not found"}))

def main():
    print(f"queue={len(STATE['queue'])}  ja={len(STATE['ja'])}  "
          f"edits={len(STATE['edits'])}  review={len(STATE['review'])}")
    print(f"→ http://127.0.0.1:{PORT}  (Ctrl+C で停止)")
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()

if __name__ == "__main__":
    main()
