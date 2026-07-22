# -*- coding: utf-8 -*-
"""locres 完全ラウンドトリップ read/write。
ソースハッシュ書換と特定エントリの訳文差替に使う。未改変なら入力とバイト一致する。
書式: MAGIC(16) ver(1) arr_off(q) entryCount(u32) nsCount(u32)
      [nsHash(u32) ns(fstr) keyCount(u32) [keyHash(u32) key(fstr) srcHash(u32) strIdx(i32)]...]...
      @arr_off: strCount(i32) [str(fstr) refCount(u32 if ver>=3)]...
fstr: int32 len; >0 => UTF-8 len bytes(末尾NUL含む); <0 => UTF-16LE (-len)*2 bytes(末尾NUL含む); 0 => 空。
"""
import struct
MAGIC = bytes.fromhex('0E147475674A03FC4A15909DC3377F1B')

def _rd_raw(b, o):
    """fstr を (text, raw_bytes_including_lenprefix, new_offset) で返す"""
    start = o
    (n,) = struct.unpack_from('<i', b, o); o += 4
    if n == 0:
        return '', b[start:o], o
    if n < 0:
        c = -n; raw = b[start:o + c*2]; txt = b[o:o+c*2].decode('utf-16-le').rstrip('\x00'); o += c*2
    else:
        raw = b[start:o + n]; txt = b[o:o+n].decode('utf-8').rstrip('\x00'); o += n
    return txt, raw, o

def wr_fstr(s):
    if s == '':
        return struct.pack('<i', 0)
    if all(ord(c) < 128 for c in s):
        data = s.encode('ascii') + b'\x00'
        return struct.pack('<i', len(data)) + data
    data = s.encode('utf-16-le') + b'\x00\x00'
    return struct.pack('<i', -(len(s) + 1)) + data

class Locres:
    def __init__(self, path):
        b = open(path, 'rb').read(); assert b[:16] == MAGIC, 'bad magic'
        self.ver = b[16]
        (self.arr_off,) = struct.unpack_from('<q', b, 17)
        o = 25
        (self.entry_count,) = struct.unpack_from('<I', b, o); o += 4
        (nsc,) = struct.unpack_from('<I', b, o); o += 4
        self.namespaces = []   # [nsHash, ns_raw, ns_text, [ [keyHash, key_raw, key_text, srcHash, idx], ... ]]
        for _ in range(nsc):
            (nsHash,) = struct.unpack_from('<I', b, o); o += 4
            ns, ns_raw, o = _rd_raw(b, o)
            (kc,) = struct.unpack_from('<I', b, o); o += 4
            keys = []
            for _ in range(kc):
                (keyHash,) = struct.unpack_from('<I', b, o); o += 4
                key, key_raw, o = _rd_raw(b, o)
                (srcHash,) = struct.unpack_from('<I', b, o); o += 4
                (idx,) = struct.unpack_from('<i', b, o); o += 4
                keys.append([keyHash, key_raw, key, srcHash, idx])
            self.namespaces.append([nsHash, ns_raw, ns, keys])
        # strings array
        p = self.arr_off
        (sc,) = struct.unpack_from('<i', b, p); p += 4
        self.strings = []   # [text, raw_fstr_bytes, refcount]
        for _ in range(sc):
            s, raw, p = _rd_raw(b, p)
            ref = 0
            if self.ver >= 3:
                (ref,) = struct.unpack_from('<i', b, p); p += 4
            self.strings.append([s, raw, ref])
        self._lookup = {}
        for nsHash, ns_raw, ns, keys in self.namespaces:
            for ent in keys:
                self._lookup[ns + '\x1f' + ent[2]] = ent

    def entry(self, ns, key):
        return self._lookup.get(ns + '\x1f' + key)

    def set_srchash(self, ns, key, new_hash):
        e = self._lookup[ns + '\x1f' + key]; e[3] = new_hash & 0xFFFFFFFF

    def set_string(self, ns, key, new_text):
        """新規文字列を末尾に追加して該当エントリのindexを差し替える(既存文字列は不変)"""
        e = self._lookup[ns + '\x1f' + key]
        new_idx = len(self.strings)
        self.strings.append([new_text, wr_fstr(new_text), 1])
        e[4] = new_idx

    def to_bytes(self):
        head = bytearray()
        head += MAGIC; head += bytes([self.ver])
        arr_off_pos = len(head); head += b'\x00' * 8
        head += struct.pack('<I', self.entry_count)
        head += struct.pack('<I', len(self.namespaces))
        for nsHash, ns_raw, ns, keys in self.namespaces:
            head += struct.pack('<I', nsHash); head += ns_raw
            head += struct.pack('<I', len(keys))
            for keyHash, key_raw, key, srcHash, idx in keys:
                head += struct.pack('<I', keyHash); head += key_raw
                head += struct.pack('<I', srcHash & 0xFFFFFFFF)
                head += struct.pack('<i', idx)
        arr_off = len(head)
        struct.pack_into('<q', head, arr_off_pos, arr_off)
        sarr = bytearray(); sarr += struct.pack('<i', len(self.strings))
        for s, raw, ref in self.strings:
            sarr += raw
            if self.ver >= 3:
                sarr += struct.pack('<i', ref)
        return bytes(head + sarr)

    def save(self, path):
        open(path, 'wb').write(self.to_bytes())
