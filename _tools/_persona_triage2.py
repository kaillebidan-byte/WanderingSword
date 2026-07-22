#!/usr/bin/env python3
import os, json, re, glob
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4=os.path.join(ROOT,"_phase4_proofread")
bc=json.load(open(f"{P4}/by_character.json",encoding="utf-8"))
src=json.load(open(f"{P4}/source_zh.json",encoding="utf-8"))
confirmed=[]
for f in glob.glob(f"{ROOT}/10_人物/*.md"):
    name=os.path.splitext(os.path.basename(f))[0]
    if re.search(r'status:\s*確定',open(f,encoding="utf-8",errors="ignore").read()): confirmed.append(name)
HUMBLE=['在下','晚辈','晚輩','末将','末將','卑职','卑職','微臣','妾身','奴家','小女子','鄙人','老朽','老夫','贫道','貧道','贫僧','貧僧','老衲','为师','為師','为父','為父']
HON=['您','阁下','閣下','足下','前辈','前輩','尊驾','尊駕','大师兄','大師兄','师父','師父','师兄','師兄','师姐','師姐']
CASUAL=['小子','你小子','臭小子','丫头','丫頭','娃娃','小鬼','贱','賤','滚','滾']
def body(z):
    b=z.split("$@$",1)[1] if "$@$" in z else z
    return re.sub(r'</?[^>]*>|\\r|\\n|[\r\n]','',b).strip()
def find(lines,markers):
    for t,ns,k in lines:
        z=body(src.get(t+"\x1f"+ns+"\x1f"+k,""))
        if any(m in z for m in markers): return z[:42]
    return ""
out=[]
for name in confirmed:
    lines=bc["lines"].get(name,[])
    txt=" ".join(body(src.get(t+"\x1f"+ns+"\x1f"+k,"")) for t,ns,k in lines)
    h=sum(txt.count(w) for w in HUMBLE); ho=sum(txt.count(w) for w in HON); c=sum(txt.count(w) for w in CASUAL)
    flag=(ho>0 and c>0) or (h>0 and c>0) or (ho>=2 and h>0)
    if not flag: continue
    out.append((name,len(lines),h,ho,c,find(lines,HUMBLE),find(lines,CASUAL)))
out.sort(key=lambda r:-r[1])
for name,n,h,ho,c,he,ce in out:
    print(f"■{name} ({n}行 謙{h}/敬{ho}/俗{c})")
    if he: print(f"  謙: {he}")
    if ce: print(f"  俗: {ce}")
