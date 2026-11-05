# 기타 텍스트 적용 (build.py에서 호출)
import json,os,glob,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import encode,tokens
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load():
    U=json.load(open(os.path.join(ROOT,'text','misc_u.json'),encoding='utf-8'))
    ko={}
    for f in glob.glob(os.path.join(ROOT,'text','ko','m*.json')):
        for e in json.load(open(f,encoding='utf-8')): ko[e['id']]=e['ko']
    return {u['ja']:ko[u['id']] for u in U if u['id'] in ko}
def strings():
    return list(load().values())+list(load2().values())
def enc_multi(s,kmap):
    parts=s.split('\n'); out=b''
    for i,p in enumerate(parts):
        if i: out+=b'\n'
        out+=encode(p,kmap)
    return out,len(tokens(parts[0]))
def load2():
    U=json.load(open(os.path.join(ROOT,'text','misc2_u.json'),encoding='utf-8'))
    ko={}
    for nm in ('m4.json','m5.json'):
        p=os.path.join(ROOT,'text','ko',nm)
        if os.path.exists(p):
            for e in json.load(open(p,encoding='utf-8')): ko[e['id']]=e['ko']
    return {u['ja']:ko[u['id']] for u in U if u['id'] in ko}
def apply2(fs,new,exe,kmap):
    """misc2: fmt D(줄마다 글자 수) / R(접두 유지)"""
    M=json.load(open(os.path.join(ROOT,'text','misc2.json'),encoding='utf-8'))
    tr=load2(); n=0
    for x in M:
        if x['ja'] not in tr: continue
        parts=tr[x['ja']].split(chr(10))
        enc=[encode(p,kmap) for p in parts]
        if x['fmt']=='D':
            body=bytes([len(enc[0])//2])+b''.join((bytes([len(e)//2]) if i else b'')+e for i,e in enumerate(enc))
        else:
            body=bytes([0])+bytes([10]).join(enc)  # 접두 바이트 자리(아래서 원본 유지)
        if len(body)-1>x['cap']: print('misc2 초과',x['src'],hex(x['off']),tr[x['ja']]); continue
        if x['src']=='exe': d=exe
        else:
            k=int(x['src'][1:])
            if k not in new: new[k]=bytes(fs[k])
            d=bytearray(new[k])
        i=x['off']
        if x['fmt']=='D': d[i]=body[0]
        b=body[1:]+bytes(x['cap']+1-(len(body)-1))
        d[i+1:i+1+len(b)]=b
        if x['src']!='exe': new[k]=bytes(d)
        n+=1
    print('misc2 적용',n)
def apply(fs,new,exe,kmap):
    M=json.load(open(os.path.join(ROOT,'text','misc.json'),encoding='utf-8'))
    tr=load(); n=0
    for x in M:
        if x['ja'] not in tr: continue
        b,first=enc_multi(tr[x['ja']],kmap)
        if len(b)>x['cap']: print('misc 초과',x['src'],hex(x['off']),tr[x['ja']]); continue
        if x['src']=='exe': d=exe
        else:
            k=int(x['src'][1:])
            if k not in new: new[k]=bytes(fs[k])
            d=bytearray(new[k])
        i=x['off']
        if x['fmt']=='A': d[i]=first
        body=b+bytes(x['cap']+1-len(b))
        d[i+1:i+1+len(body)]=body
        if x['src']!='exe': new[k]=bytes(d)
        n+=1
    print('misc 적용',n)

# 이름 입력표: 10열×6행 = 60칸 (0x736b = 빈칸)
NAME1=('가나다라마바사아자차'
       '카타파하거너더러머버'
       '서어저처커터퍼허고노'
       '도로모보소오조초코토'
       '포호구누두루무부수우'
       '주추쿠투푸후그느드르')
NAME2=('기니디리미비시이지치'
       '키티피히반진민준현영'
       '성호혁석철훈희연은윤'
       '경동명상선승재정태한'
       '빈인원용규강광남란린'
       '애에예와요유의임혜화')
def name_tables(fs,new,kmap):
    k=899; d=bytearray(new.get(k,fs[k]))
    hira='あいうえおまみむめもかきくけこや'.encode('cp932')
    kata='アイウエオマミムメモカキクケコヤ'.encode('cp932')
    for src,tbl in ((hira,NAME1),(kata,NAME2)):
        i=d.find(src); assert i>=0
        b=b''.join(kmap[c].to_bytes(2,'big') for c in tbl); assert len(b)==120
        d[i:i+120]=b
    new[k]=bytes(d)
