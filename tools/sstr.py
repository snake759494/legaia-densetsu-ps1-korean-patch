# 스크립트 내 [n][n개의 2바이트 문자] 문자열 탐지
def ischar(b0,b1):
    if 0x40<=b1<=0xfc and b1!=0x7f and (0x81<=b0<=0x84 or 0x88<=b0<=0x9f or 0xe0<=b0<=0xea): return True
    if (b0==0xf1 and b1<0x10) or b0==0xf2: return True
    if (b0==0xff and b1<0x20) or (b0==0xf7 and b1<0x10) or b0==0xf5: return True  # 연출 제어 코드
    return False
def scan(d,minn=1):
    res=[];j=0;L=len(d)
    while j<L:
        n=d[j]
        if n>=minn and j+1+2*n<=L and all(ischar(d[j+1+k],d[j+2+k]) for k in range(0,2*n,2)):
            # 첫 글자가 F1이면 엄격히
            res.append((j,n)); j+=1+2*n
        else: j+=1
    return res
def dec(b):
    out='';k=0
    while k<len(b):
        if b[k]==0xf1: out+='{N}'
        else: out+=b[k:k+2].decode('cp932','replace')
        k+=2
    return out
