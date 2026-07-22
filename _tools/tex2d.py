# -*- coding: utf-8 -*-
"""無圧縮 PF_B8G8R8A8 Texture2D(単一/複数mip・インライン) の読み書き。標準ライブラリのみ。
- parse(uexp_bytes) -> dict(sx,sy,fmt,pix_off,pix_len,rgba_off...) mip0情報
- to_png(uexp_path, png_path): mip0をPNG出力(目視用)
- patch_rgba(uexp_path, new_rgba_bgra_bytes, out_path): mip0画素を同寸で差し戻し
"""
import struct, zlib, sys

def parse(b):
    i = b.find(b'PF_B8G8R8A8')
    if i < 0: raise ValueError('not B8G8R8A8 (uncompressed) texture')
    lp = i - 4
    (slen,) = struct.unpack_from('<i', b, lp)
    sx, sy, packed = struct.unpack_from('<iii', b, lp - 12)
    p = i + slen
    first, nmips = struct.unpack_from('<ii', b, p); p += 8
    # mip0
    (bcook,) = struct.unpack_from('<i', b, p); p += 4
    flags, elem, sod = struct.unpack_from('<IIi', b, p); p += 12
    (offset,) = struct.unpack_from('<q', b, p); p += 8
    pix_off = p                      # インライン画素の開始
    pix_len = elem                   # = sx*sy*4
    assert pix_len == sx*sy*4, (pix_len, sx, sy)
    return dict(sx=sx, sy=sy, nmips=nmips, pix_off=pix_off, pix_len=pix_len)

def bgra_to_png(bgra, sx, sy, png_path):
    # B8G8R8A8 -> RGBA、PNG(stdlib)で書き出し
    out = bytearray()
    row = sx*4
    for y in range(sy):
        out.append(0)  # filter none
        r = bgra[y*row:(y+1)*row]
        # BGRA->RGBA
        rr = bytearray(len(r))
        rr[0::4] = r[2::4]; rr[1::4] = r[1::4]; rr[2::4] = r[0::4]; rr[3::4] = r[3::4]
        out += rr
    comp = zlib.compress(bytes(out), 9)
    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', sx, sy, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    open(png_path, 'wb').write(png)

def png_to_bgra(png_path):
    b = open(png_path, 'rb').read()
    assert b[:8] == b'\x89PNG\r\n\x1a\n'
    p = 8; W=H=0; idat=b''
    while p < len(b):
        ln, = struct.unpack_from('>I', b, p); typ = b[p+4:p+8]; data = b[p+8:p+8+ln]; p += 12+ln
        if typ == b'IHDR':
            W,H,bd,ct = struct.unpack_from('>IIBB', data, 0)
            assert bd==8 and ct==6, (bd,ct)
        elif typ == b'IDAT': idat += data
        elif typ == b'IEND': break
    raw = zlib.decompress(idat)
    row = W*4; out = bytearray(W*H*4); prev = bytearray(row)
    q=0
    for y in range(H):
        filt = raw[q]; q+=1
        line = bytearray(raw[q:q+row]); q+=row
        if filt==0: pass
        elif filt==1:
            for x in range(4,row): line[x]=(line[x]+line[x-4])&0xff
        elif filt==2:
            for x in range(row): line[x]=(line[x]+prev[x])&0xff
        elif filt==3:
            for x in range(row):
                a=line[x-4] if x>=4 else 0; line[x]=(line[x]+((a+prev[x])>>1))&0xff
        elif filt==4:
            for x in range(row):
                a=line[x-4] if x>=4 else 0; c=prev[x-4] if x>=4 else 0; bb=prev[x]
                pp=a+bb-c; pa=abs(pp-a); pb=abs(pp-bb); pc=abs(pp-c)
                pr=a if (pa<=pb and pa<=pc) else (bb if pb<=pc else c)
                line[x]=(line[x]+pr)&0xff
        else: raise ValueError('filter %d'%filt)
        # RGBA -> BGRA
        seg=out[y*row:(y+1)*row]
        out[y*row+0:(y+1)*row:4]=line[2::4]
        out[y*row+1:(y+1)*row:4]=line[1::4]
        out[y*row+2:(y+1)*row:4]=line[0::4]
        out[y*row+3:(y+1)*row:4]=line[3::4]
        prev=line
    return bytes(out), W, H

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'topng':
        b=open(sys.argv[2],'rb').read(); m=parse(b)
        bgra_to_png(b[m['pix_off']:m['pix_off']+m['pix_len']], m['sx'], m['sy'], sys.argv[3])
        print('wrote',sys.argv[3], m['sx'],'x',m['sy'])
    elif cmd == 'patch':
        b=bytearray(open(sys.argv[2],'rb').read()); m=parse(bytes(b))
        bgra,W,H=png_to_bgra(sys.argv[3])
        assert (W,H)==(m['sx'],m['sy']), 'size mismatch %r vs %r'%((W,H),(m['sx'],m['sy']))
        b[m['pix_off']:m['pix_off']+m['pix_len']]=bgra
        open(sys.argv[4],'wb').write(bytes(b)); print('patched ->',sys.argv[4])
