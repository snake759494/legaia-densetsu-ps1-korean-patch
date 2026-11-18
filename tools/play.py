# usage: play.py state|- "seq" outprefix [cue]
# tokens: Maddr:hex RAM write, wN sleep, S shot, SAVE savestate(slot1), Dfile RAM dump, hK:sec hold, other=key press
import sys,time,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from emu import Emu,hold
st=None if sys.argv[1]=='-' else sys.argv[1]
cue=sys.argv[4] if len(sys.argv)>4 else '../Legaia Densetsu (Japan).cue'
e=Emu(cue,state=st); time.sleep(2)
n=0
try:
  for tok in sys.argv[2].split():
    if tok.startswith('w'): time.sleep(float(tok[1:]))
    elif tok=='S': e.shot(f'{sys.argv[3]}{n}.png'); n+=1
    elif tok=='SAVE':
        sv='duck/savestates/SCPS-10059_1.sav'; t0=os.path.getmtime(sv) if os.path.exists(sv) else 0
        for _ in range(6):
            e.savestate(); time.sleep(2.5)
            if os.path.exists(sv) and os.path.getmtime(sv)>t0: break
        print('saved')
    elif tok.startswith('M') and ':' in tok:
        a,h=tok[1:].split(':'); e.write(int(a,16),bytes.fromhex(h))
    elif tok.startswith('D'): open(tok[1:],'wb').write(e.read(0x80000000,0x200000))
    elif tok.startswith('h') and ':' in tok:
        k,sec=tok[1:].split(':'); hold(e,k,float(sec))
    elif '*' in tok:
        k,c=tok.split('*')
        for _ in range(int(c)): e.key(k); time.sleep(0.25)
    else: e.key(tok); time.sleep(0.3)
finally: e.close()
