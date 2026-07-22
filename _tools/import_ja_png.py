# -*- coding: utf-8 -*-
"""_gemini_uiimg/返却/ の日本語PNGを、対応するテクスチャ(uexp)へ注入し、
ベースパスとして _work/jp に配置 → pak → deploy。
返却PNGは元と同名(例 Gamepad_A5.png)。寸法が違えば最近傍で同寸に補正。
使い方: python _tools/import_ja_png.py [--no-deploy]
"""
import os, sys, glob, shutil, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import tex2d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RET  = os.path.join(ROOT, '_gemini_uiimg', '返却')
DSTBASE = os.path.join(ROOT, r'_work\jp\Wandering_Sword\Content\JH\JHNeoUI\UIAssets')
# カテゴリ -> en抽出元ディレクトリ(uasset/uexp取得元)。返却PNG名 "cat__sub__name" は '__' を階層区切りに戻して照合。
SRC_DIRS = {
    'Gamepad':  os.path.join(ROOT, r'_ws_tmp\_gp_en\Wandering_Sword\Content\L10N\en\JH\JHNeoUI\UIAssets\Gamepad'),
    'Battle':   os.path.join(ROOT, r'_ws_tmp\_bat_en\Wandering_Sword\Content\L10N\en\JH\JHNeoUI\UIAssets\Battle'),
    'Tutorial': os.path.join(ROOT, r'_ws_tmp\_tut_en\Wandering_Sword\Content\L10N\en\JH\JHNeoUI\UIAssets\Tutorial'),
}
# en版が無いアセット用のフォールバック(base=簡体字。同寸・同フォーマットなのでドナーに使える)
FALLBACK_DIRS = {
    'Tutorial': os.path.join(ROOT, r'_ws_tmp\_tut_cn\Wandering_Sword\Content\JH\JHNeoUI\UIAssets\Tutorial'),
}

def resize_bgra(src, sw, sh, dw, dh):
    if (sw, sh) == (dw, dh): return src
    out = bytearray(dw*dh*4)
    for y in range(dh):
        sy = y*sh//dh
        base = sy*sw
        for x in range(dw):
            si = (base + x*sw//dw)*4; di = (y*dw + x)*4
            out[di:di+4] = src[si:si+4]
    return bytes(out)

def find_src(name):
    rel = name.replace('__', os.sep)   # 階層フラット名を戻す (gamepad__X -> gamepad/X)
    for sub, d in SRC_DIRS.items():
        p = os.path.join(d, rel + '.uexp')
        if os.path.exists(p): return sub, d, rel, p
    for sub, d in FALLBACK_DIRS.items():
        p = os.path.join(d, rel + '.uexp')
        if os.path.exists(p): return sub, d, rel, p
    return None, None, None, None

def main(deploy=True):
    pngs = sorted(glob.glob(os.path.join(RET, '*.png')))
    if not pngs:
        print('返却/ にPNGが無い'); return
    done = []
    for png in pngs:
        name = os.path.splitext(os.path.basename(png))[0]
        sub, sdir, rel, suexp = find_src(name)
        if not suexp:
            print(f'  SKIP {name}: 元アセットが見つからない'); continue
        b = bytearray(open(suexp, 'rb').read())
        m = tex2d.parse(bytes(b))
        bgra, W, H = tex2d.png_to_bgra(png)
        if (W, H) != (m['sx'], m['sy']):
            print(f'  resize {name}: {W}x{H} -> {m["sx"]}x{m["sy"]}')
            bgra = resize_bgra(bgra, W, H, m['sx'], m['sy'])
        b[m['pix_off']:m['pix_off']+m['pix_len']] = bgra
        dst = os.path.join(DSTBASE, sub, rel)   # relはサブフォルダ込み
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst + '.uexp', 'wb').write(bytes(b))
        shutil.copy2(os.path.join(sdir, rel + '.uasset'), dst + '.uasset')
        done.append(name)
        print(f'  OK {name} -> {sub}/{rel} (base override)')
    print(f'\n注入 {len(done)} 件')
    if deploy and done:
        os.environ.setdefault('WS_TMP', os.path.join(ROOT, '_ws_tmp'))
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        outpak = os.path.join(ROOT, r'_work\aaWanderingSword_JP_P.pak')
        repak = os.path.join(ROOT, '_tools', 'repak.exe')
        if os.path.exists(outpak): os.remove(outpak)
        subprocess.run([repak, 'pack', os.path.join(ROOT, '_work', 'jp'), outpak,
                        '--version', 'V11', '--mount-point', '../../../'], check=True)
        subprocess.run([sys.executable, os.path.join(ROOT, '_tools', 'deploy_to_game.py')], check=True)
        print('pack + deploy 完了')

if __name__ == '__main__':
    main(deploy='--no-deploy' not in sys.argv)
