# -*- coding: utf-8 -*-
"""チュートリアル画像 全文日本語化パイプライン"""
import os, sys, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SRC = 'tutorial_src'
ZH  = 'tutorial_src_簡体字'
OUT = '出力_tutorial'
os.makedirs(OUT, exist_ok=True)
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
NOTOR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOKU = '/sessions/practical-gifted-cannon/mnt/outputs/fonts/YujiBoku-Regular.ttf'
CYAN = (80,160,235)
_fc = {}
def F(size, reg=False):
    k=(size,reg)
    if k not in _fc: _fc[k]=ImageFont.truetype(NOTOR if reg else NOTO, size, index=0)
    return _fc[k]

def lum(px):
    return 0.299*px[...,0] + 0.587*px[...,1] + 0.114*px[...,2]

def erase_caption(im, box):
    x0,y0,x1,y1 = box
    im[y0:y1, x0:x1] = 0

def erase_panel(im, box, dark_text=False, thr=35, iters=2, pad=2, donor=None, fix_alpha=False):
    H,W = im.shape[:2]
    x0,y0,x1,y1 = max(0,box[0]-pad), max(0,box[1]-pad), min(W,box[2]+pad), min(H,box[3]+pad)
    c = im[y0:y1, x0:x1]
    def text_mask(cc):
        L = lum(cc[:,:,:3].astype(np.float32))
        med = np.median(L)
        if dark_text:
            return (L < med - thr)
        sat = cc[:,:,:3].max(axis=2).astype(np.int32) - cc[:,:,:3].min(axis=2).astype(np.int32)
        return (L > med + thr) | ((sat > 50) & (cc[:,:,:3].max(axis=2) > 90))
    mask = text_mask(c)
    m = cv2.dilate(mask.astype(np.uint8), np.ones((3,3),np.uint8), iterations=iters)
    if m.sum() == 0:
        return None
    color = tuple(int(v) for v in np.median(c[mask][:, :3], axis=0)) if mask.sum()>0 else (255,255,255)
    if donor is not None:
        dc = donor[y0:y1, x0:x1]
        dm = cv2.dilate(text_mask(dc).astype(np.uint8), np.ones((3,3),np.uint8), iterations=iters)
        ok = (m>0) & (dm==0)
        c[ok] = dc[ok]
        m = ((m>0) & ~ok).astype(np.uint8)
    if m.sum():
        c[:,:,:3] = cv2.inpaint(c[:,:,:3].copy(), m, 3, cv2.INPAINT_TELEA)
        if fix_alpha:
            c[:,:,3] = cv2.inpaint(c[:,:,3].copy(), m, 3, cv2.INPAINT_TELEA)
    im[y0:y1, x0:x1] = c
    return color


def draw_watermark(pil, box, text, size, fontpath, patch_alpha=235):
    """透かし置換: 楕円フェザーパッチで旧文字を覆い、影付き白文字を描く"""
    from PIL import ImageFilter
    x0,y0,x1,y1 = box
    im = np.array(pil)
    H,W = im.shape[:2]
    # パッチ色: 枠周囲リングの中央値
    ring = []
    for (a0,b0,a1,b1) in [(x0-14,y0-10,x1+14,y0-2),(x0-14,y1+2,x1+14,y1+10),
                          (x0-14,y0,x0-4,y1),(x1+4,y0,x1+14,y1)]:
        a0=max(0,a0); b0=max(0,b0); a1=min(W,a1); b1=min(H,b1)
        if a1>a0 and b1>b0: ring.append(im[b0:b1,a0:a1,:3].reshape(-1,3))
    col = tuple(int(v) for v in np.median(np.concatenate(ring),axis=0))
    m = Image.new('L', pil.size, 0)
    dm = ImageDraw.Draw(m)
    dm.ellipse([x0-10,y0-8,x1+10,y1+8], fill=patch_alpha)
    m = m.filter(ImageFilter.GaussianBlur(7))
    patch = Image.new('RGBA', pil.size, col+(0,))
    patch.putalpha(m)
    pil.alpha_composite(patch)
    # 影
    f = ImageFont.truetype(fontpath, size)
    cx, cy = (x0+x1)//2, (y0+y1)//2
    sh = Image.new('RGBA', pil.size, (0,0,0,0))
    ds = ImageDraw.Draw(sh)
    ds.text((cx+2, cy+2), text, font=f, fill=(95,85,60,170), stroke_width=2,
            stroke_fill=(95,85,60,170), anchor='mm')
    sh = sh.filter(ImageFilter.GaussianBlur(1.6))
    pil.alpha_composite(sh)
    dd = ImageDraw.Draw(pil)
    dd.text((cx, cy), text, font=f, fill=(250,247,240,255), anchor='mm')

def draw_entry(pil, e, sampled_color):
    x0,y0,x1,y1 = e['box']
    mode = e.get('mode','panel')
    text = e['ja']
    size = e.get('size') or max(8, round((y1-y0)*1.05))
    align = e.get('align', 'center' if mode=='caption' else 'left')
    color = e.get('color') or ((255,255,255) if mode=='caption' else (sampled_color or (255,255,255)))
    stroke = e.get('stroke', 2 if mode=='caption' else 0)
    pitch = e.get('pitch', size+4)
    reg = e.get('reg', False)
    clip = e.get('clip')
    alpha = e.get('alpha', 255)
    fontpath = e.get('font')
    layer = Image.new('RGBA', pil.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    lines = text.split('\n')
    total_h = pitch*(len(lines)-1)
    cy0 = (y0+y1)//2 - total_h//2
    maxw = e.get('maxw', (x1-x0)+4 if mode!='caption' else None)
    def getf(sz):
        if fontpath: return ImageFont.truetype(fontpath, sz)
        return F(sz, reg)
    for i, ln in enumerate(lines):
        s = size
        f = getf(s)
        if maxw:
            while s > 7 and d.textlength(ln, font=f) > maxw:
                s -= 1; f = getf(s)
        cy = cy0 + i*pitch
        if align == 'center':
            d.text((e.get('cx',(x0+x1)//2), cy), ln, font=f, fill=tuple(color)+(alpha,),
                   stroke_width=stroke, stroke_fill=(0,0,0,min(255,alpha)), anchor='mm')
        elif align == 'right':
            d.text((x1, cy), ln, font=f, fill=tuple(color)+(alpha,),
                   stroke_width=stroke, stroke_fill=(0,0,0,min(255,alpha)), anchor='rm')
        else:
            d.text((x0, cy), ln, font=f, fill=tuple(color)+(alpha,),
                   stroke_width=stroke, stroke_fill=(0,0,0,min(255,alpha)), anchor='lm')
    if clip:
        m2 = Image.new('L', pil.size, 0)
        ImageDraw.Draw(m2).rectangle(clip, fill=255)
        layer.putalpha(Image.composite(layer.getchannel('A'), Image.new('L',pil.size,0), m2))
    pil.alpha_composite(layer)

def render_page(name, entries, src_name=None):
    pil = Image.open(f'{SRC}/{src_name or name}.png').convert('RGBA')
    im = np.array(pil)
    colors = []
    for e in entries:
        if e.get('noerase'):
            colors.append(None); continue
        if e.get('mode','panel') == 'caption':
            erase_caption(im, e['box']); colors.append(None)
        else:
            colors.append(erase_panel(im, e['box'], e.get('dark_text',False),
                                      e.get('thr',35), e.get('iters',2)))
    pil = Image.fromarray(im)
    for e, col in zip(entries, colors):
        if e.get('ja'):
            draw_entry(pil, e, col)
    pil.save(f'{OUT}/{name}.png')
    print('done', name)

def C(box, ja, **kw):
    d = {'mode':'caption','box':box,'ja':ja,'size':17}; d.update(kw); return d
def P(box, ja, **kw):
    d = {'mode':'panel','box':box,'ja':ja}; d.update(kw); return d

GOLD = (212,180,106)
WHT  = (232,232,232)

def tabs(boxes_labels, y0, y1, size, clipy=None):
    out=[]
    for (bx0,bx1),(t,col) in boxes_labels:
        e = P([bx0,y0,bx1,y1], t, size=size, align='center', color=col)
        if clipy: e['clip']=[bx0-2,clipy[0],bx1+2,clipy[1]]
        out.append(e)
    return out

SPECS = {}

# ---------- キャプション自動検出 ----------
def find_caption_paragraphs(im):
    """透過背景上の文字成分を段落にまとめて返す [(x0,y0,x1,y1,cx), ...] 読み順"""
    a = (im[:,:,3] > 30).astype(np.uint8)
    opaque = (im[:,:,3] > 240).astype(np.uint8)
    tile = cv2.morphologyEx(opaque, cv2.MORPH_OPEN, np.ones((25,25),np.uint8))
    tile = cv2.dilate(tile, np.ones((9,9),np.uint8))
    n, lab, stats, cent = cv2.connectedComponentsWithStats(a, 8)
    comps=[]
    for i in range(1,n):
        x,y,w,h,area = stats[i]
        if area < 12 or h > 85 or h < 4: continue
        if w > 500 and h < 10: continue  # 装飾の区切り線
        if tile[y:y+h, x:x+w].any(): continue
        comps.append((x,y,w,h))
    # 行にまとめる
    lines=[[x,y,x+w,y+h] for x,y,w,h in comps]
    def try_merge(items, cond):
        changed=True
        while changed:
            changed=False
            out=[]
            for it in items:
                for o in out:
                    if cond(o,it):
                        o[0]=min(o[0],it[0]); o[1]=min(o[1],it[1]); o[2]=max(o[2],it[2]); o[3]=max(o[3],it[3])
                        changed=True; break
                else:
                    out.append(it)
            items=out
        return items
    def line_cond(L, c):
        if c[1] > L[3]+4 or c[3] < L[1]-4: return False
        return max(c[0], L[0]) - min(c[2], L[2]) < 40
    lines = try_merge(lines, line_cond)
    # 行→段落(x範囲が重なり、縦ギャップ<14)
    lines.sort(key=lambda L:(L[1],L[0]))
    paras=[]
    for L in lines:
        placed=False
        for Pg in paras:
            xov = min(Pg[2],L[2]) - max(Pg[0],L[0])
            if xov > 30 and 0 <= L[1]-Pg[3] < 14:
                Pg[0]=min(Pg[0],L[0]); Pg[1]=min(Pg[1],L[1]); Pg[2]=max(Pg[2],L[2]); Pg[3]=max(Pg[3],L[3])
                placed=True; break
        if not placed:
            paras.append(list(L))
    paras.sort(key=lambda Pg:(round(Pg[1]/150), Pg[0]))
    return paras

def render_page2(name, cap_texts, panel_entries=(), src_name=None, cap_size=17, cap_pitch=19):
    """キャプション自動検出版レンダラ"""
    pil = Image.open(f'{SRC}/{src_name or name}.png').convert('RGBA')
    im = np.array(pil)
    paras = find_caption_paragraphs(im)
    assert len(paras) == len(cap_texts), f'{name}: paras={len(paras)} texts={len(cap_texts)} {paras}'
    for (x0,y0,x1,y1), t in zip(paras, cap_texts):
        if t is None: continue
        im[max(0,y0-3):y1+3, max(0,x0-3):x1+3] = 0
    zh_im = None
    colors=[]
    for e in panel_entries:
        if e.get('noerase'): colors.append(None); continue
        dn = None
        if e.get('donor'):
            if zh_im is None:
                p = f'{ZH}/{src_name or name}.png'
                if os.path.exists(p):
                    zh_im = np.array(Image.open(p).convert('RGBA'))
            dn = zh_im
        colors.append(erase_panel(im, e['box'], e.get('dark_text',False), e.get('thr',35), e.get('iters',2), donor=dn))
    pil = Image.fromarray(im)
    d = None
    for (x0,y0,x1,y1), text in zip(paras, cap_texts):
        if not text: continue  # None/'' は描画なし
        e = {'mode':'caption','box':[x0,y0,x1,y1],'ja':text,'size':cap_size,
             'align':'center','cx':(x0+x1)//2,'pitch':cap_pitch}
        draw_entry(pil, e, None)
    for e, col in zip(panel_entries, colors):
        if not e.get('ja'): continue
        if e.get('mode') == 'wm':
            draw_watermark(pil, e['box'], e['ja'], e['size'], e.get('font') or NOTO)
        else:
            draw_entry(pil, e, col)
    pil.save(f'{OUT}/{name}.png')
    print('done', name)

CAPS = {}
PANELS = {}
SRCMAP = {}

# ---- shuoming02_diban0 詳細バナー ----
SPECS['shuoming02_diban0'] = [
 P([155,6,272,46], '詳細解説', size=28, align='center', cx=211, font=BOKU, stroke=2, color=(245,245,245), fix_alpha=True, iters=3),
]

# ---- shuoming26 洛書の仕掛け ----
CAPS['shuoming26_LuoShushuoming'] = [
 'マウスかW/A/S/Dで行・列を操作する矢印を選びます。\n選択中の矢印はハイライトされます',
 '左クリックかSpaceで選択中の矢印の方向に行・列を\n動かします。模様を洛書の図案に合わせれば\nパズル完成です',
 'ESCで画面を終了、Rで仕掛けをリセットします',
]
PANELS['shuoming26_LuoShushuoming'] = [
 P([456,562,556,600], '決定', size=16, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
 P([650,562,695,600], '終了', size=16, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
 P([790,562,868,600], 'リセット', size=15, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
]
# ---- shuoming27 猿の矢印ミニゲーム ----
CAPS['shuoming27_YuanWushuoming'] = [
 '猿の頭上に出る矢印の向きと順番を覚えます',
 'W/A/S/Dで矢印の向きを正しい順に入力するとミニゲームクリアです',
]
PANELS['shuoming27_YuanWushuoming'] = [
 P([566,584,600,608], '上', size=14, align='left'),
 P([642,584,694,608], '下', size=14, align='left'),
 P([735,584,772,608], '左', size=14, align='left'),
 P([815,584,862,608], '右', size=14, align='left'),
]

# ---- shuoming24 乗騎 ----
CAPS['shuoming24_zuoqishuoming'] = [
 'パーティ画面左下の「乗騎」ボタンを押します',
 '乗騎を選びます',
 '乗騎を選ぶと移動状態が騎乗に変わり、\n移動速度が上がります',
 '騎乗中にShiftを押すと、走るの代わりに\n歩く／騎乗を切り替えます',
 '乗騎の選択を解除すると移動状態が走るに戻ります',
]
PANELS['shuoming24_zuoqishuoming'] = [
 P([55,156,178,194], '出陣', size=17, align='center', dark_text=True),
 P([266,161,348,188], '乗騎', size=15, align='center', dark_text=True, clip=[230,150,352,200]),
 P([654,12,914,68], 'シーン移動速度+\nワールドマップ移動速度+', size=15, align='left', pitch=28, clip=[478,8,913,70], thr=30, iters=3),
 P([1102,12,1382,68], 'シーン移動速度+\nワールドマップ移動速度+', size=15, align='left', pitch=28, clip=[942,8,1381,70], thr=30, iters=3),
 P([1028,398,1346,452], 'シーン移動速度+\nワールドマップ移動速度+', size=15, align='left', pitch=28, thr=30, iters=3),
 P([130,554,262,632], 'Shiftで歩く／走る\nを切り替え', size=12, align='center', cx=196, pitch=16, thr=30, iters=3),
 P([284,572,408,608], 'WASDで移動', size=12, align='center', cx=346, thr=30, iters=3),
 P([416,578,528,600], '会話スキップ', size=12, align='center', cx=472, thr=30, iters=3),
 P([622,570,682,608], '', thr=30, iters=3),
]
# ---- shuoming25 河図の仕掛け ----
CAPS['shuoming25_HeTushuoming'] = [
 '左クリックかW/Sで回したいリングを選びます。選択中のリングは光ります',
 '矢印クリックかA/Dで石のリングを回します。他のリングも\n選択中のリングと一緒に回ります。リングの模様を\n河図の図案に合わせればパズル完成です',
 '',
 'ESCで画面を終了、Rで仕掛けをリセットします',
]
CAPS['shuoming25_HeTushuoming'].remove('')
PANELS['shuoming25_HeTushuoming'] = [
 P([818,563,898,598], '選択', size=16, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
 P([1005,563,1055,598], '終了', size=16, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
 P([1140,560,1234,600], 'リセット', size=15, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
]

# ---- shuoming22 ターン制/リアルタイム切替 ----
CAPS['shuoming22_huihejishi'] = [
 'アバター左下のアイコンをクリックするとターン制／リアルタイム制を切り替えられます',
]
PANELS['shuoming22_huihejishi'] = [
 P([376,278,412,299], '気血', size=14, align='left'),
 P([406,304,442,325], '真気', size=14, align='left'),
 P([430,330,472,351], '精力', size=14, align='left'),
 P([256,396,324,436], 'ターン', size=12, align='center', color=(230,225,215), font=BOKU, stroke=2),
 P([288,432,340,460], '即時', size=10, align='center', color=(170,170,170), font=BOKU, stroke=1),
]
# ---- shuoming23 宿場 ----
CAPS['shuoming23_yizhanshuoming'] = [
 '宿場の御者に話しかけるとファストトラベルが解放されます',
 '「移動」を選ぶと地図が開き、行き先を選べます',
 '表示された操作説明に従って地図を調整します',
 '宿場を選ぶとその地域を拡大表示します。解放済みの\n目的地へはお金を払って移動できます',
]
PANELS['shuoming23_yizhanshuoming'] = [
 P([1020,113,1088,138], '移動', size=15, align='center'),
 P([30,602,494,624], 'WASD: マップ移動　　ホイール: 拡大／縮小', size=13, align='center', color=(228,228,228)),
 P([1130,412,1290,440], '宿場', size=17, align='center', color=(240,240,240), font=BOKU, stroke=2),
 P([1100,460,1235,484], '中原', size=14, align='left'),
 P([1105,506,1248,530], '平康城宿場', size=14, align='left'),
 P([1105,550,1242,574], '武当山宿場', size=14, align='left', color=(140,140,140)),
 P([1105,593,1225,617], '閻浮鎮宿場', size=14, align='left', color=(140,140,140)),
 P([748,476,812,514], '豫村', size=12, align='center'),
]

# ---- shuoming19 ツボ(経穴) ----
CAPS['shuoming19_jingmaishuoming'] = [
 'ツボを選んで右スティック押し込みで効果を確認できます',
 '特殊なツボは最大レベルで追加効果を発揮します',
 'LB/RBで経脈図を切り替えます',
 'ツボを選んで「突く」を押します',
]
PANELS['shuoming19_jingmaishuoming'] = [
 P([335,138,420,158], '璇璣', size=13, align='left'),
 P([335,200,425,220], '臂力 +2', size=13, align='left'),
 P([1000,101,1080,121], '天突', size=13, align='left'),
 P([1000,162,1080,182], '根骨 +4', size=13, align='left'),
 P([1000,183,1290,228], '', thr=28, iters=3),
 P([1003,186,1285,201], '最大Lv: 被弾時20%の確率でデバフを', size=12, align='left', noerase=True, color=(225,225,225)),
 P([1003,203,1285,218], '1つ解除する。', size=12, align='left', noerase=True, color=(225,225,225)),
 P([1078,449,1262,472], '廉泉 : 1 / 3', size=14, align='center'),
 P([1128,494,1215,524], '突く', size=15, align='center', dark_text=True),
 P([1052,548,1292,572], '消費経脈ポイント: 15', size=14, align='center'),
]
# ---- shuoming21 コントローラ配置(手動キャプション) ----
SPECS['shuoming21_shoubingshuoming'] = [
 C([150,115,294,145], 'メニュー切替', size=14, cx=222),
 C([184,163,298,210], '戦闘モード切替', size=14, cx=241),
 C([575,96,679,126], '世界地図', size=14, cx=627),
 C([700,76,810,126], 'システムバー\n表示', size=13, cx=755, pitch=17),
 C([1088,115,1234,145], 'メニュー切替', size=14, cx=1161),
 C([1100,173,1258,203], '歩く／走る切替', size=14, cx=1179),
 C([1127,267,1196,295], '任務', size=14, cx=1161),
 C([1155,322,1224,349], 'キャンセル', size=14, cx=1189),
 C([170,347,224,373], '移動', size=14, cx=197),
 C([1168,383,1246,410], '決定', size=14, cx=1207),
 C([105,445,188,494], '押し込みで\n所持品整理', size=13, cx=146, pitch=17),
 C([518,618,634,649], 'UI切替', size=14, cx=576),
 C([692,618,810,649], '特性詳細', size=14, cx=751),
 C([816,616,912,688], 'プロフィール\n会話スキップ', size=13, cx=864, pitch=17),
]

WHT2=(235,235,235)
# ---- shuoming17 心法 ----
CAPS['shuoming17_xinfashuoming'] = [
 '武学アイコンかショートカットキーで\n武学画面を開きます',
 '武学ポイントは戦闘で獲得できます。出撃人数が\n多いほど1人あたりの獲得量は減ります。出撃して\nいない仲間も武学ポイントを獲得できます',
 'ここで心法を切り替えます',
 '技にカーソルを合わせると詳細・強化に必要な\n武学ポイント・強化後の数値変化を確認できます',
 '心法の習得・強化で、その品質に応じた経脈ポイント\nを獲得します。経脈ポイントを消費してツボを突けば\n能力が大きく上昇します',
 '「強化」を選ぶと技を強化します',
]
PANELS['shuoming17_xinfashuoming'] = [
 P([570,160,680,204], '武学ポイント', size=13, align='center', color=(240,240,240), font=BOKU, stroke=2, iters=3),
 P([960,76,1060,104], '軽功', size=13, align='center', color=(235,235,235), font=BOKU, stroke=2),
 P([1120,76,1248,104], '心法', size=14, align='center', color=(215,180,90), font=BOKU, stroke=2),
 P([938,143,1178,164], '招式配置', size=13, align='right', color=(240,240,240), font=BOKU, stroke=2, thr=25, iters=3),
 # tile4 ミニパネル+ツールチップ
 P([193,399,290,412], '招式配置', size=8, align='center'),
 P([14,418,112,432], '基礎心法', size=8, align='left', dark_text=True),
 P([14,443,45,456], '消費', size=7, align='left', dark_text=True),
 P([58,437,104,460], '強化', size=9, align='center', dark_text=True),
 P([164,460,256,477], '習得済み武学', size=9, align='left', clip=[164,458,232,479]),
 P([246,428,335,441], '基礎心法', size=9, align='left'),
 P([246,452,308,464], '攻撃範囲', size=8, align='left'),
 P([296,466,342,502], '', thr=25, iters=2),
 P([298,468,342,476], '攻撃力: 0', size=7, align='left', noerase=True, color=(180,180,180)),
 P([298,479,342,487], '真気消費: 0', size=7, align='left', noerase=True, color=(180,180,180)),
 P([298,490,344,498], '待機ターン: 1', size=7, align='left', noerase=True, color=(180,180,180)),
 P([246,506,300,518], 'スキル説明', size=8, align='left'),
 P([248,519,435,562], '', thr=25, iters=2),
 P([250,521,290,529], '江湖', size=7, align='left', noerase=True, color=WHT2),
 P([292,521,360,529], '心法', size=7, align='left', noerase=True, color=(205,60,50)),
 P([250,530,435,538], 'レベル毎に経脈P+10、気血上限+15、真気上限+20', size=7, align='left', noerase=True, color=(90,200,80)),
 P([250,539,435,547], '最も基礎的な心法。これだけでは江湖を渡れない。', size=7, align='left', noerase=True, color=WHT2),
 P([250,548,435,556], '自身のみに効果', size=7, align='left', noerase=True, color=CYAN),
 P([246,563,300,575], '使用効果', size=8, align='left'),
 P([248,576,275,584], 'なし', size=7, align='left'),
 P([246,586,325,597], '特殊効果', size=8, align='left'),
 P([248,597,430,608], '真気を15%回復。真気を消費しない。', size=7, align='left', color=CYAN, thr=25),
 # tile5 拡大パネル
 P([613,399,702,416], '待機ターン : 1', size=11, align='left'),
 P([487,440,575,458], 'スキル説明', size=12, align='left'),
 P([503,462,700,481], '', thr=28, iters=3),
 P([505,463,548,478], '江湖', size=11, align='left', noerase=True, color=WHT2),
 P([553,463,700,478], '心法', size=11, align='left', noerase=True, color=(205,60,50)),
 P([503,482,895,518], '', thr=28, iters=3),
 P([505,484,890,499], 'レベル毎に経脈ポイント+10、気血上限+15、', size=12, align='left', noerase=True, color=(90,200,80)),
 P([505,500,890,515], '真気上限+20', size=12, align='left', noerase=True, color=(90,200,80)),
 P([503,517,895,562], '', thr=28, iters=3),
 P([505,519,890,534], '最も基礎的な心法。これだけでは江湖を渡れない。', size=12, align='left', noerase=True, color=WHT2),
 P([505,545,890,560], '自身のみに効果', size=12, align='left', noerase=True, color=CYAN),
 P([487,572,580,592], '使用効果', size=12, align='left'),
 P([503,596,545,613], 'なし', size=11, align='left'),
 P([487,620,632,638], '特殊効果', size=12, align='left', clip=[480,615,700,637]),
 # tile6 拡大スロット
 P([1052,458,1262,484], '基礎心法', size=16, align='left', dark_text=True),
 P([1054,524,1096,547], '消費', size=13, align='left', dark_text=True),
 P([1196,513,1294,548], '強化', size=15, align='center', dark_text=True),
]
# ---- shuoming18 経脈 ----
CAPS['shuoming18_jingmaishuoming'] = [
 '経脈アイコンかショートカットキーで経脈画面を開きます',
 '現在の経脈ポイント。心法の習得や強化で\n獲得できます',
 '経脈図を選ぶと詳細を確認できます',
 '灰色のツボはロック中です。前提のツボをLv.3まで\n突くと解放されます',
]
PANELS['shuoming18_jingmaishuoming'] = [
 P([855,118,893,139], '陰', size=14, align='center'),
 P([1168,118,1270,139], '督', size=14, align='center'),
 P([886,148,1042,176], '経脈ポイント', size=13, align='center', iters=3),
 P([138,528,262,556], '任', size=14, align='center', iters=3),
 P([520,531,578,553], '陽', size=14, align='center'),
]
BOKU = '/sessions/practical-gifted-cannon/mnt/outputs/fonts/YujiBoku-Regular.ttf'

# ---- shuoming15 キーボード操作(手動キャプション) ----
SPECS['shuoming15_caozuoshuoming'] = [
 C([40,54,200,104], 'Escで画面を閉じる／\nシステムを開く', size=13, cx=119, pitch=16),
 C([272,64,424,90], 'Eで調べる・話す', size=13, cx=348),
 C([1100,212,1274,257], 'ホイールクリックで\n戦闘カメラを調整', size=13, cx=1187, pitch=16),
 C([20,272,80,317], '世界地図', size=12, cx=49, pitch=15),
 C([1238,285,1332,327], '右クリックで\nキャンセル', size=13, cx=1285, pitch=16),
 C([1106,486,1198,528], '左クリックで\n決定', size=13, cx=1152, pitch=16),
 C([56,614,214,702], 'Shiftで歩く／走るを\n切り替え', size=13, cx=134, pitch=16),
 C([216,620,342,650], 'WASDで移動', size=13, cx=280),
 C([358,620,442,665], '会話\nスキップ', size=13, cx=400, pitch=16),
 C([462,620,624,665], 'Spaceで\n次のセリフへ', size=13, cx=543, pitch=16),
]
# ---- shuoming16 観察/贈り物/手合わせ ----
CAPS['shuoming16_qiecuoshuoming'] = [
 'NPCに近づき「観察」を選びます',
 '好きな物を贈るとNPCの好感度を上げられます',
 '好感度が20に達したNPCとは手合わせができます',
 '手合わせに勝つとNPCの持ち物から1〜3個の\nアイテムを必ず入手できます',
]
PANELS['shuoming16_qiecuoshuoming'] = [
 P([325,38,420,62], '衛霍', size=15, align='center'),
 P([292,66,370,92], '会話', size=14, align='center'),
 P([284,114,378,140], '観察', size=14, align='center'),
 P([925,20,1100,50], '紹介', size=17, align='center', color=(235,225,185)),
 P([788,68,1048,87], '好み: 武器、消耗品', size=13, align='left'),
 P([788,95,960,114], '所属: 無所属', size=13, align='left'),
 P([786,123,1250,188], '', thr=28, iters=3),
 P([790,128,1250,140], '衛霍は梧桐村の猟師。幼くして両親を亡くしたせいか', size=12, align='left', noerase=True, color=(235,235,235)),
 P([790,143,1250,155], '人付き合いが苦手で、村人ともあまり馴染めない。', size=12, align='left', noerase=True, color=(235,235,235)),
 P([790,158,1250,170], 'だが棍の腕前は侮れない。', size=12, align='left', noerase=True, color=(235,235,235)),
 P([288,403,402,428], '装備', size=15, align='center', color=(235,225,185)),
 P([160,445,250,468], '衛霍', size=15, align='left', dark_text=True),
 P([905,543,978,573], '手合わせ', size=13, align='center', dark_text=True),
 P([1085,543,1145,573], '贈り物', size=13, align='center', dark_text=True),
 P([1250,543,1325,573], '勧誘', size=15, align='center', dark_text=True),
]

# ---- shuoming13 装備 ----
CAPS['shuoming13_zhuangbeishuoming'] = [
 'パーティアイコンかショートカットキーでパーティ画面を開きます',
 '装備',
 'ダブルクリックで装備を身につけます',
]
PANELS['shuoming13_zhuangbeishuoming'] = [
 P([262,448,428,472], '実力: 見習い', size=15, align='center', color=(240,240,240), font=BOKU, stroke=2),
 P([0,492,96,574], '', thr=30, iters=3),      # 左端の切れた説明文は消去のみ
 P([705,398,730,418], '', thr=30),             # 切れた名前
 P([1096,405,1164,425], 'プレイヤー', size=12, align='center', dark_text=True),
 P([953,506,1028,532], '装備', size=15, align='center', dark_text=True),
]
# ---- shuoming14 仲間勧誘 ----
CAPS['shuoming14_yaoqingshuoming'] = [
 'NPCに近づき「観察」を選びます',
 'キャラの名前の下に自分との好感度が表示されます',
 '好感度が60に達したキャラはパーティに勧誘できます。\n好感度に関わらず勧誘できないキャラもいます',
]
PANELS['shuoming14_yaoqingshuoming'] = [
 P([682,52,760,100], '江小彤', size=14, align='center', cx=716),
 P([640,93,706,117], '会話', size=14, align='center'),
 P([636,141,710,165], '観察', size=14, align='center'),
 P([340,408,460,432], '装備', size=15, align='center', color=(235,225,185)),
 P([206,453,356,475], '江小彤', size=15, align='left', dark_text=True),
 P([820,543,890,572], '手合わせ', size=13, align='center', dark_text=True),
 P([990,543,1065,572], '勧誘', size=15, align='center', dark_text=True),
]

# ---- shuoming11_0 スキルバー/詳細 ----
CAPS['shuoming11_zhandoushuoming0'] = [
 '技の下の数字はショートカットキーを表します',
 '技アイコンにカーソルを合わせると詳細と差し替え\n候補が表示されます。候補を選ぶと差し替えます',
 '技を選びます',
]
_cards1 = [((383,462),'通常'),((492,570),'二式'),((618,692),'三式'),((740,812),'絶式'),((843,932),'軽功'),((947,1062),'心法')]
_cards3 = [((770,840),'通常'),((870,940),'二式'),((1070,1140),'絶式'),((1157,1240),'軽功'),((1252,1335),'心法')]
PANELS['shuoming11_zhandoushuoming0'] = [
 *[P([a,88,b,117], t, size=20, align='center', color=(245,245,245), font=BOKU, stroke=2) for (a,b),t in _cards1],
 P([1070,106,1148,136], '合撃', size=16, align='center', color=(245,245,245), font=BOKU, stroke=2, clip=[1070,104,1149,138]),
 P([436,358,590,375], '無極四象功', size=11, align='left', color=(215,180,90)),
 P([440,390,505,400], '攻撃範囲', size=8, align='left'),
 P([503,410,552,421], '攻撃力 : 591', size=8, align='left'),
 P([503,422,556,432], '真気消費 : 421', size=8, align='left'),
 P([503,433,556,443], '待機ターン : 6', size=8, align='left'),
 P([445,458,500,468], 'スキル説明', size=9, align='left'),
 P([445,470,492,479], '武当派', size=8, align='left', noerase=False),
 P([493,470,556,479], '心法', size=8, align='left', color=(205,60,50)),
 P([445,479,652,495], '', thr=30, iters=3),
 P([447,482,650,491], 'レベル毎に経脈ポイント+46、気血上限+50、真気上限+65', size=8, align='left', noerase=True, color=(90,200,80)),
 P([445,495,652,505], '自身を中心に4マス以内の敵にダメージを与える', size=8, align='left'),
 P([445,508,495,518], '使用効果', size=9, align='left'),
 P([445,521,470,530], 'なし', size=8, align='left'),
 P([445,534,515,545], '特殊効果', size=9, align='left'),
 P([443,548,660,599], '', thr=28, iters=3),
 P([447,552,655,560], '自身のデバフを1つランダムに解除。', size=8, align='left', noerase=True, color=CYAN),
 P([447,561,655,569], 'Lv.5効果: 無極 - 使用で無極を4層獲得。1層につき', size=8, align='left', noerase=True, color=CYAN),
 P([447,570,655,578], '攻撃力+25%。効果中は被弾時50%で無極ダメージが', size=8, align='left', noerase=True, color=CYAN),
 P([447,579,655,587], '発動し、周囲4マスの敵全体の体力を5%減らし、', size=8, align='left', noerase=True, color=CYAN),
 P([447,588,655,596], '無極を1層消費する。', size=8, align='left', noerase=True, color=CYAN),
 P([443,602,662,624], '', thr=28, iters=3),
 P([447,605,660,613], 'Lv.10 以柔克剛: 会心攻撃を受けると無極ダメージが', size=8, align='left', noerase=True, color=CYAN),
 P([447,614,660,622], '1回発動し、真気を5%回復する。', size=8, align='left', noerase=True, color=CYAN),
 P([50,562,102,592], '通常', size=11, align='center', color=(240,240,240), stroke=1),
 P([116,562,166,592], '二式', size=11, align='center', color=(240,240,240), stroke=1),
 P([181,562,231,592], '三式', size=11, align='center', color=(240,240,240), stroke=1),
 P([246,562,296,592], '絶式', size=11, align='center', color=(240,240,240), stroke=1),
 P([307,562,357,592], '軽功', size=11, align='center', color=(240,240,240), stroke=1),
 P([368,562,430,592], '心法', size=13, align='center', color=(245,245,245), font=BOKU, stroke=2),
 *[P([a,498,b,524], t, size=18, align='center', color=(245,245,245), font=BOKU, stroke=2) for (a,b),t in _cards3],
 P([963,498,1034,524], '三式', size=18, align='center', color=(60,60,60), font=BOKU, dark_text=True),
 P([1350,498,1386,524], '', thr=30),
]
# ---- shuoming12 攻撃範囲/側面背面 ----
CAPS['shuoming12_zhandoushuoming'] = [
 '黄色のマスはこの技を使用できる範囲を示します',
 '赤いマスは実際の攻撃範囲です。赤いマスの\nどこかを選ぶと技を使用します',
 '側面からの攻撃はダメージが15%増加します',
 '背面からの攻撃は命中率が50%、ダメージが15%増加します',
]
PANELS['shuoming12_zhandoushuoming'] = [
 {'mode':'wm','box':[213,396,355,433],'ja':'側面攻撃の範囲','size':24,'font':BOKU,'noerase':True},
 {'mode':'wm','box':[203,585,350,628],'ja':'側面攻撃の範囲','size':24,'font':BOKU,'noerase':True},
 {'mode':'wm','box':[742,477,918,530],'ja':'背面攻撃の範囲','size':27,'font':BOKU,'noerase':True},
]

# ---- shuoming10 釣り ----
CAPS['shuoming10_diaoyushuoming'] = [
 '各マップにある釣りスポットを探します',
 '光の集まりに近づき「釣り」を選ぶと\n釣りを開始します',
 '竿を投げると精力を一定量消費して\n釣りが始まります',
 '「立ち去る」でいつでも釣りを中断できます',
 '右側でレベル・出現魚・確率を確認できます',
 '浮きに反応があったら時間内に「引き上げる」を\n選ぶと魚が手に入ります。時間内に引き上げないと\n何も得られません',
]
PANELS['shuoming10_diaoyushuoming'] = [
 P([693,105,740,127], '釣り', size=14, align='center'),
 P([1012,203,1104,222], '竿を投げる', size=12, align='center', dark_text=True),
 P([1220,203,1294,222], '立ち去る', size=12, align='center', dark_text=True),
 P([86,588,168,607], '竿を投げる', size=12, align='center', dark_text=True),
 P([293,588,364,607], '立ち去る', size=12, align='center', dark_text=True),
 P([840,404,882,413], 'Lv.1 魚池', size=8, align='center'),
 P([826,441,855,449], '草魚', size=7, align='center'),
 P([871,441,892,449], '鮒', size=7, align='center'),
 P([850,537,872,548], '希少', size=8, align='center'),
 P([586,620,617,628], '竿を投げる', size=7, align='center', dark_text=True),
 P([690,620,712,628], '立ち去る', size=7, align='center', dark_text=True),
]
# ---- shuoming11 戦闘基本 ----
CAPS['shuoming11_zhandoushuoming'] = [
 '頭上に白い矢印があるキャラが現在行動可能です。\n緑のバーは気血(HP)を示します',
 '黄色のバーは気力を示します。気力が満タンの\nキャラだけが行動できます',
 '明るい色のマスはこの戦闘での\n最大移動範囲を示します',
 '青いマスはこのターンで移動できる範囲です。\n移動後に右クリックで行動をやり直せます',
]

DK=(70,70,70); AC=(120,100,40)
# ---- shuoming08 裁縫(設計図選択) ----
CAPS['shuoming08_zhiyishuoming'] = [
 '作成する防具の種類を選びます',
 '作成する防具を選びます',
 '現在の裁縫レベル',
 '現在の経験値／レベルアップに必要な経験値',
 '作成後に得られる経験値',
]
_atabs1 = [((112,185),('衣服',DK)),((235,312),('頭装備',AC)),((360,430),('靴',DK)),((472,565),('装飾品',DK))]
_atabs2 = [((808,888),('衣服',DK)),((933,1015),('頭装備',AC)),((1058,1130),('靴',DK)),((1172,1265),('装飾品',DK))]
PANELS['shuoming08_zhiyishuoming'] = [
 P([252,40,404,76], '設計図', size=17, align='center', color=(235,225,185)),
 *[P([a,103,b,137], t, size=13, align='center', color=c, dark_text=True) for (a,b),(t,c) in _atabs1],
 P([218,176,404,194], '銅兜の設計図', size=13, align='left'),
 P([218,212,392,230], '必要レベル: 0', size=12, align='left'),
 *[P([a,32,b,64], t, size=13, align='center', color=c, dark_text=True) for (a,b),(t,c) in _atabs2],
 P([918,105,1104,123], '銅兜の設計図', size=13, align='left'),
 P([918,141,1090,159], '必要レベル: 0', size=12, align='left'),
 P([115,412,342,432], '銅兜の設計図', size=15, align='center', cx=228),
 P([580,412,806,432], '銅兜の設計図', size=15, align='center', cx=693),
 P([932,412,1158,432], '銅兜の設計図', size=15, align='center', cx=1045),
 P([138,479,318,505], '裁縫レベル 0', size=14, align='center', cx=228, thr=25, iters=3),
 P([602,479,786,505], '裁縫レベル 0', size=14, align='center', cx=693, thr=22, iters=3),
 P([952,479,1136,505], '裁縫レベル 0', size=14, align='center', cx=1043, thr=22, iters=3),
]
# ---- shuoming09 裁縫(素材・実行・結果) ----
CAPS['shuoming09_zhiyishuoming'] = [
 '作成に必要な素材\n数量: 必要数／所持数',
 '必要資金／所持金',
 '作成防具に必ず付く属性と\nその詳細',
 '付与される可能性のある追加属性とその詳細',
 '作成防具の品質ごとの確率と\nその詳細',
]
PANELS['shuoming09_zhiyishuoming'] = [
 P([136,0,314,24], '裁縫レベル 0', size=14, align='center', cx=228, clip=[10,0,445,25], thr=25, iters=3),
 P([26,177,120,199], '銅塊', size=11, align='center'),
 P([190,177,262,199], '石炭', size=11, align='center'),
 P([648,172,738,200], '裁縫', size=18, align='center', dark_text=True),
 P([1088,40,1264,60], '銅兜', size=15, align='center', cx=1176),
 P([988,90,1070,109], '真気上限', size=11, align='left'),
 P([988,120,1070,139], '気血上限', size=11, align='left'),
 P([282,417,405,437], '追加効果', size=15, align='center', cx=344),
 P([155,469,235,487], '防御力', size=13, align='left'),
 P([155,499,240,517], '気血上限', size=13, align='left'),
 P([995,415,1090,437], '品質確率', size=15, align='center', cx=1042),
 P([867,556,957,580], '一般', size=13, align='center', color=(225,200,140)),
 P([997,556,1090,580], '優良', size=13, align='center', color=(150,210,130)),
 P([1130,556,1224,580], '希少', size=13, align='center', color=(150,170,230)),
]

GRAY=(180,180,180)
# ---- shuoming06 鍛造(設計図選択) ----
CAPS['shuoming06_duanzaoshuoming'] = [
 '鍛造する武器の種類を選びます',
 '鍛造する武器を選びます',
 '現在の鍛造レベル',
 '現在の経験値／レベルアップに必要な経験値',
 '鍛造後に得られる経験値',
]
_wtabs1 = [((105,155),('剣',(120,100,40))),((185,240),('刀',(70,70,70))),((262,327),('棍',(70,70,70))),
           ((345,410),('拳',(70,70,70))),((425,492),('暗器',(70,70,70))),((512,567),('その他',(70,70,70)))]
_wtabs2 = [((797,860),('剣',(120,100,40))),((875,945),('刀',(70,70,70))),((960,1030),('棍',(70,70,70))),
           ((1043,1110),('拳',(70,70,70))),((1122,1192),('暗器',(70,70,70))),((1207,1272),('その他',(70,70,70)))]
PANELS['shuoming06_duanzaoshuoming'] = [
 P([252,40,404,76], '設計図', size=17, align='center', color=(235,225,185)),
 *[P([a,103,b,137], t, size=13, align='center', color=c, dark_text=True) for (a,b),(t,c) in _wtabs1],
 P([218,176,382,194], '鋼剣の設計図', size=13, align='left'),
 P([218,212,392,230], '必要レベル: 0', size=12, align='left'),
 *[P([a,32,b,66], t, size=13, align='center', color=c, dark_text=True) for (a,b),(t,c) in _wtabs2],
 P([918,105,1082,123], '鋼剣の設計図', size=13, align='left'),
 P([918,141,1090,159], '必要レベル: 0', size=12, align='left'),
 P([133,412,327,432], '鋼剣の設計図', size=15, align='center', cx=228),
 P([598,412,790,432], '鋼剣の設計図', size=15, align='center', cx=693),
 P([946,412,1142,432], '鋼剣の設計図', size=15, align='center', cx=1043),
 P([138,479,318,505], '鍛造レベル 0', size=14, align='center', cx=228, thr=25, iters=3),
 P([602,479,786,505], '鍛造レベル 0', size=14, align='center', cx=693, thr=22, iters=3),
 P([952,479,1136,505], '鍛造レベル 0', size=14, align='center', cx=1043, thr=22, iters=3),
]
# ---- shuoming07 鍛造(素材・実行・結果) ----
CAPS['shuoming07_duanzaoshuoming'] = [
 '鍛造に必要な素材\n数量: 必要数／所持数',
 '必要資金／所持金',
 '鍛造武器に必ず付く属性と\nその詳細',
 '付与される可能性のある追加属性とその詳細',
 '鍛造武器の品質ごとの確率と\nその詳細',
]
PANELS['shuoming07_duanzaoshuoming'] = [
 P([136,0,314,24], '鍛造レベル 0', size=14, align='center', cx=228, clip=[10,0,445,25], thr=25, iters=3),
 P([34,177,110,199], '鉄塊', size=11, align='center'),
 P([192,177,260,199], '木材', size=11, align='center'),
 P([347,177,413,199], '石炭', size=11, align='center'),
 P([648,172,738,200], '鍛造', size=18, align='center', dark_text=True),
 P([1115,40,1235,60], '鋼剣', size=15, align='center', cx=1175),
 P([986,90,1046,109], '攻撃力', size=12, align='left'),
 P([986,120,1062,139], '会心率', size=12, align='left'),
 P([282,417,405,437], '追加効果', size=15, align='center', cx=344),
 P([158,469,215,487], '攻撃力', size=13, align='left'),
 P([158,499,238,517], '会心率', size=13, align='left'),
 P([995,417,1090,437], '品質確率', size=15, align='center', cx=1042),
 P([867,560,957,580], '一般', size=13, align='center', color=(225,200,140)),
 P([997,560,1090,580], '優良', size=13, align='center', color=(150,210,130)),
 P([1130,560,1224,580], '希少', size=13, align='center', color=(150,170,230)),
]



# ============ shuoming20_wuxueshuoming ============
_t2 = [((508,536),('通常',GOLD)),((575,604),('二式',WHT)),((638,667),('三式',WHT)),
       ((702,742),('絶式',WHT)),((795,825),('軽功',WHT)),((860,890),('心法',WHT))]
_t5 = [((495,527),('通常',GOLD)),((543,568),('二式',WHT)),((586,611),('三式',WHT)),
       ((629,656),('絶式',WHT)),((682,709),('軽功',WHT)),((726,753),('心法',WHT))]
_t3top = [((1084,1104),('通常',WHT)),((1129,1148),('二式',WHT)),((1179,1199),('三式',WHT)),
          ((1227,1246),('絶式',WHT)),((1287,1304),('軽功',WHT)),((1333,1354),('心法',WHT))]
SPECS['shuoming20_wuxueshuoming'] = [
 C([30,280,428,324], '武学アイコンかショートカットキーで\n武学画面を開きます', cx=228),
 C([575,280,810,306], '上部で技の種類を切り替えます', cx=693),
 C([1020,280,1290,306], '左側で武器の種類を切り替えます', cx=1157),
 C([50,665,405,691], '技をダブルクリックで装填／解除', cx=228),
 C([520,665,865,691], '装填した技のみ戦闘で使用できます', cx=693),
 C([935,665,1380,745], '技の習得・強化で、その品質に応じた\n武器熟練度を獲得します。武器熟練度は\n武器のダメージに影響し、一部の上位技の\n習得条件にもなります', cx=1158, pitch=19),
 # tile2
 *tabs(_t2, 71, 89, 10),
 P([745,99,872,115], '招式配置', size=11, align='right', thr=25, iters=3),
 P([528,131,610,144], '基礎拳掌', size=10, align='left', dark_text=True),
 P([528,149,550,159], 'Lv.5', size=9, align='left', dark_text=True),
 P([755,190,862,204], '習得済み武学', size=11, align='right', thr=25, iters=3),
 # tile3
 *tabs(_t3top, 8, 16, 7, clipy=(0,17)),
 P([1250,23,1340,36], '招式配置', size=9, align='right', thr=25, iters=3),
 P([1094,46,1155,56], '基礎拳掌', size=8, align='left', dark_text=True),
 P([1095,58,1112,66], 'Lv.5', size=8, align='left', dark_text=True),
 P([1253,88,1337,100], '習得済み武学', size=9, align='right', thr=25, iters=3),
 P([1031,39,1049,45], '刀', size=8, align='center'),
 P([1028,87,1051,93], '棍', size=8, align='center'),
 P([1028,133,1054,147], '拳', size=8, align='center'),
 P([1029,180,1051,190], '暗器', size=8, align='center'),
 P([1031,228,1049,236], '剣', size=8, align='center'),
 # tile4
 P([150,470,332,492], '基礎拳掌', size=17, align='left', dark_text=True),
 P([152,507,196,525], 'Lv.5', size=13, align='left', dark_text=True),
 # tile5
 *tabs(_t5, 436, 448, 8),
 P([650,450,732,465], '招式配置', size=9, align='right', thr=25, iters=3),
 P([513,470,566,481], '基礎拳掌', size=8, align='left', dark_text=True),
 P([513,483,528,491], 'Lv.5', size=7, align='left', dark_text=True),
 P([655,508,730,522], '習得済み武学', size=9, align='right', thr=25, iters=3),
 P([878,418,907,428], 'その他', size=7, align='center'),
 # tile6
 P([940,413,977,423], '基礎拳掌', size=8, align='right', dark_text=True, clip=[938,410,978,425]),
 P([963,433,1000,450], '強化', size=10, align='center', dark_text=True),
 P([1100,464,1155,476], '習得済み武学', size=9, align='left', clip=[1100,462,1156,478]),
 P([1156,420,1240,432], '基礎拳掌', size=10, align='left'),
 P([1156,434,1176,443], 'Lv.5', size=8, align='left'),
 P([1164,446,1222,458], '攻撃範囲', size=9, align='left'),
 P([1218,464,1268,476], '攻撃力 : 51', size=9, align='left'),
 P([1218,475,1268,487], '真気消費 : 0', size=9, align='left'),
 P([1218,486,1272,498], '待機ターン : 0', size=9, align='left'),
 P([1162,506,1212,519], 'スキル説明', size=9, align='left'),
 P([1158,516,1354,560], '', thr=30, iters=3),  # 説明ゾーン一括消去
 P([1163,517,1182,527], '江湖', size=8, align='left', noerase=True, color=WHT),
 P([1184,517,1280,527], '拳・通常攻撃', size=8, align='left', noerase=True, color=(205,60,50)),
 P([1163,527,1330,537], 'レベル毎に拳の武器熟練度+0.3', size=8, align='left', noerase=True, color=(90,200,80)),
 P([1163,537,1345,547], '最も基礎的な拳法。これだけでは江湖を渡れない。', size=8, align='left', noerase=True, color=(205,205,205)),
 P([1163,547,1350,557], '自身の周囲1マスの敵にダメージ。真気消費なし。', size=8, align='left', noerase=True, color=(200,170,70)),
 P([1164,561,1205,571], '使用効果', size=9, align='left'),
 P([1163,573,1186,582], 'なし', size=8, align='left'),
 P([1164,585,1228,595], '特殊効果', size=9, align='left'),
]


# ================= gamepad 版 =================
def _cp(name):
    import copy as _c
    return _c.deepcopy(PANELS.get(name, []))

# 06/08: キャプション1行目のみ差し替え
CAPS['gamepad__gamepad_shuoming06'] = ['LB/RBで鍛造する武器の種類を切り替えます'] + CAPS['shuoming06_duanzaoshuoming'][1:]
PANELS['gamepad__gamepad_shuoming06'] = _cp('shuoming06_duanzaoshuoming')
CAPS['gamepad__gamepad_shuoming08'] = ['LB/RBで作成する防具の種類を切り替えます'] + CAPS['shuoming08_zhiyishuoming'][1:]
PANELS['gamepad__gamepad_shuoming08'] = _cp('shuoming08_zhiyishuoming')
# 10: プロンプト位置のみ変更
CAPS['gamepad__gamepad_shuoming10'] = list(CAPS['shuoming10_diaoyushuoming'])
_p10 = _cp('shuoming10_diaoyushuoming')
_p10[0] = P([668,114,724,141], '釣り', size=14, align='center')
PANELS['gamepad__gamepad_shuoming10'] = _p10
# 11
CAPS['gamepad__gamepad_shuoming11'] = CAPS['shuoming11_zhandoushuoming'][:3] + [
 '青いマスはこのターンで移動できる範囲です。\n移動後にBを押すと行動をやり直せます']
# 11_0
CAPS['gamepad__gamepad_shuoming11_0'] = [
 '技の下のボタンの組み合わせはショートカットを表します',
 'RTを押してから十字キーで技の種類や差し替え候補を\n切り替えます。右スティック押し込みで技の詳細を\n確認し、十字キーで候補を選ぶと差し替えます',
 '技を選びます',
]
PANELS['gamepad__gamepad_shuoming11_0'] = _cp('shuoming11_zhandoushuoming0')
# 12
CAPS['gamepad__gamepad_shuoming12'] = [
 CAPS['shuoming12_zhandoushuoming'][0],
 '赤いマスは実際の攻撃範囲です。十字キーで\n赤いマスを選びAで技を使用します',
 CAPS['shuoming12_zhandoushuoming'][2],
 CAPS['shuoming12_zhandoushuoming'][3],
]
PANELS['gamepad__gamepad_shuoming12'] = _cp('shuoming12_zhandoushuoming')
# 13
CAPS['gamepad__gamepad_shuoming13'] = [
 'メニューボタンを押し、十字キーでプロフィールアイコンを選んでAで開きます',
 '装備',
 '十字キーで装備を選びAを押すと「装備」が表示されます。\nもう一度Aを押すと装備します',
]
PANELS['gamepad__gamepad_shuoming13'] = _cp('shuoming13_zhuangbeishuoming')
# 17
CAPS['gamepad__gamepad_shuoming17'] = [
 'メニューボタンを押し、十字キーで武学アイコンを\n選んでAで武学画面を開きます',
 CAPS['shuoming17_xinfashuoming'][1],
 'LB/RBで上部の技の種類を切り替えます',
 '十字キーで技を選び、右スティック押し込みで詳細・\n強化に必要な武学ポイント・強化後の数値変化を\n確認できます',
 CAPS['shuoming17_xinfashuoming'][4],
 CAPS['shuoming17_xinfashuoming'][5],
]
PANELS['gamepad__gamepad_shuoming17'] = _cp('shuoming17_xinfashuoming')
for _e in PANELS['gamepad__gamepad_shuoming17']:
    if _e.get('ja') == '軽功' and _e['box'][1] == 76:
        _e['box'] = [986,60,1072,124]
    if _e.get('ja') == '心法' and _e['box'][1] == 76:
        _e['box'] = [1126,58,1238,130]
# 18
CAPS['gamepad__gamepad_shuoming18'] = [
 'メニューボタンを押し、十字キーで経脈アイコンを\n選んでAで経脈画面を開きます',
] + CAPS['shuoming18_jingmaishuoming'][1:]
PANELS['gamepad__gamepad_shuoming18'] = _cp('shuoming18_jingmaishuoming')
# 20
CAPS['gamepad__gamepad_shuoming20'] = [
 'メニューボタンを押し、十字キーで武学アイコンを\n選んでAで武学画面を開きます',
 'LB/RBで上部の技の種類を切り替えます',
 '左側で武器の種類を切り替えます',
 '十字キーで技を選び、Yで装填／解除します',
 '装填した技のみ戦闘で使用できます',
 '技の習得・強化で、その品質に応じた\n武器熟練度を獲得します。武器熟練度は\n武器のダメージに影響し、一部の上位技の\n習得条件にもなります',
]
# 20のパネルは SPECS 版から流用できないため専用処理(後述 render で対応)
# 22
CAPS['gamepad__gamepad_shuoming22'] = [
 'アバター左下のアイコンを選ぶとターン制／リアルタイム制を切り替えられます',
]
PANELS['gamepad__gamepad_shuoming22'] = _cp('shuoming22_huihejishi')
# 23: バー差し替え
CAPS['gamepad__gamepad_shuoming23'] = list(CAPS['shuoming23_yizhanshuoming'])
_p23 = [e for e in _cp('shuoming23_yizhanshuoming') if 'WASD' not in str(e.get('ja',''))]
_p23 += [
 P([62,601,154,625], 'マップ移動', size=13, align='left', color=(228,228,228), iters=3),
 P([232,600,436,626], '拡大／縮小', size=13, align='left', color=(228,228,228), iters=3),
]
PANELS['gamepad__gamepad_shuoming23'] = _p23
# 24: tile4がゲームパッド画に差し替え
CAPS['gamepad__gamepad_shuoming24'] = [
 CAPS['shuoming24_zuoqishuoming'][0],
 CAPS['shuoming24_zuoqishuoming'][1],
 CAPS['shuoming24_zuoqishuoming'][2],
 '騎乗中にRBを押すと、走るの代わりに\n歩く／騎乗を切り替えます',
 CAPS['shuoming24_zuoqishuoming'][4],
]
_p24 = [e for e in _cp('shuoming24_zuoqishuoming') if e['box'][1] < 550 or e['box'][1] > 640]
_p24 += [
 P([4,422,52,446], '地図', size=12, align='center', thr=30, iters=3),
 P([60,401,198,446], 'システムバー表示', size=12, align='center', cx=129, thr=30, iters=3),
 P([338,451,478,478], 'メニュー切替', size=12, align='center', thr=30, iters=3, color=(230,230,230)),
 P([386,503,522,527], '歩く／走る切替', size=12, align='center', thr=30, iters=3),
 P([428,582,500,603], '任務', size=12, align='center', thr=30, iters=3),
]
PANELS['gamepad__gamepad_shuoming24'] = _p24
# 25
CAPS['gamepad__shuoming25_HeTushuoming'] = [
 '十字キー↑/↓で回したいリングを選びます。選択中のリングは光ります',
 '十字キー←/→で石のリングを回します。他のリングも\n選択中のリングと一緒に回ります。リングの模様を\n河図の図案に合わせればパズル完成です',
 'Bで画面を終了、Yで仕掛けをリセットします',
]
PANELS['gamepad__shuoming25_HeTushuoming'] = _cp('shuoming25_HeTushuoming')
# 26: バーの語再配置
CAPS['gamepad__shuoming26_LuoShushuoming'] = [
 '十字キーで行・列を操作する矢印を選びます。\n選択中の矢印はハイライトされます',
 'Aを押すと選択中の矢印の方向に行・列が動きます。\n模様を洛書の図案に合わせればパズル完成です',
 'Bで画面を終了、Yで仕掛けをリセットします',
]
PANELS['gamepad__shuoming26_LuoShushuoming'] = [
 P([415,558,528,598], '決定', size=16, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
 P([645,558,702,598], '終了', size=16, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
 P([788,558,872,598], 'リセット', size=15, align='center', color=(240,240,240), font=BOKU, stroke=2, thr=50),
]
# 27
CAPS['gamepad__shuoming27_YuanWushuoming'] = [
 CAPS['shuoming27_YuanWushuoming'][0],
 '十字キーで矢印の向きを正しい順に入力するとミニゲームクリアです',
]
PANELS['gamepad__shuoming27_YuanWushuoming'] = [
 P([564,590,600,612], '上', size=14, align='center'),
 P([638,590,696,612], '下', size=14, align='center'),
 P([731,590,775,612], '左', size=14, align='center'),
 P([810,588,864,612], '右', size=14, align='center'),
]


PANELS['gamepad__gamepad_shuoming20'] = [e for e in SPECS['shuoming20_wuxueshuoming'] if e.get('mode') != 'caption']

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    skip_done = '--missing' in sys.argv
    shard = None
    for a in sys.argv[1:]:
        if a.startswith('--shard'):
            shard = int(a.split('=')[1]); target = None
    _idx = [0]
    def _take():
        _idx[0] += 1
        return shard is None or (_idx[0] % 3) == shard
    for nm, spec in SPECS.items():
        if target and not target.startswith('--') and nm != target: continue
        if not _take(): continue
        if skip_done and os.path.exists(f'{OUT}/{nm}.png'): continue
        render_page(nm, spec)
    for nm in CAPS:
        if target and not target.startswith('--') and nm != target: continue
        if not _take(): continue
        if skip_done and os.path.exists(f'{OUT}/{nm}.png'): continue
        render_page2(nm, CAPS[nm], PANELS.get(nm, ()), src_name=SRCMAP.get(nm))
