# 이미지(TIM) 속 일본어 글자 한글화: 위치(파일.청크, TIM 오프셋) → 수정 함수
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import tim,staff
from imgutil import indices,pack_ix,draw,font,textmask,dil
import numpy as np
G='Galmuri11.ttf'
def p33(ix):
    for r,s in [((16,29,1,78),'와일드 선언'),((32,45,4,72),'펀치다!!'),((48,61,4,72),'킥이다!!'),((48,61,162,251),'보너스 게임'),
                ((64,77,1,78),'와일드 선언'),((80,93,2,88),'펀치 리치!'),((97,109,2,88),'킥 리치!'),
                ((164,175,1,78),'게임 계속'),((179,191,1,79),'게임 그만두기'),((196,209,0,47),'조작 설명')]:
        draw(ix,r,s,G,12,bold=True)
def p59(ix): draw(ix,(4,60,2,214),'무투회','NanumSquareNeo-eHv.ttf',56,mode='tex',outline=False,bold=True)
def p1816(ix):
    draw(ix,(98,109,129,173),'저주',G,12,bg=13,bold=True,outline=False,align='center')
    draw(ix,(122,133,141,160),'저주','Galmuri7.ttf',8,bg=13,outline=False,align='center')
    draw(ix,(138,149,139,173),'저주',G,12,bg=13,bold=True,outline=False,align='center')
    y0,y1,x0,x1=96,119,74,111; ix[y0:y1+1,x0:x1+1]=0
    for (a,b),ch in (((97,108),'곰팡'),((108,119),'이')):
        m=textmask(ch,font(G,12)); m=m|np.pad(m,((0,0),(1,0)))[:,:-1]
        H=b-a+1; Wd=x1-x0+1; M=np.zeros((H,Wd),bool); oy=(H-m.shape[0])//2; ox=(Wd-m.shape[1])//2
        M[oy:oy+m.shape[0],ox:ox+m.shape[1]]=m
        O=dil(M)&~M; reg=ix[a:b+1,x0:x1+1]; reg[O&(reg==0)]=13; reg[M]=15
STAFFLOC={1744:('f783.0',90192),1745:('f783.0',92816),1746:('f783.0',95440),1747:('f783.0',98064),1748:('f783.0',103248),
 1751:('f788.0',138452),1752:('f788.0',141076),1768:('f798.0',82684),1769:('f798.0',109372),1771:('f798.0',123836),
 1777:('f798.0',173372),1786:('f803.0',140208),1787:('f803.0',142832),1788:('f803.0',145456),1789:('f803.0',151920),
 1792:('f808.0',64304),1793:('f808.0',68208),1794:('f808.0',70832),1795:('f813.0',76072),1796:('f813.0',81256),
 1801:('f818.0',125928),1802:('f818.0',128552),1803:('f818.0',133736),1806:('f823.0',159260),1807:('f823.0',161884),1808:('f828.0',104400)}
PATCHES=[('f1202.0',99960,p33),('f1222.0',33324,p59),('f872',66640,p1816)]
for n,(src,o) in STAFFLOC.items(): PATCHES.append((src,o,lambda ix,n=n: staff.apply(n,ix)))
def patch_bytes(d,o,fn):
    d=bytearray(d); t=tim.parse(bytes(d),o); ix=indices(t); fn(ix); nb=pack_ix(t,ix)
    p=bytes(d).find(t['pix'],o); assert p>=0 and len(nb)==len(t['pix'])
    d[p:p+len(nb)]=nb; return bytes(d)
