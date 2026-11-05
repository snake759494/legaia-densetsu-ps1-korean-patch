# f869 몬스터 데이터(0x14000 슬롯, [크기][LZSS]) 속 이름
import sys,os,struct,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lzs
S=0x14000
def recs(d):
    for r in range(len(d)//S):
        b=d[r*S:(r+1)*S]; n=struct.unpack_from('<I',b,0)[0]
        if n<0x100 or n>0x40000: continue
        x,p=lzs.decomp(b+bytes(64),n,4); yield r,x,p
def findname(x):
    for i in range(0x40,0x400):
        c=x[i]
        if not 2<=c<=12: continue
        s=x[i+1:i+1+2*c]
        if x[i+1+2*c]!=0: continue
        try: t=s.decode('cp932')
        except UnicodeDecodeError: continue
        if len(t)==c and re.fullmatch('[ァ-ヴー・＄０-９一-龥〈〉]+',t) and re.search('[ァ-ヴ]',t): return i,t
    return None
if __name__=='__main__':
    sys.path.insert(0,'tools'); from prot import files
    d=files()[869]; seen={}
    for r,x,p in recs(d):
        f=findname(x); print(r,hex(p),f)
import json
_TB=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"text","tables.json"),encoding="utf-8"))
T=_TB['mon']; SERU=_TB['seru']; SN=_TB['sn']  # text/tables.json (비공개)
def ko(t):
    suf=''
    m=re.match('(.*?)(＄[０-９])$',t)
    if m: t,suf=m.group(1),m.group(2)
    if t in T: return T[t]+suf
    if t[:2] in SERU and t[2:] in SN: return SERU[t[:2]]+' '+SN[t[2:]]+suf
    return None
def strings(): return list(T.values())+list(SERU.values())+list(SN.values())+['＄０１２３４５６７８９']
def patch(fs,new,kmap):
    from kenc import encode
    d=bytearray(fs[869]); n=0; miss=set()
    for r,x,p in recs(bytes(d)):
        f=findname(x)
        if not f: continue
        i,t=f; k=ko(t)
        if not k: miss.add(t); continue
        e=i+1+2*len(t)+1
        while x[e]==0 and e%4: e+=1
        kb=encode(k,kmap)
        if len(kb)+1>e-i-1: kb=encode(k.replace(' ',''),kmap)
        c=len(kb)//2
        if len(kb)+1>e-i-1: miss.add(t+'(길이)'); continue
        y=bytearray(x); y[i]=c; y[i+1:e]=kb+bytes(e-i-1-len(kb))
        cb=lzs.comp(bytes(y))
        if 4+len(cb)>S: miss.add(t+'(압축)'); continue
        d[r*S:(r+1)*S]=struct.pack('<I',len(x))+cb+bytes(S-4-len(cb)); n+=1
    new[869]=bytes(d); print('몬스터 이름',n,'미처리',sorted(miss))
