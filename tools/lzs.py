# Legaia LZSS (Okumura 4096 ring, r=0xFEE, flag bit1=literal, len=(b1&15)+3)
def decomp(src,outlen,pos=0):
    ring=bytearray(4096); r=0xfee; out=bytearray(); flags=0
    while len(out)<outlen:
        flags>>=1
        if not flags&0x100: flags=src[pos]|0xff00; pos+=1
        if flags&1:
            c=src[pos]; pos+=1; out.append(c); ring[r]=c; r=(r+1)&0xfff
        else:
            a=src[pos]; b=src[pos+1]; pos+=2
            off=a|((b&0xf0)<<4); n=(b&15)+3
            for k in range(n):
                c=ring[(off+k)&0xfff]; out.append(c); ring[r]=c; r=(r+1)&0xfff
    return bytes(out[:outlen]),pos
def comp(data):
    """LZSS with full hash chains + optimal parse (DP); compatible with decomp."""
    N=4096;F=18;n=len(data)
    from collections import defaultdict
    heads=defaultdict(list); best=[(0,0)]*n
    for i in range(n):
        bl=0;bp=0
        if i+2<n:
            lst=heads[data[i:i+3]]
            for j in reversed(lst):
                if i-j>N-F: break
                if data[j+bl:j+bl+1]!=data[i+bl:i+bl+1] and bl: continue
                l=3
                while l<F and i+l<n and data[j+l]==data[i+l]: l+=1
                if l>bl: bl=l;bp=j
                if l==F: break
            lst.append(i)
        best[i]=(bl,bp)
    # DP in bits: literal 9, match 17
    cost=[0]*(n+1); ch=[0]*(n+1)
    for i in range(n-1,-1,-1):
        c=cost[i+1]+9; k=1
        bl,bp=best[i]
        for l in range(3,bl+1):
            v=cost[i+l]+17
            if v<c: c=v;k=l
        cost[i]=c; ch[i]=k
    out=bytearray(); i=0; bit=8; fp=0
    while i<n:
        if bit==8: fp=len(out); out.append(0); bit=0
        k=ch[i]
        if k>=3:
            ro=(0xfee+best[i][1])&0xfff
            out.append(ro&0xff); out.append(((ro>>4)&0xf0)|(k-3))
        else:
            out[fp]|=1<<bit; out.append(data[i])
        i+=k; bit+=1
    return bytes(out)
