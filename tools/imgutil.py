import sys,os,pickle,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import tim
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    idx=json.load(open(os.path.join(W,'tmp','sheets','index.json')))
    S=pickle.load(open(os.path.join(W,'tmp','tims.pkl'),'rb'))
    e=idx[n]; t,clut,l=S[e['h']]; t=dict(t); t['clut']=clut
    return t,e['locs']
def indices(t):
    h=t['h']; a=np.frombuffer(t['pix'],np.uint8)
    if t['bpp']==0:
        a=a.reshape(h,t['w']*2); r=np.zeros((h,t['w']*4),np.uint8); r[:,0::2]=a&15; r[:,1::2]=a>>4; return r
    return a.reshape(h,t['w']*2).copy()
def blobs(ix,bg=0,gap=2):
    """행 단위로 비배경 띠 찾기 → [(y0,y1,x0,x1)]"""
    m=ix!=bg; rows=np.where(m.any(1))[0]; out=[]
    if not len(rows): return out
    s=rows[0]; p=rows[0]
    for y in list(rows[1:])+[10**9]:
        if y>p+gap:
            seg=m[s:p+1]; cols=np.where(seg.any(0))[0]
            # 열 방향으로도 분할
            cs=cols[0]; cp=cols[0]
            for x in list(cols[1:])+[10**9]:
                if x>cp+8: out.append((s,p,cs,cp)); cs=x
                cp=x
            s=y
        p=y
    return out
from PIL import Image,ImageDraw,ImageFont
from collections import Counter
FD=os.path.join(W,'fonts'); FD2=os.path.dirname(W)
def font(name,size):
    p=os.path.join(FD,name)
    if not os.path.exists(p): p=os.path.join(FD2,name)
    return ImageFont.truetype(p,size)
def textmask(text,fnt,thr=110):
    im=Image.new('L',(len(text)*fnt.size*2+20,fnt.size*3),0); d=ImageDraw.Draw(im)
    d.text((4,4),text,font=fnt,fill=255)
    a=np.array(im)>thr; ys,xs=np.nonzero(a)
    return a[ys.min():ys.max()+1,xs.min():xs.max()+1]
def dil(m,r=1):
    o=m.copy()
    for dy in range(-r,r+1):
        for dx in range(-r,r+1):
            s=np.roll(np.roll(m,dy,0),dx,1)
            o|=s
    return o
def draw(ix,rect,text,fname,size,mode='flat',bg=0,align='left',bold=False,outline=None,minsize=7,stretch=False):
    y0,y1,x0,x1=rect; R=ix[y0:y1+1,x0:x1+1].copy(); H,Wd=R.shape
    txt=R!=bg
    edge=txt & dil(~txt)
    inner=txt & ~edge
    ec=Counter(R[edge].tolist()); ic=Counter(R[inner].tolist())
    has_ol=outline if outline is not None else (len(ec)>0 and len(ic)>0 and ec.most_common(1)[0][0] not in dict(ic.most_common(2)))
    olc=ec.most_common(1)[0][0] if ec else 1
    pad=2 if has_ol else 0
    s=size
    while True:
        f=font(fname,s); m=textmask(text,f)
        if bold: m=m|np.pad(m,((0,0),(1,0)))[:,:-1]
        if (m.shape[0]+pad<=H and m.shape[1]+pad<=Wd) or s<=minsize: break
        s-=1
    if stretch and m.shape[0]+pad<H:
        im=Image.fromarray((m*255).astype(np.uint8)).resize((m.shape[1],H-pad),Image.NEAREST); m=np.array(im)>127
    if m.shape[1]+pad>Wd:
        im=Image.fromarray((m*255).astype(np.uint8)).resize((Wd-pad,m.shape[0]),Image.NEAREST); m=np.array(im)>127
    M=np.zeros((H,Wd),bool); oy=(H-m.shape[0])//2
    ox=pad//2 if align=='left' else (Wd-m.shape[1])//2
    M[oy:oy+m.shape[0],ox:ox+m.shape[1]]=m
    out=np.full((H,Wd),bg,R.dtype)
    if has_ol:
        O=dil(M)&~M; out[O]=olc
    src=inner if inner.any() else txt
    pool=R[src] if src.any() else np.array([olc])
    rowcol={}
    for y in range(H):
        c=Counter(R[y][src[y]].tolist())
        rowcol[y]=c.most_common(1)[0][0] if c else None
    rng=np.random.default_rng(1)
    for y,x in zip(*np.nonzero(M)):
        if mode=='tex':
            out[y,x]=R[y,x] if src[y,x] else pool[rng.integers(len(pool))]
        else:
            c=rowcol[y]
            if c is None:
                for d in range(1,H):
                    c=rowcol.get(y-d) or rowcol.get(y+d)
                    if c is not None: break
            out[y,x]=c if c is not None else olc
    ix[y0:y1+1,x0:x1+1]=out
def pack_ix(t,ix):
    if t['bpp']==0: return (ix[:,0::2]|(ix[:,1::2]<<4)).astype(np.uint8).tobytes()
    return ix.astype(np.uint8).tobytes()
def render(t,ix,path,scale=3):
    t2=dict(t); t2['pix']=pack_ix(t,ix); im=tim.to_img(t2,0); im.resize((im.size[0]*scale,im.size[1]*scale),0).save(path)
