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

## 분류의 기준선 — UI Text KR의 훅이 어디까지 닿나

이관 가능 여부는 「문구인가」가 아니라 **「UI Text KR의 훅이 그 문자열을 붙잡는가」**로
갈린다. `mods/UI Text KR/001_UiText.rb` 실측 훅 넷:

| 훅 | 붙잡는 경로 |
|---|---|
| `Window_AdvancedTextPokemon#setText` | `Kernel.pbMessage` · `pbConfirmMessage` · `pbDisplay` · `Kernel.pbCreateMessageWindow`로 만든 창의 `.text=` |
| `Window_UnformattedTextPokemon#text=` | 서식 없는 창 |
| `pbDrawTextPositions` | `textpos` 배열 그리기(메뉴 라벨·화면 하단 안내) |
| `pbGetBasicMapNameFromId` | 불러오기 화면 지명 |

치환 대상은 **완성된 런타임 문자열**이므로 보간(`#{...}`)이 든 문구도 정규식 짝으로
잡힌다 — 보간은 번역표(①층)의 벽이지 치환표(③층)의 벽이 아니다.

## (a) 코어에 남는다 — 기능 필수 (8자리 · 33줄 + 조사 109줄)

| 섹션 | 줄 | 무엇이며 왜 필수인가 |
|---|---|---|
| `Josa Select` (추가) | 109 | 조사 자동 선택 `\j[받침형,무받침형]`. 번역 정본이 이 문법을 전제해 분리 불가 |
| `Settings` | 3 | `LANGUAGES`에 `["한국어","korean.dat"]` 등록. **이게 없으면 korean.dat 자체가 안 읽힌다** |
| `PScreen_Options` L454 | 1 | `@language = 0 → 1`. 기본 언어를 한국어로 |
| `Messages` | 2 | 맵 이벤트 선택지에 `MessageTypes.getFromMapHash` 배선. 없으면 선택지가 스페인어로 남는다 |
| `PItem_ItemEffects` L33–67 | 18 | 부적 18종 판정을 이름 문자열 비교 → `isConst?` 상수 비교로. 이름을 번역하면 로직이 깨지는 자리(⑤층) |
| `Following` · `PokeBattle_Battle` L87 · `PokeBattle_Battler` · `Cambia Habilidades` | 6 | `#{}` 보간 → `_INTL("{1}",…)` 템플릿 수술(④층). 스페인어 원문은 그대로고 배선만 바뀐다 |
| `PScreen_Summary` L377·398 | 2 | `sprintf` 끝의 `\n` 제거 — 줄바꿈 레이아웃 |
| `TextEntry` L1023 | 1 | 이름 입력 문자표 배열. 그리기 훅이 닿지 않는 데이터 리터럴 |

`PScreen_Summary` L342(성격 25종 한국어 배열)는 (c)를 보라.

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
`#{type_name}타입 …` · `#{pokemon.name}(으)로 정할까?`)은 고정부를 정규식으로 물고
캡처를 되돌려주는 짝으로 옮긴다.

**이관하면 코어의 수정 섹션은 30 → 11로 줄어든다**(오직 (b)에만 걸린 19섹션이 순정으로 돌아간다).

### 이관이 오히려 안전한 자리 — `Menu Mejorado`

`@options[i][0]`은 화면에 그려지는 라벨이면서 **동시에 스프라이트 해시 키**다
(`@sprites[@options[i][0]]`, L1547·1551·1624 실측). 지금처럼 코어 리터럴을 고치면
키까지 한국어로 바뀐다. UI Text KR로 옮기면 그리기 층에서만 바뀌고 키는 원문으로
남아, 다른 모드가 같은 키를 참조해도 어긋나지 않는다.

## (c) 훅이 안 닿는다 — 번역표로 올리는 편이 낫다 (1줄)

`PScreen_Summary` L342는 성격 25종을 한국어 배열로 하드코딩하고 `PBNatures.getName`을
폴백으로 둔다. 이 문자열은 `drawTextEx` 경로로 그려져 UI Text KR의 현재 훅 넷이
못 잡는다(조사 시스템은 이 훅을 이미 갖고 있다).

**다만 순정의 `PBNatures.getName`은 `_INTL("Fuerte")` 꼴이다**(base `PBNatures` 섹션
실측) — 즉 번역표를 지나는 문자열이다. 25항목을 `translate/ko/`에 얹어 korean.dat을
다시 구우면 이 코어 수정은 통째로 사라진다. 훅을 늘리는 것보다 이쪽이 옳다.

착수 전 확인: `probe.py "Fuerte"` 실측으로는 dat에 단독 항목이 없다(canon에는
`natures es=Fuerte ko=노력`이 있다). 어느 절에 들어가야 하는지부터 짚을 것.

## 남은 것

- (b) 68줄을 UI Text KR 치환표로 옮기고, 옮긴 섹션을 코어에서 순정으로 되돌리는 실작업.
- UI Text KR 카드에 `requires: ["한글패치 통합"]` 선언(조사 의존 — 사용자 확정).
- 되돌린 코어로 실기 검증: 19섹션이 순정으로 돌아가도 화면이 그대로인지.
