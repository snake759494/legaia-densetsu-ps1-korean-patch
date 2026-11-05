# PROT 하위 컨테이너: [N][total][(size|type<<24, off)]*N ; 압축 여부 판단
import struct
def parse(f):
    n=struct.unpack_from('<I',f,0)[0]
    if not (1<=n<=40): return None
    tot=struct.unpack_from('<I',f,4)[0]
    ents=[]
    for k in range(n):
        st,off=struct.unpack_from('<II',f,8+8*k)
        ents.append((st>>24,st&0xffffff,off))
    if ents[0][2]!=8+8*n: return None
    return tot,ents
def build(chunks,comp):
    """chunks: [(type,raw bytes, cached_compressed or None)]"""
    n=len(chunks); hdr=bytearray(struct.pack('<II',n,sum(len(r) for t,r,c in chunks)))
    body=bytearray(); off=8+8*n
    for t,r,c in chunks:
        cd=c if c is not None else comp(r)
        hdr+=struct.pack('<II',(t<<24)|len(r),off+len(body)); body+=cd
    return bytes(hdr+body)
