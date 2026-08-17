# 층 오배정 후보 전량 — stage0 기반 재료화 (2026-08-18)

Z-53이 삼킨 두 티켓([Z-55](../../tickets/Z-55.md) 층 오배정 · [Z-67](../../tickets/Z-67.md)
전투 종료 대사)의 설계 약속 — 「0단계 빌드가 그 목록을 낸다」 — 를 이행한다. `translate/stage0/`가
선 뒤 처음 하는 층 오배정 전수 추출이다. **정본·판정 반영은 하지 않았다 — 재료만 갖춘다.**

## 무엇으로 쟀나

원자료는 `translate/stage0/sites.jsonl`(37,006행, 자리 하나에 한 줄)과 짝지어진
`messages.jsonl`(값, ref 참조 포함). 층(`layer`: N·PS·PC)·종류(`kind`: text·choice·battle)·
귀속법(`how`)·화자(`speaker`=그림, `who`=이름표)가 자리마다 실려 있어 기존 귀속표
(`translate/data/speaker-attr.jsonl.gz`)를 다시 조인할 필요가 없다. `sites.jsonl`은
`gen.py`가 귀속표에서 그대로 옮긴 값이라 스프라이트·이름표 두 신호는 여전히
`translate/speaker.py`의 `person_sprite()`·`person_tag()`가 정본이다 — 이 문서는 그 결과값
위에서 후보를 고른 것이지 새 판정 로직을 만들지 않았다.

재현: `python3 -c "import json; ..."`으로 `translate/stage0/sites.jsonl`을 한 줄씩 읽어
`layer`·`kind`·`speaker`·`how`·`src`로 거른다. 스크립트는 이 조사의 스크래치패드에만
있고 정본에는 없다(지침 「손대기 전에 읽는다」의 스무 남짓 도구 목록에 안 들어간다).

## 수치 — 방향별·묶음별

| 방향 | 묶음 | 행 수 | 신호 | 확정도 |
|---|---|--:|---|---|
| A (N인데 사람 말) | `battle_N` | 70 | `kind=="battle" and layer=="N"` | 실측 — [Z-67](../../tickets/Z-67.md) 재현치와 정확히 일치 |
| A | `object_sprite_bug` | 10 | `layer=="N" and speaker=="cazadorHerido"` | 실측 |
| A | `pokemon_village` | 29 | 맵356(포켓몬마을) & `speaker`가 숫자 접두 & 마을주민 스프라이트 11종 | 실측 |
| A | `functional_pokemon_npc` | 39 | `speaker` in {115,474,181,096} | 실측 |
| **A 합계** | | **148** | | |
| B (PS/PC인데 사람 말 아님) | `system_template_inherited` | 16 | 정형 시스템 문구 11종이 `layer` PS/PC로 나온 자리 | 실측(정밀) — 재현율은 미측정 |
| **총계** | | **164** | | |

**battle_N 70은 Z-67의 실측(`kind="전투호출"` & `cls="N"`)과 정확히 같은 수다** — 같은 조건을
stage0에서 다시 셌을 뿐이니 당연한 결과이고, stage0가 귀속표의 층·종류 값을 무손실로
옮겼다는 교차 검증이기도 하다(가공 없이 옮긴다는 `gen.py`의 설계 그대로).

**A 148행은 Z-55의 어림 「60여 행」보다 크다.** 원인은 방법이 다르기 때문이다 — Z-55의
60여 행은 사람이 Z-65 컷신 층을 눈으로 훑다 만난 것이고, 이 문서의 A는 그 눈훑기가 안
닿았던 두 갈래(`pokemon_village` 29행·`functional_pokemon_npc` 39행, 아래 「새로 든 것」
참조)를 기계로 새로 찾은 것이다. `object_sprite_bug`(10행, cazadorHerido)는 Z-55가 말한
「간호사·다친 사냥꾼·포켓몬마을 주민 등, 기계 분류가 놓친 구멍 2자리」의 그 구멍과 같은
스프라이트로 보인다(cazadorHerido = 다친 사냥꾼). `battle_N` 70행은 Z-55 집계에 안 들어가고
Z-67에 따로 있다.

**B 16행은 Z-55의 「반대 방향 20줄」보다 작다.** Z-55의 20줄 중 다섯(맵116·136·211·276·297)을
stage0에서 재조회해 셋(맵116 Zafra 파티가득·맵136 golperoca 확인창·맵276 Anturia류)은 이
문서의 정형 문구 신호로도 다시 걸리는 것을 확인했지만, 나머지(맵211 내레이션·맵297 명단
오류)는 **문장 구조 신호가 아니라 서사 판단**(「여왕이 제 일행을 낮춰 존대할 리 없다」·
「총사가 제 뒤에 숨을 수 없다」)이 필요해 이 조사의 기계 신호로는 못 잡는다. 아래 「B의
한계」에 시도와 실패를 적는다.

## 판정이 쉬운 순서

### 1. `battle_N` (70행) — 가장 쉽다

기계적으로 이미 확정에 가깝다. Z-67 연구([2026-08-16-battle-line-register](2026-08-16-battle-line-register.md))가
21페이지를 전부 열어 62/70이 사람 말임을 이미 확인했고, 이 문서는 그 조건을 stage0에서
그대로 재현한 것이다. 남은 일은 Z-67의 P-1(층 판정이 `how="전투호출"`을 스프라이트로
안 거르게 고치는 것)이다.

### 2. `object_sprite_bug` (10행) — 스프라이트 명단 한 줄 고치면 끝

`translate/sprite-groups.json`의 `사물지문` 그룹에 `cazadorHerido`(다친 사냥꾼)가 올라
있다. 맵141(고목내마을) 이벤트33의 대사 10행(페이지 0·1에 복제) 전부가 1인칭·호격
("Aspirante"=후보생, 플레이어 호칭)이 뚜렷한 사람 말이다.

```
m141.e33.p0.c1  Agh... no te acerques a mí, Aspirante. Estoy gravemente enfermo...
  으윽... 나한테 가까이 오지 마, 후보생. 심하게 아파서 옮길지도 몰라.
m141.e33.p0.c46 Gracias, valiente Aspirante, por liberarme de esta maldición.
  용감한 후보생, 이 저주에서 풀어줘서 고마워.
```

명단에서 `cazadorHerido` 한 줄을 빼면(또는 `voices.md`/`sprite-groups.json`의 사람 그룹으로
옮기면) 이 10행은 저절로 재분류된다 — **행 단위 수정이 아니라 명단 수정으로 끝나는
자리**라 판정 비용이 가장 낮다.

### 3. `pokemon_village` (29행) — 맵356 하나에 몰려 있다

맵356(포켓몬마을)은 포켓몬 그림(숫자 접두 스프라이트)이 마을 「주민」 역할로 1인칭
대사를 하는 특수 맵이다. `person_sprite()`는 숫자로 시작하는 스프라이트를 전부
비인물(포켓몬 도감번호 그림)로 빼므로, 이 맵 전체가 구조적으로 N층에 갇힌다.

| 스프라이트 | 행 | 예시 원문 |
|---|--:|---|
| `242` | 4 | 「¡Soy la mejor en esto!」(난 이걸 제일 잘해!) — 치료 담당 |
| `325` | 4 | 「¡JE, JE, JE, JE! Tengo que seguir saltando... Si en algún momento dejo de saltar, ¡moriré!」 |
| `465` | 4 | 조부 이야기를 전하는 화자 |
| `301` | 3 | 「Villa Pokémon es un refugio que acoge a...」(마을 소개) |
| `195` | 2 | 「¿Tú venir a quitarnos bayas? Yo tener pocas bayas...」(서투른 화법) |
| `547`·`055`·`294`·`903`·`068`·`316s` | 각 2 | 1인칭 독백 |

전부 한 맵 안이라 **한 번에 판정하기 좋다** — 이 맵을 인물 층으로 옮길지, 이 맵 전용의
「포켓몬 주민」 예외 명단을 세울지 하나만 정하면 29행이 한꺼번에 풀린다. 같은 맵의
`181`(기술 리마인더 정형구, 8행)은 아래 4번과 겹치므로 이 표에서 뺐다.

### 4. `functional_pokemon_npc` (39행) — 정형구라 처방이 가볍다

돌봄센터 카랑코(스프라이트 `115`, 13행)·기술 리마인더 포켓몬(`474`·`181`, 24행)·
레스토랑 웨이터 드로우지(`096`, 2행). 전부 서비스 정형구라 [events-and-speech](../../guides/events-and-speech.md)의
「등급 3: 전 맵 반복 정형구」에 해당한다 — 페르소나 재작성이 아니라 층 재분류 + 정형구
통일 규칙 적용이면 된다. `474`/`181`은 같은 정형구가 서로 다른 맵에서 이미 PS/PC로도
서 있어(예: 정본 인물이 같은 대사를 쓰는 자리) **판정 재료가 이미 있다** — 아래 예시.

```
m206.e16.p0.c1  ¿Qué necesitas?           무엇이 필요해?         layer=N  speaker=474
m206.e16.p0.c29 Eso es un huevo, pedazo de inútil.  그건 알이잖아, 이 멍청아.
```

같은 정형구(「¿Qué necesitas?」·「¿Qué Pokémon debería recordar un movimiento?」류)가
이름 붙은 인물의 PS/PC 자리에서도 확인된다 — 즉 이 정형구 자체는 이미 「사람이 말하는
문구」로 처리된 전례가 있고, 포켓몬 그림이 말할 때만 예외적으로 N에 갇힌다.

### 5. `system_template_inherited` (16행, 방향 B) — 가장 판단이 갈린다

정형 시스템 문구(파티 가득 알림·확인창·보상 알림) 11종이 우연히 인물이 있는 페이지에
낀 자리다. 페이지 층이 인물(PS/PC)이면 그 안의 시스템 줄도 인물 층을 그대로 물려받는다
— [events-and-speech](../../guides/events-and-speech.md) 「텍스트에도 네 부류가 있다」가
이미 경고한 축 혼입(`how="지문"`·`prompt`는 표시일 뿐 판정이 아니다)과 같은 뿌리다.

```
m16.e14.p0.c3   ¿Usar Polvo Explosivo?     폭발가루를 사용할까?    layer=PS speaker=golperoca
m116.e36.p0.c87 ¡Oh, vaya! No tienes espacio en tu equipo.   layer=PS who=Zafra
```

`golperoca`(사물지문 그룹의 바위 그림)가 낀 confirm 세 자리(맵16 이벤트14·15, 맵136
이벤트9)는 다른 방향(A2 `object_sprite_bug`)과 거울상이다 — **같은 원인(사물지문 그룹
스프라이트)이 어느 페이지에 있느냐에 따라 층을 양쪽으로 다 어긋나게 만든다.** 나머지는
「파티 가득」·「~할까?」류 정형구가 gitana·mosqueterow·anciano·acrilico4·monjeYantra·
zafraow·pirata·prisionero1 등 여러 인물의 페이지에 흩어져 있다. **이 묶음은 층을 바꿀지
말지가 아니라 "이 줄만 시스템으로 뗄지, 페이지 층을 따를지"의 처방 판단**이 더 필요해
위 넷보다 판정이 무겁다.

## 반대 방향(B)의 한계 — 정직하게 적는다

Z-55의 「반대 방향 20줄」에서 서사 판단이 필요한 자리(맵211 회상 끝 내레이션·맵297
명단1 오귀속)는 이 조사의 기계 신호로 **재현하지 못했다.** 시도한 것과 실패한 이유:

- **동일 원문의 층 교차 대조**(같은 (맵,원문)이 N으로도 PS/PC로도 서는지) — 615건이
  걸렸지만 정밀도가 낮다. 압도 다수가 「같은 정형구를 여러 인물이 각자 다른 맥락에서
  쓰는」 정상 자리였다(예: 크리산토·히소포가 각자의 사연을 1인칭으로 설명하는 대사가
  우연히 다른 인물의 대사와 겹친 경우). 표본을 열어 확인.
- **이름표 상속이 서술문까지 가는 자리**(`how="상속"` & 3인칭 서술 시작 낱말) — 150건
  걸렸으나 표본 30건을 열어 보니 대부분이 정상적인 1인칭 회고 대사였다(정밀도 낮음,
  채점 안 함 — 후보로 못 올린다).

**결론(추정 아님, 이 조사의 관측)**: 방향 B는 방향 A보다 기계 신호의 정밀도가 훨씬
낮다. A는 스프라이트 명단 하나(`person_sprite()`의 그림 신호)만 보면 되지만, B는
「이 문장이 그 인물이 할 법한 말인가」라는 서사 판단이 신호로 안 잡힌다. Z-55의 기존
20줄은 사람이 페이지를 읽어 얻은 것이고, 이 조사는 그중 시스템 정형구로 걸리는 부분
집합(추정 3~4줄)만 재확인했을 뿐 나머지를 독립적으로 재발견하지 못했다 — **B의
추가 후보가 필요하면 사람이 페이지를 읽는 방식을 다시 쓰는 수밖에 없다.**

## 산출

- `docs/log/research/2026-08-18-layer-misassign-candidates.jsonl` (164행, 190KB) — 자리마다
  `id`·`map`·`map_name`·`event`·`page`·`cmd`·`direction`(A/B)·`bucket`·`confidence`·`note`·
  `layer`·`kind`·`how`·`speaker`·`who`·`es`·`ko`·`context`(앞뒤 2줄, 원문+번역+층 표시)를 담는다.
  `context`는 플레이어가 겪는 순서(cmd 오름차순)로 이어 붙여 페이지를 열지 않아도 앞뒤를
  볼 수 있게 했다.
- 이 문서.

## 한계 (전체)

- **정본·`translate/ko/*.jsonl`·`speaker.py`·`sprite-groups.json`은 손대지 않았다.** 위
  cazadorHerido·village 후보를 반영하려면 유지자 판정 뒤 `sprite-groups.json` 편집이 먼저다.
- 이 조사의 스크립트는 스크래치패드에만 있고 저장소에 없다 — 재현하려면 위 「무엇으로
  쟀나」 절의 조건으로 `translate/stage0/sites.jsonl`을 다시 훑으면 된다.
- `functional_pokemon_npc`·`pokemon_village`는 **번역 정본에 이미 값이 있다**(`ko` 칸에
  값이 참) — 층만 바뀌면 되고 새로 번역할 것은 없다. `object_sprite_bug`도 마찬가지다.
- Z-55의 반대 방향 20줄 중 15줄은 이 조사로 재발견하지 못했다 — 기존 티켓의 표가 여전히
  그 15줄의 유일한 재료다.
