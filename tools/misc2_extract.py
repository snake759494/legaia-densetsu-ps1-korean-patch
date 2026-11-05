# 기존 misc 추출에서 빠진 문자열 → text/misc2.json
# fmt D: [n1]줄1[n2]줄2...[00] (줄마다 글자 수), fmt R: 접두 바이트 유지, 본문만 교체
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from uncovered import runs
from prot import files; from chunks import classify
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RANGES={'exe':(0x800,0x6200),'f898':(0,0x400),'f899':(0,0x26a40),'f900':(0x27900,0x29700),'f901':(0,0x21f20),
 'f943':(0x1c00,0x1d00),'f956':(0x2400,0x2700),'f969':(0xe00,0x1600),'f970':(0xe00,0x1000),'f974':(0x2d0,0x800)}
SKIP=lambda s: re.search('[ъэ]',s) or s.startswith(('よさしすせそ','ヨサシスセソ','はひふへほ')) or s in('懲馭',)
def cap(d,j):
    k=j+1
    while k<len(d) and d[k]==0 and k%4!=0: k+=1
    return k-1
def collect():
    M=json.load(open(os.path.join(ROOT,'text','misc.json'),encoding='utf-8'))
    cov={}
    for m in M: cov.setdefault(m['src'],[]).append((m['off'],m['off']+1+m['len']))
    fs=files(); exe=open(os.path.join(ROOT,'orig','SCPS_100.59'),'rb').read()
    out=[]
    for n,(lo,hi) in RANGES.items():
        d=exe if n=='exe' else fs[int(n[1:])]
        for i,j,s in runs(d,lo,hi):
            if any(a<=i<b for a,b in cov.get(n,[])) or SKIP(s): continue
            # 세그먼트 분해
            segs=[];k=i;cur=b'';ctl=[]
            while k<j:
                if d[k]<0x20: segs.append(cur); ctl.append(d[k]); cur=b''; k+=1
                else: cur+=d[k:k+2]; k+=2
            segs.append(cur)
            p=d[i-1]; cnts=[p]+ctl
            fmt='D' if all(c==len(sg)//2 for c,sg in zip(cnts,segs)) else 'R'
            if fmt=='R' and ctl and not all(c==0x0a for c in ctl): continue
            out.append({'src':n,'fmt':fmt,'off':i-1,'len':j-i,'cap':cap(d,j)-i,'ja':s})
    return out
if __name__=='__main__':
    it=collect()
    json.dump(it,open(os.path.join(ROOT,'text','misc2.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    for x in it: print(x['src'],hex(x['off']),x['fmt'],x['cap'],x['ja'].replace('\n','/'))
    print(len(it))
