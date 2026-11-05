# misc.json이 덮지 않는 일본어 문자열 찾기
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import files; from chunks import classify
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def jp(b0,b1):
    if not(0x81<=b0<=0x84 or 0x88<=b0<=0x9f or 0xe0<=b0<=0xea): return False
    if not(0x40<=b1<=0xfc and b1!=0x7f): return False
    try: c=bytes([b0,b1]).decode('cp932')
    except: return False
    return True
def runs(d,lo=0,hi=None):
    hi=hi or len(d); i=lo; out=[]
    while i<hi-1:
        if jp(d[i],d[i+1]):
            j=i; s=''
            while j<hi-1 and (jp(d[j],d[j+1]) or d[j] in (0x0a,0x08,0x09,0x0b,0x0c) and j>i):
                if d[j]<0x20: s+='\n'; j+=1
                else: s+=d[j:j+2].decode('cp932'); j+=2
            if j<len(d) and d[j]==0 and re.search('[぀-ヿ一-鿿]',s) and len(s.replace('\n',''))>=2:
                out.append((i,j,s))
            i=j if j>i else i+1
        else: i+=1
    return out
if __name__=='__main__':
    M=json.load(open(os.path.join(ROOT,'text','misc.json'),encoding='utf-8'))
    cov={}
    for m in M: cov.setdefault(m['src'],[]).append((m['off'],m['off']+1+m['len']))
    fs=files(); exe=open(os.path.join(ROOT,'orig','SCPS_100.59'),'rb').read()
    srcs=[('exe',exe)]+[('f%d'%k,f) for k,f in enumerate(fs) if not classify(f)[0]]
    res=[]
    for n,d in srcs:
        if n!='exe' and n not in cov: continue
        for i,j,s in runs(d):
            if any(a<=i<b for a,b in cov.get(n,[])): continue
            res.append((n,i,j,d[i-1],s))
    for r in res: print(r[0],hex(r[1]),'%02x'%r[3],r[4].replace('\n','/'))
    print(len(res))
