# 2026-08-19 코어 그림 자산 언어 전수 검수

`한글패치 코어/Graphics/` 아래 151개 파일 전부를 Read 도구로 직접 열어 확인했다(그림
이름으로 짐작하지 않음). 흰 배경에 흰 글자로 렌더링돼 육안으로 안 보이던 파일 3개는
검은 배경에 합성해 별도로 확인했다(`cartelFinal1.png` · `cartelFinal2.png` ·
`introText3.png` — 알파 채널에 텍스트가 있는데 Read 미리보기가 흰 배경에 얹어 안 보였다).

## 요약

- 전수: 151개 (`Pictures/` 113 · `Battlers/` 16 · `Characters/` 6 · `Icons/` 16)
- 설치본(`/mnt/d/Game/Pokemon Z/V2.18/Graphics/`) `.orig` 백업: **151개 전부 있음**
- 판정별 개수: `ko` 30 · `en` 60 · `none` 61 · `es` 0
- `en`(영어가 섞여 들어온 것) 목록은 아래 "en 판정 상세" 절 참고. `tutorialBat.png`
  포함 61개 파일 중 60개가 이번 검수로 새로 확인된 것이다.

## en 판정 상세 (읽은 문구 인용)

| 경로 | 읽은 문구(발췌) |
|---|---|
| Pictures/PokedexForm.png | 탭 "INFO / AREA / FORMS / ADV" |
| Pictures/pokedexEntry.png | 탭 "INFO / AREA / FORMS / ADV" |
| Pictures/pokedexNest.png | 탭 "INFO / AREA / FORMS / ADV" |
| Pictures/pokedexSearchbg.png | "EXIT" / "SEARCH" / "PG-UP" / "PG-DN" |
| Pictures/pokedexbg.png | "EXIT" / "SEARCH" / "PG-UP" / "PG-DN" |
| Pictures/mapbg.png | "EXIT" |
| Pictures/boxpartytab.PNG | "EXIT" |
| Pictures/boxsides.png | "PKM TEAM" / "EXIT" |
| Pictures/cartaBayas.PNG | "BERRY RECIPE", "CHERI BERRY COLOR RED / CURES PARALYSIS" 등 항목 전부 영어 |
| Pictures/battleCommandButtons.png | 한국어("싸운다/포켓몬/가방/도망")와 영어("CALL/BALL/ROCK/BAIT/BALL")가 한 시트에 섞여 있음 — 낚시 미니게임용 버튼으로 보이는 뒤쪽 5개가 미번역 |
| Pictures/cartelActo1.png | "ACT 1: POKÉTOUR" |
| Pictures/cartelActo2.png | "ACT 2: BETRAYAL" |
| Pictures/cartelActo3.png | "ACT 3: ULTIMATE WEAPON" |
| Pictures/cartelFinal1.png | (흰 글자, 검은 배경 합성 후 확인) "A WHILE LATER..." |
| Pictures/cartelFinal2.png | (흰 글자, 검은 배경 합성 후 확인) "EPILOGUE / 50 YEARS LATER" |
| Pictures/cred5.png | "Created by EricLostie" |
| Pictures/cred6.png | "Thank you very much for playing!" |
| Pictures/helpbg.png | "CONTROLS", "Movement" / "Interact/Menu" / "Interact/Run" / "Back" / "Turbo" |
| Pictures/introText1.png | "POKÉMON WORLD" |
| Pictures/introText2.png | "ASTER ZÉPHYR" |
| Pictures/introText3.png | (흰 글자, 검은 배경 합성 후 확인) "MANY HUMANS AND POKÉMON PERISHED DURING THIS CONFLICT" |
| Pictures/introText4.png | "GREAT" / "WAR" |
| Pictures/introText5.png | "WEAPON" |
| Pictures/introText6.png | "POWER" |
| Pictures/introText7.png | "POWER" (introText6과 동일 문구, 다른 위치) |
| Pictures/introText8.png | "STORY OF" / "HOW" |
| Pictures/introTexto1.png | "300 YEARS AGO..." |
| Pictures/prisionRot.png | "OBLIVION PRISON" |
| Pictures/rot10Cendera2.png | "COUNTESS OF WINTER" |
| Pictures/rot11Siempreviva2.png | "MISTRESS OF CEREMONIES" |
| Pictures/rot12Arrayan2.png | "THE LOST REGENT" |
| Pictures/rot13Mirra2.png | "HERALD OF GOLD" |
| Pictures/rot1Canola2.png | "SWORDS MASTER" |
| Pictures/rot2F3.png | "MECHANICAL WONDER" |
| Pictures/rot2Hisopo2.png | "SHADOW OF THE OPERA" |
| Pictures/rot2Lider7.png | "ENSLAVER OF MINDS" |
| Pictures/rot2Loto.png | "DEMON OF THE SKY AND THE SEA" |
| Pictures/rot4Zafra2.png | "BUDDING CHEF" |
| Pictures/rot6Belladona2.png | "THE DEADLY THORN" |
| Pictures/rot8Anturia2.png | "FLAME WITCH" |
| Pictures/rot9Rupico2.png | "BADGE FORGER" |
| Pictures/rotAZ.png | "ASTER AND ANGELINE" |
| Pictures/rotAZ2.png | "THE LAST KINGS" |
| Pictures/rotAlcaFinal2.png | "THE ULTIMATE WEAPON" |
| Pictures/rotMazmorra1.png | "THE DARK TOWER" |
| Pictures/rotMazmorra2.png | "POKÉ BALL FACTORY" |
| Pictures/rotMazmorra3.png | "FROZEN CAVERN" |
| Pictures/rotMazmorra4.png | "FLOODED ANCIENT FORGE" |
| Pictures/rotMazmorra6.png | "NIGHTMARE OF THE CIRCUS" |
| Pictures/rotMazmorra7.png | "PRISM TOWER" |
| Pictures/rotMazmorra8.png | "THE ULTIMATE WEAPON" |
| Pictures/sitioArma1.png | "VIRIDIAN CITY, KANTO" |
| Pictures/sitioArma2.png | "STRIATON CITY, UNOVA" |
| Pictures/sitioArma3.png | "IKI TOWN, ALOLA" |
| Pictures/summary1.png | 우하단 "EXP" 라벨만 영어, 나머지는 그래프뿐(텍스트 없음) |
| Pictures/summary3.png | 스탯 그래프 라벨 "PS"(영어도 스페인어도 아닌 약어로 보임 — 원본이 뭐였는지 미확인, 한글은 아님) |
| Pictures/tutorialBat.png | (기존 보고와 동일) "1. Defeat enemy soldiers to help Crisanto's army..." |
| Pictures/tutorialLegendarios.png | "You will have to find the 3 Legendary Pokémon..." |
| Pictures/tutorialRandom.png | "YOU'VE UNLOCKED RANDOM MODE!", "From now on, in new games you start..." |

## ko 판정 (한국어 확인됨, 30개)

`Pictures/MenuClas.png` · `MenuClasSel.png` · `MenuComp.png` · `MenuCompSel.png` ·
`MenuNormalClaro.png` · `MenuNormalOsc.png` · `MenuNuzAyudaClaro.png` ·
`MenuNuzAyudaOsc.png` · `MenuNuzNuzClaro.png` · `MenuNuzNuzOsc.png` · `MenuRand.png` ·
`MenuRandSel.png` · `bag1.png` · `bag1f.png` · `bag2.png` · `bag2f.png` · `bag3.png` ·
`bag3f.png` · `bag4.png` · `bag4f.png` · `bag5.png` · `bag5f.png` · `bag6.png` ·
`bag6f.png` · `bag7.png` · `bag7f.png` · `bag8.png` · `bag8f.png` · `pokedexTypes.png`
(타입 이름 전부 한국어) · `types.png`(타입 이름 전부 한국어)

## none 판정 (읽을 텍스트 없음, 61개)

- `Battlers/` 16개 전부 — 포켓몬 배틀 스프라이트 시트, 텍스트 없음.
- `Characters/` 6개 전부 — 필드 캐릭터 스프라이트, 텍스트 없음.
- `Icons/` 16개 전부 — 아이템·포켓볼 아이콘, 텍스트 없음.
- `Pictures/ball00.png` · `ball00_open.png` · `ball01.png` · `ball01_open.png` ·
  `ball02_open.png` · `ball03.png` · `ball03_open.png` · `ball04.png` ·
  `ball04_open.png` · `ball24.png` · `ball24_open.png` — 포켓볼 그림만.
- `Pictures/helpArrowKeys.png` · `helpCkey.png` · `helpF5key.png` · `helpXkey.png` ·
  `helpZkey.png` — 키 아이콘만, 글자 없음(알파벳 한 글자는 키 표시이지 텍스트가 아님).
- `Pictures/summary2.PNG` · `summary4.png` · `summary5.png` — 빈 칸/그래프 틀만.
- `Pictures/summaryball04.png` · `summaryball24.png` · `summaryball25.png` ·
  `summaryball26.png` · `summaryball27.png` — 포켓볼 그림만.

## 확정도와 한계

- 확정도: **실측** — 151개 파일 전부를 Read 도구로 직접 열어 확인했다. 흰 배경/흰 글자로
  안 보이던 3개(`cartelFinal1.png` · `cartelFinal2.png` · `introText3.png`)는 Python
  Pillow로 검은 배경에 합성한 사본을 다시 Read로 확인했다(재현: 파이썬으로 RGBA를
  검은 배경에 `alpha_composite` 후 저장·확인).
- `.orig` 백업 유무는 파일 존재만 확인했고 내용까지 대조하지는 않았다(설치본 원본이
  스페인어인지는 이번 검수 범위 밖 — `tutorialBat.png`류를 통해 이미 스페인어임이
  알려진 것만 참고).
- `Pictures/summary3.png`의 "PS" 라벨은 스페인어("Puntos de Salud")인지 영어 약어인지
  판단하지 못했다 — 두 글자뿐이라 문맥 확정이 어렵다. `es`로도 `en`으로도 단정하지
  않고 en 표에 별도로 적어 뒀다.
- `es`(스페인어 미번역) 판정은 0건이었다 — 이번 코어 자산 151개 안에서는 전부 한국어
  아니면 영어였다.
- 이 문서는 사실만 기록한다. 원인 추정이나 수정 방법은 다루지 않는다.
