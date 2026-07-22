# -*- coding: utf-8 -*-
import os, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SRC = 'tutorial_src_簡体字'
OUT = '返却'
WS = '_tut_ws'
os.makedirs(OUT, exist_ok=True)
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
YUJI = '../_uassets_menu/YujiSyuku-Regular.ttf'

def font(size, brush=False):
    if brush:
        return ImageFont.truetype(YUJI, size)
    return ImageFont.truetype(NOTO, size, index=0)

def sample_color(im, x0, y0, x1, y1, amin=60):
    reg = im[y0:y1, x0:x1]
    m = reg[:, :, 3] > amin
    if m.sum() < 5:
        return (255, 255, 255)
    px = reg[m][:, :3].astype(np.float32)
    return tuple(int(v) for v in px.mean(axis=0))

def col_segments(im, x0, y0, x1, y1, gap=14):
    reg = (im[y0:y1, x0:x1, 3] > 10)
    cols = reg.sum(axis=0)
    xs = np.nonzero(cols)[0]
    if len(xs) == 0:
        return [(x0, x1)]
    segs = []
    s = xs[0]; p = xs[0]
    for x in xs[1:]:
        if x - p > gap:
            segs.append((x0 + s, x0 + p + 1)); s = x
        p = x
    segs.append((x0 + s, x0 + p + 1))
    return segs

def fit_size(draw, text, size, maxw, brush, minsize=13):
    s = size
    while s > minsize:
        if draw.textlength(text, font=font(s, brush)) <= maxw:
            break
        s -= 1
    return s

def draw_lines(pil, lines, cx, cy, size, fill, maxw, brush=False, anchor='m', stroke=0):
    d = ImageDraw.Draw(pil)
    n = len(lines)
    s = size
    for t in lines:
        s = min(s, fit_size(d, t, size, maxw, brush))
    lh = s + (5 if n >= 3 else 7)
    y0 = cy - (n - 1) * lh / 2
    anc = {'m': 'mm', 'l': 'lm', 'r': 'rm'}[anchor]
    for i, t in enumerate(lines):
        d.text((cx, y0 + i * lh), t, font=font(s, brush), fill=fill + (255,),
               anchor=anc, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))

def process(fname, boxes, entries):
    im = np.array(Image.open(os.path.join(SRC, fname)).convert('RGBA'))
    H, W = im.shape[:2]
    jobs = []
    keys = sorted((k for k in entries if k.isdigit()), key=int)
    for k in keys:
        i = int(k)
        e = entries[k]
        if e is None:
            continue
        box = boxes[i] if i < len(boxes) else e['rect']
        x0, y0, x1, y1 = box
        if 'sub' in e:
            x0, y0, x1, y1 = e['sub']
        ey1 = y0 + e['top'] if 'top' in e else y1
        color = sample_color(im, x0, y0, x1, ey1)
        segs = col_segments(im, x0, y0, x1, ey1) if e.get('segs') else None
        band = None
        if e.get('hl'):
            band = color
            color = (20, 16, 8)
        jobs.append((e, (x0, y0, x1, ey1), color, segs, band))
        im[max(0, y0 - 2):min(H, ey1 + 2), max(0, x0 - 2):min(W, x1 + 2)] = 0
    pil = Image.fromarray(im)
    rects = [j[1] for j in jobs]
    md = ImageDraw.Draw(pil)
    plan = []   # 中央寄せ通常テキスト(衝突解決対象)
    direct = [] # segs/バンド/アンカー付き(即時描画)
    for e, (x0, y0, x1, ey1), color, segs, band in jobs:
        lines = e['t']
        brush = bool(e.get('brush'))
        cy = (y0 + ey1) // 2
        h = ey1 - y0
        n = len(lines)
        stroke = 0
        if brush:
            base = max(16, min(24, int(h / n) - 2))
            if sum(color) / 3 > 130:
                color, stroke = (255, 255, 255), 2
        else:
            base = 21 if n == 1 else max(15, min(21, (h - (n - 1) * 5) // n))
            if band is None:
                stroke = 2
                if max(color) > 140 and (max(color) - min(color)) < 45:
                    color = (255, 255, 255)  # 灰白系は純白へ(灰背景での沈み対策)
        if band is not None:
            s_fit = fit_size(md, lines[0], base, 2 * min((x0 + x1) // 2, W - (x0 + x1) // 2) - 24, brush)
            tw = md.textlength(lines[0], font=font(s_fit, brush))
            bcx = (x0 + x1) // 2
            md.rectangle([bcx - tw / 2 - 10, y0 - 3, bcx + tw / 2 + 10, ey1 + 3], fill=band + (255,))
            direct.append((lines, bcx, cy, s_fit, color, brush, stroke, 'm'))
            continue
        if segs and len(segs) >= len(lines) == 2:
            (a0, a1), (b0, b1) = segs[0], segs[-1]
            sA = fit_size(md, lines[0], base, a1 - 40, brush)
            sB = fit_size(md, lines[1], base, W - b0 - 12, brush)
            direct.append(([lines[0]], a1, cy, sA, color, brush, stroke, 'r'))
            direct.append(([lines[1]], b0, cy, sB, color, brush, stroke, 'l'))
            continue
        anchor = e.get('a', 'm')
        if anchor == 'r':
            cx, maxw = x1, min(x1 - 12, int((x1 - x0) * 2.6) + 60)
        elif anchor == 'l':
            cx, maxw = x0, min(W - x0 - 12, int((x1 - x0) * 2.6) + 60)
        else:
            cx = (x0 + x1) // 2
            if brush:
                maxw = (x1 - x0) + 70
                if e.get('wide'):
                    maxw = 2 * min(cx, W - cx) - 8
                maxw = min(maxw, 2 * min(cx, W - cx) - 8)
            else:
                maxw = 2 * min(cx, W - cx) - 24
        s = base
        for t in lines:
            s = min(s, fit_size(md, t, base, maxw, brush))
        if anchor != 'm':
            direct.append((lines, cx, cy, s, color, brush, stroke, anchor))
        else:
            plan.append({'lines': lines, 'cx': cx, 'cy': cy, 'y0': y0, 'y1': ey1,
                         's': s, 'color': color, 'brush': brush, 'stroke': stroke})
    # 衝突解決: 同一行帯・中央寄せ同士で重なるなら大きい方を縮める
    def width_of(p):
        return max(md.textlength(t, font=font(p['s'], p['brush'])) for t in p['lines'])
    changed = True
    it = 0
    while changed and it < 60:
        changed = False; it += 1
        for i in range(len(plan)):
            for j in range(len(plan)):
                a, b = plan[i], plan[j]
                if a['cx'] >= b['cx'] or a['y1'] < b['y0'] or a['y0'] > b['y1']:
                    continue
                wa, wb = width_of(a), width_of(b)
                if a['cx'] + wa / 2 > b['cx'] - wb / 2 - 10:
                    tgt = a if wa >= wb else b
                    if tgt['s'] > 14:
                        tgt['s'] -= 1; changed = True
    for p in plan:
        draw_lines(pil, p['lines'], p['cx'], p['cy'], p['s'], p['color'], 10 ** 6,
                   p['brush'], anchor='m', stroke=p['stroke'])
    for lines, cx, cy, s, color, brush, stroke, anchor in direct:
        draw_lines(pil, lines, cx, cy, s, color, 10 ** 6, brush, anchor=anchor, stroke=stroke)
    Image.fromarray(np.array(pil)).save(os.path.join(OUT, fname))

def process_haogan_banner():
    fname = 'shuoming02_haoganshuoming.png'
    im = np.array(Image.open(os.path.join(SRC, fname)).convert('RGBA'))
    H, W = im.shape[:2]
    bright = (im[:, :, :3].min(axis=2) > 190) & (im[:, :, 3] > 200)
    colsum = bright.sum(axis=0)
    xs = np.nonzero(colsum)[0]
    segs = []
    s = xs[0]; p = xs[0]
    for x in xs[1:]:
        if x - p > 25:
            segs.append((s, p)); s = x
        p = x
    segs.append((s, p))
    # 細かいクラスタ(gap>=3)に割り、右から4つ=中文4文字。左のアイコンは温存
    fine = []
    s2 = xs[0]; p2 = xs[0]
    for x in xs[1:]:
        if x - p2 >= 3:
            fine.append((s2, p2)); s2 = x
        p2 = x
    fine.append((s2, p2))
    chars = fine[-4:]
    tx0, tx1 = chars[0][0], fine[-1][1]
    ys = np.nonzero(bright[:, tx0:tx1 + 1].sum(axis=1))[0]
    ty0, ty1 = ys.min(), ys.max()
    size = (ty1 - ty0) + 2
    text_x0 = tx0
    mask = np.zeros((H, W), np.uint8)
    mask[ty0 - 4:ty1 + 5, text_x0 - 4:tx1 + 6] = bright[ty0 - 4:ty1 + 5, text_x0 - 4:tx1 + 6]
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    keep = im.copy()
    for c in range(3):
        im[:, :, c] = cv2.inpaint(im[:, :, c], mask, 4, cv2.INPAINT_TELEA)
    im[:, :text_x0 - 8] = keep[:, :text_x0 - 8]
    pil = Image.fromarray(im)
    d = ImageDraw.Draw(pil)
    d.text((text_x0, (ty0 + ty1) // 2 + 1), '好感度説明', font=font(size),
           fill=(255, 255, 255, 255), anchor='lm')
    pil.save(os.path.join(OUT, fname))
    print('banner ok', fname)

def main():
    boxes_all = json.load(open(os.path.join(WS, 'caption_boxes.json'), encoding='utf-8'))
    caps = json.load(open('tut_captions.json', encoding='utf-8'))
    caps.pop('_comment', None)
    done = 0
    for fname, entries in caps.items():
        boxes = boxes_all.get(fname, [])
        missing = [i for i in range(len(boxes)) if str(i) not in entries]
        if missing:
            print(f'!! {fname}: box {missing} 訳無し')
        if not any(v for v in entries.values()):
            continue
        process(fname, boxes, entries)
        done += 1
    process_haogan_banner()
    print(f'done {done + 1} -> {OUT}/')

if __name__ == '__main__':
    main()
