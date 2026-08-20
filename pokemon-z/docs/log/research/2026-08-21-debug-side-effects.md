# `$DEBUG`가 여는 자리 전수 — 무엇이 딸려 오나 (2026-08-21)

디버그 모드를 켜면 무엇이 함께 열리는지 몰라 「라이드에서 그치나?」는 물음이 나왔다.
게임 설치본(`V2.18`)의 `Scripts.rxdata`에서 `$DEBUG`를 읽는 줄을 전수로 캐 갈랐다.

재현: 절을 풀어 `$DEBUG`를 grep하고, 같은 줄이나 앞뒤 한 줄에
`Input.press?/trigger?(Input::CTRL|F9|F6|ALT|SHIFT)`가 있으면 「키 조건부」로 센다.

## 셈

| 갈래 | 수 | 뜻 |
|---|---|---|
| 전체 | 98 | `MOD:` 절 제외 |
| 키 조건부 | 26 | CTRL 등을 함께 눌러야 발동 — 평소에는 영향 없음 |
| `PField_HiddenMoves` | 22 | 비전기술·라이드 통과 판정 |
| 나머지 | 50 | 아래에서 하나씩 읽었다 |

## 판을 바꾸는 것 (모드가 토글 뒤로 넣은 것)

| 자리 | 무엇이 열리나 | 모드 |
|---|---|---|
| `PField_HiddenMoves` 22줄 | 거합베기·박치기·바위깨기·괴력·파도타기·폭포오르기·잠수와 파도타기라이드 아이템 판정을 배지·기술 보유 없이 통과 | 「비전기술·라이드 자동 통과」(기본 켬) |
| `PokeBattle_Battle#pbEndOfBattle` | 원본 디버그 배포판이 끼운 전투 후 전원 회복 | 「전투 후 자동 회복」(기본 켬) |
| `PScreen_RegionMap:372` | 리전 맵을 **편집기로** 연다. 확인 버튼이 지점 이름 편집이 되고, 나갈 때 저장에 승낙하면 `townmap.dat`를 덮어쓴다 | 「개발자 모드」(기본 끔) |
| `PScreen_Bag:619,625` | 중요한 도구에도 「버리기」가 뜨고 「이상한 소포 만들기」 항목이 붙는다 | 〃 |
| `PItem_Items:616` | 알에게 기술을 가르칠 수 있다 | 〃 |
| `PTrainer_NPCTrainers:245,275` | 데이터에 없는 트레이너를 부르면 「새 트레이너를 추가할까?」를 묻는다 | 〃 |

리전 맵만 인자를 직접 넘긴다 — 그쪽은 `$DEBUG`를 판정이 아니라 「편집기로 열까」라는
**값**으로 쓰므로, 통째로 내리면 같은 화면의 미방문 지점 이동(CTRL) 같은 딴 기능까지
함께 죽는다. 나머지는 진입점에서 `$DEBUG`를 잠깐 내렸다 되돌린다.

## 조건이 붙어 지금은 안 도는 것

- `Compiler:4156` — 시작할 때 `PBS/*.txt`가 `Data/*.dat`보다 새것이면 **데이터를 통째로
  재컴파일**한다. `PBS` 폴더가 아예 없으면 만들고 전 데이터를 텍스트로 뽑는다.
  이 설치본은 조건이 거짓이다(실측 2026-08-21: PBS 최신 `2026-08-07 02:56:29` <
  Data 최신 `2026-08-07 02:56:34`, 목록에 든 21개 dat 기준). **PBS를 건드리면 발동한다.**
- `Compiler:4041 pbImportNewMaps` — 새 `Map###.rxdata`가 있으면 맵 트리에 넣는다(Data 쓰기).

## 무해한 것

파티·박스·일시정지 메뉴에 「디버거」 항목이 붙는 것(`PScreen_Party` · `PScreen_Storage` ·
`PScreen_PauseMenu` · `RepExp`) · 그림을 못 찾았을 때 콘솔 알림(`Titulo` · `Transiciones` ·
`LukaUtilities` · `Objetos Batalla` · `Evolucion`) · 배틀 로그 파일 쓰기(`PBDebug` —
`$INTERNAL`까지 켜져야 한다) · 파티가 0마리일 때 「SKIPPING BATTLES…」 알림
(`PTrainer_NPCTrainers:295` 등 — 건너뛰는 것 자체는 `$DEBUG`와 무관) ·
`PBattle_OrgBattleGenerator#pbWriteCup`(디버그가 아니면 no-op) · 랜덤라이저 도전 중
레이더에 야생 목록 표시(`RandomMain:1528`) · 타이틀 대신 불러오기로 시작
(`Main:44` — 안내문에 이미 적혀 있다).

## 덧 — 타이틀로 돌아가면 디버그가 꺼진다

`Titulo`·`LukaUtilities`가 실릴 때 `$memDebug = $DEBUG` 뒤 `PLAY_ON_DEBUG`(참)라
`$DEBUG = false`로 내리고, `Scene_Intro#main`이 `$DEBUG = $memDebug`로 되돌린다.
그 시점의 `$memDebug`는 디버그 배포판이 `Main` 머리에 심는 `$DEBUG = true`보다
**먼저** 잡힌 값이라 거짓이다. 안내문의 「타이틀로 돌아가면 디버그는 꺼집니다」가
이 경로다. `VAYA:1`의 `$DEBUG = false`는 절 254라 절 283의 `Main`이 이긴다.
