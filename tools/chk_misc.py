# python tools/chk_misc.py m0 → text/ko/m0.json [{"id","ko"}]
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import tokens
from chk import bad_chars
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def clen_nl(s): return sum(1 for t in tokens(s) if t!='\n')
for b in sys.argv[1:]:
    ja={r['id']:r for r in json.load(open(os.path.join(ROOT,'text','ja',b+'.json'),encoding='utf-8'))}
    ko=json.load(open(os.path.join(ROOT,'text','ko',b+'.json'),encoding='utf-8'))
    err=0;seen=set()
    for e in ko:
        i=e['id'];seen.add(i);r=ja.get(i)
        if not r: print(b,i,'unknown id');err+=1;continue
        k=e['ko']
        if k.count('\n')!=r['ja'].count('\n'): print(b,i,'줄바꿈 수 불일치');err+=1
        n=clen_nl(k)
        if n>r['max']: print(b,i,'글자 %d>%d'%(n,r['max']),k);err+=1
        if n==0: print(b,i,'빈 문자열');err+=1
        import re
        if sorted(re.findall(r'\{[0-9a-f]{4}\}|\{N\}',k))!=sorted(re.findall(r'\{[0-9a-f]{4}\}|\{N\}',r['ja'])): print(b,i,'토큰 불일치');err+=1
        bc=[c for c in bad_chars(k.replace('\n','')) ]
        if bc: print(b,i,'허용 안 되는 문자',''.join(bc));err+=1
    miss=[i for i in ja if i not in seen]
    print(b,'오류',err,'누락',len(miss),miss[:20])
