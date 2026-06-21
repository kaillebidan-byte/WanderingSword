"""uexp内FTextソース文字列の置換 v2: 入れ子コンテナのSizeも全て補正する"""
import struct, re, os

PAT=re.compile(rb'\x21\x00\x00\x00([0-9A-F]{32})\x00', re.S)

def read_fstr(b,o):
    (n,)=struct.unpack_from('<i',b,o); o+=4
    if n==0: return '',o
    if n<0: c=-n; return b[o:o+c*2].decode('utf-16-le','replace').rstrip('\x00'),o+c*2
    return b[o:o+n].decode('latin1').rstrip('\x00'),o+n

def parse_names(ua):
    # summary: tag,legacy,legacyUE3,verUE4,verLic (5*4) + customversions + headersize + folder + flags + namecount/offset
    o=4*5
    (cvn,)=struct.unpack_from('<i',ua,o); o+=4+cvn*20
    o+=4  # TotalHeaderSize
    _,o=read_fstr(ua,o)  # FolderName
    o+=4  # PackageFlags
    (nc,)=struct.unpack_from('<i',ua,o); o+=4
    (noff,)=struct.unpack_from('<i',ua,o); o+=4
    names=[]; p=noff
    for _ in range(nc):
        s,p=read_fstr(ua,p)
        p+=4  # two uint16 hashes
        names.append(s)
    return names

def find_export_chain(ua, usize, xsize):
    i=ua.find(struct.pack('<q',usize))
    while i>=0:
        q=i-8; qq=q; off_expect=usize; ents=[]
        while qq+16<=len(ua):
            (sz,)=struct.unpack_from('<q',ua,qq); (off,)=struct.unpack_from('<q',ua,qq+8)
            if off!=off_expect or sz<=0 or sz>0x10000000: break
            ents.append((qq,sz,off)); off_expect=off+sz; qq+=104
        if ents and off_expect==usize+xsize-4:
            return ents
        i=ua.find(struct.pack('<q',usize),i+1)
    raise RuntimeError("export map not found")

class Walker:
    """exportのタグ付きプロパティ列を歩き、target offsetを包む全Sizeフィールド位置を返す"""
    def __init__(self, ux, names):
        self.b=ux; self.names=names
    def fname(self,o):
        (i,)=struct.unpack_from('<i',self.b,o); (num,)=struct.unpack_from('<i',self.b,o+4)
        return (self.names[i] if 0<=i<len(self.names) else f"<bad{i}>"), o+8
    def walk_stream(self, o, end, target, chain):
        """o..end のタグ列を歩く。targetを包むSizeフィールドをchainに積む。終端Noneで返る"""
        b=self.b
        while o<end:
            name,o=self.fname(o)
            if name=="None": return o
            typ,o=self.fname(o)
            sizepos=o
            (size,)=struct.unpack_from('<i',b,o); o+=4
            o+=4  # ArrayIndex
            inner=None; keyt=None
            if typ=="StructProperty": o+=8+16
            elif typ in ("ByteProperty","EnumProperty"): o+=8
            elif typ=="BoolProperty": o+=1
            elif typ in ("ArrayProperty","SetProperty"): inner,o=self.fname(o)
            elif typ=="MapProperty": keyt,o=self.fname(o); inner,o=self.fname(o)
            hg=b[o]; o+=1+(16 if hg==1 else 0)
            vstart=o; vend=o+size
            if vstart<=target<vend:
                chain.append(sizepos)
                if typ=="StructProperty":
                    self.walk_stream(vstart,vend,target,chain)
                elif typ=="ArrayProperty":
                    if inner=="StructProperty":
                        p=vstart+4  # count
                        # inner struct tag
                        _n,p=self.fname(p); _t,p=self.fname(p)
                        isz_pos=p; (isz,)=struct.unpack_from('<i',b,p); p+=4
                        p+=4  # arrayindex
                        p+=8+16  # structname+guid
                        hg2=b[p]; p+=1+(16 if hg2==1 else 0)
                        if p<=target<p+isz:
                            chain.append(isz_pos)
                            # 要素はタグ列の連結。targetを含む位置からの走査:
                            q=p
                            while q<p+isz:
                                q2=self.walk_stream(q,p+isz,target,chain)
                                if q2 is None or q<=target<q2: break
                                q=q2
                    elif inner=="TextProperty":
                        pass  # 生FText列: タグなし(パターン検証で除外されるはず)
                    else:
                        pass
                elif typ=="MapProperty":
                    raise RuntimeError("FText inside MapProperty: unsupported")
                return None  # target処理済み(これ以上の同階層走査不要)
            o=vend
        return o
    def chain_for(self, exp_start, exp_end, target):
        chain=[]
        self.walk_stream(exp_start, exp_end, target, chain)
        return chain

def patch_file2(head_path, uexp_path, out_head, out_uexp, TM, verbose=False):
    ua=bytearray(open(head_path,'rb').read())
    ux=bytearray(open(uexp_path,'rb').read())
    usize=len(ua); xsize=len(ux)
    names=parse_names(bytes(ua))
    exports=find_export_chain(bytes(ua), usize, xsize)
    w=Walker(bytes(ux), names)
    # 置換対象の収集
    repl=[]
    for m in PAT.finditer(bytes(ux)):
        o=m.end()
        (slen,)=struct.unpack_from('<i',ux,o)
        if slen<0:
            n=-slen
            if n<2 or n>3000: continue
            end=o+4+2*n; src=ux[o+4:end-2].decode('utf-16-le','replace')
        elif 0<slen<=3000:
            end=o+4+slen; src=ux[o+4:end-1].decode('latin1')
        else: continue
        if not any('一'<=c<='鿿' for c in src): continue
        ja=TM.get(src)
        if not ja: continue
        # 所属exportとサイズチェーン
        ax=usize+o
        owner=[(qq,sz,off) for qq,sz,off in exports if off<=ax<off+sz]
        if not owner: raise RuntimeError(f"no export for {hex(o)}")
        qq,sz,off=owner[0]
        chain=w.chain_for(off-usize, off-usize+sz, o)
        if not chain: raise RuntimeError(f"no enclosing property for {hex(o)} ({src[:10]})")
        newb=struct.pack('<i',-(len(ja)+1))+ja.encode('utf-16-le')+b'\x00\x00'
        repl.append({"o":o,"end":end,"new":newb,"src":src,"ja":ja,"chain":chain,"export_q":qq})
    if not repl: return 0
    # 後ろから適用。サイズフィールド補正は元オフセット基準で全置換分まとめて計算
    deltas=[(r["o"], len(r["new"])-(r["end"]-r["o"])) for r in repl]
    # 1) 各サイズフィールド(int32, uexp内位置)の合計delta
    sizefix={}
    for r in repl:
        d=len(r["new"])-(r["end"]-r["o"])
        for sp in r["chain"]:
            sizefix[sp]=sizefix.get(sp,0)+d
    for sp,d in sizefix.items():
        (cur,)=struct.unpack_from('<i',ux,sp)
        struct.pack_into('<i',ux,sp,cur+d)
        if verbose: print(f"  size@{hex(sp)} {cur}->{cur+d}")
    # 2) 文字列置換(後方から)
    for r in sorted(repl,key=lambda r:-r["o"]):
        ux[r["o"]:r["end"]]=r["new"]
        if verbose: print(f"  @{hex(r['o'])} {r['src'][:14]!r}->{r['ja'][:14]!r} chain={len(r['chain'])}")
    # 3) export map補正
    for qq,sz,off in exports:
        newsz=sz; newoff=off
        for (xo,d) in deltas:
            ax=usize+xo
            if off<=ax<off+sz: newsz+=d
            if ax<off: newoff+=d
        struct.pack_into('<q',ua,qq,newsz)
        struct.pack_into('<q',ua,qq+8,newoff)
    # 4) BulkDataStartOffset
    total=sum(d for _,d in deltas)
    locs=[]
    for cand in (usize+xsize-4, usize+xsize):
        j=ua.find(struct.pack('<q',cand),0,512)
        while j>=0:
            locs.append((j,cand)); j=ua.find(struct.pack('<q',cand),j+8,512)
        if locs: break
    if len(locs)!=1: raise RuntimeError(f"bulk locs {len(locs)}")
    struct.pack_into('<q',ua,locs[0][0],locs[0][1]+total)
    os.makedirs(os.path.dirname(out_head),exist_ok=True)
    open(out_head,'wb').write(ua)
    open(out_uexp,'wb').write(ux)
    return len(repl)

def verify_top(ux, ua_names, exports, usize, modified_axs):
    """変更exportのトップレベルタグ列を歩いて整合確認(名前妥当・None到達・境界内)"""
    w=Walker(bytes(ux), ua_names)
    res=[]
    for qq,sz,off in exports:
        if not any(off<=ax<off+sz for ax in modified_axs): continue
        start=off-usize; end=start+sz
        o=start; props=[]
        while o<end:
            name,o2=w.fname(o)
            if name=="None": o=o2; break
            if name.startswith("<bad"): raise RuntimeError(f"bad name at {hex(o)} in export@{hex(off)}")
            typ,o2=w.fname(o2)
            (size,)=struct.unpack_from('<i',ux,o2); o2+=8
            if typ=="StructProperty": o2+=24
            elif typ in ("ByteProperty","EnumProperty"): o2+=8
            elif typ=="BoolProperty": o2+=1
            elif typ in ("ArrayProperty","SetProperty"): o2+=8
            elif typ=="MapProperty": o2+=16
            hg=ux[o2]; o2+=1+(16 if hg==1 else 0)
            if o2+size>end: raise RuntimeError(f"prop {name} overruns export@{hex(off)}")
            props.append((name,typ,size))
            o=o2+size
        leftover=end-o
        if leftover<0 or leftover>64: raise RuntimeError(f"leftover {leftover} in export@{hex(off)}")
        res.append((off,props,leftover))
    return res
