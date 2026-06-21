# -*- coding: utf-8 -*-
"""非対話(Buff与道具)の未訳説明を翻訳して locres 書込＋_work repak。
deployはしない(他の修正とまとめてデプロイするため)。--apply で書込。
"""
import os, sys, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")
TBL, NS = "Buff与道具", "Buffs"

NEW = {
    "3011_Description": "この招式を使用時、15%の確率で目標に（自身の内力*3）の追加ダメージを与える。",
    "1010_Description": "両儀連華剣を使用時、1つの目標を攻撃するごとに自身に武当剣法招式強化効果を1層付与する。",
    "8511_Description": "いずれかの通常攻撃系江湖武学を使用時、自身の真気+50。",
    "1072_Description": "天羽奇剣を使用後、自身に天羽勢効果を2～3層追加で付与する。",
    "2060_Description": "この技能を使用時、会心は発生せず、自身の気血+10%。",
    "2063_Description": "この技能を使用時、会心は発生せず、自身の気血+10%。",
    "1080_Description": "この招式を使用時、自身に剣気効果がある場合、目標の気血-8%。目標1体ごとに剣気効果を1層消費する。",
    "1060_Description": "この招式で1つの目標を攻撃するごとに、自身に剣気効果を1層付与する。",
    "2020_Description": "武当派のすべての刀法招式を使用時、1つの目標を攻撃するごとに自身の真気+3%。",
    "2073_Description": "燃木刀法を使用時、8%の確率で800点の追加ダメージを与える。",
    "3511_ViewName": "全槍棍招式ダメージ増加",
    "300_Description": "受けたダメージの1%を反射する。",
    "301_Description": "受けたダメージの10%を反射する。",
    "3031_ViewName": "大日如来-目標3体気絶",
    "2120_Description": "すべての悪人谷刀法招式のダメージ+7%。",
    "2061_Description": "会心0。",
    "1073_Description": "15%の確率で目標に（自身の身法*3）の追加ダメージを与える。",
    "2010_Description": "この武学の会心+30%。",
    "2011_Description": "この武学の会心{0}上昇。",
    "2132_Description": "この武学の会心{0}上昇。",
    "2021_Description": "1つの目標を攻撃するごとに自身の真気+3%。",
    "3520_Description": "1つの目標を攻撃するごとに自身の防御+3%、最大10層まで重ねがけ、2ターン持続。",
    "2153_Description": "気血が1%減るごとに、被ダメージ+0.6%。",
    "207_Description": "目標の集気値を除去して0にする。現在の集気値が満タンの目標には無効。",
    "206_ViewName": "灼熱ダメージ*1層",
    "3643_ViewName": "玉龍百式 強化判定",
    "1031_Description": "自身の真気上限100点ごとに、真武剣気のダメージ+10点。",
    "1020_Description": "自身の移動力1点ごとに清風剣法のダメージ+7%。",
    "2072_Description": "1000点のダメージを与える。",
    "3031_Description": "ランダムな3体の目標に気絶効果を与える。",
}

def key_index_map(b):
    o = 17; (arr_off,) = struct.unpack_from('<q', b, o); o += 8
    o += 4; (nsc,) = struct.unpack_from('<I', b, o); o += 4
    def rf(b, o):
        (n,) = struct.unpack_from('<i', b, o); o += 4
        if n == 0: return '', o
        if n < 0:
            c = -n; return b[o:o+c*2].decode('utf-16-le').rstrip('\x00'), o+c*2
        return b[o:o+n].decode('utf-8').rstrip('\x00'), o+n
    m = {}
    for _ in range(nsc):
        o += 4; ns, o = rf(b, o); (kc,) = struct.unpack_from('<I', b, o); o += 4
        for _ in range(kc):
            o += 4; key, o = rf(b, o); o += 4; (idx,) = struct.unpack_from('<i', b, o); o += 4
            m[ns+'\x1f'+key] = idx
    return m, arr_off

def main():
    apply = "--apply" in sys.argv
    lp = glob.glob(f"{LOC}/{TBL}/zh-Hans/*.locres")[0]
    cur = locres.parse(lp)[1]
    for k, nv in NEW.items():
        old = cur.get(NS + "\x1f" + k, "")
        print(f"[{k}]\n  旧: {old}\n  新: {nv}")
    if not apply:
        print("\n[プレビュー] --apply で書込(deployはしない)"); return
    b = open(lp, "rb").read()
    kmap, arr_off = key_index_map(b)
    _, ver, _, arr, _ = L.load(lp)
    n = 0
    for k, nv in NEW.items():
        i = kmap.get(NS + "\x1f" + k)
        if i is None: print(f"  ⚠ key無し {k}"); continue
        if arr[i][0] != nv:
            arr[i][0] = nv; n += 1
    open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    if os.path.exists(outpak):
        try: os.remove(outpak)
        except PermissionError: open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11", "--mount-point", "../../../"], check=True)
    print(f"\n✅ 書込 {n}件 / repak -> {outpak}  (deployは未実施)")

if __name__ == "__main__":
    main()
