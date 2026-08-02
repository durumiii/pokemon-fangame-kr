# Pokémon Z Fangame — 게임 해부 핸드오프

> 2026-08-01, fangame-library 세션의 Claude가 작성해 넘긴다. 이 게임의 코딩·모딩은
> 앞으로 poke-essentials에서 진행하기로 했다(사용자 결정). 아래는 라이브러리에 들이는
> 과정에서 실측으로 알아낸 것들이고, 근거의 등급(실측/추정)을 문장에 붙였다.
> 원 기록은 `../../fangame-library/docs/CHANGELOG.md`의 2026-08-01 절.

## 신원

- 정식 이름 **Pokémon Z Fangame**(사용자 확인). 스페인어권 제작, 공식 배포처
  https://pokemonzfangame.com — 첫 화면 `og:title`이 현재 판을 실어 준다
  (`Pokemon Z v2.18 - RPGXP Fangame for PC`, 실측). fangame-library의 `pokemonz.py`가
  이 자리만 읽어 새 판을 감시한다.
- 설치: `D:\Game\Pokemon Z\V2.18`(정본) · `V2.18 한글패치 v3`(중복 확인용, 지워도 되는 상태).
  `Game.ini`의 `Title=Pokémon Z Fangame`이 라이브러리·모드·배포처 표의 열쇠다.
  é가 CP949에 없어 **Game.ini는 UTF-8**이다(옛 RGSS 창 제목만 그 두 글자가 어색할 수 있다).

## 엔진 — 여기가 제일 중요하다

**PC의 `Game.exe`는 원본 RGSS가 아니라 이름만 바꾼 mkxp-z 구판이다**(실측 — 바이너리
문자열에 `mkxp-z`·`mkxp.json`·fluidsynth 폴백 문구). 내장 루비는 **1.8.7**
(`/lib/ruby/1.8/i386-mingw32`, 32비트 PE). 함의:

- 폴더의 `RGSS102E/102J/104E.dll`은 장식이다 — mkxp는 안 쓴다.
- `mkxp.json`이 PC 실행의 실제 설정이다(글꼴 치환 `fontSub`, `smoothScaling` 등).
  `$MKXP`가 참이라 스크립트의 Win32 우회 코드(`Sprite_Resizer` 등)는 `if !$MKXP`로 죽어 있다.
- `preload.rb`는 `Zlib`을 `MKXP.zinflate`로 돌리는 조이플레이용 봉합이다. **mkxp-z 본가에는
  zinflate가 없고**(소스 전수 grep 0건), preload는 `preloadScript` 키에 명시해야만 돈다 —
  PC에서는 안 물려 있고 그게 맞다.
- 함께 있는 DLL 다섯(rgssdisp·rubyscreen·KleinBitmap·gif·fluidsynth) 중 **부팅 필수는
  없다**(전부 lazy·`safeExists?`·`$MKXP` 가드, 실측). gif.dll의 실사용처는
  `Graphics/Pictures/evolutionbg.gif` 한 장. fluidsynth는 mkxp가 스스로 로드하며 실패해도
  "MIDI만 끔". BGM은 전부 .ogg라 실질 무관.

**스크립트는 구형 Essentials다.** `Data/Scripts.rxdata` 한 덩어리(스크립트 255개,
511만 자)에 전부 들어 있고 **플러그인 묶음(`PluginScripts.rxdata`)이 없다.** 그리고
**루비 1.8 전용 구문(`when x:` 콜론형)이 531곳**이다(실측) — 루비 3.1로 고정된 최신
mkxp-z 기성 빌드로는 파싱조차 안 된다. 조이플레이의 「Ruby 1.8 사용」 토글이 필수인
이유이자, 이 게임의 실행기를 함부로 갈 수 없는 이유다.

## 모딩의 지형

- **코드 수정 = 코어 통째 교체다.** 소원의별처럼 플러그인을 얹는 길이 없다. 코드 모드
  여럿의 합성은 지금 구조로는 안 되고, 필요해지면 `Scripts.rxdata`(Marshal 배열
  `[id, 제목, zlib(소스)]`)에 **항목을 덧붙이는** 길이 열려 있다 — RGSS는 배열 순서대로
  실행해 나중 정의가 이긴다. 아직 수요가 없어 안 만들었다(비용으로 적어 둔 상태).
  Marshal 판독·기록은 fangame-library의 `rubyread`/`rubywrite`가 이미 한다(루비가 세는
  대로 번호를 매길 것 — 그쪽 AGENTS의 함정 참조).
- **한글패치는 fangame-library의 「한글패치 통합」 모드가 정본이다**
  (`D:\GameVault\mods\한글패치 통합\`, 파일 182개). 한글패치 v3 + 갤러리 통파일(글 223917,
  몬볼 그래픽·울음소리 손질) + 배틀 버튼 한글화(글 223597)를 원본 V2.18과 전수 대조해
  합친 것. 스크립트 없는 **에셋 전용 모드**라 설치·제거·백업(`.orig`)·호환 검사
  (`replaces_crc` — 덮을 자리의 원본 지문 대조)를 라이브러리가 맡는다. **이 게임을 고칠 때는
  게임 폴더를 직접 고치지 말고 이 모드(보관소)를 고쳐 재설치하는 흐름을 지킬 것** —
  poke-essentials의 modding-runbook과 같은 원칙이고, 갈리는 것은 수확 형태(플러그인이
  아니라 파일)뿐이다.
- `Data/Constants.rxdata`(PBS 컴파일 캐시, 여섯 절의 도장만 변함)와 `MapChecker.dat`
  (맵 시각 목록 508칸)는 **게임이 스스로 다시 굽는 캐시**다(Marshal 열어 실측) — 패치에
  담지 말 것.
- 한글 텍스트의 정본은 `Data/korean.dat`(4.5MB)이고 타이틀 [Idioma]로 스페인어 원문
  전환이 된다(한글패치 안내문). 판독 대상으로 유망하다 — **아직 안 열어 봤다.**

## 화면·폰트 (해결된 상태)

- 4K 뭉개짐은 둘이었다: Game.exe 매니페스트 부재로 인한 DPI 가상화(레지스트리
  `HIGHDPIAWARE` 재정의로 해결, HKCU AppCompatFlags\Layers에 두 버전 폴더 등록됨)와
  mkxp의 확대 보간(`mkxp.json`에 `"smoothScaling": false` — 이 구판은 불리언 세대,
  `integerScaling` 키는 바이너리에 없다).
- 폰트는 **갈무리9의 0.72배 재구움판으로 확정**(사용자 확인). 법칙 둘 — 원래 DPPt풍
  폰트는 한글이 2,355자뿐이라 빈 네모 결함이 있었고, 갈무리 계열은 em 비율이 45% 커서
  그대로는 잘리고 줄이면 얇아진다. **크기는 배율이, 굵기는 격자가 정한다**(픽셀 한 칸:
  옛 DPPt 0.0625em, 갈무리14@0.72 0.048, 갈무리9@0.72 0.072). 재구움은 fontTools
  `scale_upem`으로 줄이고 upem만 원복 — 좌표가 픽셀 격자 정수라 무손실. 갈무리11·14
  재구움판과 Neo둥근모가 Fonts/에 동봉돼 있어 `fontSub` 한 줄로 갈아탄다.
  **게임이 떠 있으면 기존 폰트 파일이 잠긴다**(새 파일 추가는 됨) — 교체는 종료 후.

## 경계 (누가 무엇을 맡나)

fangame-library가 게임·버전·세이브·모드 **보관**을 맡고(지문·백업·배포처 감시 포함),
poke-essentials가 게임 **내용**(데이터 판독·개조 설계)을 맡는다 — 기존 경계 그대로다.
이 게임에서 새로 생길 일(korean.dat 판독, Scripts.rxdata 개조, 구문 변환 실험)은 여기
poke-essentials에서 하되, 산출물을 게임에 앉힐 때는 위 「한글패치 통합」 모드 흐름을 탄다.

주의: 이 게임의 데이터 판독은 Wishing Star와 다를 수 있다 — 구형 Essentials라
`.dat` 대신 `.rxdata` 세대이고 PBS 캐시 구조(`Constants.rxdata`)도 신형과 다르다.
기존 판독기를 그대로 들이대기 전에 세대 차이부터 잴 것.
