import json,os,sys,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M=json.load(open(os.path.join(ROOT,'text','misc.json'),encoding='utf-8'))
u=collections.OrderedDict()
for x in M:
    t=x['ja']; nl=t.count('\n'); mx=(x['cap']-nl)//2
    if t in u: u[t]['max']=min(u[t]['max'],mx); u[t]['src'].add(x['src'])
    else: u[t]={'max':mx,'src':{x['src']}}
items=[{'id':i,'ja':t,'max':v['max'],'src':sorted(v['src'])} for i,(t,v) in enumerate(u.items())]
json.dump(items,open(os.path.join(ROOT,'text','misc_u.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
N=4; per=(len(items)+N-1)//N
for b in range(N):
    json.dump(items[b*per:(b+1)*per],open(os.path.join(ROOT,'text','ja','m%d.json'%b),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(items),per)
