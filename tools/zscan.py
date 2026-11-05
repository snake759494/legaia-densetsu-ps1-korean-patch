# 널 종료 SJIS 문자열 탐지 (앞이 00 이거나 시작, 뒤 00)
import re
CH=rb'(?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc])'
PAT=re.compile(rb'(?<=\x00)'+CH+rb'+(?=\x00)')
def zscan(d,minc=1):
    out=[]
    for m in PAT.finditer(d):
        s=m.group()
        try: t=s.decode('cp932')
        except UnicodeDecodeError: continue
        if len(t)<minc: continue
        out.append((m.start(),len(s),t))
    return out
def plausible(t):
    import unicodedata
    good=sum(1 for c in t if '぀'<=c<='ヿ' or c in '　、。！？…ー・（）「」＋－％０１２３４５６７８９ＨＰＭＧ' or 'Ａ'<=c<='Ｚ')
    return good>=max(1,len(t)*0.3)
