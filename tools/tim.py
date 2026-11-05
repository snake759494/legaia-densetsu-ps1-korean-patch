import struct,numpy as np
from PIL import Image
def find_tims(b):
    res=[];i=0
    while True:
        i=b.find(b'\x10\x00\x00\x00',i)
        if i<0 or i+8>len(b): break
        fl=struct.unpack_from('<I',b,i+4)[0]
        if fl in (8,9,2,3,0,1):
            res.append(i)
        i+=4
    return res
def parse(b,o):
    fl=struct.unpack_from('<I',b,o+4)[0]; p=o+8; clut=None
    if fl&8:
        ln,cx,cy,cw,ch=struct.unpack_from('<IHHHH',b,p); clut=np.frombuffer(b[p+12:p+12+cw*ch*2],np.uint16).reshape(ch,cw); p+=ln
    ln,x,y,w,h=struct.unpack_from('<IHHHH',b,p)
    pix=b[p+12:p+12+w*h*2]
    return dict(bpp=fl&3,clut=clut,x=x,y=y,w=w,h=h,pix=pix,end=p+ln,cxy=(cx,cy) if clut is not None else None)
def to_img(t,ci=0,gray=False):
    w,h=t['w'],t['h']; a=np.frombuffer(t['pix'],np.uint8).reshape(h,w*2)
    if t['bpp']==0:
        idx=np.zeros((h,w*4),np.uint8); idx[:,0::2]=a&15; idx[:,1::2]=a>>4
    elif t['bpp']==1: idx=a
    else:
        v=np.frombuffer(t['pix'],np.uint16).reshape(h,w)
        return Image.fromarray(np.dstack([(v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3]).astype(np.uint8))
    if gray or t['clut'] is None: return Image.fromarray((idx*(17 if t['bpp']==0 else 1)).astype(np.uint8))
    c=t['clut'][ci%len(t['clut'])]; v=c[idx]
    return Image.fromarray(np.dstack([(v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3]).astype(np.uint8))
