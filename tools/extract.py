# 대사 런 추출 → text/runs.json (고유 런), text/locs.json (위치)
import sys,os,json,pickle,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import *; from chunks import *; from sstr import scan
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def dec(b):
    out='';k=0
    while k<len(b):
        c=b[k:k+2]
        if c==b'\xf1\x00': out+='{N}'
        elif c[0] in (0xff,0xf7): out+='{%s}'%c.hex()
        else:
            try: out+=c.decode('cp932')
            except UnicodeDecodeError: out+='{%s}'%c.hex()
        k+=2
    return out
def script_chunks(fs):
    for k,f in enumerate(fs):
        kind,ents=classify(f)
        if not kind or k==876: continue
        for ci,(t,s,o) in enumerate(ents):
            if t==3: yield k,kind,ci,get(f,kind,t,s,o)
def runs_of(d):
    sc=scan(d); out=[];cur=[];prev=-1
    for j,n in sc:
        if j!=prev and cur: out.append(cur); cur=[]
        cur.append((j,n)); prev=j+1+2*n
    if cur: out.append(cur)
    return out
if __name__=='__main__':
    fs=files(); uniq={}; order=[]; locs=[]; labs=[]
    for k,kind,ci,d in script_chunks(fs):
        for r in runs_of(d):
            lines=tuple(dec(d[j+1:j+1+2*n]) for j,n in r)
            jl,nl=r[-1]; lab=len(r)==1 and d[r[0][0]-2:r[0][0]]==bytes([0xfe,0xff]) and d[jl+1+2*nl]==0
            if lines not in uniq: uniq[lines]=len(order); order.append(lines); labs.append(lab)
            elif not lab: labs[uniq[lines]]=False
            locs.append([k,ci,r[0][0],uniq[lines]])
    json.dump([{'id':i,'ja':list(l),'label':labs[i]} for i,l in enumerate(order)],open(os.path.join(ROOT,'text','runs.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    json.dump(locs,open(os.path.join(ROOT,'text','locs.json'),'w'))
    print(len(order),len(locs),sum(sum(len(x) for x in l) for l in order))
