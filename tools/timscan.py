# 모든 파일/청크의 TIM 이미지 열거·렌더 (고유 픽셀 기준)
import sys,os,struct,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import files
from chunks import classify,get
import tim
def all_tims():
    fs=files(); seen={}
    for k,f in enumerate(fs):
        kind,ents=classify(f)
        srcs=[(f'f{k}',f)] if not kind else [(f'f{k}.{ci}',get(f,kind,*e)) for ci,e in enumerate(ents)]
        for n,d in srcs:
            for o in tim.find_tims(d):
                try:
                    t=tim.parse(d,o)
                    if t['w']<2 or t['h']<4 or t['w']*t['h']*2>len(d)-o or t['w']>1024 or t['h']>512: continue
                    if len(t['pix'])!=t['w']*t['h']*2: continue
                    hsh=hashlib.md5(t['pix']).hexdigest()
                    if hsh in seen: seen[hsh][1].append((n,o)); continue
                    seen[hsh]=(t,[(n,o)])
                except Exception: pass
    return seen
if __name__=='__main__':
    import pickle
    S=all_tims(); print(len(S))
    from collections import Counter
    print(Counter(t['bpp'] for t,_ in S.values()))
    pickle.dump({h:(dict((k,v) for k,v in t.items() if k!='clut'),t['clut'],l) for h,(t,l) in S.items()},open('tmp/tims.pkl','wb'))
