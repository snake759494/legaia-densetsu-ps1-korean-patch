# 한글패치 빌드: python tools/build.py <출력.bin>
import sys,os,json,glob,struct,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from prot import files,load
from chunks import classify,get
from lzs import comp
import pack,kfont,tim,protw
from kenc import tokens,clen,encode,ishangul
from extract import runs_of,script_chunks
from disc import Writer
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J=lambda *p: os.path.join(ROOT,*p)
EXE_ORG=0x80010000
def ea(a): return a-EXE_ORG+0x800

def load_ko():
    ko={}
    for f in sorted(glob.glob(J('text','ko','b*.json'))):
        if '_p' in os.path.basename(f): continue
        for e in json.load(open(f,encoding='utf-8')): ko[e['id']]=e['ko']
    return ko
def all_hangul(strings):
    s=set()
    for x in strings:
        for c in x:
            if ishangul(c): s.add(c)
    return sorted(s)
# 추출기가 놓친 문자열 직접 교체 (파일, 오프셋, 원문, 번역: 같은 글자 수)
# 전투 훔치기 메시지(exe): (주소, 칸 바이트, 번역)
STEAL=[(0x69ed9,51,'훔쳐 간 「'),(0x69f0c,20,'」 손에 넣었다!'),(0x69f21,43,'도둑맞은 「'),(0x69f4c,28,'」 되찾았다!'),
       (0x69f69,39,'적이 가진 「'),(0x69f90,20,'」 훔쳤다!'),(0x69fa5,42,'훔쳐 간 아이템을 전부 되찾았다!')]
import rawtxt,mon
RAWFIX=[(901,0x17699,'火','화'),(901,0x1769d,'風','풍'),(901,0x176a1,'雷','뇌')]
def make_kmap(syl):
    idxs=[i for i in range(1600)]+[i for i in range(1694,1694+1600)]
    assert len(syl)<=len(idxs),len(syl)
    return {c:kfont.idx2code(idxs[i]) for i,c in enumerate(syl)},{c:idxs[i] for i,c in enumerate(syl)}

def fit_run(ja_lines,ko_lines,center=False):
    L=[clen(x) for x in ja_lines]; T=sum(L)
    K=[tokens(x) for x in ko_lines]
    S=sum(len(k) for k in K); assert S<=T,(ja_lines,ko_lines)
    P=T-S; mx=max(len(k) for k in K)
    out=[list(k) for k in K]
    # 1) 줄을 현재 최대 폭까지
    for k in out:
        while P and len(k)<mx: k.append('　'); P-=1
    # 2) 나머지는 마지막 줄
    out[-1]+=['　']*P
    if center:
        out=[]
        for k,l in zip(K,L): out.append(k)
        # 중앙 정렬: 각 줄 원래 길이 기준 앞뒤 분배 (원문 길이 l에 맞춤 가능할 때)
        rem=T-S; res=[]
        for k,l in zip(K,L):
            pad=max(0,min(l-len(k),rem)); rem-=pad
            res.append(['　']*(pad//2)+list(k)+['　']*(pad-pad//2))
        res[-1]+=['　']*rem; out=res
    return [''.join(x) for x in out]

def build(outbin):
    R={r['id']:r for r in json.load(open(J('text','runs.json'),encoding='utf-8'))}
    locs=json.load(open(J('text','locs.json')))
    ko=load_ko()
    import misc,arts
    extra=misc.strings()+['반노아가라테라',misc.NAME1,misc.NAME2]+[k for _,_,_,k in RAWFIX]+[t for _,_,t in STEAL]+rawtxt.strings()+mon.strings()+arts.strings()
    syl=all_hangul([l for v in ko.values() for l in v]+extra)
    kmap,kidx=make_kmap(syl)
    json.dump({c:'%04x'%v for c,v in kmap.items()},open(J('text','kmap.json'),'w',encoding='utf-8'),ensure_ascii=False)
    print('한글 음절',len(syl))
    fs=files(); new={}
    # --- 대사 ---
    byfile={}
    for k,ci,off,rid in locs: byfile.setdefault((k,ci),[]).append((off,rid))
    chunk_new={}; bad=set()
    for k,kind,ci,d in script_chunks(fs):
        reps=byfile.get((k,ci),[])
        d=bytearray(d); changed=False
        runs={r[0][0]:r for r in runs_of(bytes(d))}
        for off,rid in reps:
            if rid not in ko: continue
            r=runs[off]; ja=R[rid]['ja']
            if len(ko[rid])!=len(ja) or sum(clen(x) for x in ko[rid])>sum(clen(x) for x in ja):
                bad.add(rid); continue
            lines=fit_run(ja,ko[rid],center=(k==751))
            for (j,n),line in zip(r,lines):
                b=encode(line,kmap); n2=len(b)//2
                # 줄 길이 재배분: 길이 바이트 갱신
                pass
            # 연속 재기록
            pos=r[0][0]; buf=bytearray()
            for line in lines:
                b=encode(line,kmap); buf.append(len(b)//2); buf+=b
            end=r[-1][0]+1+2*r[-1][1]
            assert len(buf)==end-pos,(rid,len(buf),end-pos,k,ci,off,lines,[encode(l,kmap).hex() for l in lines])
            if d[pos:end]!=buf: d[pos:end]=buf; changed=True
        if changed: chunk_new[(k,ci)]=bytes(d)
    if bad: print('제약 위반으로 건너뜀',len(bad),sorted(bad)[:20])
    # --- 이미지 속 일본어 ---
    import imgpatch
    rawtxt.apply(fs,new,kmap)
    mon.patch(fs,new,kmap)
    rawimg={}
    for src,o,fn in imgpatch.PATCHES:
        if '.' in src:
            k,ci=map(int,src[1:].split('.')); f=fs[k]; kind,ents=classify(f)
            base=chunk_new.get((k,ci)) or get(f,kind,*ents[ci])
            chunk_new[(k,ci)]=imgpatch.patch_bytes(base,o,fn)
        else:
            k=int(src[1:]); rawimg[k]=imgpatch.patch_bytes(rawimg.get(k,fs[k]),o,fn)
    for src,o,w,h,fn in imgpatch.RAWPATCHES:
        k,ci=map(int,src[1:].split('.')); f=fs[k]; kind,ents=classify(f)
        base=chunk_new.get((k,ci)) or get(f,kind,*ents[ci])
        chunk_new[(k,ci)]=imgpatch.patch_raw(base,o,w,h,fn)
    print('이미지 수정',len(imgpatch.PATCHES)+len(imgpatch.RAWPATCHES))
    for k in sorted(set(k for k,ci in chunk_new)):
        f=fs[k]; kind,ents=classify(f)
        if kind=='raw':
            b=bytearray(f)
            for ci,(t,s,o) in enumerate(ents):
                if (k,ci) in chunk_new: b[o:o+s]=chunk_new[(k,ci)]
            new[k]=bytes(b)
        else:
            ch=[]
            for ci,(t,s,o) in enumerate(ents):
                end=ents[ci+1][2] if ci+1<len(ents) else None
                if (k,ci) in chunk_new: ch.append((t,chunk_new[(k,ci)],None))
                else:
                    raw=get(f,kind,t,s,o)
                    if end is None:
                        # 마지막 청크: 압축 길이 계산 위해 재압축 대신 원본 끝까지(패딩 제외) 사용 시도
                        from lzs import decomp
                        _,e2=decomp(f,s,o); ch.append((t,raw,f[o:e2]))
                    else: ch.append((t,raw,f[o:end]))
            new[k]=pack.build(ch,comp)
    new.update(rawimg)
    # --- 글꼴 ---
    font_tims(fs,new,kmap,kidx)
    # --- 기타 텍스트 / exe ---
    exe=bytearray(open(J('orig','SCPS_100.59'),'rb').read())
    battle_font(fs,new,exe,kmap)  # 전투(글자 모드 12)는 기본 글꼴만 씀 → 한글을 기본 글꼴에 배치
    misc.apply(fs,new,exe,kmap)
    misc.apply2(fs,new,exe,kmap)
    from kenc import encode as _enc
    for a,cap,t in STEAL:
        b=_enc(t,kmap); assert len(b)<cap,(hex(a),t); exe[a:a+cap]=b+bytes(cap-len(b))
    arts.patch(fs,new,kmap)
    misc.name_tables(fs,new,kmap)
    for f,off,ja,ko in RAWFIX:
        b=bytearray(new.get(f,fs[f])); jb=ja.encode('cp932'); kb=encode(ko,kmap)
        assert b[off:off+len(jb)]==jb and len(kb)==len(jb),(f,off,ko)
        b[off:off+len(jb)]=kb; new[f]=bytes(b)
    P=protw.rebuild(new)
    shutil.copy(J('..','Legaia Densetsu (Japan).bin'),outbin)
    w=Writer(outbin)
    n1=w.patch('/PROT.DAT',P,open(J('orig','PROT.DAT'),'rb').read())
    n2=w.patch('/SCPS_100.59',bytes(exe),open(J('orig','SCPS_100.59'),'rb').read())
    cue=os.path.splitext(outbin)[0]+'.cue'
    open(cue,'w').write('FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'%os.path.basename(outbin))
    print('sectors',n1,n2,'files',len(new))

def font_tims(fs,new,kmap,kidx):
    from PIL import ImageFont
    font=ImageFont.truetype(kfont.FONT,12)
    f=bytearray(new.get(894,fs[894])); offs=[]
    for o in (0xc,0x822c):
        cl=struct.unpack_from('<I',f,o+8)[0]; offs.append(o+8+cl+12)
    orig=[bytes(f[o:o+0x8000]) for o in offs]
    tims=[bytearray(x) for x in orig]
    for c,i in kidx.items(): kfont.put_full(tims,i,kfont.glyph(c,font))
    for o,t in zip(offs,tims): f[o:o+0x8000]=t
    new[894]=bytes(f)
    g=fs[876]; kind,ents=classify(g); ch=[]
    for ci,(t,s,o) in enumerate(ents):
        x=bytearray(get(g,kind,t,s,o)); end=ents[ci+1][2] if ci+1<len(ents) else None
        o0=x.find(orig[0]); o1=x.find(orig[1])
        if o0>=0 and o1>=0:
            x[o0:o0+0x8000]=tims[0]; x[o1:o1+0x8000]=tims[1]; ch.append((t,bytes(x),None))
        else:
            if end is None:
                from lzs import decomp
                _,e2=decomp(g,s,o); ch.append((t,bytes(x),g[o:e2]))
            else: ch.append((t,bytes(x),g[o:end]))
    new[876]=pack.build(ch,comp)

def base_put(f,pix,plane,idx,ink):
    r=idx%100; v=(idx//100)*64+(r//20)*12; u=((r%20)//5)*64+(r%5)*12
    sh=plane*2
    def setp(x,y,val):
        o=pix+(v+y)*128+(u+x)//2; s4=4 if (u+x)&1 else 0
        cur=(f[o]>>s4)&15; cur=(cur&~(3<<sh))|(val<<sh)
        f[o]=(f[o]&~(15<<s4)&0xff)|(cur<<s4)
    for y in range(12):
        for x in range(12): setp(x,y,0)
    S=set(ink)
    for x,y in ink: setp(x,y,3)
    for x,y in ink:
        for dx,dy in ((1,0),(1,1)):
            if (x+dx,y+dy) not in S and x+dx<12 and y+dy<12: setp(x+dx,y+dy,2)
def base_font(fs,new):
    import gfx
    f=bytearray(gfx.patch(new.get(0,fs[0]))); pix=0x6774
    base_put(f,pix,0,0,[(2,8),(2,9),(1,10)])   # 、 → ,
    base_put(f,pix,0,1,[(2,9),(2,10)])          # 。 → .
    new[0]=bytes(f)

def battle_chars():
    # 전투 중 표시될 수 있는 문자열: 실행파일·전투 파일(895~982) 기타 문자열, 기술·적 이름, 전투 메시지, 이름 입력 음절
    import misc,arts
    H=lambda t:{c for c in t if ishangul(c)}
    ja={};ko={};S=set()
    for f in glob.glob(J('text','ja','m*.json')):
        for e in json.load(open(f,encoding='utf-8')): ja[e['id']]=e
    for f in glob.glob(J('text','ko','m*.json')):
        for e in json.load(open(f,encoding='utf-8')): ko[e['id']]=e['ko']
    for i,e in ja.items():
        src=e['src'] if isinstance(e['src'],list) else [e['src']]
        if any(x=='exe' or (x.startswith('f') and 895<=int(x[1:])<=982) for x in src): S|=H(ko.get(i,''))
    for v in list(arts.T.values())+mon.strings()+rawtxt.strings()+[t for *_,t in STEAL]+[misc.NAME1,misc.NAME2,'반노아가라']: S|=H(v)
    return S
BASE_TAB=0x80075780  # 기본 글꼴 코드 표(정렬, 400 + 376): 앞 400 = 평면0, 뒤 376 = 평면1
def battle_font(fs,new,exe,kmap):
    from PIL import ImageFont
    o=ea(BASE_TAB); old=[exe[o+2*i]<<8|exe[o+2*i+1] for i in range(776)]
    keep=[c for c in old if c<0x889f]       # 기호·영숫자·가나
    kor=sorted(kmap[c] for c in battle_chars())
    nk=776-len(kor); assert nk>=61,len(kor)  # 기호 61개는 반드시 유지
    tab=keep[:nk]+kor; assert tab==sorted(tab) and len(set(tab))==776
    for i,c in enumerate(tab): exe[o+2*i]=c>>8; exe[o+2*i+1]=c&255
    import gfx
    f=bytearray(gfx.patch(new.get(0,fs[0]))); pix=0x6774
    base_put(f,pix,0,0,[(2,8),(2,9),(1,10)])   # 、 → ,
    base_put(f,pix,0,1,[(2,9),(2,10)])          # 。 → .
    font=ImageFont.truetype(kfont.FONT,12); inv={v:k for k,v in kmap.items()}
    for i in range(nk,776):
        g=kfont.glyph(inv[tab[i]],font)
        base_put(f,pix,0 if i<400 else 1,i%400,[(x,y) for y in range(12) for x in range(12) if g[y][x]])
    new[0]=bytes(f)
    print('전투 글꼴 한글',len(kor),'가나 유지',nk-61)

if __name__=='__main__': build(sys.argv[1])
