# 한글패치 통합 코어(Scripts.rxdata) 30섹션 분류 — 무엇이 남고 무엇이 나가나

핸드오프 `handoff-2026-08-04-kr-patch-slimming.md`의 작업 1번. 순정 V2.18 대비 바뀐
30개 섹션 + 추가된 1개를 전부 열어, 코어에 남길 것과 UI Text KR로 이관할 것을 갈랐다.

**재현** (essentials-modkit에서, 30초):

```
uv run python -c "
import pathlib; from modkit import moddiff
b=moddiff.sections(pathlib.Path(r'/mnt/c/Users/durumii/Downloads/Modkit-Test/Pokemon Z V2.18/Data/Scripts.rxdata').read_bytes())
m=moddiff.sections(pathlib.Path(r'/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/Scripts.rxdata').read_bytes())
d=moddiff.diff(b,m); print(len(d.changed), d.added)"
```

실측: base 255섹션 · mine 256 · changed 30 · added 1(`Josa Select`) · removed 0.
바뀐 총량은 30섹션을 합쳐 **100여 줄**뿐이다.

## 넘지 않는 선 — 한글패치는 혼자서 작동해야 한다

**분류에 앞서 걸린 제약이다**(사용자 2026-08-04). 한글패치 통합만 설치해도 게임이
한국어로 돌아가야 한다. 조사 시스템을 2026-08-03에 코어로 흡수한 이유가 바로 이것이다.

혼자 작동하는 데 필요한 것은 셋이다 — `Settings`의 언어 등록, `PScreen_Options`의
기본 언어 값, 그리고 `Josa Select`. 이 셋이 빠지면 korean.dat을 아예 안 읽거나
`\j[은,는]`이 화면에 그대로 나온다. 따라서 **`Data/Scripts.rxdata`를 안 싣는 안은
없다.** 줄일 수 있는 것은 그 안의 수정 자리 수이지 파일 자체가 아니다.

「혼자 작동한다」가 「모든 문구가 한국어다」는 아니다. 아래 (b)를 UI Text KR로 옮기면
그 68줄은 한글패치만 설치했을 때 스페인어로 남는다 — 그림 3장을 Z GUI에 맡긴 것과
같은 선이다.

## 분류의 기준선 — UI Text KR의 훅이 어디까지 붙잡나

이관 가능 여부는 「문구인가」가 아니라 **「UI Text KR의 훅이 그 문자열을 붙잡는가」**로
갈린다. `mods/UI Text KR/001_UiText.rb` 실측 훅 넷:

| 훅 | 붙잡는 경로 |
|---|---|
| `Window_AdvancedTextPokemon#setText` | `Kernel.pbMessage` · `pbConfirmMessage` · `pbDisplay` · `Kernel.pbCreateMessageWindow`로 만든 창의 `.text=` |
| `Window_UnformattedTextPokemon#text=` | 서식 없는 창 |
| `pbDrawTextPositions` | `textpos` 배열 그리기(메뉴 라벨·화면 하단 안내) |
| `pbGetBasicMapNameFromId` | 불러오기 화면 지명 |

치환 대상은 **완성된 런타임 문자열**이므로 보간(`#{...}`)이 든 문구도 정규식 짝으로
잡힌다 — 보간이 막는 것은 번역표(①층)이지 치환표(③층)가 아니다.

## (a) 코어에 남는다 — 6섹션 · 27줄 + 조사 109줄

| 섹션 | 줄 | 무엇이며 왜 남는가 |
|---|---|---|
| `Josa Select` (추가) | 109 | 조사 자동 선택 `\j[받침형,무받침형]`. **자립 조건** — 번역 정본이 이 문법을 전제한다 |
| `Settings` | 3 | `LANGUAGES`에 `["한국어","korean.dat"]` 등록. **자립 조건** — 이게 없으면 korean.dat 자체를 안 읽는다 |
| `PScreen_Options` L454 | 1 | `@language = 0 → 1`. **자립 조건** — 기본 언어를 한국어로 |
| `Messages` | 2 | 맵 이벤트 선택지에 `MessageTypes.getFromMapHash` 배선. 없으면 선택지가 스페인어로 남는다 |
| `PItem_ItemEffects` L33–67 | 18 | 부적 18종 판정을 이름 문자열 비교 → `isConst?` 상수 비교로. 이름을 번역하면 로직이 틀어지는 자리(⑤층) |
| `PScreen_Summary` L377·398 | 2 | `sprintf` 끝의 `\n` 제거 — 줄바꿈 레이아웃 |
| `TextEntry` L1023 | 1 | 이름 입력 문자표 배열. 그리기 훅이 못 잡는 데이터 리터럴 |

`PScreen_Summary` L342(성격 25종 한국어 배열)는 (c)를 보라.

### 여기서 빠지는 것 — 보간 템플릿 수술 6줄

`Following` · `PokeBattle_Battle` L87 · `PokeBattle_Battler` · `Cambia Habilidades`의
`#{}` 보간 → `_INTL("{1}",…)` 수술(④층) **6줄은 필요 없어진다.** 보간이 끝난 완성
문자열을 UI Text KR 정규식이 잡으므로, 번역 정본이 번역표(①층)에서 치환표(③층)로
내려가는 대신 코어 수정이 사라진다.

대가: 그 6줄은 `verify.py`의 canon 정합 검사 밖으로 나간다. 넷 다 포켓몬 이름·타입명을
끼우는 문장이라 canon 대조가 실제로 걸리는 자리다 — **옮기기 전에 치환표 쪽 검사
수단을 먼저 마련할 것.**

### 별도: 진단 (기능도 문구도 아님)

`PSystem_System` 2줄 — `Constants.rxdata` 적재 실패·빈 상수를 `p`로 알리는
`KR-PATCH DIAG` 로그. 남기되 「진단」으로 표식한다(z 수술 범위 기준의 진단 표면화 몫).

## (b) UI Text KR로 이관한다 — 문구 조립 (22섹션 · 68줄)

메시지 창 경로(`pbMessage` 계열) — 훅 1이 그대로 붙잡는다:

| 섹션 | 줄 | 섹션 | 줄 |
|---|---|---|---|
| `Incubadora` | 6 | `PokeBattle_Battle`(날씨 3문구) | 3 |
| `PScreen_PurifyChamber` | 5 | `PBattle_BugContest` | 3 |
| `Monotype` | 3 | `DiplomaPokedex` | 2 |
| `Editor` | 2 | `Export to Showdown` | 2 |
| `PokeBattle_MoveEffects` | 2 | `PokeBattle_Scene` | 2 |
| `Sacar Equipo` | 2 | `Vsync` | 2 |
| `PItem_ItemEffects`(능력 상승 2문구) | 2 | `Diploma Nuz1` · `Diploma Nuz2` | 각 1 |
| `FotoRemington` | 1 | `PMinigame_VoltorbFlip` | 1 |
| `PScreen_Storage` | 1 | | |

`textpos` 경로(훅 3): `Menu Mejorado` 11 · `Crafteo` 3 · `Guia Personajes` 3.

메시지 창으로 확인된 자리(훅 1): `PScreen_Options` 설명문 10줄 — `@sprites["textbox"]`가
`Kernel.pbCreateMessageWindow` 산출물이다(PScreen_Options.base L481 실측).

보간이 든 6줄(`#{pokemon.name}의 능력이 올랐다!` · `배지: #{…}` · `최대 레벨: #{…}` ·
`#{type_name}타입 …` · `#{pokemon.name}(으)로 정할까?`)은 고정된 앞뒤를 정규식으로 잡고
가운데 값을 그대로 돌려주는 짝으로 옮긴다.

**이관하면 오직 (b)에만 걸린 19섹션이 순정으로 돌아간다.** 보간 6줄까지 치환표로
내리면 코어의 수정 섹션은 30 → 6이 된다.

### 이관이 오히려 안전한 자리 — `Menu Mejorado`

`@options[i][0]`은 화면에 그려지는 라벨이면서 **동시에 스프라이트 해시 키**다
(`@sprites[@options[i][0]]`, L1547·1551·1624 실측). 지금처럼 코어 리터럴을 고치면
키까지 한국어로 바뀐다. UI Text KR로 옮기면 그리기 층에서만 바뀌고 키는 원문으로
남아, 다른 모드가 같은 키를 참조해도 어긋나지 않는다.

## (c) 훅이 못 잡는다 — 번역표로 올리는 편이 낫다 (1줄)

`PScreen_Summary` L342는 성격 25종을 한국어 배열로 하드코딩하고 `PBNatures.getName`을
폴백으로 둔다. 이 문자열은 `drawTextEx` 경로로 그려져 UI Text KR의 현재 훅 넷 어디에도
안 걸린다(조사 시스템은 이 훅을 이미 갖고 있다).

**다만 순정의 `PBNatures.getName`은 `_INTL("Fuerte")` 꼴이다**(base `PBNatures` 섹션
실측) — 즉 번역표를 지나는 문자열이다. 25항목을 `translate/ko/`에 얹어 korean.dat을
다시 만들면 이 코어 수정은 통째로 사라진다. 훅을 늘리는 것보다 이쪽이 옳다.

착수 전 확인: `probe.py "Fuerte"` 실측으로는 dat에 단독 항목이 없다(canon에는
`natures es=Fuerte ko=노력`이 있다). 어느 절에 들어가야 하는지부터 짚을 것.

## 이 분류의 결론

코어 수정 섹션 **30 → 6**, 추가 섹션은 조사 하나 그대로. `Data/Scripts.rxdata`는
자립 조건 때문에 계속 실린다.

한글패치 통합이 스스로 하는 일은 이렇게 남는다 — korean.dat을 읽히고, 조사를 붙이고,
맵 이벤트 선택지를 번역표로 보내고, 부적 로직이 이름 번역에 안 흔들리게 하고,
이름 입력 문자표와 요약 화면 줄바꿈을 맞춘다. 그 밖의 화면 문구는 UI Text KR 몫이다.

## 남은 것

- (b) 68줄을 UI Text KR 치환표로 옮기고, 옮긴 섹션을 코어에서 순정으로 되돌리는 실작업.
- 보간 6줄을 치환표로 내리기 전에 canon 대조를 대신할 검사 수단 마련.
- UI Text KR 카드에 `requires: ["한글패치 통합"]` 선언(조사 의존 — 사용자 확정).
- 되돌린 코어로 실기 검증: 19섹션이 순정으로 돌아가도 화면이 그대로인지.
