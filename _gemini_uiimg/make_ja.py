# -*- coding: utf-8 -*-
"""焼き込みUI画像 日本語化スクリプト
簡体字版をベースに、アイコンを保持して中文テキストを消去し、日本語をフォント描画する。
"""
import os, sys, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = 'src_簡体字'
OUT = '出力_ja'
os.makedirs(OUT, exist_ok=True)

NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
BOKU = '/tmp/fonts/YujiBoku-Regular.ttf'
NOTO_INDEX = 0  # JP想定。実行時に検証する。

def jfont(size, path=NOTO):
    if path == NOTO:
        return ImageFont.truetype(path, size, index=NOTO_INDEX)
    return ImageFont.truetype(path, size)

# ---------------- 汎用ストリップ処理 ----------------

STRIP_SPECS = {
 'Gamepad_A1': ['移動','決定','戻る','並べ替え','情報','切替','区分','即時使用'],
 'Gamepad_A2': ['移動','強化','戻る','出陣/解除','情報','隊列スクロール','切替'],
 'Gamepad_A3': ['主脈選択','決定','戻る','情報','隊列スクロール'],
 'Gamepad_A4': ['経絡選択','決定','戻る','情報','切替'],
 'Gamepad_A5':   ['マス選択','決定/取消\n対象情報','戦場情報','視点変更','自動/手動','戦闘速度','カメラ調整'],
 'Gamepad_A5_0': ['マス選択','決定/取消\n対象情報','戦場情報','視点変更','カメラ調整'],
 'Gamepad_A5_1': ['マス選択','決定/取消\n対象情報','戦場情報','視点変更','自動/手動','戦闘速度','カメラ調整'],
 'Gamepad_A5_2': ['マス選択','決定/取消\n対象情報','戦場情報','視点変更','カメラ調整'],
 'Gamepad_A6': ['移動','決定','取消','任務状況'],
 'Gamepad_A7': ['移動/数量変更','決定','取消','整理','情報','切替','一括売却フィルタ'],
 'Gamepad_A8': ['移動','決定','戻る','整理','情報','贈り物'],
 'Gamepad_A9': ['移動','戻る','情報'],
 'Gamepad_B1': ['移動','決定','情報'],
 'Gamepad_B2': ['移動','決定','戻る','切替'],
 'Gamepad_B3': ['移動','決定','戻る','整理','情報','切替','即時使用','一括売却フィルタ'],
 'Gamepad_B4': ['移動','決定','取消','情報','所持品切替'],
 'Gamepad_B5': ['決定','取消','切替'],
 'Gamepad_B6': ['移動','決定','取消','情報'],
 'Gamepad_B7': ['移動','決定','戻る','削除','セーブ名変更'],
 'Gamepad_B7_1': ['移動','決定','戻る','削除','切替','セーブ名変更'],
 'Gamepad_B7_2': ['移動','決定','戻る','切替'],
 'Gamepad_B8': ['移動','決定'],
 'Gamepad_B9': ['マップ移動'],
 'Gamepad_C1': ['移動','決定','取消','リセット'],
 'Gamepad_C2': ['移動','決定','戻る','情報'],
 'Gamepad_C3': ['上:最大 下:最小 左:減 右:増','決定','取消'],
 'Gamepad_C4': ['戻る','マップ移動','拡大/縮小'],
 'Gamepad_C5': ['WASD:移動','ホイール:拡大縮小'],
 'Gamepad_C6': ['移動','決定','取消'],
 'Gamepad_C7': ['WASD:移動','ホイール:カメラ角度調整'],
 'Gamepad_C8': ['移動','減/増','決定','取消','左右切替','リセット','スクロール','情報'],
 'Gamepad_C9': ['移動','決定','戻る','マップ移動','拡大/縮小'],
 'Gamepad_D1': ['移動','決定','取消','切替','情報'],
 'Gamepad_D2': ['移動','戻る','切替'],
}

def components(im_np, thr=30, min_area=8):
    a = (im_np[:,:,3] > thr).astype(np.uint8)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(a, 8)
    comps = []
    for i in range(1, n):
        x,y,w,h,area = stats[i]
        if area < min_area: continue
        comps.append((x,y,w,h,i))
    return comps, lab

def strip_blocks(comps):
    icons = [c for c in comps if c[3] >= 28 and c[2] <= 60]
    texts = sorted([c for c in comps if not (c[3] >= 28 and c[2] <= 60)])
    blocks = []
    for c in texts:
        x0,y0,w,h,_ = c
        if blocks and x0 - blocks[-1][1] <= 16:
            b = blocks[-1]
            blocks[-1] = [min(b[0],x0), max(b[1],x0+w), min(b[2],y0), max(b[3],y0+h)]
        else:
            blocks.append([x0, x0+w, y0, y0+h])
    # '+'コネクタ除外: 幅<=18 かつ 両側12px以内にアイコン
    def is_conn(b):
        if b[1]-b[0] > 18: return False
        lg = min((b[0]-(ix+iw) for ix,iy,iw,ih,_ in icons if ix+iw <= b[0]+4), default=999)
        rg = min((ix-b[1] for ix,iy,iw,ih,_ in icons if ix >= b[1]-4), default=999)
        return lg <= 12 and rg <= 12
    blocks = [b for b in blocks if not is_conn(b)]
    return icons, blocks

def draw_label(draw, text, size, cx_mode, x_anchor, cy, max_w, font_path=NOTO,
               fill=(255,255,255,255), stroke=(0,0,0,255), stroke_w=2):
    s = size
    while s > 12:
        f = jfont(s, font_path)
        w = draw.textlength(text, font=f)
        if w <= max_w: break
        s -= 1
    f = jfont(s, font_path)
    anchor = 'lm' if cx_mode=='left' else ('rm' if cx_mode=='right' else 'mm')
    draw.text((x_anchor, cy), text, font=f, fill=fill,
              stroke_width=stroke_w, stroke_fill=stroke, anchor=anchor)

def process_strip(name):
    spec = STRIP_SPECS[name]
    pil = Image.open(f'{SRC}/{name}.png').convert('RGBA')
    im = np.array(pil)
    H, W = im.shape[:2]
    comps, lab = components(im)
    icons, blocks = strip_blocks(comps)
    assert len(blocks) == len(spec), f'{name}: blocks={len(blocks)} spec={len(spec)} {blocks}'
    # 消去(拡張bbox)
    for x0,x1,y0,y1 in blocks:
        im[max(0,y0-3):min(H,y1+3), max(0,x0-3):min(W,x1+3)] = 0
    pil = Image.fromarray(im)
    d = ImageDraw.Draw(pil)
    obstacles = sorted([(c[0], c[0]+c[2]) for c in icons] + [(b[0], b[1]) for b in blocks])
    for (x0,x1,y0,y1), text in zip(blocks, spec):
        # 右隣の障害物
        nxt = [ox0 for ox0,ox1 in obstacles if ox0 >= x1 - 4]
        nxt_x = min(nxt) if nxt else W
        prv = [ox1 for ox0,ox1 in obstacles if ox1 <= x0 + 4]
        prv_x = max(prv) if prv else 0
        right_aligned = (nxt_x - x1) <= 15 < (x0 - prv_x)
        if '\n' in text:
            l1, l2 = text.split('\n')
            maxw = nxt_x - x0 - 10 if nxt_x < W else W - x0 - 8
            draw_label(d, l1, 19, 'left', x0, 16, maxw)
            draw_label(d, l2, 19, 'left', x0, 38, maxw)
        else:
            cy = (y0 + y1) // 2
            if right_aligned:
                maxw = x1 - prv_x - 10
                draw_label(d, text, 20, 'right', x1, cy, maxw)
            else:
                maxw = nxt_x - x0 - 10 if nxt_x < W else W - x0 - 8
                draw_label(d, text, 20, 'left', x0, cy, maxw)
    pil.save(f'{OUT}/{name}.png')

# ---------------- Gamepad_08 (按 A 继续) ----------------

def process_g08():
    name = 'Gamepad_08'
    pil = Image.open(f'{SRC}/{name}.png').convert('RGBA')
    im = np.array(pil)
    H, W = im.shape[:2]
    comps, lab = components(im)
    # h>=30: Aアイコン+菱形装飾。アイコン=画像中心に最も近いもの。テキスト: h<30
    big = [c for c in comps if c[3] >= 30]
    texts = [c for c in comps if 15 <= c[3] < 30 and c[2] < 200]
    icon = min(big, key=lambda c: abs(c[0] + c[2]/2 - W/2))
    ix0, ix1 = icon[0], icon[0]+icon[2]
    erased = []
    for x,y,w,h,i in texts:
        # アイコンから左右150px以内のテキストのみ消去対象(装飾は遠い/大きい)
        if x+w < ix0 and ix0 - (x+w) < 60:   # 「按」
            erased.append((x,y,w,h)); im[y-2:y+h+2, x-2:x+w+2] = 0
        elif x > ix1 and x - ix1 < 60:        # 「继续」
            erased.append((x,y,w,h)); im[y-2:y+h+2, x-2:x+w+2] = 0
    pil = Image.fromarray(im)
    d = ImageDraw.Draw(pil)
    cy = icon[1] + icon[3]//2
    draw_label(d, 'で続行', 22, 'left', ix1 + 8, cy, 300)
    pil.save(f'{OUT}/{name}.png')
    print('G08 erased:', erased)

# ---------------- Gamepad_13 / 13_0 (右寄せ2段) ----------------

def process_g13(name):
    pil = Image.open(f'{SRC}/{name}.png').convert('RGBA')
    im = np.array(pil)
    H, W = im.shape[:2]
    comps, lab = components(im)
    icons = [c for c in comps if c[3] >= 26]
    texts = [c for c in comps if c[3] < 26]
    assert len(icons) == 2, icons
    icons = sorted(icons, key=lambda c: c[1])
    for x,y,w,h,i in texts:
        im[max(0,y-3):y+h+3, max(0,x-3):x+w+3] = 0
    pil = Image.fromarray(im)
    d = ImageDraw.Draw(pil)
    for icon, label in zip(icons, ['情報','スキル選択']):
        cy = icon[1] + icon[3]//2
        draw_label(d, label, 19, 'right', icon[0]-6, cy, icon[0]-8)
    pil.save(f'{OUT}/{name}.png')

# ---------------- 毛筆テキスト描画 ----------------

def brush_text(pil, text, cx, cy, size, fill=(255,255,255,255), halo=True,
               halo_alpha=235, grad=None, fit_w=None):
    """黒ハロー+白(or グラデ)毛筆文字を中央(cx,cy)に描く"""
    s = size
    tmp = Image.new('RGBA', pil.size, (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    while s > 10:
        f = jfont(s, BOKU)
        w = td.textlength(text, font=f)
        if fit_w is None or w <= fit_w: break
        s -= 1
    f = jfont(s, BOKU)
    if halo:
        hl = Image.new('L', pil.size, 0)
        hd = ImageDraw.Draw(hl)
        hd.text((cx, cy), text, font=f, fill=255, stroke_width=6, anchor='mm')
        hl = hl.filter(ImageFilter.GaussianBlur(2.2))
        halo_img = Image.new('RGBA', pil.size, (0,0,0,0))
        halo_np = np.array(halo_img)
        hl_np = np.array(hl).astype(np.float32) / 255.0
        halo_np[:,:,3] = (hl_np * halo_alpha).astype(np.uint8)
        pil.alpha_composite(Image.fromarray(halo_np))
    td = ImageDraw.Draw(tmp)
    td.text((cx, cy), text, font=f, fill=(255,255,255,255), stroke_width=1, anchor='mm')
    if grad is not None:
        (top_rgb, bot_rgb) = grad
        tn = np.array(tmp).astype(np.float32)
        ys = np.nonzero(tn[:,:,3].sum(axis=1))[0]
        if len(ys):
            y0g, y1g = ys.min(), ys.max()
            for y in range(y0g, y1g+1):
                t = (y - y0g) / max(1, y1g - y0g)
                col = [top_rgb[k]*(1-t) + bot_rgb[k]*t for k in range(3)]
                tn[y,:,0:3] = col
        tmp = Image.fromarray(tn.astype(np.uint8))
    pil.alpha_composite(tmp)

# ---------------- Gamepad_09 / T_SkipCG ----------------

def process_skip(name):
    pil = Image.open(f'{SRC}/{name}.png').convert('RGBA')
    im = np.array(pil)
    H, W = im.shape[:2]
    # アイコンとテキストのハローが連結している → アルファ列和の谷で分割
    a = im[:,:,3] > 10
    colsum = a.sum(axis=0)
    xcut = int(np.argmin(colsum[30:90])) + 30
    im[:, xcut:] = 0
    pil = Image.fromarray(im)
    cx = (xcut + W) // 2
    brush_text(pil, '長押しスキップ', cx, H//2 + 1, 30, fit_w=W - xcut - 10)
    pil.save(f'{OUT}/{name}.png')

# ---------------- T_PlayCG ----------------

def process_playcg(name, label):
    pil = Image.open(f'{SRC}/{name}.png').convert('RGBA')
    im = np.array(pil)
    H, W = im.shape[:2]
    if name in ('T_PlayCG0','T_PlayCG1'):
        # Yアイコン + 枠 + ▶/Ⅱ + テキスト。枠内テキスト領域を塗り直す
        # 枠fill色: 枠内テキスト左の空き領域からサンプル
        # ▶ の右端を探す: x=55..90 で輝度の高い画素(R>150)が終わる位置
        # ▶/Ⅱ は x=48..61 付近、テキストは x>=71。x=66から枠内側右端まで塗り直す
        x0e, x1e = 66, W - 10
        y0e, y1e = 4, H - 5
        # 行ごとに右端内側の無地部分から塗り色をサンプル(縦グラデ保持)
        for yy in range(y0e, y1e):
            im[yy, x0e:x1e] = im[yy, x1e - 2]
        pil = Image.fromarray(im)
        cx = (x0e + x1e) // 2
        brush_text(pil, label, cx, H//2, 27, fit_w=x1e - x0e - 6, halo_alpha=200)
    else:
        # 丸アイコン + テキスト(透過)
        a = im[:,:,3] > 10
        colsum = a.sum(axis=0)
        xcut = int(np.argmin(colsum[30:90])) + 30
        im[:, xcut:] = 0
        pil = Image.fromarray(im)
        cx = (xcut + W) // 2
        brush_text(pil, label, cx, H//2, 34, fit_w=W - xcut - 8)
    pil.save(f'{OUT}/{name}.png')

# ---------------- zhandou ボタン ----------------

def process_zhandou(name, label, diamond=False, size=None, two_line=False, use_donor=True):
    pil = Image.open(f'{SRC}/{name}.png').convert('RGBA')
    im = np.array(pil)
    en = np.array(Image.open(f'src/{name}.png').convert('RGBA'))
    H, W = im.shape[:2]
    def bright(arr):
        return (arr[:,:,:3].max(axis=2).astype(np.int32) > 115) & (arr[:,:,3] > 110)
    mask = bright(im)
    if diamond:
        yy, xx = np.mgrid[0:H, 0:W]
        dm = (np.abs(xx - W/2)/(W/2) + np.abs(yy - H/2)/(H/2)) < 0.62
        mask &= dm
    m = mask.astype(np.uint8)
    if m.sum() < 30:
        raise RuntimeError(f'{name}: text mask too small')
    ys, xs = np.nonzero(m)
    cx, cy = int(xs.mean()), int(ys.mean())
    bb_h = ys.max() - ys.min()
    # グラデ色サンプル(上端/下端の平均色)
    band = max(2, bb_h // 4)
    top_sel = ys <= ys.min() + band
    bot_sel = ys >= ys.max() - band
    top_rgb = im[ys[top_sel], xs[top_sel], :3].mean(axis=0)
    bot_rgb = im[ys[bot_sel], xs[bot_sel], :3].mean(axis=0)
    # 消去: 英語版をドナーに(同座標が英語側で明るくない画素のみコピー)、残りはinpaint
    md = cv2.dilate(m, np.ones((5,5), np.uint8)).astype(bool)
    if use_donor:
        en_ok = md & ~cv2.dilate(bright(en).astype(np.uint8), np.ones((5,5),np.uint8)).astype(bool)
        im[en_ok] = en[en_ok]
    else:
        en_ok = np.zeros_like(md)
    rest = (md & ~en_ok).astype(np.uint8)
    if rest.sum():
        for c in range(4):
            im[:,:,c] = cv2.inpaint(im[:,:,c], rest, 4, cv2.INPAINT_TELEA)
    pil = Image.fromarray(im)
    sz = size if size else bb_h + 6
    mid = tuple(top_rgb*0.5 + bot_rgb*0.5)
    if two_line and len(label) == 4:
        off = sz // 2 + 3
        brush_text(pil, label[:2], cx, cy - off, sz, halo=True, halo_alpha=150, grad=None, fit_w=int(W*0.8))
        brush_text(pil, label[2:], cx, cy + off, sz, halo=True, halo_alpha=150, grad=None, fit_w=int(W*0.8))
    else:
        brush_text(pil, label, cx, cy, sz, halo=False,
                   grad=(tuple(top_rgb), tuple(bot_rgb)), fit_w=int(W*0.92))
    pil.save(f'{OUT}/{name}.png')

# ---------------- main ----------------

if __name__ == '__main__':
    # フォントindex確認
    for i in range(5):
        try:
            f = ImageFont.truetype(NOTO, 20, index=i)
            print('index', i, f.getname())
        except Exception as e:
            break
    for nm in STRIP_SPECS:
        process_strip(nm)
        print('strip ok', nm)
    process_g08()
    process_g13('Gamepad_13')
    process_g13('Gamepad_13_0')
    process_skip('Gamepad_09')
    process_skip('T_SkipCG')
    process_playcg('T_PlayCG0', '自動再生')
    process_playcg('T_PlayCG1', '再生停止')
    process_playcg('T_PlayCG2', '自動再生')
    process_playcg('T_PlayCG3', '再生停止')
    for nm in ['zhandou84_chakan0','zhandou85_chakan1','zhandou86_chakan2']:
        process_zhandou(nm, '情報')
    for nm in ['zhandou17_taopaoanniou0','zhandou18_taopaoanniou1','zhandou19_taopaoanniou2']:
        process_zhandou(nm, '逃走')
    process_zhandou('zhandou100_taopao0', '降参')
    process_zhandou('zhandou107_tiaoguo0', 'スキップ', diamond=True, size=27, two_line=True, use_donor=False)
    print('ALL DONE')
