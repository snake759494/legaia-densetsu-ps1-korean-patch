# 재빌드

번역 대본과 원문은 저장소에 없습니다. 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물

빌드 스크립트는 저장소 폴더를 작업 폴더로 씁니다. 원본 디스크와 나눔스퀘어 네오 글꼴은 **그 상위 폴더**에서 찾습니다.

```
<상위 폴더>/
  Legaia Densetsu (Japan).bin    ← README의 해시와 일치해야 함
  NanumSquareNeo-bRg.ttf  NanumSquareNeo-cBd.ttf  NanumSquareNeo-eHv.ttf
  xdelta3.exe (배포 파일을 만들 때만)
  <이 저장소>/
    fonts/Galmuri11.ttf  fonts/Galmuri9.ttf  fonts/Galmuri7.ttf
    orig/                ← 원본 디스크에서 추출 (아래 1단계)
    text/                ← 원문·번역 (저장소 미포함)
```

- Python 3.13, `numpy`, `Pillow` (`zstandard`, `capstone`은 분석용)
- 글꼴 출처는 `docs/FONT_CREDITS.md`를 참고하세요.

## 순서

모든 명령은 저장소 폴더에서 실행합니다.

1. 원본 파일 추출: `python tools/extract_orig.py "../Legaia Densetsu (Japan).bin"` → `orig/PROT.DAT`, `SCPS_100.59`, `SYSTEM.CNF`
2. 원문 추출
   - 대사: `python tools/extract.py` → `text/runs.json`, `text/locs.json`. 장 단위로 나누려면 `tools/mkbatch.py`(→ `text/ja/bNN.json`)
   - 기타 문자열: `tools/misc_extract.py`, `tools/misc2_extract.py`, `tools/chain_extract.py` → `text/misc*.json`, `tools/mkmisc.py`(→ `text/ja/mN.json`)
   - 이미지 목록: `python tools/timscan.py` → `tmp/` (그림 글자 작업용)
3. 번역 작성 (형식은 `docs/TRANSLATION_GUIDE.md`)
   - `text/ko/bNN.json`, `text/ko/mN.json` = `[{"id", "ko"}]`
   - `text/tables.json` = 기술 이름(`arts`), 적 이름(`mon`, `seru`, `sn`), 추출기 밖 문자열(`fix`, `str`)의 원문→번역 표
   - 검사: `python tools/chk.py bNN`, `python tools/chk_misc.py mN`
4. 빌드: `python tools/build.py "../Legaia Densetsu (Japan) [KOR].bin"`
5. 남은 일본어 검사: `python tools/scanjp.py "../Legaia Densetsu (Japan) [KOR].bin"`
6. 배포 파일:

```powershell
xdelta3 -e -0 -S none -A -s "Legaia Densetsu (Japan).bin" "Legaia Densetsu (Japan) [KOR].bin" LegaiaDensetsu_PS1_KO_v1.2.xdelta
```

## 화면 확인

`tools/emu.py`, `tools/play.py`, `tools/play2.py`는 DuckStation 휴대용 복사본(`duck/`)을 백그라운드로 띄웁니다. 그 상태에서 GDB 서버로 메모리를 읽고 쓰며, 키 입력과 스크린샷을 합니다. 에뮬레이터는 저장소에 넣지 않았습니다. 테스트 전에 이전에 띄운 에뮬레이터가 남아 있지 않은지 확인하세요.
