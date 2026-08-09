# 한국어 윈도우에서의 실행 — 코드페이지 옵션과 기본 실행기의 실물 (2026-08-09)

제보 두 건(`RandomObjects` NameError · `Spriteset_Map:28` NoMethodError, 둘 다 「윈도우
기본 실행기」)을 가르다 나온 조사. 결론부터: **기본 실행기는 RGSS Player가 아니라 게임이
동봉한 mkxp-z(루비 1.8.7)이고**, 우리가 지금까지 한 PC 실기 확인은 전부 **코드페이지가
UTF-8(65001)인 이 개발 기계에서만** 이뤄졌다. 보통의 한국어 윈도우(CP949)에서 이 패치가
도는지는 **아직 확인된 바 없다.**

## 1. 기본 실행기의 실물 — mkxp-z + 루비 1.8.7 (실측)

`/mnt/d/Game/Pokemon Z/V2.18/Game.exe`(11.7MB, PE32 32비트):

```
$ grep -ao "mkxp-z" Game.exe | sort -u        → mkxp-z, mkxp-z.exe
$ strings -a Game.exe | grep -o "/lib/ruby/1.8[^ ]*"   → /lib/ruby/1.8/i386-mingw32
$ file Game.exe → PE32 executable ... Intel i386
```

폴더에 남아 있는 `RGSS102E.dll`·`RGSS104E.dll`과 `Game.ini`의 `Library=RGSS104E.dll`은
mkxp-z가 안 쓰는 잔재다(mkxp-z는 스스로 RGSS 1을 흉내 낸다 — 부팅 로그 첫 줄이
`RGSS version 1 (RPG Maker XP)`).

따라오는 것 셋:

- **루비 1.8.7이므로 Z-34가 시험대에서 잡은 SyntaxError(`invalid multibyte escape`)는
  기본 실행기에서 안 난다.** 그 문법 제한은 루비 1.9부터다. 시험대에 얹은 mkxp-z는
  Pokemon Wishing Star가 싣고 있던 **루비 3.1** 빌드라, 배포판과 다른 런타임이다.
- **글자 그리기는 코드페이지와 무관하다.** mkxp-z는 제 폰트 엔진으로 UTF-8을 직접
  그린다 — RGSS Player처럼 ANSI 코드페이지를 거치지 않는다. 즉 CP949 기계에서
  한글이 깨질 걱정은 이 실행기에 한해 없다(추정 — mkxp의 텍스트 경로를 소스로
  확인하지는 않았다).
- 모바일(JoiPlay·Runa)과 데스크탑 mkxp-z는 서로 다른 런타임이다. 한쪽 관측을 다른
  쪽으로 옮기지 마라.

## 2. 이 개발 기계는 보통의 한국어 윈도우가 아니다 (실측)

```
HKLM\SYSTEM\CurrentControlSet\Control\Nls\CodePage → ACP=65001, OEMCP=65001
Get-WinSystemLocale → ko-KR
```

**「Beta: 세계 언어 지원을 위해 Unicode UTF-8 사용」이 켜져 있다.** 한국어 윈도우의
기본값은 CP949이므로, 지금까지의 「PC 실기 확인 통과」는 전부 소수파 환경의 관측이다.
제보자들은 십중팔구 CP949다.

RPG Maker 계열 커뮤니티는 이 체크박스를 **끄라고** 안내한다(RPG Maker 2000/2003 FAQ:
"Remember to uncheck the 'Beta: Use Unicode UTF-8 for worldwide language support' box",
https://hackmd.io/@Mirai/RPGMakerQA_eng). RPG Maker XP(RGSS1)를 직접 지목한 근거는
못 찾았다 — 인접 판 사례에서의 유추다.

## 3. 원작이 문서화한 오류와 해법 (실측 인용)

게임 폴더의 `1SI TIENES PROBLEMAS PARA JUGAR LEE ESTO.txt`:

> GUIA DE UNA SOLUCIÓN SI TIENES UN ERROR de Random: NameError ocurred EN PC
> 1. Ve a Panel de Control de tu PC 2. Ve a "Región" 3. Ve a la pestaña
> "Administrativo" 4. Cambia el idioma a Español para Programas no Unicode

곧 **원작이 아는 문제**이고, 해법은 비유니코드 프로그램용 언어를 스페인어로 바꾸는 것.
「Random」은 우리 제보의 `RandomObjects` 절과 같은 자리로 읽힌다.

우리 코어의 `RandomObjects`·`Spriteset_Map` 두 절은 순정 백업(`Scripts.rxdata.orig`)과
**바이트 동일**이다(대조 스크립트로 실측 — 우리가 고친 절은 34개, 이 둘은 그 안에 없다).

## 4. 시스템 로캘을 바꾸는 법 (웹 다수 사례)

Windows 11 기준, 두 경로가 같은 대화상자로 간다.

1. `Win+R` → `control` → 시계 및 지역 → 지역 → **관리** 탭 → 「시스템 로캘 변경」
2. 설정 → 시간 및 언어 → 언어 및 지역 → 관리자 언어 설정

「비 유니코드 프로그램용 언어」를 **스페인어(스페인)**로 바꾸고 **재부팅**한다(로그아웃만으론
안 된다). UAC 확인이 뜬다. 근거: Microsoft Q&A 한국어 답변
(https://learn.microsoft.com/ko-kr/answers/questions/3928171/11).

대가 — 이 설정은 **비유니코드 프로그램의 글자 표시 방식만** 바꾸지만, 그 말은 한국어
비유니코드 프로그램(옛 국산 유틸리티·설치 프로그램 등)의 글자가 깨진다는 뜻이다.

### 앱 하나에만 씌우는 우회

- **Locale Emulator** — https://github.com/xupefei/Locale-Emulator (사용법
  https://xupefei.github.io/Locale-Emulator/). 오늘날 이 계열의 사실상 표준.
  관리자 권한 요구·Defender 오탐 여부는 **미확인**.
- **NTLEA / ntleas** — 2015년 이후 개발 중단(https://en.namu.wiki/w/NTLEA). Windows 11
  지원 여부는 문서에 언급이 없다(침묵이지 부정은 아니다).
- RGSS 게임에 이 도구들을 쓴 성패 보고는 **일본어 게임을 비일본어 로캘에서 돌리는
  사례**만 찾았다(DxWnd 스레드 https://sourceforge.net/p/dxwnd/discussion/general/thread/456fe38937/
  — "RPG Maker XP/VX/VXAce shares the same engine as RGSS … they have different problem
  in non-Japanese systems"). 방향이 반대인 인접 사례다.

## 5. 기전은 아직 모른다 (미확인)

로캘이 왜 상수 로드를 깨뜨리는지 설명하는 1차 근거는 못 찾았다. 웹에서 확인되는 로캘의
영향은 **비ASCII 파일명**과 **폰트 로드**까지이고, 「로캘 불일치 → 상수 누락 → NameError」를
잇는 보고는 없다. 루비 1.8은 인코딩 개념 자체가 없어(M17N은 1.9부터) 스크립트 파싱이
코드페이지를 타지도 않는다.

한편 코드가 말하는 사슬은 확실하다(실측):

- `PSystem_System` 105~116행이 `Data/Constants.rxdata`를 읽어 각 절을 `eval`한다.
  이 로드는 `begin/rescue`로 **실패를 조용히 삼킨다**(`consts=[]`).
- 상수가 통째로 빠지면, 로드 시점 최상위에서 상수를 처음 건드리는 자리가
  `RandomObjects` 23행(`PBItems::HERRAMIENTAS`)이라 거기서 NameError로 터진다.
- `HERRAMIENTAS`는 V2.18 `Constants.rxdata`의 마지막 도구(id 948)다. 즉 **게임 본체가
  V2.18보다 낮으면** 파일이 멀쩡해도 같은 자리에서 같은 오류가 난다.

곧 「로캘」은 이 사슬을 깨뜨리는 **여러 원인 중 하나의 후보**일 뿐이다. 나머지 후보:
Constants.rxdata 자체가 없음(Data 폴더 통째 교체 — 우리 zip의 Data에는 7개 파일만 들어
있다) · 게임 본체 판 불일치.

## 6. 이 기계에서 해 본 시험 (실측)

- **한글 경로** — `D:\Game\_probe\한글경로시험` 정션으로 게임을 띄웠다. **정상 부팅**
  (40초 유지, 오류 없음). 한계 둘: 정션이라 파일시스템이 ASCII 실경로로 풀었을 수
  있고, 이 기계는 ACP 65001이다. CP949에서의 한글 경로는 여전히 미검증.
- **Constants.rxdata 제거** — 파일을 게임 폴더 밖으로 치우고 부팅했다. 우리 진단 수술이
  **그대로 작동했다**(PC 실기 첫 확인). 창 목록을 Win32로 훑어 잡은 실물:

  ```
  WIN class=#32770 title=Pokemon Z
     CHILD class=Static text="KR-PATCH DIAG: Constants.rxdata load failed -
        Errno::ENOENT: No such file or directory - Data/Constants.rxdata"
     CHILD class=Button text=OK
  ```

  알게 된 것 둘: 루비의 `p`는 mkxp-z에서 **메시지 상자**로 뜬다(표준출력·표준오류에는
  한 줄도 안 남는다 — 그래서 앞선 시도들이 「멀쩡히 도는 것」처럼 보였다). 그리고 이
  상자가 뜨는 동안 부팅이 멈추므로 **RandomObjects까지 가지도 않는다.**

  ⚠ 곧 **판별 기준이 생겼다**: v5.3(모드 v2.1) 이상을 쓰는 사람이 Constants 파일을
  잃었다면 NameError보다 **이 DIAG 상자가 먼저** 뜬다. 제보가 DIAG 없이 곧장
  `RandomObjects` NameError라면 둘 중 하나다 — ① 진단이 없던 옛 판(v5.2.1 이하)이거나
  ② **파일은 멀쩡한데 상수가 모자란 것**(게임 본체가 V2.18보다 낮아 `HERRAMIENTAS`가
  없는 경우가 여기에 해당한다).

## 7. 남은 것

- 제보자 확인 질문: 오류 전체 문구 · **「KR-PATCH DIAG」 상자가 먼저 떴는지** ·
  게임 폴더 경로에 한글이 있는지 · `Data\Constants.rxdata` 파일이 있는지 ·
  게임 본체 판 번호 · 패치 판 번호.
- **CP949 실기 시험** — Locale Emulator로 코드페이지 949를 씌워 이 게임을 띄우면
  시스템 로캘을 안 건드리고 재현을 시도할 수 있다. 도구 설치가 필요하니 유지자 판정.
- 안내문(`share/읽어주세요.txt`)에 이 오류 절을 넣을지 — 지금은 로캘 얘기가 한 줄도
  없다. 넣는다면 ① 원작 해법(로캘 스페인어) ② Data 폴더 통째 교체 금지(이미 있음)
  ③ 게임 본체 V2.18 요구를 함께 적는 꼴이 된다.

## 재현 방법 (다음 사람이 쓸 수 있게)

게임 창 뒤에 뜬 메시지 상자는 화면 갈무리로는 잘 안 잡힌다. 창을 Win32로 훑는 편이
빠르고 확실하다 — `D:\Game\_probe\probe2.ps1`이 그 스크립트다(게임을 띄우고 15초 뒤
그 PID의 창·자식 창 제목을 전부 찍은 다음 죽인다). 시험 파일을 치울 때는 **게임 폴더
밖으로** 옮겨라. 같은 폴더에 `Constants.rxdata.bak` 식으로 두면 결과가 흐려질 수 있다.
