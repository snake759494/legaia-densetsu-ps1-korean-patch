# 레전드 오브 레가이아 PS1 한글패치

PS1 일본판 **レガイア伝説 (Legaia Densetsu, SCPS-10059)**용 비공식 한국어 패치입니다. 필드와 이벤트의 **대사·선택지**를 모두 한국어로 옮겼습니다. **메뉴, 아이템·장비·마법, 전투 메시지, 필살기 이름, 적 이름, 미니게임, 튜토리얼**도 한국어로 바꿨습니다. **전투 UI 라벨, 슬롯머신, 「무투회」 타이틀, 스태프롤 같은 그림 글자**는 한글로 다시 그렸습니다. 현재 배포판은 **v1.4 (2026-11-19)**입니다.

[패치 다운로드](https://github.com/snake759494/legaia-densetsu-ps1-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈에는 한글패치 **LegaiaDensetsu_PS1_KO_v1.4.xdelta** 하나만 첨부합니다. 저장소에는 제작 도구와 기술 문서만 공개합니다. 다음은 포함하지 않습니다.

- 원본·완성 디스크 이미지와 추출한 게임 파일
- 일본어 원문과 번역 대본
- 글꼴 파일과 외부 실행 파일

GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며, 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『レガイア伝説』는 소니 컴퓨터 엔터테인먼트가 1998년에 PS1으로 낸 RPG입니다. 사람을 미치게 하는 〈안개〉에 뒤덮인 세계에서, 림 엘름 마을의 소년 반이 〈라 세루〉와 함께 〈안개〉를 걷어 내려고 여행을 떠납니다. 방향키 입력을 조합해 필살기를 만드는 전투 시스템이 특징입니다.

이 패치는 **PS1 일본판 SCPS-10059의 BIN/CUE 이미지(단일 트랙, MODE2/2352)**에만 적용됩니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SCPS-10059 |
| 원본 형식 | 수정되지 않은 일본판 BIN/CUE (트랙 1개) |
| 원본 BIN 크기 | 467,443,536 바이트 |
| **원본 BIN MD5** | `e6cb8e42797aea85c0771044db12d575` |
| 원본 BIN SHA-1 | `49440bc2b060fe54079253f8e309abd54100278a` |
| 원본 BIN SHA-256 | `b0d18d8fd3b414c7c040ff9cfaf71955831c557e0122dc0dd620b683543e216c` |
| xdelta 파일 크기 | 13,269,972 바이트 |
| xdelta SHA-256 | `8a5ccff2a61279cfbe868c76135deb4e88860573281784f85745bb030888b041` |
| 적용 결과 BIN 크기 | 467,443,536 바이트 (원본과 같음) |
| 적용 결과 BIN SHA-1 | `a6320d979660f37a54061f5bb4e083dcdf31150e` |
| 적용 결과 BIN SHA-256 | `a8a35607e09b795ee1c9928f7ba6e3c6f265d7148decdc2d3427fe039ff4fb0a` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Legaia Densetsu (Japan).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, PBP, ECM, 압축 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `LegaiaDensetsu_PS1_KO_v1.4.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Legaia Densetsu (Korean).bin`).
5. 원본 `.cue`를 복사해 결과 BIN과 같은 이름으로 바꿉니다. 그리고 안의 `FILE "..."` 줄을 결과 BIN 파일 이름으로 고칩니다.

```
FILE "Legaia Densetsu (Korean).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
```

xdelta 파일은 호환성을 위해 압축, 2차 압축, 파일 경로 헤더를 모두 빼고 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Legaia Densetsu (Japan).bin' '.\LegaiaDensetsu_PS1_KO_v1.4.xdelta' '.\Legaia Densetsu (Korean).bin'
```

해시 검사와 CUE 생성까지 자동으로 해 주는 도구도 있습니다. Python 3과 xdelta3가 필요합니다. 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Legaia Densetsu (Japan).bin' --patch '.\LegaiaDensetsu_PS1_KO_v1.4.xdelta' --output '.\Legaia Densetsu (Korean).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(실행파일과 데이터가 다릅니다). 메모리 카드 세이브는 원본판과 형식이 같아 그대로 쓸 수 있을 것으로 봅니다. 다만 직접 확인하지는 못했습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 대사 | 필드·이벤트 대사와 선택지 런 11,456개(약 26,700줄) |
| 짧은 문자열 | 메뉴·아이템·장비·마법·전투 메시지·미니게임 등 약 1,600개 |
| 전투 | 필살기 이름 62개, 적 이름 186개(압축 데이터 안)<br>훔치기 메시지, 보스 대사, 필살기 습득·소환 레벨 상승 알림, 전투 튜토리얼 |
| 글꼴 | 갈무리11 한글 1,162자(게임 한자 글꼴 영역에 배치)<br>전투용 기본 글꼴에 전투 문자열·이름 입력 음절 660자 별도 배치 |
| 그림 글자 | 전투 UI 상태 이상·장비 라벨<br>슬롯머신 화면, 「무투회」 타이틀, 상태 이상 아이콘<br>스태프롤 26장(직책·캐릭터 이름·회사 이름) |

게임 데이터 대부분이 들어 있는 `PROT.DAT`는 청크마다 LZSS로 압축되어 있습니다. 번역을 넣고 다시 압축해서 커진 파일은 뒤 파일들을 밀어 배치하고 TOC를 고쳤습니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다(`docs/TRANSLATION_GUIDE.md`).
- 원문 자리에 덮어쓰는 방식이라, 글자 수와 줄 폭에 맞춰 간결하게 의역했습니다.
- 인명·지명은 원문 발음을 따르되 널리 쓰이는 표기를 썼습니다(반, 노아, 가라, 〈세루〉, 〈안개〉, 림 엘름 등).

### 번역하지 않은 것

- 음성과 무비
- 제작사 로고·저작권 표기
- 스태프롤의 실명
- 화면에 나오지 않는 스크립트 디버그 라벨, 사운드 테스트 메뉴 일부, 이름 입력 원본 표(전투용 글꼴에 한글 자리를 만들려고 가나 일부를 뺐기 때문에, 남은 일본어 문구는 일부 글자가 비어 보일 수 있습니다)

## 알려진 한계

- 모든 화면을 직접 확인하지는 못했습니다. 프롤로그, 이름 입력, 선택지, 대화창, 메뉴는 에뮬레이터로 확인했고 잘리는 곳이 없었습니다. 전투용 글꼴은 대화창을 전투 글자 모드로 바꿔 확인했고, 실제 전투 화면은 아직 직접 보지 못했습니다. 칸을 넘치거나 어긋난 문구가 있으면 이슈로 알려 주세요.
- 원문 자리에 덮어쓰므로, 몇몇 문장은 원문보다 짧게 줄였습니다.
- 인게임 확인은 DuckStation으로 했습니다. 실기에서의 동작은 확인하지 못했습니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/build.py` | 전체 빌드(대사·기타 문자열 교체, 글꼴, 실행파일, 그림 글자, PROT.DAT 재구성, 디스크 기록) |
| `tools/prot.py`, `tools/pack.py`, `tools/chunks.py`, `tools/protw.py`, `tools/lzs.py` | PROT.DAT 읽기·청크·LZSS·재배치 |
| `tools/kfont.py`, `tools/kenc.py` | 한글 글꼴 코드 배정과 문자열 인코딩 |
| `tools/misc.py`, `tools/rawtxt.py`, `tools/arts.py`, `tools/mon.py` | 기타 문자열, 추출기 밖 문자열, 필살기 이름, 적 이름 |
| `tools/gfx.py`, `tools/imgpatch.py`, `tools/staff.py`, `tools/imgutil.py`, `tools/tim.py` | 그림 글자 다시 그리기 |
| `tools/disc.py`, `tools/iso.py`, `tools/cdsec.py` | 디스크 섹터 교체와 EDC/ECC 재계산 |
| `tools/extract_orig.py`, `tools/extract.py`, `tools/*_extract.py`, `tools/sstr.py`, `tools/nscan.py`, `tools/zscan.py` | 원본 파일과 원문 추출 |
| `tools/chk.py`, `tools/chk_misc.py`, `tools/scanjp.py`, `tools/uncovered.py` | 번역 검사와 남은 일본어 전수 조사 |
| `tools/apply_release.py` | 해시 검사 후 적용 |
| `tools/emu.py`, `tools/play.py`, `tools/play2.py`, `tools/boot.py` | DuckStation 테스트 조작 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처, 번역 지침 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
