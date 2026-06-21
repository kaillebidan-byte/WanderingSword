#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""機械置換の先行適用(コスト削減の主軸)。
キャラの確定ペルソナ `10_人物/<キャラ>.md` の「## 機械置換」節に列挙した
**曖昧さの無い1:1 JA→JA置換**(半端漢字・固定呼称・笑い声など)を、そのキャラの全行に先に当てる。
register依存(私/です・ます等)は載せない=LLMの判断に残す。

使い方:
  python _tools/mechanical_pass.py "<キャラ>"            # 適用→locres書き戻し→_work pak再パック
  python _tools/mechanical_pass.py "<キャラ>" --dry       # 件数だけ(書き込みなし)
  python _tools/mechanical_pass.py "<キャラ>" --dry --src <Localizationルート>  # 別ツリーで削減量実測
"""
import sys, os, re, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import json
import locres
import locres_write as L
P4 = os.path.join(ROOT, "_phase4_proofread")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")
WORK = os.path.join(ROOT, "_work", "jp")
DEFAULT_SRC = os.path.join(WORK, "Wandering_Sword", "Content", "Localization")


# 安全弁: これらを置換キー(旧)にするのは禁止。文脈無視の全置換で文を壊すため。
# 一人称/二人称代名詞・コピュラ・終助詞(=register依存。LLMの判断に残すべきもの)。
RISKY_OLD = {
    "私", "我", "你", "君", "俺", "僕", "あたし", "わたし", "わたくし",
    "あなた", "お前", "おまえ", "貴方", "彼", "彼女",
    "です", "ます", "だ", "だわ", "のよ", "わよ", "わね", "かしら",
    "よ", "わ", "ね", "の", "ですわ", "ますわ", "でしょう", "ません",
}


def validate_subs(subs):
    """安全な置換だけ通す。危険(代名詞/コピュラ/1文字)は弾く。"""
    safe, risky = [], []
    for old, new in subs:
        if len(old) < 2 or old in RISKY_OLD:
            risky.append((old, new))
        else:
            safe.append((old, new))
    return safe, risky


def load_subs(character):
    """ペルソナの「## 機械置換」節から (旧, 新) を読む。行形式: 旧 => 新"""
    md = os.path.join(ROOT, "10_人物", f"{character}.md")
    if not os.path.exists(md):
        return []
    text = open(md, encoding="utf-8").read()
    m = re.search(r"^##\s*機械置換.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return []
    subs = []
    for line in m.group(1).splitlines():
        line = line.strip().lstrip("-").strip()
        if "=>" not in line:
            continue
        old, new = line.split("=>", 1)
        old, new = old.strip(), new.strip()
        if old:
            subs.append((old, new))
    return subs


def apply_subs(ja, subs):
    """$@$ より後ろ(本文)だけに置換を当てる。話者名・接頭辞は不変。"""
    if "$@$" in ja:
        head, body = ja.split("$@$", 1)
        for old, new in subs:
            body = body.replace(old, new)
        return head + "$@$" + body
    out = ja
    for old, new in subs:
        out = out.replace(old, new)
    return out


def key_index_map(b):
    """(ns\x1fkey) -> 文字列プールindex"""
    o = 16; ver = b[o]; o += 1
    o += 8            # arr_off
    o += 4            # extra uint32
    (nsc,) = struct.unpack_from('<I', b, o); o += 4
    out = {}
    for _ in range(nsc):
        o += 4
        ns, o = locres.rd(b, o)
        (kc,) = struct.unpack_from('<I', b, o); o += 4
        for _ in range(kc):
            o += 4
            key, o = locres.rd(b, o)
            o += 4
            (idx,) = struct.unpack_from('<i', b, o); o += 4
            out[ns + "\x1f" + key] = idx
    return out


def wlp(src_root, t):
    return glob.glob(f"{src_root}/{t}/zh-Hans/*.locres")[0]


def main():
    args = [a for a in sys.argv[1:]]
    dry = "--dry" in args
    src_root = DEFAULT_SRC
    if "--src" in args:
        src_root = args[args.index("--src") + 1]
    # キャラ名: WS_CHAR優先(PowerShell 5.1のCJK引数化け回避)、無ければ第1非フラグ引数
    character = os.environ.get("WS_CHAR") or next((a for a in args if not a.startswith("--")), None)
    if not character:
        print("キャラ名を環境変数 WS_CHAR か第1引数で指定してください"); return

    subs = load_subs(character)
    if not subs:
        print(f"[skip] {character}: ペルソナに「## 機械置換」節が無い(または空)。LLMのみで校正。")
        return
    subs, risky = validate_subs(subs)
    for o, n in risky:
        print(f"[警告] 危険な置換をスキップ(代名詞/コピュラ/1文字はregister依存=LLM判断に残す): {o!r} => {n!r}")
    if not subs:
        print(f"[skip] {character}: 安全な機械置換エントリが無い。LLMのみで校正。")
        return
    data = json.load(open(f"{P4}/by_character.json", encoding="utf-8"))
    rows = data["lines"].get(character, [])
    by_t = {}
    for t, ns, key in rows:
        by_t.setdefault(t, []).append((ns, key))

    total_lines = 0
    per_sub = {f"{o}=>{n}": 0 for o, n in subs}
    touched_targets = []
    for t, keys in by_t.items():
        lp = wlp(src_root, t)
        b = open(lp, "rb").read()
        _, ver, _, arr, _ = L.load(lp)
        kmap = key_index_map(b)
        changed = 0
        for ns, key in keys:
            i = kmap.get(ns + "\x1f" + key)
            if i is None:
                continue
            old_ja = arr[i][0]
            if not old_ja:
                continue
            new_ja = apply_subs(old_ja, subs)
            if new_ja != old_ja:
                changed += 1; total_lines += 1
                for o, n in subs:
                    if o in (old_ja.split("$@$", 1)[-1]):
                        c = old_ja.split("$@$", 1)[-1].count(o)
                        if c:
                            per_sub[f"{o}=>{n}"] += c
                if not dry:
                    arr[i][0] = new_ja
        if changed and not dry:
            arr_off = struct.unpack_from('<q', b, 17)[0]
            open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
            touched_targets.append((t, changed))

    print(f"[{character}] {'DRY ' if dry else ''}機械置換: 変更行 {total_lines}  (src={src_root.split('Content')[-1] or src_root})")
    for k, v in per_sub.items():
        if v:
            print(f"   {k}: {v}")
    if not dry and total_lines:
        outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
        if os.path.exists(outpak):
            try: os.remove(outpak)
            except PermissionError: open(outpak, "wb").close()
        subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11",
                        "--mount-point", "../../../"], check=True)
        print(f"   再パック完了: {[t for t, _ in touched_targets]}")
    elif not dry:
        print("   変更なし(再パック不要)")


if __name__ == "__main__":
    main()
