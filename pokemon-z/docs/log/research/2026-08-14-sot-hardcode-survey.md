# Z-53 하드코딩 전수 조사 — 코드·프롬프트에 박힌 번역쌍/용어/문안

조사 범위: `/home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z`
읽기 전용. 파일 수정·커밋 없음.

---

## 0. 이미 처리된 것 — TITLES → term-pairs.jsonl 이관 결과 (실측)

**스키마**: 한 줄 = `{"es": <원문>, "ko": <표기>}` — 필드 둘뿐. 근거·이력 칸 없음.

```
$ wc -l translate/term-pairs.jsonl   → 57
$ head -5 translate/term-pairs.jsonl
{"es": "Arma Definitiva", "ko": "최종병기"}
{"es": "Team Azoth", "ko": "아조스단"}
{"es": "Alquimia Pokémon", "ko": "포켓몬 연금술"}
{"es": "pokécuartos/pokéfrancos", "ko": "포켓프랑"}
{"es": "Legislador", "ko": "입법관"}
```

**읽는 코드는 한 군데뿐**: `translate/batch_pages.py:802` 상수 `TERMS`,
`:805 term_pairs()`. 파일이 없으면 `_term_pairs_md()`(:819)가 `glossary.md` 표를
파싱하는 과도기 폴백. 소비처는 `batch_pages.py:989 glossary_for()`(프롬프트 용어
규칙 삽입), `:1125`(장면 표기표), `translate/screen.py:144`(선별층 용어 이탈 검사)
— screen은 `import batch_pages as B` 로 같은 함수를 쓴다.

```
$ grep -rn "term-pairs\|term_pairs" --include='*.py' .
```
→ 코드 히트는 위 6줄 전부. 다른 도구·모드는 이 파일을 안 읽는다.

**이관 커밋**: `aa7cfa1 refactor(z): 용어 SoT 이관 — TITLES 해체, term-pairs가
유일 정본 (유지자 지시)` (2026-08-13). 커밋 메시지 실측: term-pairs +5(무슈·마담·
마드모아젤 이관, Profesor 분기, bastión→요새), batch_pages의 TITLES 삭제.

⚠ **다만 「유일 정본」은 아직 아니다.** 아래 §1-A 참조 — 이관한 무슈·마담·
마드모아젤이 `batch_pages.CORE_TERMS`와 `prompt-pages.md`에 **그대로 남아 있다**.

---

## 1. 발견 목록

### A. batch_pages.py `CORE_TERMS` — 무조건 실리는 용어 규칙 블록

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 발췌 | 쓰임 |
|---|---|---|---|---|
| `translate/batch_pages.py:770-784` | `CORE_TERMS` (문자열 리터럴) | 규칙 6줄 · 그 안에 명시 번역쌍 약 12개 | `damage is 「데미지」 (not 대미지)`, `pokécuartos/pokéfrancos is 「포켓프랑」`, `monsieur→무슈, madame→마담, mademoiselle→마드모아젤`, `máscara → 마스크 (not 가면)`, `Franchise vocabulary: 배틀 · 트레이너 · 체육관 · 기술머신 · 몬스터볼 · 도감`, `Status: 독/맹독/화상/마비/잠듦/얼음`, `Mamma mia→「맘마미아」` | `glossary_for()`(:1005)가 **모든** 프롬프트 앞머리에 무조건 붙인다. 장면별 발췌(term-pairs·ledger)는 그 뒤에 덧붙는다 |

**의견: 정본 복제 (최우선).** term-pairs.jsonl과 **실제로 중복**한다 — 실측:

```
$ grep -n '무슈\|마담\|마드모아젤\|포켓프랑\|마스크' translate/term-pairs.jsonl
4:{"es": "pokécuartos/pokéfrancos", "ko": "포켓프랑"}
33:{"es": "monsieur", "ko": "무슈"}
34:{"es": "madame", "ko": "마담"}
35:{"es": "mademoiselle", "ko": "마드모아젤"}
38:{"es": "máscara", "ko": "마스크"}
```

5쌍이 두 곳에 산다. 유지자가 term-pairs.jsonl만 고치면 CORE_TERMS가 낡은 채
**무조건 실린다** — TITLES 사고와 같은 모양이고, CORE_TERMS는 장면 필터를 안 타서
오히려 영향이 더 넓다. 「데미지(not 대미지)」·프랜차이즈 어휘 6종·상태이상 6종은
term-pairs에 없어서 여기가 사실상 유일 정본 — 그것도 코드 안이다.

### B. prompt-pages.md — 같은 쌍이 세 번째로

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `translate/prompt-pages.md:109-110`, `:230-231` | 규칙 M(A판/B판 각 1회) | 3쌍 ×2 | `Address titles are always Korean: monsieur→무슈, madame→마담, mademoiselle→마드모아젤. Never turn 무슈 back into monsieur.` | `batch_pages.build_prompt()`가 이 md를 통째로 읽어 시스템 프롬프트로 |
| `translate/prompt-pages.md:59`, `:180` | 규칙 F | 5개 | `age-based address terms (「오빠/누나/언니/아가씨/총각」)` | 금칙 호칭 지시 |
| `translate/prompt-pages.md:88`, `:209` | 규칙 | 1쌍 | `Luuuull… of Morelull → 「자마아…」 of 자마슈` | 포켓몬 울음소리 예시 |
| `translate/prompt-pages.md:67,70-71,73-75,81,84-85,194-196,202,205-206` | 규칙 I·K·L·N 예시 | 약 12개 | `el largo y férreo estoque de la ley → 「법의 철퇴」`, `¡Pero no tuvo ningún efecto! → 「그러나 아무 일도 일어나지 않았다!」`, `Acepto → 「그렇게 하죠」` | 번역 요령 본보기 |

**의견**: monsieur/madame/mademoiselle 3쌍은 **정본 복제**(A와 같은 이유, 세 번째
사본). 「오빠/누나/언니/아가씨/총각」은 **감시용 목록** — `screen.py:31
BANNED_ADDRESS`의 짝이고 번역쌍이 아니다. 나머지 예시(법의 철퇴 등)는 **판정성
상수**로 본다 — 프롬프트 본보기지 용어 정본이 아니다. 단 「¡Pero no tuvo ningún
efecto!→그러나 아무 일도 일어나지 않았다!」는 절23 실제 문안과 겹치므로, 정본이
바뀌면 프롬프트가 낡는다(약한 복제).

### C. mods/UI Text KR/001_UiText.rb `TABLE` — 최대 규모 번역쌍 하드코딩

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 발췌 | 쓰임 |
|---|---|---|---|---|
| `mods/UI Text KR/001_UiText.rb:7-73` | `UiTextKR::TABLE` | **53행** (`grep -c '^    \[' → 53`), 그중 정규식 인명 23개 | `["Medalla Guardia", "가르디아 배지"]`, `["Esta zona no tiene encuentros", "이 지역에는 나오는 포켓몬이 없습니다"]`, `["Normal Save", "일반 저장"]`, `[/\bOlivier\b/, "올리비에"]`, `[/\bCrisanto\b/, "크리산토"]`, `["Hombre del Saco", "자루 든 남자"]` | 게임 런타임에서 `Window_AdvancedTextPokemon#setText`·`pbDrawTextPositions` 등 훅 넷이 그리기 직전 gsub |

**의견: 정본 복제.** 인명 23개는 `translate/names.json`(361쌍)의 부분집합을 손으로
베낀 것 — 「올리비에」 표기가 바뀌면 여기가 낡는다. `Hombre del Saco→자루 든 남자`는
주석이 스스로 "대사 정본"이라 밝힌다. 배지 12개도 표기 판정 대상. 생성기 없음
(실측: `grep -rn 'UiText\|UI Text KR' --include='*.py' --include='*.rb'` → 참조는
`inject.py:6` 사용법 문자열, `share/qa-mod-cycles.py:32` 모드 목록, `verify.py:37
UI_MOD` 검사 뿐 — **이 .rb를 만들어 내는 코드는 없다**). 손으로 유지하는 표다.

부수 결합: `share/patch_debug.py:31-34`가 디버그판에서 `["[A] Curar"` → `["A Curar"`
로 대괄호를 벗기고, UI Text KR은 그 무괄호 짝을 별도 3행으로 중복 등재해 대응한다
(`001_UiText.rb:14-16`). 두 하드코딩 목록이 서로를 전제한다.

### D. share/patch_intl.py `_NATURE_ADJ` — 성격 25종 한국어 활용형

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 발췌 | 쓰임 |
|---|---|---|---|---|
| `share/patch_intl.py:112-115` | `_NATURE_ADJ` | 25 | `노력하는, 외로움을 타는, 용감한, 고집스러운, 개구쟁이, …, 변덕스러운` | 바로 아래 EDIT(:116-121)이 `PScreen_Summary`의 `naturename=PBNatures.getName(...)` 를 이 25칸 루비 배열 리터럴로 갈아 끼운다 — 요약 화면에서만 명사→활용형 |

**의견: 정본 복제.** 성격명 명사형은 번역 정본(korean.dat 성격 절)에 있고, 이
활용형은 그 정본에서 파생된 짝인데 코드에만 있다. 성격 표기 판정이 바뀌면
(예: 「개구쟁이」 재판정) 정본만 고치고 이 표는 남는다. 짝 문안 「{1} 성격이다.」는
절23 정본에 있다고 주석이 밝힌다 — 반쪽만 SoT다.

### E. share/patch_intl.py `_AMULETOS` — 스페인어 원문 18종

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 발췌 | 쓰임 |
|---|---|---|---|---|
| `share/patch_intl.py:139-147` | `_AMULETOS` | 18 | `("Amuleto Bicho","AMULETOBICHO")`, `("Amuleto Siniestro","AMULETOSINIESTRO")`, `("Amuleto Dragón","AMULETODRAGON")` | `PBItems.getName(item)=="Amuleto X"` 문자열 비교를 `isConst?(item,PBItems,:AMULETOX)`로 수술 — 한글화되면 깨지는 기능 버그 방어 |

**의견: 감시용/판정성 상수(잔류).** 한국어가 없다. 원문 자구는 게임 소스와 맞아야
하는 값이지 번역 판정 대상이 아니다. 근거 링크만 달아 두면 충분.

같은 파일 `EDITS`(:33-100)의 스페인어 원문·새 문구도 같은 갈래 — 다만 앙코르
수선(:80-85)의 새 문자열 `"¡{1} ha sufrido los efectos de Otra Vez!"`는 절23 번역과
**짝을 이루는 키**라, 저쪽 키가 바뀌면 함께 바뀌어야 한다(약한 복제).

### F. translate/apply_dialogue_terms.py `TERM_SWAPS`

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 발췌 | 쓰임 |
|---|---|---|---|---|
| `translate/apply_dialogue_terms.py:34-49` | `TERM_SWAPS` | 14 | `("명예볼도 하나 더 받는다","프리미어볼도 하나 더 받는다")`, `("실드포스로 데미지를 막았다","불가사의부적으로 데미지를 막았다")`, `("해독제 덕분에","포이즌힐 덕분에")` | korean.dat의 대사 절(0,20,22,23)에 부분 문자열 치환 |
| 같은 파일 :68-72 | (인라인) | 2 | `("기합의띠","기합의머리띠")` 맞바꿈 확인 | 절7·8의 [113]/[114] 스왑 |

**의견: 정본 복제 — 다만 갈래가 다르다.** 이건 **korean.dat에 직접 손대는 일회성
마이그레이션 도구**로 보인다(문서 근거: docstring "실기 제보(2026-08-01)와 대사
전수 스캔의 확정분"). 지금 파이프라인의 정본은 `translate/ko/*.jsonl` → `build.py`
→ korean.dat이므로, 이 도구가 아직도 돌면 정본을 우회한 두 번째 쓰기 경로다.
**확정도: 추정** — 이 도구가 현행 파이프라인에서 아직 호출되는지는 확인 못 했다
(§한계 참조). 유지자에게 「이미 SoT에 반영됐고 도구는 박제 대상인가」를 물어야 한다.

### G. translate/apply_terms.py `MOVE_FIXES` + combate 통일

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `translate/apply_terms.py:27-31` | `MOVE_FIXES` | 3 | `98:("깨뜨리다","깨트리기")`, `296:("탐내다","탐내기")`, `336:("프섭정 ","프레젠트")` | 절5(기술명) 위치별 치환 |
| `translate/apply_terms.py:62` | 인라인 | 2 | `.replace("시합","배틀").replace("대결","배틀")` | 원문 키에 `combate`가 든 행만 |

**의견: F와 같음 — 일회성 마이그레이션 도구의 정본 복제.** 「배틀」은 CORE_TERMS의
프랜차이즈 어휘와도 겹친다.

### H. translate/screen.py — 선별층 감시 목록

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `translate/screen.py:31` | `BANNED_ADDRESS` | 5 | `("오빠","누나","언니","아가씨","총각")` | 새 번역에 이 호칭이 새로 끼면 flag |
| `translate/screen.py:33` | `TITLES` | 5 | `("무슈","마담","마드모아젤","폐하","전하")` | 새로 끼면 근거 확인용 flag |

**의견: 감시용 목록(잔류).** 번역쌍이 아니라 검사 대상이다. 다만 `TITLES`의 앞
셋은 term-pairs.jsonl의 ko 값과 같은 낱말이라, 표기가 바뀌면 감시가 헛돈다 —
term-pairs에서 파생시킬 수 있으면 그쪽이 낫다(선택). 이름이 해체된 `batch_pages`의
옛 TITLES와 같아 혼동 주의 — **다른 물건이다**.

### I. translate/verify.py `SENTINELS`

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `translate/verify.py:44-48` | `SENTINELS` | 3 | `("Fuerte","노력")`, `("¡{1} ha perdido energía!","체력을 흡수")`, `("¡{1} alteró las dimensiones!","시공")` | 절23 키로 조회해 기대 한국어 조각이 있는지 — 재배포 게이트 |

**의견: 감시용 목록(잔류).** 다만 (es키, 기대 한국어 부분문자열) 쌍이라 **문안이
재번역되면 게이트가 오탐한다.** 근거 링크와 「문안 바뀌면 여기도」 주석 권장.

### J. translate/speaker.py — 화자 판정 정답 자리

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 발췌 | 쓰임 |
|---|---|---|---|---|
| `speaker.py:62-70` | `KNOWN` | 7 | `("Para nosotros, se parecen mucho a las letras","Mirra","맵119 손수정")` — 스페인어 원문 조각 + 기대 화자 | selftest 정답 표본 |
| `speaker.py:74-78` | `KNOWN_CLS` | 7 | `("who","Anturia","PS")`, `("sprite","flareow","PC")` | 층 판정 정답 |
| `speaker.py:81` | `KNOWN_ONCE` | 4 | `((22,3,7), True)` | 1회소비 판정 정답 |
| `speaker.py:139` | `VOICES_SPECIAL` | 3 | `{"az":"AZ","f3":"F3","druidaFicus":"대드루이드 피쿠스"}` | 스프라이트→한국어 인물명 예외 |
| `speaker.py:190` | `STEM_CONFLICT` | 3 | `{"flare","flara","luigi"}` | 어간 충돌 제외 |
| `speaker.py:243` | `COMPASS` | 4 | `{"Norte","Sur","Este","Oeste"}` | 방위 이름표는 사람 아님 |
| `speaker.py:136` | `VOICES_STRIP` | 정규식 18어 | `Montado|Reventada|Caduca|…` | 스프라이트 접미 제거 |

**의견**: 대부분 **판정성 상수(잔류)** — 근거가 주석에 이미 달려 있다(감사 날짜·절).
예외 하나: `VOICES_SPECIAL`의 `"druidaFicus": "대드루이드 피쿠스"`는 **정본 복제** —
한국어 인물명이 `names.json`에 있어야 할 값을 코드에 적었다.

### K. translate/batch_pages.py `bad` (페르소나 블랙리스트)

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `batch_pages.py:188` | `bad` (지역 변수) | 4 | `{"Revolucionaria", "유죄 판결을 받은 남성", "나카르", "Nácar"}` | 페르소나표가 낡은 화자 — 프롬프트에 페르소나를 안 붙인다 |

**의견: 판정성 상수(잔류).** 근거 주석이 바로 위에 있다(2026-08-06 전수 검토 17건).
다만 ES 표기와 KO 표기가 한 집합에 섞여 있고 지역 변수라, 화자명 표기가 바뀌면
조용히 무력화된다. 모듈 상수로 올리고 근거 링크를 다는 정도 권장.

### L. tools/status_icon.py `WORDS`

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `tools/status_icon.py:57` | `WORDS` | 1 | `{"쇠약": ["쇠","약"]}` | 상태이상 아이콘 그림에 글자를 찍는다 |

**의견: 정본 복제(소규모).** 「쇠약」은 상태이상 표기 판정 대상이다 — 실제로
`c34730c fix(z): 상태이상 Caduco 표기 재판정 — 쇠락 → 쇠약` 커밋이 있다. 다음
재판정이 나면 아이콘만 낡는다.

### M. translate/fill.py 프롬프트의 인명 예시

| 파일:줄 | 식별자 | 항목 수 | 박힌 값 | 쓰임 |
|---|---|---|---|---|
| `translate/fill.py:57` | `PROMPT_NEW` 안 | 1 | `고유명사(인명 Bill 등 로마자 이름)는 음차한다(Bill→빌)` | 시스템 문구 신규 번역 프롬프트 |

**의견: 판정성 상수(잔류).** 본보기 한 쌍. 용어 규칙 자리는 `{GLOSSARY}`로
주입되므로 정본 경로는 살아 있다.

### N. 번역쌍이 아니라고 판정한 것들 (근거와 함께 잔류 권고)

| 자리 | 무엇 | 왜 잔류 |
|---|---|---|
| `translate/reg.py:58-69` (`MENU`·`HAGE_STRONG`·`RULES` 등) | 한국어 종결어미 분류 규칙 수십 개 | 문법 분류기다. 번역 판정과 무관 |
| `translate/reg_check.py:6-…` | 종결어미 분류 테스트 표본(한국어 문장 다수) | 테스트 픽스처 |
| `translate/apply_josa.py:26-53` (`CONVERSIONS`·`BARE`) | `(은)는 → \j[은,는]` 15+9쌍 | 조사 문법 변환. 용어 아님 |
| `translate/validate.py:25` `EXACT` | 마크업 정규식 | 구조 검사 |
| `translate/export.py:33` `SECTION_NAMES` | 절 번호→영문 파일명 24개 | 파일 이름 |
| `translate/canon_sweep.py:24` `SRC_RANK` | 본가 판본 우선순위 9개 | 출처 순위 |
| `translate/pilot_npc.py:34` `MUST` | 스프라이트 이름 20개 | 표본 선정 |
| `translate/judge.py:40`·`mine.py:41`·`screen_llm.py:35` PROMPT | LLM 검수 지시문(한국어 장문) | 지시문이지 용어 정본 아님. 단 `screen_llm` 예시의 「메를로 대장님」은 인명 의존 |
| `mods/Battle Order/*.rb`, `mods/DPPT Font/*.rb` 등 | 스페인어 `_INTL(...)` 원문 다수 | 상류 게임 소스 사본. `_INTL`이 korean.dat를 타므로 정상 경로. **다만 원문 자구가 상류와 어긋나면 번역 키가 안 맞는다** |
| `share/baked-korean-fixes.jsonl` (30줄) | `{"sec","line","old","new","why"}` | **이미 데이터로 외부화됨** — `patch_baked_korean.py`가 읽기만 한다. 좋은 선례 |
| `translate/names.json` (names 361 / keep 8 / fragments 4 / class_slots 4 / phrases 4 / dialogue_literals 1) | 인명 정본 | SoT. UI Text KR이 이걸 베낀 게 문제(§C) |

---

## 2. 우선순위 제안 (의견)

1. **§A CORE_TERMS** — 중복 5쌍이 실증됐고, 무조건 실려 영향이 가장 넓다.
2. **§C UI Text KR TABLE** — 53행, 인명 23개가 names.json 복제. 규모 최대.
3. **§B prompt-pages.md의 무슈/마담/마드모아젤** — A와 같은 쌍의 세 번째 사본.
4. **§D `_NATURE_ADJ`** — 25종, 정본에서 파생 가능한 활용형.
5. **§F·§G apply_* 도구** — 먼저 「현행 파이프라인에서 도는가」를 유지자에게 확인.
6. §J `VOICES_SPECIAL` 1건, §L `WORDS` 1건 — 소품.

---

## 3. 한계 (못 한 것 · 불확실한 것)

- **「전수」라고 말할 수 있는 범위**: 아래 두 명령이 훑은 범위 안에서만 전수다.
  ```
  grep -rln '[가-힣]' --include='*.py' --include='*.rb' --include='*.html' --include='*.js' .
    (제외: .git, share/dist/, webapp/vendor/)   → 파일 92개
  grep -rn '[áéíóúñ¿¡ÁÉÍÓÚÑü]' --include='*.py' --include='*.rb' --include='*.html' --include='*.js' .
  ```
  `share/dist/`(배포 산출 사본)와 `webapp/vendor/rubymarshal`(외부 라이브러리)은
  의도적으로 뺐다. `share/dist/*/번역표/빌드.py`는 `share/빌드.py`의 사본이라
  거기에 새 하드코딩이 있을 가능성은 낮지만 **확인 안 했다**.
- **§F·§G의 「일회성인가」는 추정이다.** docstring과 `build.py`(정본→dat)의 존재로
  추정했을 뿐, 이 도구들이 현행 빌드 절차에서 호출되는지 `docs/guides/`를 끝까지
  읽지 않았다. 유지자 확인 필요.
- **`docs/` 안의 하드코딩은 조사 대상 밖**으로 뒀다(지침·대장·기록은 정본 자체이거나
  기록층). `docs/ledger/glossary.md`가 `_term_pairs_md()` 폴백 경로로 여전히 코드에
  읽힌다는 사실만 적어 둔다(`batch_pages.py:819`).
- **`webapp/`은 훑었으나 번역쌍 없음.** 확인 명령:
  `grep -n '[가-힣]' webapp/core.py webapp/*.js webapp/index.html | grep -E '\["|\{"|:\s*"'`
  → 히트는 docstring·UI 라벨(`빌드 → 게임 반영` 등)뿐. 스페인어→한국어 쌍 0건.
- **`translate/fixgui.py`·`fixgui.html`·`review_gui.py`·`review_page.py`(스튜디오)에는
  번역쌍이 없다.** 한국어는 전부 화면 라벨·상태값(`STATE_VALS = ["수정","메모"]`,
  `LAYERS = {"screen":"휴리스틱"}`)과 셀프테스트 픽스처(`review_page.py:373-382`의
  "기니아"/"안녕" 표본). 확인:
  `grep -n '[가-힣]' translate/fixgui.py | grep -E '^\S+:[0-9]+:[A-Za-z_]+ *=|\{"|\["'`
- **여러 줄에 걸친 한국어 목록**도 한 번 더 훑었다:
  ```
  grep -rn '^\s*["\x27][가-힣][^"\x27]*["\x27]\s*[,:]' --include='*.py' translate/ tools/ runa/ share/
  ```
  새로 나온 것은 셋뿐이고 전부 번역쌍이 아니다:
  `translate/register.py:70,195-197`(어미 급 라벨·보고서 산문),
  `tools/status_icon.py:30,43`(「쇠」·「약」 글자 비트맵 — §L의 부품),
  `translate/reference/tools/namu_emit.py:13-50+`(나무위키 판본명 →
  PokéAPI slug 매핑 약 40개). namu_emit은 **참조 코퍼스 수집 도구**로 Z 번역
  정본과 무관하다 — **감시용/외부 매핑(잔류)**.
- **본문을 끝까지 읽지 않은 코드**: `runa/*.py`(글꼴 도구 8개), `tools/bulba/*`,
  `translate/harvest.py`·`survey.py`·`probe.py`·`make_speakers.py`·`dexswap.py`·
  `provenance.py`·`unified.py`. 위 세 종류 grep(한국어 문자 / 스페인어 문자 /
  줄머리 한국어 리터럴)에는 다 걸었고 번역쌍 꼴은 안 나왔지만, **문자열을 f-string
  이나 변수 조립으로 만드는 꼴은 어떤 grep에도 안 걸린다.** 확정도: 이 파일들은
  「grep 세 종에 안 걸림」까지가 사실이고, 「없다」는 **미확인**.
