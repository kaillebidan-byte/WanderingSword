# -*- coding: utf-8 -*-
import sys,glob,struct,subprocess,os,re
sys.path.insert(0,'_tools'); import locres, locres_write as L
NL=lambda s:s.replace('\r','').replace('\n','')   # 改行除去キー
# 改行無視の簡体キー -> 日本語(JP内の \n は実改行へ)
RAW={
"鞋":"靴","动画音效":"アニメ効果音","向下移动":"下へ移動","刀法精通":"刀法熟練度","未知喜好":"好みは不明",
"场景移动速度加成":"マップ移動速度ボーナス","世界地图移动速度加成":"ワールドマップ移動速度ボーナス",
"精力高于{0}好感度高于{1}":"精力が{0}以上\n好感度が{1}以上",
"消耗{0}武学点撰写{1}本感悟心得":"武学ポイント{0}を消費して心得を{1}冊執筆",
"前往{0}需要{1}钱币是否确定？":"{0}へ向かうには{1}銭が必要です\nよろしいですか？",
'是否覆盖"{0}"，覆盖后将丢失该存档':'「{0}」に上書きしますか？上書きするとこのセーブは失われます',
'是否删除"{0}"，删除后将丢失该存档':'「{0}」を削除しますか？削除するとこのセーブは失われます',
"取消将失去对阵列表的修改。是否确定取消？":"キャンセルすると編成の変更が失われます。\nキャンセルしますか？",
"是否将<Y>战斗模式</>切换为<Y>即时</>":"<Y>戦闘モード</>を<Y>リアルタイム</>に切り替えますか？",
"是否将<Y>战斗模式</>切换为<Y>回合</>":"<Y>戦闘モード</>を<Y>ターン</>に切り替えますか？",
"是否立刻退出战斗，返回标题界面？<Y>（未保存进度将会丢失）</>":"今すぐ戦闘を終了してタイトルに戻りますか？\n<Y>（未保存の進行は失われます）</>",
# メニュー(系统/Quests等に散在)
"继续游戏":"ゲームを続ける","保存进度":"セーブ","读取进度":"ロード","游戏设置":"ゲーム設定",
"新手教程":"チュートリアル","返回标题":"タイトルへ戻る","退出游戏":"ゲームを終了","开始游戏":"ゲーム開始",
"读取存档":"セーブを読み込む","设置":"設定","游戏":"ゲーム",
}
# 卡关ツールチップ(前方一致で対応)
PREFIX=[
("此项内容影响战斗难度","この項目は戦闘難易度に影響し、<R>詰み</>を引き起こす可能性があります。\n一度ロックすると、<Y>現在の進行および以降のセーブ</>は解放できず、再変更もできません"),
("此拓展项有可能导致","この拡張項目は<R>詰み</>を引き起こす可能性があります。\nその場合は<Y>ゲーム開始後</>の<R>【システム】-【ゲーム設定】-【その他設定】</>から閉じてください"),
]
TL={NL(k):v.replace('\\n','\n') for k,v in RAW.items()}
def kmap_ao(b):
    o=17;(ao,)=struct.unpack_from('<q',b,o);o+=8;o+=4;(nsc,)=struct.unpack_from('<I',b,o);o+=4
    def rf(b,o):
        (n,)=struct.unpack_from('<i',b,o);o+=4
        if n==0:return '',o
        if n<0:c=-n;return b[o:o+c*2].decode('utf-16-le').rstrip('\x00'),o+c*2
        return b[o:o+n].decode('utf-8').rstrip('\x00'),o+n
    m={}
    for _ in range(nsc):
        o+=4;ns,o=rf(b,o);(kc,)=struct.unpack_from('<I',b,o);o+=4
        for _ in range(kc):
            o+=4;key,o=rf(b,o);o+=4;(idx,)=struct.unpack_from('<i',b,o);o+=4
            m[ns+'\x1f'+key]=idx
    return m,ao
def tl(s):
    k=NL(s)
    if k in TL: return TL[k]
    for pre,jp in PREFIX:
        if k.startswith(pre): return jp
    return None
def apply_target(tgt):
    total=0
    for path in glob.glob(f'_work/jp/Wandering_Sword/Content/Localization/{tgt}/*/*.locres'):
        b=open(path,'rb').read();km,ao=kmap_ao(b);_,ver,_,arr,_=L.load(path);n=0
        for fk,idx in km.items():
            jp=tl(arr[idx][0])
            if jp and arr[idx][0]!=jp: arr[idx][0]=jp;n+=1
        if n:open(path,'wb').write(b[:ao]+L.write_string_array(arr,ver));total+=n;print('  ',path.split('Localization/')[1],n)
    return total
# Quests/系统 の zh-Hant も対象にするため、まず本体から不足文化を取り出す
R='_tools/repak'; BASE="/sessions/keen-tender-tesla/mnt/Wandering Sword/Wandering_Sword/Content/Paks/Wandering_Sword-WindowsNoEditor.pak"
for tgt in ['系统','Quests任务表','门派地图与提示']:
    for cul in ['zh-Hant']:
        if not glob.glob(f'_work/jp/Wandering_Sword/Content/Localization/{tgt}/{cul}/*.locres'):
            subprocess.run([R,'unpack',BASE,'-o','_work/jp','-i',f'Wandering_Sword/Content/Localization/{tgt}/{cul}/{tgt}.locres'],capture_output=True)
tot=0
for tgt in ['程序_导出','系统','Quests任务表','门派地图与提示','坐骑']:
    tot+=apply_target(tgt)
print('UI追加翻訳 反映:',tot,'件')
outpak='_work/aaWanderingSword_JP_P.pak'
if os.path.exists(outpak):
    try:os.remove(outpak)
    except PermissionError:open(outpak,'wb').close()
subprocess.run([R,'pack','_work/jp',outpak,'--version','V11','--mount-point','../../../'],check=True)
print('再パックOK')
