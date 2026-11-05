import sys,os,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu import Emu
cue=sys.argv[1]; e=Emu(cue)
try:
    for t in range(int(sys.argv[2]) if len(sys.argv)>2 else 6):
        time.sleep(8); print(e.shot('tmp/b%02d.png'%t))
finally: e.close()
