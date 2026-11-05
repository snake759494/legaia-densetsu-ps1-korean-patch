# 번역 검사: python tools/chk.py b00  (text/ko/b00.json)
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import tokens,clen
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED=set('、。．・：？！々ー／～…（）〈〉「」【】＋－×％＆＊＝＜＞’”＃＄＠；＿＾　♂♀★◆Φ∈○●△▽□■☆→←↑↓『』〓｜')
def bad_chars(s):
    out=[]
    for t in tokens(s):
        if t.startswith('{'): continue
        if '가'<=t<='힣': continue
        if '０'<=t<='９' or 'Ａ'<=t<='Ｚ' or 'ａ'<=t<='ｚ': continue
        if t in ALLOWED: continue
        try:
            t.encode('cp932')
            if '぀'<=t<='ヿ' or '一'<=t<='鿿': out.append(t)
        except Exception: out.append(t)
    return out
def check(b):
    ja={r['id']:r for r in json.load(open(os.path.join(ROOT,'text','ja',b+'.json'),encoding='utf-8'))}
    ko=json.load(open(os.path.join(ROOT,'text','ko',b+'.json'),encoding='utf-8'))
    err=[];seen=set()
    for e in ko:
        i=e['id']; seen.add(i)
        if i not in ja: err.append((i,'unknown id')); continue
        r=ja[i]; k=e['ko']
        if len(k)!=len(r['ja']): err.append((i,'줄 수 %d≠%d'%(len(k),len(r['ja'])))); continue
        L=[clen(x) for x in k]
        if sum(L)>r['tot']: err.append((i,'총 글자 %d>%d'%(sum(L),r['tot'])))
        if max(L)>r['w']: err.append((i,'줄 길이 %d>%d'%(max(L),r['w'])))
        import re
        tk=lambda L: sorted(re.findall(r'\{[^}]+\}|[-]',''.join(L)))
        if tk(k)!=tk(r['ja']): err.append((i,'토큰 불일치(원문 토큰 '+' '.join(tk(r['ja']))+')'))
        bc=[c for x in k for c in bad_chars(x)]
        if bc: err.append((i,'허용 안 되는 문자 '+''.join(bc)))
    miss=[i for i in ja if i not in seen]
    return err,miss
if __name__=='__main__':
    for b in sys.argv[1:]:
        err,miss=check(b)
        for i,m in err: print(b,i,m)
        print(b,'오류',len(err),'누락',len(miss), miss[:20])
