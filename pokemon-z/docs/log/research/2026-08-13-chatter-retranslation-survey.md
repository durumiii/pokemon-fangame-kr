# 잡담 층 3,925행 재번역 물결 타당성 조사 (2026-08-13, 읽기 전용)

실행 위치 `/home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z`.
스크립트는 같은 폴더의 `pool.py`(엄격 필터 재현) · `pool2.py`(3,925 재현) ·
`pool3.py`(접기·제외) · `pool4.py`(페르소나 커버리지) · `sample_ch.py`(표본 35).
정본·원장·코드 무수정(`git status` 확인).

## 0. 풀 정의 재현 (실측)

2026-08-09 표본 감사가 쓴 정의 = 엄격(strict) 통과 + 애매 층 flash 트리아지 통과.

```
uv run pool2.py
엄격 1664 · 트리아지통과 192 · 겹침 0
풀 페이지 1856 · text행 3925          ← 티켓·감사 기록의 3,925와 일치
  엄격분 3626 · 통과분 299
```
엄격 필터: `scene=잡담` ∧ `trigger=말걸기` ∧ `n_msg<=6` ∧ 이름표 전무 ∧ `Trainer(n)` 아님 ∧
스프라이트 있음 ∧ `stem(sprite) ∉ 사물지문∪포켓몬특수`. 기계 제외(숫자·trchar·rayos)는
**엄격 판정에 안 들어 있다**(감사 기록의 「누수」와 같은 상태). 교차 검산: 이름표 없는
scene=잡담 페이지 3,142 − 엄격 1,664 = **1,478** = 트리아지 대상 수와 정확히 일치.
트리아지 라벨은 세션 스크래치의 `triage-flash.jsonl`(1,478줄)·`ambiguous.jsonl`이 실물로 남아 있다.

## 1. 접기 후 실규모

접기 규칙은 `batch_pages.dedupe()` 그대로: 통일 원문(`unified_originals()`)은 원문 1회,
그 밖은 (원문, 화자=스프라이트 · 화자 없으면 맵) 1회.

```
uv run pool3.py
== 전체 풀 ==
원본:                 페이지 1856 · 행 3925 · 접은 뒤 종 2946
기계 스프라이트 제외:  페이지 1856 · 행 3715 · 접은 뒤 종 2836
== 보호·승인 제외 후 사정권 ==
원본:                 페이지 1413 · 행 2613 · 접은 뒤 종 2232
기계제외+정본대응:     페이지 1413 · 행 2477 · 접은 뒤 종 2157
   제외로 빠진 페이지 443 (행 1312)
how 분포(사정권): 그림 2295 · 미상 163 · 지문 19
접힘: 1자리 종 1943 · 2자리 이상 214 · 최대 25자리
```

**물어야 할 원문 종 = 2,157** (보호·승인·기계 제외 후). 접기가 깎는 몫은 2,477 → 2,157로
**13%뿐**이다. 규모를 실제로 줄이는 것은 접기가 아니라 **보호·승인 제외(3,925 → 2,477, −37%)**다.

## 2. 결함률 재확인

### 2026-08-09 표본의 정의 (원본 기록 + 그 세션 실행 코드)

- 기록: `docs/log/research/2026-08-09-z4-sample-audit.md` 19~22줄.
  「잡담 층 (유효 74행 — 시스템 오염 5행·기판정 1행 제외): **명시적 결함 9행 ≈ 12%.**
  오역 1 · 원문에 없는 문두 감탄사 1 · 「당신」 번역투 2 · 직역투·어색 3 · 띄어쓰기 1 ·
  말투 문어체 잔존 1. 나머지 88%는 자연스럽다.」
- 추출: 축약본 `/tmp/transcript-digest/e8361145.md` 3,266~3,270줄의 실행 코드 —
  `random.seed(20260809)`, 풀은 **행 단위**(접기 없음), 보호·승인 페이지 **미제외**,
  기계 제외 **미적용**(그래서 시스템 5행이 섞임).

### 이번 표본 35행 (접은 뒤 유니크 원문에서)

```
uv run sample_ch.py     # random.seed(20260813), sorted(keys) 위에서 random.sample(…, 35)
```
사정권(보호·승인 제외 + 기계 제외 + 정본 대응) 2,157종에서 뽑았다. 원시 출력은
`chatter-sample-raw.txt`. 판정: **정상 29 · 의심 5 · 결함 1**.

| # | 자리 | 스프라이트 | 원문(발췌) | 현행(발췌) | 판정·근거 |
|---|---|---|---|---|---|
| 1 | 184:9:0:0 | burguesaow | La Galería de Arte no para de expandirse… | 미술관이 계속 넓어지고 있군요… | 정상 |
| 2 | 135:7:0:1 | mujer2 | aún no nos han robado ni causado demasiado alboroto | 아직 물건을 훔치거나 큰 소동을 일으키진 않았는데 | 정상 |
| 3 | 306:8:0:12 | (미상) | ¡Uy! ¡Je, je, je! ¡Pero qué bonita eres! | 앗! 헤헤헤! 참으로 어여쁘구먼! | 정상 |
| 4 | 392:29:1:0 | ninaSonadoraOW | capturaré a los Pokémon más raros y bonitos | 가장 희귀하고 예쁜 포켓몬들을 잡을 거예요 | 정상 |
| 5 | 243:27:0:0 | burguesow | Es el entrenador el que elige… (원문 자체가 순환문) | 체육관 관장을 선택하는 건 트레이너이고… | 정상 — 원문의 엉킴을 그대로 옮김 |
| 6 | 361:28:0:2 | burguesaow2 | se habrá convertido en todo un bellezón | 아주 아름다운 여성이 되었을 거예요 | 정상 |
| 7 | 13:18:0:0 | hombre1 | no está preparado para gestionar conflictos | 갈등을 해결할 수완은 없지 | 정상(「준비가 안 됐다」→「수완이 없다」 경미한 이동) |
| 8 | 106:15:0:0 | mosqueterow | ¡Me gustan las flores! | 난 꽃을 좋아해! | 정상 |
| 9 | 478:12:0:0 | anciana | esos desalmados | 그 몰염치한 자들 | 정상(무자비→몰염치, 맥락상 수용) |
| 10 | 392:13:0:1 | burguesow | nuestra agua mediterránea | 우리 지중해성 수질 | 정상 |
| 11 | 283:23:0:0 | anciano | tiene a una nueva encargada desde hace un par de años | 2년 전부터 새 관리인이 들어앉았다네 | **의심** — 「들어앉았다」가 원문에 없는 부정적 뉘앙스 |
| 12 | 247:10:1:0 | lenador2 | ¿Habrá llegado el momento de irse? | 이제 떠날 때가 된 걸까? | 정상 |
| 13 | 360:37:0:0 | hombre2 | misteriosos incidentes que acabaron con la vida… | 관객 여럿의 목숨을 앗아간 의문의 사건들 | 정상 |
| 14 | 302:10:1:0 | anciana | me habéis alegrado la tarde | 정말 즐거운 오후를 보냈단다 | 정상 |
| 15 | 482:36:0:98 | (미상) | ¡Los... los Pokémon se han liberado! | 포... 포켓몬들이 풀려났다! | 정상 |
| 16 | 59:18:0:1 | anciana | sin ellos… no sería ni una sombra de lo que es ahora | **그애들이** 없었다면 우리 문명도 지금 같지 않았을 거라는 걸 | **결함** — ① 「그애들」 붙여쓰기(비표준, 정본 전체에서 1건) ② 「ni una sombra de」의 강도가 「지금 같지 않았을」로 소실 |
| 17 | 80:31:0:1 | hombre1 | construyó su laboratorio personal el Regente Sapin | 사핀 섭정이 개인 연구실을 지어 뒀는데 | 정상 |
| 18 | 163:14:0:0 | burguesaow2 | Escapar pitando, ¿sabes? | 쏜살같이 도망치고 싶을 때가 있어요! | **의심** — 물음(¿sabes?)이 사라지고 감탄으로 바뀜 |
| 19 | 310:23:1:0 | mosqueterow | Aférrate a tus Pokémon y a tus amigos. Aunque son lo mismo. | 꼭 의지해라. 둘 다 같은 뜻이긴 하지만. | **의심** — 「포켓몬이 곧 친구다」가 「낱말 뜻이 같다」로 읽힘 |
| 20 | 224:20:0:1 | prisionero2 | mi <i>king</i> … <i>What a bad luck</i> | 내 <i>king</i> … <i>What a bad luck</i> | 정상(원문 영어 유지가 맞다) |
| 21 | 261:11:0:0 | hombre1 | Era como si alguien más estuviese en la habitación | 마치 방에 나 말고 누가 같이 있는 것 같았다고 | 정상 |
| 22 | 161:15:0:0 | campesinaw | una anciana que vive en la catedral | 대성당에 사는 할머니 | 정상 |
| 23 | 20:4:0:0 | mosqueterow | El orgullo de los que no pueden edificar es destruir | 아무것도 건설하지 못하는 자들의 자부심이란 고작 파괴하는 것뿐이다 | 정상 |
| 24 | 226:20:0:1 | carabinerow | Sal del recinto de celdas hacia el patio exterior | 감방 구역을 나가서 바깥 뜰로 가라 | 정상 |
| 25 | 133:10:0:4 | burguesaow2 | Una civilización avanzada es aquella que no come Pokémon | 포켓몬을 먹지 않는 사회야말로 진정 진보한 문명 아니겠어요! | 정상(평서→수사의문, 페르소나 범위) |
| 26 | 4:18:1:1 | anciano | intentar fabricarlas por tu cuenta | 직접 만드는 것도 방법이고 말이지 | 정상 |
| 27 | 296:5:0:1 | alquimista2OW | trataron de reclutarme | 저를 스카우트하려고 하더라고요 | 정상 |
| 28 | 80:23:0:3 | hombre2 | puertas selladas con magia… época de la Reina Fundadora | 마법으로 봉인된 문… 건국 여왕 시절에 | 정상 |
| 29 | 247:16:0:1 | mosqueterow | un plan del Legislador Mirra | 입법관 미라 님이 …계획의 일환이다 | 정상 |
| 30 | 21:13:0:0 | burguesow | ¿Has preparado bien a tu equipo, Aspirante? | 후보생님, 지닌 포켓몬은 잘 준비하셨나요? | 정상 |
| 31 | 179:6:1:1 | burguesaow | Eso es lo que he aprendido en esta cafetería | 카페에서 만나면서 깨달은 게 바로 그거랍니다 | 정상 |
| 32 | 184:5:0:0 | mosqueterow | ¡Te damos la bienvenida a la Galería de Arte! | 미술관에 온 걸 환영한다! | 정상 |
| 33 | 240:4:0:1 | burguesaow | Ahora solo quedan ruinas y despojos | 이제 남은 건 폐허와 잔해뿐인가 보네요 | 정상 |
| 34 | 232:18:0:1 | obrerow | Tengo que recorrerlos cada vez que voy y vengo | 여길 지나쳐야 하는데 | **의심** — 복수 지시(los)가 「여기」로 뭉개짐. 앞줄 문맥 필요 |
| 35 | 50:2:2:0 | brujita | Quiero saber si acaso tú conmigo quieres bailar... | 혹시 나와 함께 춤추고 싶은지 알고 싶구나... | **의심** — 「-구나」가 소녀 화자에 안 맞음(말투 축) |

**결함 1/35 ≈ 3%(95% 상한 대략 15%), 의심 포함 6/35 ≈ 17%.** 오역다운 오역 0건.
결의 방향이 2026-08-09와 다르다 — 그때 결함 9건 중 넷(「당신」 2 · 무근거 감탄사 1 ·
문어체 잔존 1)이 그 뒤 스윕·급 통일로 처리된 축이고, 이번에 남은 것은 문체·강도·
지시 대상 같은 미세 축이다.

## 3. 물결 설계 후보와 비용

### 도구가 닿는가

`translate/batch_pages.py:378`
```python
if npc and (rows[0].get("scene") not in ("컷신", "대화")
            or any(x.get("how") == "태그" for x in rows)):
    continue
```
잡담은 이 한 줄에서 통째로 빠진다. 확장 지점 둘뿐:
1. 위 튜플에 `"잡담"`을 더한다(또는 갈래 인자).
2. `:384` `if r["kind"] != "text" or r["how"] != "그림": continue` — 사정권 2,477행 중
   2,295행이 `그림`이라 그대로도 93%가 잡힌다. 미상 163·지문 19는 남긴다(별건).

그 밖 배관은 그대로 맞는다: `dedupe()`가 npc 갈래에서 화자=스프라이트로 접고,
`excluded_pages()`가 보호·승인·인트로를 뺀다. ⚠ 산출 경로가 `batch_npc.py`와 겹치는
문제(`translate/batch/npc-chunks.jsonl`·`npc-out/`)는 컷신·대화 물결과 동일하게 걸린다 —
잡담을 별도 stem으로 두지 않으면 현행 40페이지 계획을 덮어쓴다.

### 페르소나표 커버리지 (사정권 2,477행 기준, `pool4.py`)

```
등재 스프라이트 행 2177 (88%) · 미등재 스프라이트 37종 137행 · 스프라이트 없는 행 163
미등재 상위: luchador 12 · monjeYantraAnciano 11 · monjaYantraAnciana 9 · rangera 8 ·
             lenador2 8 · carabineraEnow 7 · clerigo 6 · gogoatsGrupo 6 …
```
37종 중 사물·연출이 섞여 있다(portonCerrado · cartaFlotante · guijarros · baya2 · luz ·
nidoIncursion). 사람으로 보이는 20여 종만 등재하면 커버리지는 95%를 넘는다.

### 비용

단가 실측 둘: 이번 파일럿 75행 $0.056(행당 $0.00075, 부모 전달) · `translate/batch/log.txt:625`
766행 $0.45(행당 $0.00059).

| 항목 | 수 | 비용 |
|---|--:|--:|
| 재번역(접은 종) | 2,157 | $1.3 ~ $1.6 |
| 접기 안 했을 때 | 2,477 | $1.5 ~ $1.9 |
| 선별 층(행당 $0.0004) | 2,477 | ~$1.0 |
| 합 | | **$2.3 ~ $2.6** |

돈은 판단 근거가 못 된다 — 세 달러 아래다. 판단 근거는 손교정 뒤엎을 위험과 유지자 판정 시간이다.

### 재번역 모드 (a) 교정형 / (b) 자유 재작성

`docs/guides/events-and-speech.md:45-56`의 처방 등급으로 갈린다.
- **등급 1(순수 행인 잡담)** — 문체까지 자유 재작성이 지침상 허용. 사정권의 다수가 여기다.
- **등급 2(퀘스트·기능 대사)** · **등급 3(전 맵 반복 정형구)** — 내용 고정 / 재작성 금지.
  접힘 2자리 이상 214종은 지침대로 자동으로 3에 가깝게 떨어진다.

의견: **(a) 교정형을 기본으로, 등급 1 중 「의심」 신호가 붙은 자리에만 (b)**. 근거는 표본이다 —
결함 1·의심 5의 성격이 「문장을 새로 쓸 문제」가 아니라 「한 낱말·한 어미가 어긋난 문제」이고,
현행 88%가 자연스럽다는 08-09 판독과 이번 판독이 같은 방향이다. 자유 재작성은 그 88%를
새 문장으로 갈아 끼우며 손교정·통일 상태를 흔든다.

## 확정도·한계

- **실측**: 풀 재현(3,925), 접기 후 종 수, 보호 제외 후 사정권, how 분포, 페르소나 커버리지,
  도구 게이트 줄 번호. 위 스크립트 재실행으로 30초 안에 같은 수.
- **1회 관측**: 표본 35행 판정. 단일 표본이라 층 전체 결함률로 일반화할 수 없다.
- **추정**: 비용표(단가 두 점의 선형 외삽), 「사람 스프라이트 20여 종」 눈대중.
- **미확인**: 트리아지 통과 192페이지의 라벨 품질(그 기록 자체가 「확실 층과 동급 아님」이라 못 박음).
- **한계**: 표본은 접은 뒤 대표 행 하나만 읽었다. 같은 원문의 다른 자리 문맥은 안 봤다.
