# 빌드된 bin에서 남은 일본어(가나, 또는 kmap에 없는 한자) 전수 조사
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
from prot import files
from chunks import classify,get
import pack
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KM={int(v,16) for v in json.load(open(os.path.join(ROOT,'text','kmap.json'),encoding='utf-8')).values()}
def sj(b0,b1):
    if not(0x81<=b0<=0x84 or 0x88<=b0<=0x9f or 0xe0<=b0<=0xea): return None
    if not(0x40<=b1<=0xfc and b1!=0x7f): return None
    try: return bytes([b0,b1]).decode('cp932')
    except: return None
def scan(d):
    out=[];i=0;n=len(d)
    while i<n-1:
        c=sj(d[i],d[i+1])
        if c is None: i+=1; continue
        j=i;s='';bad=0;kana=0
        while j<n-1:
            c=sj(d[j],d[j+1])
            if c is None:
                if d[j] in (0x0a,) or (d[j]<0x20 and j+2<n and sj(d[j+1],d[j+2])): s+='/'; j+=1; continue
                break
            code=d[j]<<8|d[j+1]
            if 'ぁ'<=c<='ヺ': kana+=1
            elif d[j]>=0x88 and code not in KM: bad+=1
            s+=c; j+=2
        if re.search('[ぁ-ヺ][ぁ-ヺ]',s) or (bad>=1 and kana>=1): out.append((i,s,kana,bad))
        i=j if j>i else i+1
    return out
if __name__=='__main__':
    bin=sys.argv[1]
    D=Disc(bin); ents={e[0]:(e[1],e[2]) for e in D.walk()}
    def getf(name):
        for p,(l,s) in ents.items():
            if p.upper().endswith(name.split(';')[0]): return D.read(l,s)
    prot=getf('PROT.DAT;1'); exe=getf('SCPS_100.59;1')
    srcs=[('exe',exe)]
    for k,f in enumerate(files(prot)):
        kind,ents=classify(f)
        if kind:
            for ci,(t,sz,o) in enumerate(ents):
                try: srcs.append(('%s%d.%d.t%d'%(kind[0],k,ci,t),get(f,kind,t,sz,o)))
                except Exception: srcs.append(('f%d!'%k,f))
        else: srcs.append(('f%d'%k,f))
    for n,d in srcs:
        for i,s,ka,bad in scan(d): print(n,hex(i),ka,bad,s)
