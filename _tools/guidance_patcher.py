import struct, re, json, os, sys

TM=json.load(open("/sessions/determined-zealous-franklin/tm.json"))
PAT=re.compile(rb'(\x21\x00\x00\x00[0-9A-F]{32}\x00)(....)', re.S)

def wr_utf16(s):
    d=s.encode('utf-16-le')+b'\x00\x00'
    return struct.pack('<i',-(len(s)+1))+d

def patch_file(uasset_path, uexp_path, out_uasset, out_uexp, verbose=False):
    ua=bytearray(open(uasset_path,'rb').read())
    ux=bytearray(open(uexp_path,'rb').read())
    usize=len(ua); xsize=len(ux)
    # 1. find FText source strings to replace
    repl=[]  # (start,end,newbytes) in uexp
    for m in PAT.finditer(bytes(ux)):
        o=m.start(2)
        (slen,)=struct.unpack_from('<i',ux,o)
        if slen<0:
            n=-slen
            if n<2 or n>2000: continue
            end=o+4+2*n
            src=ux[o+4:end-2].decode('utf-16-le','replace')
        elif 0<slen<=2000:
            end=o+4+slen
            src=ux[o+4:end-1].decode('latin1')
        else: continue
        if not any('一'<=c<='鿿' for c in src): continue
        ja=TM.get(src)
        if not ja:
            if verbose: print("  NO-TM:",src[:30]); continue
        # FPropertyTag Size check: value starts at key_lenfield-10 (flags4+hist1+ns5)
        val_start=m.start(1)-10
        (tag_size,)=struct.unpack_from('<i',ux,val_start-9)
        expected=10+37+(end-o)
        if tag_size!=expected:
            raise RuntimeError(f"tag size mismatch {tag_size}!={expected} in {uexp_path}")
        repl.append((o,end,wr_utf16(ja),src,ja,val_start-9))
    if not repl: return 0
    # 2. locate export map in uasset: chain of (SerialSize int64, SerialOffset int64) stride 104
    # find first export entry: SerialOffset==usize at q+8
    chain=None
    i=0
    while True:
        i=ua.find(struct.pack('<q',usize),i)
        if i<0: break
        q=i-8  # SerialSize position
        if q>=0:
            ents=[]; qq=q; off_expect=usize
            while qq+16<=len(ua):
                (sz,)=struct.unpack_from('<q',ua,qq)
                (off,)=struct.unpack_from('<q',ua,qq+8)
                if off!=off_expect or sz<=0 or sz>0x10000000: break
                ents.append((qq,sz,off)); off_expect=off+sz; qq+=104
            if ents and off_expect==usize+xsize-4:
                chain=ents; break
        i+=1
    if chain is None: raise RuntimeError("export map not found "+uasset_path)
    # 3. apply replacements back-to-front in uexp; compute per-export deltas
    deltas=[]  # (abs_offset, delta)
    for (o,end,new,src,ja,sizepos) in sorted(repl,key=lambda r:-r[0]):
        old_len=end-o
        d=len(new)-old_len
        (tag_size,)=struct.unpack_from('<i',ux,sizepos)
        struct.pack_into('<i',ux,sizepos,tag_size+d)
        ux[o:end]=new
        deltas.append((usize+o, d))
        if verbose: print(f"  @{o:#x} {old_len}->{len(new)}B tagSize {tag_size}->{tag_size+d} {src[:14]!r}->{ja[:14]!r}")
    # 4. fix export map
    for (qq,sz,off) in chain:
        newsz=sz; newoff=off
        for (ax,d) in deltas:
            if off<=ax<off+sz: newsz+=d
            if ax<off: newoff+=d
        struct.pack_into('<q',ua,qq,newsz)
        struct.pack_into('<q',ua,qq+8,newoff)
    total_delta=sum(d for _,d in deltas)
    # 5. fix BulkDataStartOffset in summary (first 512 bytes)
    fixed_bulk=0
    locs=[]
    for cand in (usize+xsize-4, usize+xsize):
        j=ua.find(struct.pack('<q',cand),0,512)
        while j>=0:
            locs.append((j,cand)); j=ua.find(struct.pack('<q',cand),j+8,512)
        if locs: break
    for j,cand in locs:
        struct.pack_into('<q',ua,j,cand+total_delta); fixed_bulk+=1
    if fixed_bulk!=1: raise RuntimeError(f"bulk fix count {fixed_bulk} in {uasset_path}")
    os.makedirs(os.path.dirname(out_uasset),exist_ok=True)
    open(out_uasset,'wb').write(ua)
    open(out_uexp,'wb').write(ux)
    if verbose: print(f"  exports={len(chain)} delta={total_delta} bulkfix={fixed_bulk}")
    return len(repl)

if __name__=="__main__":
    src=sys.argv[1]; dst=sys.argv[2]
    n=patch_file(src+".uasset",src+".uexp",dst+".uasset",dst+".uexp",verbose=True)
    print("patched",n)
