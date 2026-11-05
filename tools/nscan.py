# [n][SJIS... (0A 줄바꿈)][00] 문자열 탐지. n = 첫 줄 글자 수
from sstr import ischar
def nscan(d):
    out=[];i=0;L=len(d)
    while i<L-3:
        n=d[i]
        if 1<=n<=60:
            j=i+1;cnt=0;first=None;ok=True;chars=0
            while j<L-1:
                b=d[j]
                if b==0: break
                if b==0x0a:
                    if first is None: first=cnt
                    j+=1; continue
                if ischar(b,d[j+1]): cnt+=1; j+=2
                else: ok=False; break
            if ok and j<L and d[j]==0 and cnt>0:
                f=first if first is not None else cnt
                if f==n:
                    out.append((i,j-i-1)); i=j+1; continue
        i+=1
    return out
def dec(b):
    out='';k=0
    while k<len(b):
        if b[k]==0x0a: out+='\n'; k+=1; continue
        c=b[k:k+2]
        if c[0] in (0xf1,0xf2): out+='{%s}'%c.hex()
        else:
            try: out+=c.decode('cp932')
            except UnicodeDecodeError: out+='{%s}'%c.hex()
        k+=2
    return out
