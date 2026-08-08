# 고유명 3건 조사 — Le Prodige · Milintercambios · Cornelio

조사일 2026-08-05. **판정은 유지자 몫**이고, 이 문서는 재료만 담는다.
모든 인용은 `translate/ko/00-maps.jsonl`(정본)과 `docs/research/map-speaker-join.jsonl.gz`(화자 조인표) 실측이다.

공용 재현 한 줄 (조인표 조회):

```sh
zcat docs/research/map-speaker-join.jsonl.gz | grep '<문자열>' \
  | python3 -c "import sys,json;[print(json.loads(l)['map'],json.loads(l)['map_name'],json.loads(l)['event_name']) for l in sys.stdin]"
```

---

## 조사 1 — `Le Prodige`

### 셈 (원시 수 / 실제 수)

`grep -c "Le Prodige" translate/ko/*.jsonl` → `00-maps.jsonl:11`, 나머지 24개 파일 전부 0.
이 11이 곧 실제 수다(부분 문자열 헛잡음 0건 — 문자열에 공백이 있어 다른 단어에 걸리지 않는다).
그중 **번역문에 로마자가 그대로 남은 행이 10, 「르 프로디주」로 음차된 행이 1**(`00-maps.jsonl:11820`).

```
$ python3 -c "…'Le Prodige' in k / in v…"
es 행: 11 | ko 로마자 잔류: 10
```

확정도: 실측.

### 정체 — 지역을 떠도는 교환 전문 NPC 한 명

11행 전부 같은 대사 `¡Hola, soy <b>Le Prodige</b>!`(= 「안녕하세요, 저는 X예요!」)이고,
조인표에서 **11군데 모두 이벤트 이름·스프라이트가 `prodigio`로 동일**하다.

| 맵 | 맵 이름 | 이벤트 |
|---|---|---|
| 27 | Ruta 4 | 25 |
| 68 | Casa Grande | 1 |
| 91 | Ruta 8 Oeste | 26 |
| 126 | Fort Leviatán | 13 |
| 137 | Ruta 12 | 12 |
| 163 | Ciudad Luminalia - Norte | 6 |
| 258 | Pirineos de Kalos | 28 |
| 284 | Ruta 16 | 11 |
| 360 | Pueblo Sanguino | 33 |
| 375 / 430 | Estación Luminalia | 2 |

같은 이벤트의 전체 대사(맵 27 기준, 11군데가 문구까지 동일):

```
¡Hola, soy <b>Le Prodige</b>!
Puedo cambiarte a uno de tus Pokémon por otro de valor similar según la suma total de sus estadísticas.
¿Qué te parece?
¿No? Pues te pierdes Pokémon maravillosos...
No tengo más Pokémon que ofrecerte por ahora.
Búscame en otros lugares del mundo para seguir haciendo intercambios.
```

마지막 줄 `Búscame en otros lugares del mundo`(= 「세계 다른 곳에서 저를 찾아 주세요」)는
**같은 개인이 여러 지역을 돌아다닌다**는 설정을 못 박는다. 맵 360(Pueblo Sanguino)에서는
`No pensé que me encontrarías, aquí escondido`(「이렇게 숨어 있는 절 찾아내실 줄은 몰랐네요」)로,
숨은 자리를 찾아내는 수집형 NPC임을 확인해 준다.

스프라이트 `/mnt/d/Game/Pokemon Z/V2.18/Graphics/Characters/prodigio.png` 실물 확인 —
넓은 챙 모자 위에 몬스터볼을 잔뜩 얹고 다니는 행상 차림. `translate/sprite-groups.json`에서
그룹 `학자`(`ilustrado`·`cientifico`·`alquimista` 등과 동군)로 묶여 있다.

재현: `zcat docs/research/map-speaker-join.jsonl.gz | grep "Le Prodige"` — 11행, 전부 `prodigio`.
확정도: 실측.

### ① 별명(고유명)으로 읽히는 근거

1. **자기소개 문형이 이름 자리다.** `¡Hola, soy X!`는 스페인어에서 이름을 대는 정형이다.
   보통명사를 넣으면(`soy el prodigio`) 관사 `el`이 붙지 스페인어 문장 한가운데 프랑스어 정관사 `Le`가 오지 않는다.
2. **스페인어 문장 안의 프랑스어 덩어리.** 원문은 스페인어인데 `Le Prodige`만 프랑스어다.
   이 게임은 칼로스(프랑스) 정서를 프랑스어 조각으로 뿌린다 —
   `s'il vous plait`·`oui`·`monsieur`·`mademoiselle`·`madame`가 정본에 그대로 살아 있다
   (`00-maps.jsonl:12294`, `12818`, `12832`). 이 계열의 장식으로 보는 게 자연스럽다.
3. **볼드 처리.** 이 정본에서 `<b>…</b>`는 고유명·중요어에 붙는다. `Cornelio`·`Alca`·`Orden Yantra`와 같은 취급이다.
4. **선례가 있다.** `Restaurante Le Chonk` → 「레스토랑 르 총크」(`00-maps.jsonl:13`).
   프랑스어 `Le` + 명사를 통째로 이름으로 보고 음차한 자리가 이미 정본에 있다.
   `르 X` 음차형은 정본에 흔하다(르 제피르 107회, 르 궁전 38회, 르 그랜드 14회 — `grep -ohE "르 [가-힣]+"` 집계).

### ② 보통명사(「그 천재」)로 읽히는 근거

1. **`prodige`는 뜻이 그대로 읽힌다.** 프랑스어 `prodige` = 천재·신동. 한국 독자에게 음차 「르 프로디주」는 아무 뜻도 전달하지 못한다.
2. **내부 이름이 스페인어 보통명사다.** 이벤트·스프라이트 이름이 `prodigio`(스페인어 「천재」)다.
   즉 제작자가 이 NPC를 부르는 내부 호칭은 이름이 아니라 **역할·별칭**이다.
3. **관사 포함 = 별명 문법.** `Le Prodige`는 성명이 아니라 `정관사+명사` 구조다.
   한국어 「그 천재」·「천재님」처럼 이명(異名)으로 옮기는 쪽이 원문 감각에 가깝다.
4. **본가 대응이 없다.** `translate/canon/messages.jsonl.gz`에 대응 표제가 없다(`probe.py` ④ 미스).
   즉 공식 한국어명이 강제하는 답이 없고, 이 자리는 순전히 판단 문제다.

### ③ 조사자가 더 그럴듯하다고 보는 쪽 — **별명이되 뜻을 살린 이름** (추정)

근거 ①-1(자기소개 문형)이 결정적이라고 본다. 화자가 스스로 대는 호칭이므로
이 게임 안에서는 **고유명 자리**를 차지한다. 다만 근거 ②-1·②-2 때문에
순수 음차(「르 프로디주」)는 독자에게 정보가 0이다 — 스페인어 원어민에게는
`prodige`가 즉시 읽히지만 한국 독자에게 「프로디주」는 읽히지 않는다.
**뜻이 보이는 별명형**으로 옮기는 쪽이 원문의 체감에 가깝다는 게 조사자 소견이다.
확정도: 추정(문형·내부 이름 근거는 실측, 어느 쪽이 나은지는 판단).

### ④ 뜻으로 옮길 때의 한국어 후보

문형이 `안녕하세요, 저는 ___예요!`이므로 뒤에 이름처럼 놓이는 말이어야 한다.

| 후보 | 문장에 넣으면 | 성격 |
|---|---|---|
| **르 프로디주** | 안녕하세요, 저는 **르 프로디주**예요! | 음차. 11820 선례·`르 총크` 선례와 일관. 뜻 전달 0 |
| **천재 씨** | 안녕하세요, 저는 **천재 씨**예요! | 어색 — 자칭에 「씨」는 안 붙는다. 탈락 |
| **그 천재** | 안녕하세요, 제가 바로 **그 천재**예요! | 유지자 안. 「제가 바로」와 붙으면 자연스럽고, 자화자찬 캐릭터로 읽힌다 |
| **천재님** | 안녕하세요, 제가 바로 **천재님**이에요! | 자칭 존칭이라 능청스러움이 살지만 과할 수 있음 |
| **르 천재** | 안녕하세요, 저는 **르 천재**예요! | 프랑스어 관사 + 우리말. 칼로스 정서와 뜻을 동시에 남기는 절충 |

「르 천재」는 [[feedback-no-invented-korean]] 기준(독자가 이미 쓰는 말인가)에 걸릴 소지가 있다 — 판정 필요.

### 한계

- 이 NPC의 **본명**은 정본 어디에도 없다. 다른 NPC가 3인칭으로 언급하는 대사도 0건
  (`grep "Le Prodige"`가 잡은 11행이 전부 본인 자기소개다). 정체는 「이름 없는 떠돌이 교환상」까지가 확인 한계.
- 게임 스크립트 소스(`Scripts.rxdata`)에는 이 문자열이 없다(`probe.py` ③). 맵 이벤트 전용이다.

---

## 조사 2 — `Milintercambios`

### 셈

`grep -c` → `00-maps.jsonl:4`, 나머지 24개 파일 0. 헛잡음 0건.
**로마자 잔류 3행**(`5749`·`8049`·`8945`), **「교환 게시판」으로 옮긴 행 1**(`10173`).

### 정체 — 교환 상대를 못 구한 NPC가 광고를 내겠다는 「중고 거래 사이트」

4행 모두 원문이 한 글자도 다르지 않다:

```
¡Vaya! Al final tendré que poner un anuncio en Milintercambios.
```

조인표 조회 결과, 4군데 모두 **이벤트 이름이 `Trader - Basic`**인 일반 교환 NPC다.

| 맵 | 맵 이름 | 이벤트 | 스프라이트 |
|---|---|---|---|
| 163 | Ciudad Luminalia - Norte | 16 | burguesow |
| 246 | Casa | 12 | mosqueteraw |
| 273 | Centro Pokémon | 3 | burguesaow |
| 308 | Casa | 12 | ranger |

맵 163 이벤트 16의 전체 대사(다른 셋도 포켓몬 이름만 바뀐 같은 틀):

```
Oye, ¿tienes por casualidad uno de esos Electivire?      저기, 혹시 에레키블 하나 가지고 계신가요?
¿No te gustaría cambiarlo por mi Magmortar?              제 마그마번과 교환해보지 않으실래요?
…
¡Vaya! Al final tendré que poner un anuncio en Milintercambios.
```

**용법이 확정된다**: 플레이어가 교환을 거절했을 때 나오는 대사다.
「원하는 포켓몬을 못 구했으니 결국 *어딘가에* 광고를 내야겠다」 — 즉
`Milintercambios`는 **광고를 올리는 곳**이고, 문장 안의 자리는 장소·매체다.

재현: `zcat docs/research/map-speaker-join.jsonl.gz | grep Milintercambios`
확정도: 실측(4행 전부, 이벤트·맵 확인).

### 어원 — 스페인 최대 생활 광고 사이트 `Milanuncios`의 말장난 (추정, 웹 1소스 + 관용구 일치)

- 스페인에 `Milanuncios.com`이 실재한다. 스페인 최대의 무료 생활 광고(중고 거래) 게시판이고,
  이름은 `mil`(천) + `anuncios`(광고)다. 하루 33,000건이 올라오는, 스페인 사람이면 다 아는 사이트다.
  (출처: <https://en.wikipedia.org/wiki/Milanuncios>, <https://www.milanuncios.com/publicar-anuncios-gratis/>)
- 결정적인 건 **관용구가 통째로 일치**한다는 점이다. 스페인어권에서 이 사이트를 쓰는 표현이
  정확히 `poner un anuncio en Milanuncios`(밀아눈시오스에 광고를 올리다)이고,
  게임 원문은 `poner un anuncio en Milintercambios`다. `anuncios` 자리에 `intercambios`(교환)만 갈아 끼운 꼴이다.
- 따라서 `Mil` + `intercambios` = 「천 개의 교환」 = **포켓몬 교환판 중고나라**.
  `mi`+`l`로 쪼개는 독법은 이 관용구 일치를 설명하지 못하므로 배제한다.

확정도: **추정(강)**. 실물 사이트와 관용구는 확인했으나, 제작자가 그 말장난을 의도했다는
직접 증거(제작자 코멘트·크레딧)는 못 찾았다. 게임 내부에 어원을 설명하는 대사도 없다.

### ① 무엇을 가리키는가

게임 세계 안의 **포켓몬 교환 광고 게시판·사이트**. 실물이 등장하는 맵·UI는 없다 —
말로만 언급되는 배경 소품이다(스크립트 소스에도 없음, `probe.py` ③ 「없음」).

### ② 이름인가 기능 설명인가

**이름이다.** 대문자로 시작하고 관사 없이 `en Milintercambios`로 쓰인다.
보통명사라면 `en el tablón de intercambios`처럼 관사가 붙었을 것이다.
다만 **그 이름 자체가 기능을 그대로 말하는 이름**(교환 + 천)이라, 뜻으로 옮겨도 손실이 적다.

### ③ 한국어 후보

이미 `10173`이 「교환 게시판」을 쓰고 있다. 나머지 3행을 여기에 맞출지, 넷 다 다른 쪽으로 갈지가 선택지다.

| 후보 | 문장에 넣으면 | 성격 |
|---|---|---|
| **교환 게시판** | 이런! 결국 **교환 게시판**에 글이라도 올려야겠네요. | 이미 1행이 채택. 뜻은 통하나 고유명 느낌·말장난은 사라진다 |
| **천개교환** | 이런! 결국 **천개교환**에 광고를 올려야겠네요. | `Mil`(천)을 살린 직역 조어. 「중고나라」처럼 서비스명으로 읽힌다. 다만 없는 말을 짓는 셈 |
| **포켓교환마켓** / **교환장터** | 이런! 결국 **교환장터**에 글이라도 올려야겠네요. | 한국 독자에게 「당근·중고나라」의 결이 즉시 전달됨. 고유명 티도 남음 |

셋 다 「원문 말장난은 못 살린다」는 점은 같다 — `Milanuncios`에 해당하는 한국 사이트를
끌어오면(중고나라 등) 현실 상표가 게임에 박히므로 권하지 않는다.
**「교환 게시판」으로 4행을 통일하는 것이 가장 안전**하고, 고유명 맛을 남기고 싶다면 「교환장터」가 차선이라는 게 조사자 소견(추정).

### 한계

- 제작자 의도의 직접 증거 없음. `Milanuncios` 패러디설은 관용구 일치에 기댄 추론이다.
- 이 게임 안에 비교할 만한 다른 실사회 패러디 서비스명을 찾지 못했다
  (`grep -nE "anuncio|foro|página web"` 결과 관련 행은 포켓몬센터 게시판 안내 1건뿐).
  즉 「제작자가 이런 말장난을 즐긴다」는 방증을 확보하지 못했다.

---

## 조사 3 — `Cornelio` = 본가 콘콤부르인가

### 출발점 (부모 확인 사실, 재검증함)

```sh
zcat translate/canon/messages.jsonl.gz | grep -i Cornelio
```

```json
{"es":"¿Sabes cómo se llama en realidad el Megayayo?\n¡Cornelio! …","ko":"메가진화 아저씨...\n그 사람의 진짜 이름은 콘콤부르","src":"xy","kind":"storytext","file":"284"}
{"es":"Cornelio","ko":"주원","src":"oras","kind":"gametext","file":"22"}
```

**둘째 쌍은 무관하다.** ORAS `gametext` 파일 22를 통째로 열어 보면
`수영`·`금청`·`지훈`·`셀리나`·`마리&다이` 같은 값이 100종 들어 있는 **일반 트레이너 이름 목록**이다.
`Cornelio → 주원`은 그 목록에서 무작위로 대응된 잡몹 이름이고, 인물 정체와 무관하다.

재현: `zcat translate/canon/messages.jsonl.gz | python3 -c "import sys,json;[print(json.loads(l)['ko']) for l in sys.stdin if json.loads(l).get('src')=='oras' and json.loads(l).get('file')=='22']" | head -20`
확정도: 실측.

### 셈

`00-maps.jsonl`에서 원문에 `Cornelio`가 있는 행 **14**, 그중 번역문에 로마자가 남은 행 **1**(`12836`).
`14-trainer-names.jsonl:339`에 `{"k":"Cornelio","v":"콘콤부르"}` 표제 1건. 헛잡음 0건.

### ① 동일 인물(=본가 콘콤부르) 근거 — 매우 강하다

세 축이 전부 겹친다.

**직함이 같다.** `00-maps.jsonl:12290`:

```
Yo soy <b>Cornelio</b>, líder de la <b>Orden Yantra</b> y Maestro de la Megaevolución.
나는 콘콤부르, 얀트라 교단의 수장이자 메가진화의 스승이다.
```

`Maestro de la Megaevolución`(메가진화의 스승)은 본가 XY에서 콘콤부르를 가리키는 바로 그 호칭이다.

**있는 장소가 같다.** 조인표에서 이 대사가 나오는 맵은 **397 / 424 `Torre Maestra`**,
소속 도시는 **`Ciudad Yantra`**다. 그리고 `docs/research/2026-08-05-place-name-table.md`가
이미 확정해 둔 대응은:

| 게임 표기 | 본가 영문 | 본가 한국어 | 근거 줄 |
|---|---|---|---|
| Torre Maestra | Tower of Mastery | 마스터타워 | place-name-table.md:215 |
| Ciudad Yantra | Shalour City | 사라시티 | place-name-table.md:36 |

본가에서 콘콤부르가 있는 곳이 **사라시티의 마스터타워**다. 완전 일치다.

**가문 설화가 같다.** `00-maps.jsonl:12328`~`12330`(맵 399 포켓몬센터, 얀트라 수도사):

```
El jefe de nuestra orden es el venerable monje <b>Cornelio</b>.
Su antepasado fue la primera persona en lograr una Megaevolución en la región de <b>Kalos</b>. Y lo hizo a través de su Lucario.
```

「그의 조상이 칼로스 최초로, 루카리오로 메가진화를 이뤘다」 — 본가 콘콤부르 가문 설정 그대로다.
맵 397의 안내판들도 이를 되풀이한다: `Lucario fue el primer Pokémon en megaevolucionar. Y lo hizo dentro de esta torre.`
(「루카리오가 최초로 메가진화한 포켓몬이며, 바로 이 탑 안에서였다」)

재현: `grep -n "Cornelio\|Orden Yantra" translate/ko/00-maps.jsonl`
확정도: 실측.

### ② 별개 인물(조상·동명이인) 근거 — 시대가 안 맞는다

**이 게임의 무대는 본가 XY 현재가 아니다.** 연대 언급을 모으면:

| 정본 줄 | 내용 |
|---|---|
| `00-maps.jsonl:13069` | 「**최종병기**는 **300년 전** … 한 청년에 의해 봉인되었다」 |
| `00-maps.jsonl:13097` | 「**300년 전** 칼로스를 휩쓴 대격전 이후 그 모습을 갖추게 되었다」 |
| `00-maps.jsonl:1532` | 「칼로스 지방은 **1000년 전** … 세워졌습니다」 |
| `00-maps.jsonl:12558` | 「사라시티는 약 **500년 전** 말보 왕에게 포위당한 뒤 단절되었습니다」 |

본가 XY에서 AZ의 전쟁과 최종병기는 **3000년 전**이다. 이 게임에서는 **300년 전**이고,
AZ 본인이 살아서 대사를 한다(`00-maps.jsonl:9370`~`9375`). 즉 본가 현재보다 **한참 이전 시대**다.

**세계 구조도 재설계돼 있다.** 체육관 8개·사천왕 대신 **12명의 섭정(12 Regentes)** 체제이고
(`00-maps.jsonl:63`, `283`, `286`), 얀트라 교단은 이 게임 고유의 종교 조직이다.
본가에서 콘콤부르는 교단의 수장이 아니다.

**성격이 다르다.** 이 게임의 콘콤부르는 후반부에 **적으로 돌아선다** —
`00-maps.jsonl:12836` `¡El nuevo mundo nos pertenece a nosotros! ¡Postraos ahora mismo!`
(「새로운 세상은 우리의 것이다! 당장 무릎을 꿇어라!」), 패배 후 `12838`
`¡La Orden Yantra... es eterna!`. 본가의 온화한 노스승과 전혀 다른 인물상이다.

**이 게임은 본가 이름을 다른 시대에 재배치하는 습관이 있다.** 사천왕 드라세나(Drácena)는
여기서 얀트라 교단의 **suma sacerdotisa**(대사제)로 말보 왕을 섬긴다(맵 209 `Cámaras de Reflexión`).
`docs/research/2026-08-01-z-names-proposal.md:390`도 같은 관찰을 남겨 뒀다 —
「이 게임이 사천왕을 '상급 기사단'으로 재해석했으므로 … 공식 한국어명을 쓸지 음차할지 자체가 사용자 결정 사항」.

확정도: 실측(연대·직함·대사 전부 정본 줄로 확인).

### 「어쩌다 콘콤부르가 됐나」에 대한 답

번역이 지어낸 게 아니다. **본가 스페인어판이 이 인물을 `Cornelio`로 부르고, 본가 한국어판이 그를 「콘콤부르」로 부른다.**
위 XY `storytext` 쌍이 두 이름을 한 문장 안에서 직접 연결한다.
정본 `14-trainer-names.jsonl:339`의 표제가 그 대응을 그대로 받아 적용한 결과다.

### ③ 판정이 갈릴 때 무엇을 더 보면 닫히는가

정리하면, **역할·장소·가문 설화는 본가 콘콤부르와 완전히 겹치고, 시대와 성격은 어긋난다.**
「본가 그 인물의 먼 조상에게 같은 이름과 같은 자리를 준 재해석」으로 읽는 게 관측에 가장 잘 맞는다(추정).
다만 이건 결국 **번역 방침의 문제**지 사실 규명의 문제가 아니다 —
같은 자리·같은 직함이면 본가 정식명을 쓸지, 재해석 인물로 보고 음차할지는
`2026-08-01-z-names-proposal.md:390`이 이미 「사용자 결정 사항」으로 넘겨 둔 항목이다.

그래도 재료를 더 굳히고 싶다면 확인할 것:

1. **콜니(Corelia)의 부재.** 본가에서 콘콤부르의 손녀인 사라시티 체육관 리더 콜니는
   이 게임 정본에 **한 행도 없다**(`grep "Corelia\|Korrina\|콜니" translate/ko/*.jsonl` → 관련 0건;
   `14-trainer-names.jsonl:271`의 「라스콜니코프」가 부분 문자열로 걸린 1건이 전부다).
   후손이 아직 없다는 뜻이므로 **조상 세대 쪽 방증**이다. (실측)
2. **제작자 문서.** 게임 크레딧·공식 위키에 인물 계보 설명이 있는지 — 미조사.
3. **다른 본가 재배치 인물들의 처리와 일관성.** 드라세나·말보·플라드리 등이 정본에서
   본가 정식명으로 갔는지 음차로 갔는지를 한 표로 놓고 보면, 콘콤부르만 따로 판단할 이유가 없어진다.
   현재 정본은 드라세나·콘콤부르 모두 본가 정식명을 쓰고 있다.

### 한계

- 이 게임의 콘콤부르가 본가 인물의 **조상이라고 명시하는 대사는 없다**.
  게임은 「그의 조상이 최초 메가진화자」라고만 말할 뿐, 그의 후손에 대해서는 침묵한다.
  침묵은 부정의 증거가 아니므로 「별개 인물임이 확정」이라고 쓸 수 없다.
- 게임 밖 자료(제작자 인터뷰·공식 위키)는 조사하지 않았다.

---

## 세 건 공통 — 확인한 것과 못 한 것

- 세 문자열 모두 **게임 스크립트 소스에는 없다**(`probe.py` ③ 전부 「없음」). 맵 이벤트 텍스트 전용이라
  정본 jsonl만 고치면 되는 자리다. (실측)
- `korean.dat` 절23 조회는 세 건 다 MISS다(`probe.py` ①) — 아직 빌드에 반영되지 않은 상태를 뜻할 뿐,
  키 어긋남 판정으로 읽지 말 것.
- **아무 파일도 수정하지 않았고, 빌드·주입 도구도 실행하지 않았다.** `probe.py`(읽기 전용)만 돌렸다.
