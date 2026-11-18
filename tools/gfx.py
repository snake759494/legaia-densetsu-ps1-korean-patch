# 파일0 TIM(0xd4) 전투 UI 그림 글자 한글화
import sys,os,struct,collections,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import tim
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT=lambda n,s: ImageFont.truetype(os.path.join(ROOT,'fonts',n),s)
STATUS=[(5,48,'독'),(5,64,'마비'),(5,80,'수면'),(5,96,'폭주'),
        (53,48,'맹독'),(53,64,'저주'),(53,80,'석화'),(53,96,'기절'),(53,112,'곰팡이')]
TAGS=[(0,'무기'),(20,'왼손'),(40,'하단'),(64,'세루'),(84,'오른손'),(104,'상단')]
def mask(text,font,w,h):
    im=Image.new('L',(w*2,h*2),0); d=ImageDraw.Draw(im)
    d.text((0,0),text,font=font,fill=255)
    a=np.array(im)>128
    ys,xs=np.nonzero(a)
    a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    return a
def place(a,w,h):
    out=np.zeros((h,w),bool); mh,mw=a.shape
    assert mw<=w and mh<=h,(mw,w,mh,h)
    oy=(h-mh)//2; ox=(w-mw)//2
    out[oy:oy+mh,ox:ox+mw]=a; return out
def bold(a):
    b=a.copy(); b[:,1:]|=a[:,:-1]; return b
def patch(f):
    f=bytearray(f); o=0xd4; t=tim.parse(bytes(f),o)
    W=t['w']*4; H=t['h']
    p=f.find(t['pix'],o)
    a=np.frombuffer(bytes(t['pix']),np.uint8).reshape(H,t['w']*2)
    idx=np.zeros((H,W),np.uint8); idx[:,0::2]=a&15; idx[:,1::2]=a>>4
    # 상태 라벨: 영역 x0+2..x0+39, y0+2..y0+15
    aw,ah=37,14
    stack=[idx[y+2:y+2+ah,x+2:x+2+aw] for x,y,_ in STATUS]
    bg=np.full((ah,aw),3,np.uint8)
    for yy in range(ah):
        for xx in range(aw):
            c=collections.Counter(int(s[yy,xx]) for s in stack if s[yy,xx] not in (14,15))
            if c: bg[yy,xx]=c.most_common(1)[0][0]
    f11=FONT('Galmuri11.ttf',12)
    for x,y,txt in STATUS:
        m=bold(place(mask(txt,f11,aw,ah),aw-1,ah)); m=np.pad(m,((0,0),(0,1)))
        r=bg.copy()
        m=m|np.pad(m,((1,0),(0,0)))[:-1]   # 획을 2줄 두께로: 14/15 교대 줄 어느 쪽에서도 보이게
        for yy in range(ah): r[yy][m[yy]]=15 if (y+2+yy)%2==0 else 14
        idx[y+2:y+2+ah,x+2:x+2+aw]=r
    # 무기/손/발 태그: x104..127, y0+3..y0+14
    tw,th=24,12
    stack=[idx[y+3:y+3+th,104:104+tw] for y,_ in TAGS]
    bg=np.full((th,tw),14,np.uint8)
    for yy in range(th):
        for xx in range(tw):
            c=collections.Counter(int(s[yy,xx]) for s in stack if s[yy,xx] in (13,14,15))
            if c: bg[yy,xx]=c.most_common(1)[0][0]
    f7=FONT('Galmuri7.ttf',8)
    for y,txt in TAGS:
        if len(txt)==2:
            # 화면에서 가로로 축소되어 표시되므로 가로를 꽉 채워 늘림(ㅏ 짧은 획 보존), 그림자 자리 1px
            m0=mask(txt,f11,tw-1,th-1); m0=np.array(Image.fromarray(m0.astype(np.uint8)*255).resize((tw-1,m0.shape[0]),Image.NEAREST))>0
            m=place(m0,tw-1,th-1); m=np.pad(m,((0,1),(0,1)))
        else: m=place(mask(txt,f7,tw,th),tw,th)
        r=bg.copy()
        # 원본처럼 글자 = 1, 오른쪽·아래 그림자 = 2
        sh=(np.pad(m,((1,0),(0,0)))[:-1]|np.pad(m,((0,0),(1,0)))[:,:-1]|np.pad(m,((1,0),(1,0)))[:-1,:-1])&~m
        r[sh]=2; r[m]=1
        idx[y+3:y+3+th,104:104+tw]=r
    # (ラ·セル) → (라세루)
    x0,y0,w,h=0,159,40,14
    m=place(mask('(라세루)',FONT('Galmuri9.ttf',10),w-2,h-2),w-2,h-2); m=np.pad(m,1)
    ol=np.zeros_like(m)
    for dy in (-1,0,1):
        for dx in (-1,0,1): ol|=np.roll(np.roll(m,dy,0),dx,1)
    r=np.zeros((h,w),np.uint8); r[ol]=7; r[m]=4
    idx[y0:y0+h,x0:x0+w]=r
    nb=(idx[:,0::2]|(idx[:,1::2]<<4)).astype(np.uint8).tobytes()
    f[p:p+len(nb)]=nb
    return bytes(f)
if __name__=='__main__':
    from prot import files
    g=patch(files()[0]); t=tim.parse(g,0xd4)
    tim.to_img(t,gray=True).resize((1024,768),0).save(sys.argv[1] if len(sys.argv)>1 else 'tmp/big2.png')
