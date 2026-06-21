# -*- coding: utf-8 -*-
"""典故・古典引用を読み下し/定訳に置換(00_ルール/典故・古典引用ノート 準拠)。
前置き『ID - 名 $@$』と末尾記号は現在値から保ち、本文のみ差し替える。--apply で書込+repak。
"""
import os, sys, glob, struct, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
import locres, locres_write as L
LOC = f"{ROOT}/_work/jp/Wandering_Sword/Content/Localization"
WORK = os.path.join(ROOT, "_work", "jp")
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")

# (tbl, ns, key): 新・本文($@$以降。末尾記号も明示で含める)
NEWBODY = {
    # A 論語(八佾+子罕) 謝学士
    ("Npc", "NPCs", "28222_DefaultTalks_Index0_Dlgs_Index0_Text"):
        "郁郁乎(いくいくこ)として文(ぶん)なるかな、多ならんや、多ならざるなり〜",
    # B 楚辞 九歌・山鬼 (？？？)
    ("CG表", "QuestDlgs", "12396_1_Dlgs_Index1_Text"):
        "山中の人 杜若(とじゃく)に芳(かんば)し、石泉を飲み松柏に蔭(かく)る……",
    ("CG表", "QuestDlgs", "12396_1_Dlgs_Index0_Text"):
        "公子を怨みて悵(ちょう)として帰るを忘れ、君 我を思へど閑(いとま)を得ず……",
    ("CG表", "QuestDlgs", "12396_3_Dlgs_Index0_Text"):
        "雷 填填(てんてん)として雨 冥冥(めいめい)たり、猿 啾啾(しゅうしゅう)として狖(ゆう)夜に鳴く……",
    ("CG表", "QuestDlgs", "12396_3_Dlgs_Index1_Text"):
        "風 颯颯(さつさつ)として木 蕭蕭(しょうしょう)たり、公子を思ひて徒(いたずら)に憂ひに離(かか)る……",
    # C 詩経 陳風・月出 (顧思帰/白惟一)
    ("CG表", "QuestDlgs", "8864_2_Dlgs_Index0_Text"):
        "月出でて皎(こう)たり、佼人(こうじん)僚(りょう)たり。舒(おもむ)ろにして窈糾(ようきゅう)たり、心を労して悄(しょう)たり……",
    ("CG表", "QuestDlgs", "8864_2_Dlgs_Index1_Text"):
        "月出でて皓(こう)たり、佼人(こうじん)……",
    ("Npc", "NPCs", "19700_DefaultTalks_Index0_Dlgs_Index0_Text"):
        "月出でて皎たり〜月出でて皎たり〜",
    ("Npc", "NPCs", "19701_DefaultTalks_Index0_Dlgs_Index0_Text"):
        "月出でて皎たり〜月出でて皎たり〜",
    ("Npc", "NPCs", "20016_DefaultTalks_Index0_Dlgs_Index0_Text"):
        "月出でて皎たり〜月出でて皎たり〜",
    ("Npc", "NPCs", "19969_DefaultTalks_Index0_Dlgs_Index0_Text"):
        "月出でて皎たり～月出でて皎たり～",
    # D 道家・内丹の詩 (道玄) ※もじりの可能性込みで読み下し化
    ("Quests任务表", "Quests", "5223_FinishingDlgs_Index0_Text"):
        "……虚室 却(かえ)って光を生じ、静中 又(また)陽を復す。采(と)り来たりて勤めて鍛錬し、化して紫金の霜を就(な)す……",
    ("Quests任务表", "Quests", "5223_FinishingDlgs_Index7_Text"):
        "……朗朗たる夜明(やめい)の珠、皎潔ならざる処(ところ)無し……",
    # === 第2弾 ===
    # E 七言詩(荀杳杳)
    ("CG表", "QuestDlgs", "12633_2_Dlgs_Index0_Text"):
        "十年の身事(しんじ)各(おのおの)萍(うきくさ)の如く、白首(はくしゅ)相(あい)逢うて涙 纓(えい)に満つ。",
    ("CG表", "QuestDlgs", "12633_6_Dlgs_Index0_Text"):
        "十年の身事(しんじ)各(おのおの)萍(うきくさ)の如く、白首(はくしゅ)相(あい)逢うて涙 纓(えい)に満つ。",
    # F 太極拳論(虚霊頂勁) 宇文逸
    ("CG表", "QuestDlgs", "5345_3_Dlgs_Index0_Text"):
        "虚霊頂勁(きょれいちょうけい)、蓄(たくわ)へて后(のち)に発す……",
    ("CG表", "QuestDlgs", "5455_3_Dlgs_Index0_Text"):
        "虚霊頂勁(きょれいちょうけい)、蓄(たくわ)へて后(のち)に発す……",
    # G 鮑照「舞鶴賦」窮陰殺節
    ("CG表", "QuestDlgs", "21284_1_Dlgs_Index5_Text"):
        "窮陰(きゅういん)節を殺(そ)ぎ——急景(きゅうけい)年を凋(しぼ)ましむ！",
    ("CG表", "QuestDlgs", "16201_2_Dlgs_Index2_Text"):
        "窮陰(きゅういん)節を殺(そ)ぎ、急景(きゅうけい)……",
    ("CG表", "QuestDlgs", "16202_2_Dlgs_Index2_Text"):
        "窮陰(きゅういん)節を殺(そ)ぎ、急景(きゅうけい)……",
    # H 唯識(万法唯識) 法滅尽
    ("CG表", "QuestDlgs", "22142_4_Dlgs_Index0_Text"):
        "万法(ばんぽう)唯(ただ)識(しき)のみ、拝見(はいけん)。",
    # I 道家咒(上極九清) 宇文逸/円慧
    ("CG表", "QuestDlgs", "5160_9_Dlgs_Index10_Text"):
        "上(かみ)は九清(きゅうせい)を極め、炁(き)を陰陽に復す……",
    ("CG表", "QuestDlgs", "18782_2_Dlgs_Index0_Text"):
        "上(かみ)は九清(きゅうせい)を極め、炁(き)を陰陽に復す……",
    # J 内丹・剣訣の口訣(竅開玄衝/気清生雲) 乞丐/宇文逸 ※やや自信中
    ("CG表", "QuestDlgs", "5390_12_Dlgs_Index2_Text"):
        "……竅(きょう)開きて玄衝(げんしょう)し、神(しん)凝(こ)りて虚(きょ)を破る……",
    ("CG表", "QuestDlgs", "5390_12_Dlgs_Index3_Text"):
        "（……竅(きょう)開きて玄衝(げんしょう)し、神(しん)凝(こ)りて虚(きょ)を破る……）",
    ("CG表", "QuestDlgs", "5390_12_Dlgs_Index1_Text"):
        "気(き)清(す)みて雲を生じ……三合御剣、六華週始、九天演一……",
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
    cache = {}
    edits = {}   # tbl -> [(ns,key,old,new)]
    for (tbl, ns, key), nb in NEWBODY.items():
        if tbl not in cache:
            cache[tbl] = locres.parse(glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0])[1]
        old = cache[tbl].get(ns + "\x1f" + key)
        if old is None or "$@$" not in old:
            print(f"  ⚠ SKIP {tbl}|{key}: 取得不可 old={old!r}"); continue
        head = old.split("$@$", 1)[0] + "$@$"
        new = head + nb
        edits.setdefault(tbl, []).append((ns, key, old, new))
        print(f"[{tbl}|{key}]\n  旧: {old.split('$@$',1)[1]}\n  新: {nb}")
    if not apply:
        print("\n[プレビュー] 実書込は --apply")
        return
    touched = []
    for tbl, es in edits.items():
        lp = glob.glob(f"{LOC}/{tbl}/zh-Hans/*.locres")[0]
        b = open(lp, "rb").read()
        kmap, arr_off = key_index_map(b)
        _, ver, _, arr, _ = L.load(lp)
        n = 0
        for ns, key, old, new in es:
            i = kmap.get(ns + "\x1f" + key)
            if i is None: print(f"  ⚠ key無し {key}"); continue
            if arr[i][0] == new: continue
            if arr[i][0] == old:
                arr[i][0] = new; n += 1
            else:
                print(f"  ⚠ 不一致 {key}: now={arr[i][0]!r}")
        if n:
            open(lp, "wb").write(b[:arr_off] + L.write_string_array(arr, ver))
            touched.append((tbl, n))
    outpak = os.path.join(ROOT, "_work", "aaWanderingSword_JP_P.pak")
    if os.path.exists(outpak):
        try: os.remove(outpak)
        except PermissionError: open(outpak, "wb").close()
    subprocess.run([REPAK, "pack", WORK, outpak, "--version", "V11",
                    "--mount-point", "../../../"], check=True)
    print(f"\n✅ 書込 {touched} / repak -> {outpak}")

if __name__ == "__main__":
    main()
