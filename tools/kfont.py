# 한글 글꼴/코드 배정
import os,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT=os.path.join(ROOT,'fonts','Galmuri11.ttf')
def idx2code(i):
    """full-font linear index -> SJIS code (inverse of exe 0x800375bc)"""
    # idx = 188*(hi-0x88) - 0x40 + lo' - 0x5e  , lo' = lo-1 if lo>=0x80
    t=i+0x40+0x5e
    hi=0x88+t//188; r=t%188  # r = lo' 
    # lo' range 0x40..0xfb  (r+? ) : t = 188R + lo'  with lo' in [0x40, 0x40+187]
    r=t-188*(hi-0x88)
    if r<0x40: hi-=1; r+=188
    if r>0x40+187: hi+=1; r-=188
    lo=r if r<0x7f else r+1
    return hi<<8|lo
def code2idx(c):
    hi,lo=c>>8,c&0xff
    if lo>=0x80: lo-=1
    return 188*(hi-0x88)-0x40+lo-0x5e
def check():
    for i in range(0,3300):
        c=idx2code(i); assert code2idx(c)==i,(i,hex(c))
        hi,lo=c>>8,c&0xff
        assert 0x40<=lo<=0xfc and lo!=0x7f
check()
def glyph(ch,font=None):
    f=font or ImageFont.truetype(FONT,12)
    im=Image.new('1',(12,12),0); d=ImageDraw.Draw(im)
    d.text((0,-1),ch,font=f,fill=1)
    return np.array(im,dtype=np.uint8)
def put_full(tims,idx,g):
    """tims: [bytearray pix of TIM1 (idx 0..1599), TIM2 (idx 1694..)] 4bpp 256x256 (128 bytes/row)"""
    if idx>=1694: t=tims[1]; idx-=1694
    else: assert idx<1600; t=tims[0]
    p=idx//400; c=idx%400; u=(c%20)*12; v=(c//20)*12
    m=1<<p
    for y in range(12):
        for x in range(12):
            o=(v+y)*128+(u+x)//2; sh=4 if (u+x)&1 else 0
            if g[y][x]: t[o]|=m<<sh
            else: t[o]&=~(m<<sh)&0xff
