# 전투 기술 이름 (f865 반 / f866 노아 / f867 가라): LZSS 블록 [h0 압축끝][h1 다음구역][h2][h3 원본크기] @0x10
import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lzs
from chain_extract import chains
from kenc import encode
import json
_TB=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"text","tables.json"),encoding="utf-8"))
T=_TB['arts']  # 원문→번역 표는 text/tables.json (비공개)
def strings(): return list(T.values())
def patch(fs,new,kmap):
    for k in (865,866,867):
        f=bytearray(new.get(k,fs[k])); h=list(struct.unpack_from('<4I',f,0))
        d=bytearray(lzs.decomp(bytes(f),h[3],0x10)[0]); n=0
        for c in chains(bytes(d),0,len(d)):
            if c['ja'] not in T: continue
            b=encode(T[c['ja']],kmap); assert len(b)<=c['cap'],(c['ja'],T[c['ja']])
            i=c['off']; d[i]=len(b)//2; d[i+1:i+1+c['cap']]=b+bytes(c['cap']-len(b)); n+=1
        cz=lzs.comp(bytes(d)); assert lzs.decomp(cz,len(d))[0]==bytes(d)
        # h0~h1 사이는 다른 표 → 압축 결과가 원래 블록(0x10~h0) 안에 들어가야 함
        assert 0x10+len(cz)<=h[0],(k,hex(0x10+len(cz)),hex(h[0]))
        f[0x10:h[0]]=cz+bytes(h[0]-0x10-len(cz))
        new[k]=bytes(f); print('arts',k,n,hex(h[0]),hex(h[1]))
