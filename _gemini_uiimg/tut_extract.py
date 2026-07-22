# -*- coding: utf-8 -*-
"""チュートリアル画像: キャプション(透過帯の白文字)検出→boxes JSON＋読み取り用モンタージュ生成"""
import os, json
import numpy as np
import cv2
from PIL import Image, ImageDraw

SRC = 'tutorial_src_簡体字'
WS = '_tut_ws'
os.makedirs(WS, exist_ok=True)

def caption_boxes(im):
    """パネル(大面積成分)外のテキスト行ボックスを返す [(x0,y0,x1,y1),...]"""
    a = im[:,:,3] > 10
    H, W = a.shape
    n, lab, stats, _ = cv2.connectedComponentsWithStats(a.astype(np.uint8), 8)
    cap = a.copy()
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area > 15000 or (w > W*0.4 and h > 60):  # パネル/大装飾
            cap[lab == i] = False
    has = cap.sum(axis=1) > 0
    lines = []
    y = 0
    while y < H:
        if has[y]:
            y0 = y
            while y < H and has[y]:
                y += 1
            lines.append((y0, y))
        else:
            y += 1
    boxes = []
    for y0, y1 in lines:
        if y1 - y0 < 8:  # ノイズ
            continue
        colcnt = cap[y0:y1].sum(axis=0)
        xs = np.nonzero(colcnt)[0]
        if len(xs) == 0:
            continue
        segs = []
        s = xs[0]; p = xs[0]
        for x in xs[1:]:
            if x - p > 60:
                segs.append((s, p)); s = x
            p = x
        segs.append((s, p))
        for x0, x1 in segs:
            if x1 - x0 < 10:
                continue
            boxes.append((int(x0), int(y0), int(x1) + 1, int(y1)))
    return boxes

def main():
    files = sorted(f for f in os.listdir(SRC) if f.endswith('.png'))
    meta = {}
    strips = []
    for f in files:
        im = np.array(Image.open(os.path.join(SRC, f)).convert('RGBA'))
        boxes = caption_boxes(im)
        meta[f] = boxes
        for bi, (x0, y0, x1, y1) in enumerate(boxes):
            crop = im[max(0,y0-2):y1+2, max(0,x0-2):x1+2].copy()
            bg = np.zeros_like(crop); bg[:,:,3] = 255
            al = crop[:,:,3:4].astype(np.float32)/255
            comp = (crop[:,:,:3]*al + bg[:,:,:3]*(1-al)).astype(np.uint8)
            strips.append((f'{f} #{bi}', comp))
    json.dump(meta, open(os.path.join(WS,'caption_boxes.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    PAGE_H = 1800
    LABEL_H = 18
    page, ph, pi = [], 0, 0
    def flush(page, pi):
        if not page:
            return pi
        Wm = max(c.shape[1] for _, c in page) + 320
        Hm = sum(c.shape[0] + LABEL_H + 6 for _, c in page)
        canvas = Image.new('RGB', (Wm, Hm), (20,20,20))
        d = ImageDraw.Draw(canvas)
        y = 0
        for label, c in page:
            d.text((4, y+2), label, fill=(120,200,120))
            canvas.paste(Image.fromarray(c), (310, y + LABEL_H))
            y += c.shape[0] + LABEL_H + 6
        canvas.save(os.path.join(WS, f'montage_{pi:02d}.png'))
        return pi + 1
    for label, c in strips:
        h = c.shape[0] + LABEL_H + 6
        if ph + h > PAGE_H and page:
            pi = flush(page, pi); page, ph = [], 0
        page.append((label, c)); ph += h
    pi = flush(page, pi)
    n = sum(len(v) for v in meta.values())
    print(f'{len(files)}files / captions {n} / montages {pi} -> {WS}/')
    for f, v in meta.items():
        if not v:
            print('  no-caption:', f)

if __name__ == '__main__':
    main()
