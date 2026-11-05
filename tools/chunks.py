# 모든 PROT 파일의 청크 열거: (file, kind, type, size, off) ; kind 'raw' = 단일 비압축 청크, 'pack' = 압축 번들
import struct,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pack import parse
from lzs import decomp
def classify(f):
    p=parse(f) if len(f)>=16 else None
    if p:
        tot,ents=p
        if sum(s for t,s,o in ents)==tot and all(o<len(f) for t,s,o in ents): return 'pack',ents
    ents=[];o=0
    while o+4<=len(f):
        st=struct.unpack_from('<I',f,o)[0]; t=st>>24; s=st&0xffffff
        if st==0 and ents: break
        if not(1<=t<=0x20 and 0<s<=len(f)-o-4): return None,None
        ents.append((t,s,o+4)); o+=4+s
    if ents and all(x==0 for x in f[o:]) : return 'raw',ents
    return None,None
def get(f,kind,t,s,o):
    if kind=='raw': return f[o:o+s]
    return decomp(f,s,o)[0]
