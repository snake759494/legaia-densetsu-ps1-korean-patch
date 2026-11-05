# PROT.DAT 재구성: 원래 위치를 최대한 유지하고, 넘치는 파일은 뒤 파일들을 밀어서 배치(TOC 갱신)
import struct,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import load
def rebuild(newfiles):
    d,n,offs=load(); total=offs[n]
    data=[newfiles.get(i, d[offs[i]*2048:offs[i+1]*2048]) for i in range(n)]
    # 원본 파일의 실제 끝(뒤 0 패딩 제외)은 알 수 없으므로 원본은 원래 섹터 수 유지, 새 파일은 필요한 섹터만
    need=[(len(x)+2047)//2048 if i in newfiles else offs[i+1]-offs[i] for i,x in enumerate(data)]
    no=[0]*(n+1); cur=offs[0]
    for i in range(n):
        cur=max(cur,offs[i]); no[i]=cur; cur+=need[i]
    # 밀린 경우 원래 위치로 되돌아갈 때까지 이어짐. 끝 넘치면 실패
    no[n]=max(cur,total)
    if no[n]>total: raise ValueError('PROT overflow %d>%d'%(no[n],total))
    out=bytearray(total*2048); out[:offs[0]*2048]=d[:offs[0]*2048]
    struct.pack_into('<%dI'%(n+1),out,8,*no)
    moved=[i for i in range(n) if no[i]!=offs[i]]
    if moved: print('PROT 이동 파일',len(moved),moved[:10])
    for i in range(n):
        x=data[i]; cap=(no[i+1]-no[i])*2048
        assert len(x)<=cap,(i,len(x),cap)
        out[no[i]*2048:no[i]*2048+len(x)]=x
    return bytes(out)
