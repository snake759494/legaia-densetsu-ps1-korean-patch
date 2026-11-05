import json,os,sys,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import clen
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R=json.load(open(os.path.join(ROOT,'text','runs.json'),encoding='utf-8'))
def lim(r):
    L=[clen(x) for x in r['ja']]
    return max(max(L),18) if len(L)>1 else L[0], sum(L)
skip=lambda r: all(re.fullmatch(r'(\{[0-9a-f]{4}\})+',x) for x in r['ja'])
items=[r for r in R if not skip(r) and not r['label']]
N=int(sys.argv[1]) if len(sys.argv)>1 else 30
per=(len(items)+N-1)//N
for b in range(N):
    part=items[b*per:(b+1)*per]
    out=[{'id':r['id'],'ja':r['ja'],'w':lim(r)[0],'tot':lim(r)[1]} for r in part]
    json.dump(out,open(os.path.join(ROOT,'text','ja','b%02d.json'%b),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(items),per)
