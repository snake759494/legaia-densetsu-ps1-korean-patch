# 재추출 후 기존 번역 id 유지(원문 같으면 같은 id), 새 런은 20000번부터
import json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J=lambda *a: os.path.join(ROOT,'text',*a)
O=json.load(open(J('runs_old.json'),encoding='utf-8')); N=json.load(open(J('runs.json'),encoding='utf-8'))
L=json.load(open(J('locs.json')))
om={tuple(r['ja']):r['id'] for r in O}
remap={}; nid=20000; out=[]
for r in N:
    k=tuple(r['ja'])
    remap[r['id']]=om[k] if k in om else nid
    if k not in om: nid+=1
    out.append({'id':remap[r['id']],'ja':r['ja'],'label':r['label']})
for l in L: l[3]=remap[l[3]]
json.dump(out,open(J('runs.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(L,open(J('locs.json'),'w'))
new=[r for r in out if r['id']>=20000]
print('total',len(out),'new',len(new))
