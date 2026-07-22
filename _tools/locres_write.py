import struct
MAGIC=bytes.fromhex('0E147475674A03FC4A15909DC3377F1B')
def rd_fstr(b,o):
    (n,)=struct.unpack_from('<i',b,o); o+=4
    if n==0: return '',o
    if n<0: c=-n; return b[o:o+c*2].decode('utf-16-le').rstrip('\x00'),o+c*2
    return b[o:o+n].decode('utf-8').rstrip('\x00'),o+n
def wr_fstr(s):
    if s=='' : return struct.pack('<i',0)
    if all(ord(c)<128 for c in s):
        data=s.encode('ascii')+b'\x00'; return struct.pack('<i',len(data))+data
    data=s.encode('utf-16-le')+b'\x00\x00'; return struct.pack('<i',-(len(s)+1))+data
def read_string_array(b,arr_off,ver):
    p=arr_off; (sc,)=struct.unpack_from('<i',b,p); p+=4
    arr=[]
    for _ in range(sc):
        s,p=rd_fstr(b,p); ref=0
        if ver>=3: (ref,)=struct.unpack_from('<i',b,p); p+=4
        arr.append([s,ref])
    return arr,p
def write_string_array(arr,ver):
    out=bytearray(); out+=struct.pack('<i',len(arr))
    for s,ref in arr:
        out+=wr_fstr(s)
        if ver>=3: out+=struct.pack('<i',ref)
    return bytes(out)
def load(path):
    b=open(path,'rb').read(); assert b[:16]==MAGIC
    ver=b[16]; (arr_off,)=struct.unpack_from('<q',b,17)
    arr,end=read_string_array(b,arr_off,ver)
    return b,ver,arr_off,arr,end
