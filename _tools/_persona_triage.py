#!/usr/bin/env python3
import os, json, re, glob
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4=os.path.join(ROOT,"_phase4_proofread")
bc=json.load(open(f"{P4}/by_character.json",encoding="utf-8"))
src=json.load(open(f"{P4}/source_zh.json",encoding="utf-8"))

# 確定キャラ一覧
confirmed=[]
for f in glob.glob(f"{ROOT}/10_人物/*.md"):
    name=os.path.splitext(os.path.basename(f))[0]
    t=open(f,encoding="utf-8",errors="ignore").read()
    if re.search(r'status:\s*確定',t): confirmed.append(name)

HUMBLE=['在下','晚辈','晚輩','末将','末將','卑职','卑職','微臣','妾身','奴家','小女子','鄙人','老朽','老夫','贫道','貧道','贫僧','貧僧','老衲','为师','為師','为父','為父']
HON=['您','阁下','閣下','足下','前辈','前輩','尊驾','尊駕','大师兄','大師兄','师父','師父','师兄','師兄','师姐','師姐']
CASUAL=['小子','你小子','臭小子','丫头','丫頭','娃娃','小鬼','贱','賤','滚','滾']

def body(z):
    b=z.split("$@$",1)[1] if "$@$" in z else z
    return re.sub(r'</?[^>]*>|\\r|\\n|[\r\n]','',b)

rows=[]
for name in confirmed:
    lines=bc["lines"].get(name,[])
    txt=" ".join(body(src.get(t+"\x1f"+ns+"\x1f"+k,"")) for t,ns,k in lines)
    n=len(lines)
    h=sum(txt.count(w) for w in HUMBLE)
    ho=sum(txt.count(w) for w in HON)
    c=sum(txt.count(w) for w in CASUAL)
    # 切替候補=敬+俗が同居 / 謙譲が出る
    flag = (ho>0 and c>0) or (h>0 and c>0) or (ho>=2 and h>0)
    rows.append((name,n,h,ho,c,flag))

rows.sort(key=lambda r:(-r[5],-r[1]))
cand=[r for r in rows if r[5]]
print(f"確定キャラ {len(confirmed)}件 / モード切替候補 {len(cand)}件\n")
print("=== 切替候補(原文に敬+俗/謙譲が同居=要・本書き) ===")
print("キャラ | 行数 | 謙譲 | 敬称 | 俗称")
for name,n,h,ho,c,fl in cand:
    print(f"{name} | {n} | {h} | {ho} | {c}")
print(f"\n=== 単一モード({len(rows)-len(cand)}件・軽処理でよい) ===")
print("、".join(r[0] for r in rows if not r[5]))
