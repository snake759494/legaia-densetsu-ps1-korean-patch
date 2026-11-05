# 백그라운드 실행 + 긴 시퀀스용 (play.py와 동일, 시작 상태를 슬롯 파일로)
import sys,os,runpy
sys.argv=[sys.argv[0]]+sys.argv[1:]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'play.py'),run_name='__main__')
