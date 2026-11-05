# 한국어 문자열 → 게임 바이트 (한글은 kmap 코드, 나머지는 SJIS 전각)
import json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HW2FW={' ':'　',',':'、','.':'。','!':'！','?':'？','(':'（',')':'）',':':'：','/':'／','%':'％','&':'＆','+':'＋','-':'－','~':'～','*':'＊','=':'＝','<':'＜','>':'＞','\'':'’','"':'”','[':'【',']':'】','·':'・','…':'…','#':'＃','$':'＄','@':'＠',';':'；','_':'＿','^':'＾'}
def norm(s):
    out=''
    for c in s:
        if c in HW2FW: c=HW2FW[c]
        elif '0'<=c<='9' or 'A'<=c<='Z' or 'a'<=c<='z': c=chr(ord(c)+0xfee0)
        out+=c
    return out
def tokens(s):
    """{N}, {xxxx} 는 1글자 토큰"""
    i=0; out=[]
    while i<len(s):
        if s[i]=='{' and '}' in s[i:]:
            j=s.index('}',i); out.append(s[i:j+1]); i=j+1
        else: out.append(norm(s[i])); i+=1
    return out
def clen(s): return len(tokens(s))
def ishangul(c): return '가'<=c<='힣'
def encode(s,kmap):
    b=bytearray()
    for t in tokens(s):
        if t=='{N}': b+=b'\xf1\x00'
        elif t.startswith('{'): b+=bytes.fromhex(t[1:-1])
        elif ishangul(t): b+=kmap[t].to_bytes(2,'big')
        else: b+=t.encode('cp932')
    return bytes(b)
