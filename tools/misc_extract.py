# 메뉴/전투/미니게임 등 기타 문자열 추출 → text/misc.json
import sys,os,json,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import files; from chunks import classify,get
from nscan import nscan,dec
from sstr import ischar
from zscan import plausible
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def bscan(d):
    """0x60 [text][00]"""
    out=[]
    for m in re.finditer(rb'\x60',d):
        i=m.start(); j=i+1; cnt=0
        while j<len(d)-1 and d[j]!=0:
            if d[j]==0x0a: j+=1; continue
            if ischar(d[j],d[j+1]) or (d[j]==0xfe): cnt+=1; j+=2
            else: break
        if j<len(d) and d[j]==0 and cnt>=1: out.append((i,j-i-1))
    return out
def cap(d,i,l):
    """문자열 본문 시작 i+1, 길이 l, 뒤 0 패딩 포함 최대 바이트(종료 00 1바이트 남김), 4바이트 경계까지만"""
    end=i+1+l  # 종료 00 위치
    j=end+1
    while j<len(d) and d[j]==0 and j%4!=0: j+=1
    return j-(i+1)-1
def collect():
    fs=files(); items=[]
    e=open(os.path.join(ROOT,'orig','SCPS_100.59'),'rb').read()
    srcs=[('exe',None,e,'A')]
    for k,f in enumerate(fs):
        kind,ents=classify(f)
        if kind: continue
        srcs.append(('f%d'%k,k,f,None))
    for name,k,d,fmt in srcs:
        found=[]
        if fmt in (None,'A'):
            for i,l in nscan(d):
                t=dec(d[i+1:i+1+l])
                if name=='exe':
                    if i<0x6200 or (0x65c00<i<0x6e000 and (l>=4 or t in('↓',))): found.append(('A',i,l,t))
                elif plausible(t) and l>=4: found.append(('A',i,l,t))
        if fmt is None:
            for i,l in bscan(d):
                t=dec(d[i+1:i+1+l])
                if plausible(t) and l>=4: found.append(('B',i,l,t))
        if name!='exe' and len(found)<3: continue
        for fm,i,l,t in found:
            items.append({'src':name,'fmt':fm,'off':i,'len':l,'cap':cap(d,i,l),'ja':t})
    return items
if __name__=='__main__':
    it=collect()
    json.dump(it,open(os.path.join(ROOT,'text','misc.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    import collections
    c=collections.Counter(x['src'] for x in it); print(c)
    print(len(it),len(set(x['ja'] for x in it)),sum(len(x['ja']) for x in it))
