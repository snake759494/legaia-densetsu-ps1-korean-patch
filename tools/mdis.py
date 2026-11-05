import sys,capstone,struct
d=open(sys.argv[3] if len(sys.argv)>3 else 'orig/SCPS_100.59','rb').read()
ORG=0x80010000
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
def dis(addr,n):
    off=addr-ORG+0x800
    for i in md.disasm(d[off:off+n*4],addr): print(hex(i.address),i.mnemonic,i.op_str)
if __name__=='__main__': dis(int(sys.argv[1],16),int(sys.argv[2]))
