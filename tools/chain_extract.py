# [n1]줄1[n2]줄2...[00] 체인(줄마다 글자 수, 토큰 ff/f1/f2/f7 포함) 추출 → 기존 misc/misc2와 겹치면 교체 대상
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import files
from chunks import classify
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def unit(b0,b1):
    if b0 in (0xff,0xf7) and b1<0x20: return '{%02x%02x}'%(b0,b1)
    if b0==0xf1 and b1<0x10: return '{N}' if b1==0 else '{%02x%02x}'%(b0,b1)
    if b0==0xf2: return bytes([b0,b1]).decode('cp932','replace') if False else '{%02x%02x}'%(b0,b1)
    if (0x81<=b0<=0x84 or 0x88<=b0<=0x9f or 0xe0<=b0<=0xea) and 0x40<=b1<=0xfc and b1!=0x7f:
        try: return bytes([b0,b1]).decode('cp932')
        except: return None
    return None
def line_at(d,j):
    n=d[j]
    if not(1<=n<=0x1f) or j+1+2*n>len(d): return None
    s=''
    for k in range(n):
        u=unit(d[j+1+2*k],d[j+2+2*k])
        if u is None: return None
        s+=u
    return s,j+1+2*n
def chains(d,lo,hi):
    out=[];j=lo
    while j<hi:
        r=line_at(d,j)
        if r:
            lines=[r[0]];e=r[1]
            while e<len(d) and d[e]!=0:
                r2=line_at(d,e)
                if not r2: break
                lines.append(r2[0]); e=r2[1]
            if e<len(d) and d[e]==0 and re.search('[ぁ-ヺ一-鿿]',''.join(lines)):
                k=e+1
                while k<len(d) and d[k]==0 and k%4!=0: k+=1
                out.append({'off':j,'end':e,'cap':k-1-(j+1),'ja':'\n'.join(lines)})
                j=e+1; continue
        j+=1
    return out
def collect():
    M=json.load(open(os.path.join(ROOT,'text','misc.json'),encoding='utf-8'))
    M2=json.load(open(os.path.join(ROOT,'text','misc2.json'),encoding='utf-8'))
    srcs=sorted({m['src'] for m in M+M2})
    fs=files(); exe=open(os.path.join(ROOT,'orig','SCPS_100.59'),'rb').read()
    out=[]
    for s in srcs:
        if s=='exe': C=chains(exe,0x800,0x6200)+chains(exe,0x65c00,0x6e000)
        else: d=fs[int(s[1:])]; C=chains(d,0,len(d))
        cov=[(m['off'],m['off']+1+m['len']) for m in M+M2 if m['src']==s]
        for c in C:
            if any(a==c['off'] and b==c['end'] for a,b in cov): continue
            # 기존 항목과 겹치지 않는 새 체인은 여러 줄이거나 토큰 있을 때만(오탐 방지)
            ov=any(c['off']<=a<c['end'] for a,b in cov)
            if not ov and '\n' not in c['ja'] and '{' not in c['ja']: continue
            c['src']=s; c['fmt']='D'; c['len']=c['end']-c['off']-1; out.append(c)
    return out
if __name__=='__main__':
    C=collect()
    for c in C: print(c['src'],hex(c['off']),c['cap'],c['ja'].replace('\n','/'))
    print(len(C))
