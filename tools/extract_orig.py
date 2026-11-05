import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
d=Disc(sys.argv[1]); out=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'orig')
for p,l,sz,_,_ in d.walk():
    if p in('/SCPS_100.59','/PROT.DAT','/SYSTEM.CNF','/CDNAME.TXT'):
        open(os.path.join(out,p[1:]),'wb').write(d.read(l,sz))
