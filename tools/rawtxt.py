# 기존 추출에서 빠진 전투/튜토리얼 문자열 (원문을 파일에서 찾아 같은 자리에 기록)
import re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import encode,tokens
def jenc(s):
    out=b''
    for p in re.split(r'(\{[0-9a-f]{4}\})',s):
        if not p: continue
        out+=bytes.fromhex(p[1:-1]) if p.startswith('{') and len(p)==6 else p.encode('cp932')
    return out
# F: 같은 토큰 수로 맞춤(모자라면 뒤에 공백), 개수 바이트 그대로
import json
_TB=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"text","tables.json"),encoding="utf-8"))
# 원문→번역 표는 text/tables.json (비공개). FIX: 같은 토큰 수 / STR: C=[개수][문자열][00], N=개수 없음
FIX=_TB['fix']; STR=_TB['str']
def strings(): return [k for *_,k in FIX]+[k for *_,k in STR]
def apply(fs,new,kmap):
    n=0
    for ks,ja,ko in FIX:
        jb=jenc(ja); L=len(tokens(ja)); kt=len(tokens(ko)); assert kt<=L,(ja,ko)
        kb=b''.join(encode(p,kmap) if not p.startswith('{') else jenc(p) for p in re.split(r'(\{fe0[0-9]\})',ko) if p)+encode(' '*(L-kt),kmap) if '{fe0' in ko else encode(ko+' '*(L-kt),kmap); assert len(kb)==len(jb),(ko,len(kb),len(jb))
        for k in ks:
            d=bytearray(new.get(k,fs[k])); i=bytes(d).find(jb)
            if i<0: print('rawtxt 없음',k,ja); continue
            d[i:i+len(jb)]=kb; new[k]=bytes(d); n+=1
    for ks,m,ja,ko in STR:
        jb=jenc(ja)+b'\0'
        for k in ks:
            d=bytearray(new.get(k,fs[k])); i=bytes(d).find(jb)
            if i<0: print('rawtxt 없음',k,ja); continue
            if m=='N' and i>0 and d[i-1]!=0: print('rawtxt N 앞',k,ja)
            e=i+len(jb)
            while e<len(d) and d[e]==0 and e%4: e+=1
            kb=encode(ko,kmap); assert len(kb)<e-i,(k,ko)
            if m=='C': d[i-1]=d[i-1]-len(tokens(ja))+len(tokens(ko))
            d[i:e]=kb+bytes(e-i-len(kb)); new[k]=bytes(d); n+=1
    print('rawtxt 적용',n)
