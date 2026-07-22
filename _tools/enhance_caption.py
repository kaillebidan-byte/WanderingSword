# -*- coding: utf-8 -*-
"""チュートリアル画像のキャプション文字を「グレー→白＋黒縁」に強調。
キャプション帯(パネルから分離した透過帯)のみ処理。パネル/罫線/アイコンは不変。
使い方: python _tools/enhance_caption.py in.png out.png [radius]
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import tex2d

def enhance(bgra, W, H, radius=2):
    bgra = bytearray(bgra)
    A = 3
    def idx(x, y): return (y*W + x)*4
    # 行ごとの不透明画素数
    rowop = [0]*H
    for y in range(H):
        c = 0; base = y*W*4
        for x in range(W):
            if bgra[base + x*4 + A] > 60: c += 1
        rowop[y] = c
    # テキスト行 = 5 < 不透明 < W*0.55(パネル行を除外)
    panel_thr = int(W*0.55)
    is_text_row = [5 < rowop[y] < panel_thr for y in range(H)]
    # テキスト画素マスク(グレー文字。黒罫線 lum<40 と 明色 lum>190 は除外)
    text = bytearray(W*H)  # 0/1
    for y in range(H):
        if not is_text_row[y]: continue
        base = y*W*4
        for x in range(W):
            i = base + x*4
            a = bgra[i+A]
            if a <= 100: continue
            lum = (bgra[i] + bgra[i+1] + bgra[i+2]) // 3
            if lum >= 40:   # 黒罫線(lum<40)以外の文字=グレーも白見出しも対象
                text[y*W + x] = 1
    # 黒縁: テキスト近傍(半径radius)で「現在ほぼ透明」の画素を黒不透明に
    r = radius
    for y in range(H):
        if not is_text_row[y]: continue
        for x in range(W):
            if not text[y*W + x]: continue
            for dy in range(-r, r+1):
                yy = y+dy
                if yy < 0 or yy >= H: continue
                for dx in range(-r, r+1):
                    xx = x+dx
                    if xx < 0 or xx >= W: continue
                    if text[yy*W + xx]: continue
                    j = idx(xx, yy)
                    if bgra[j+A] < 90:  # 透明 → 黒縁
                        bgra[j] = 0; bgra[j+1] = 0; bgra[j+2] = 0; bgra[j+3] = 255
    # 文字を白へ(アルファは維持)
    for y in range(H):
        if not is_text_row[y]: continue
        for x in range(W):
            if text[y*W + x]:
                i = idx(x, y)
                bgra[i] = 255; bgra[i+1] = 255; bgra[i+2] = 255
    return bytes(bgra)

if __name__ == '__main__':
    inp, outp = sys.argv[1], sys.argv[2]
    r = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    bgra, W, H = tex2d.png_to_bgra(inp)
    out = enhance(bgra, W, H, r)
    tex2d.bgra_to_png(out, W, H, outp)
    print(f"enhanced -> {outp} ({W}x{H}, r={r})")
