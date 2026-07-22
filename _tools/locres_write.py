import struct

MAGIC = bytes.fromhex("0E147475674A03FC4A15909DC3377F1B")


def rd_fstr(data, offset):
    (length,) = struct.unpack_from("<i", data, offset)
    offset += 4
    if length == 0:
        return "", offset
    if length < 0:
        chars = -length
        end = offset + chars * 2
        return data[offset:end].decode("utf-16-le").rstrip("\x00"), end

    end = offset + length
    # Unrealの正数長FStringはANSIバイト列。通常はUTF-8として読めるが、
    # 旧資産にはcp1252等の単一バイトが残る。surrogateescapeなら
    # 意味を勝手に置換せず、書き戻し時に元バイトへ完全往復できる。
    return data[offset:end].decode("utf-8", "surrogateescape").rstrip("\x00"), end


def wr_fstr(value):
    if value == "":
        return struct.pack("<i", 0)

    has_escaped_bytes = any("\udc80" <= char <= "\udcff" for char in value)
    if has_escaped_bytes:
        encoded = value.encode("utf-8", "surrogateescape") + b"\x00"
        return struct.pack("<i", len(encoded)) + encoded

    if all(ord(char) < 128 for char in value):
        encoded = value.encode("ascii") + b"\x00"
        return struct.pack("<i", len(encoded)) + encoded

    encoded = value.encode("utf-16-le") + b"\x00\x00"
    return struct.pack("<i", -(len(value) + 1)) + encoded


def read_string_array(data, array_offset, version):
    offset = array_offset
    (string_count,) = struct.unpack_from("<i", data, offset)
    offset += 4
    values = []
    for _ in range(string_count):
        value, offset = rd_fstr(data, offset)
        ref_count = 0
        if version >= 3:
            (ref_count,) = struct.unpack_from("<i", data, offset)
            offset += 4
        values.append([value, ref_count])
    return values, offset


def write_string_array(values, version):
    output = bytearray()
    output += struct.pack("<i", len(values))
    for value, ref_count in values:
        output += wr_fstr(value)
        if version >= 3:
            output += struct.pack("<i", ref_count)
    return bytes(output)


def load(path):
    data = open(path, "rb").read()
    assert data[:16] == MAGIC
    version = data[16]
    (array_offset,) = struct.unpack_from("<q", data, 17)
    values, end = read_string_array(data, array_offset, version)
    return data, version, array_offset, values, end
