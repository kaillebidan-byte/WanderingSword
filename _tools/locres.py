import struct, sys
MAGIC=bytes.fromhex('0E147475674A03FC4A15909DC3377F1B')
def rd(b,o):
    (n,)=struct.unpack_from('<i',b,o); o+=4
    if n==0: return '',o
    if n<0: c=-n; return b[o:o+c*2].decode('utf-16-le','replace').rstrip('\x00'),o+c*2
    return b[o:o+n].decode('utf-8','replace').rstrip('\x00'),o+n
def parse(path):
    b=open(path,'rb').read(); assert b[:16]==MAGIC
    o=16; ver=b[o]; o+=1
    (arr_off,)=struct.unpack_from('<q',b,o); o+=8
    strings=[]; p=arr_off
    (sc,)=struct.unpack_from('<i',b,p); p+=4
    for _ in range(sc):
        s,p=rd(b,p)
        if ver>=3: p+=4
        strings.append(s)
    o+=4                                   # extra uint32 (entry count?)
    (nsc,)=struct.unpack_from('<I',b,o); o+=4
    out={}; nslist=[]
    for _ in range(nsc):
        o+=4                               # ns hash
        ns,o=rd(b,o)
        (kc,)=struct.unpack_from('<I',b,o); o+=4
        nslist.append((ns,kc))
        for _ in range(kc):
            o+=4                           # key hash
            key,o=rd(b,o)
            o+=4                           # src hash
            (idx,)=struct.unpack_from('<i',b,o); o+=4
            out[ns+'\x1f'+key]=strings[idx] if 0<=idx<len(strings) else None
    return ver,out,o,len(b),nslist,sc
if __name__=='__main__':
    ver,d,o,ln,nslist,sc=parse(sys.argv[1])
    print(f'ver{ver} strings={sc} entries={len(d)} parsed={o}/{ln} {"OK" if o==ln else "MISMATCH"}')
    print('namespaces:',[(n,k) for n,k in nslist])
