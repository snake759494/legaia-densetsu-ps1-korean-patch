import struct,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p=os.path.join(ROOT,'orig','PROT.DAT')):
    d=open(p,'rb').read()
    n=struct.unpack_from('<I',d,4)[0]
    offs=struct.unpack_from('<%dI'%(n+1),d,8)
    return d,n,offs
def files(d=None):
    if d is None: d,n,offs=load()
    else: n=struct.unpack_from('<I',d,4)[0]; offs=struct.unpack_from('<%dI'%(n+1),d,8)
    return [d[offs[i]*2048:offs[i+1]*2048] for i in range(n)]
