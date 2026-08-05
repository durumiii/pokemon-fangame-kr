# 한국어 번역값에 로마자로 남은 낱말 — 전수 조사 (2026-08-05)

조사만 한 문서다. **아무것도 고치지 않았다.** 판정은 유지자 몫이다.

## 조사 방법

`translate/ko/*.jsonl` 24개 파일 전량에서, 한국어(한글)가 한 글자라도 들어 있는
번역값만 골라 로마자 낱말을 뽑았다. 한글이 없는 값은 아예 미번역이거나 엔진·디버그
문자열이라 이번 대상이 아니다.

제어 코드(`\c[N]`, `\PN`, `\v[N]`, `\se[...]` 등)와 태그(`<b>`, `<i>`, `<ac>`)는
낱말로 세기 전에 지웠다.

```
한글 있는 행 중 로마자를 품은 행 1,154 / 서로 다른 로마자 낱말 373 / 등장 1,651회
```

이 373개에서 프랑스어·스페인어 감탄과 상용구, 엔진 식별자(`txt`, `PBS`, `BGM`,
`MysteryGift` 등), 능력치 약어(`HP`, `PP`, `IV`)를 걷어내면 판정 후보는 아래 표들이다.

재현:

```
python3 - <<'EOF'
import json,glob,re,collections
CTRL=re.compile(r'\\[a-zA-Z]+(?:\[[^\]]*\])?|</?[a-zA-Z][^>]*>|\{\d+\}')
TOK=re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]*")
HAN=re.compile(r'[가-힣]')
c=collections.Counter()
for f in sorted(glob.glob('translate/ko/*.jsonl')):
    for l in open(f,encoding='utf-8'):
        v=json.loads(l).get('v') or ''
        if HAN.search(v): c.update(TOK.findall(CTRL.sub(' ',v)))
print(len(c), sum(c.values()))
EOF
```

---

## 1. 이미 쓰이는 한국어 표기가 corpus 안에 있는 것 — 판정이 쉬운 쪽

같은 대상이 다른 행에서는 이미 한국어로 적혀 있다. 마지막 칸은 **찾아낸 것**이지
지어낸 것이 아니다(전거를 함께 적었다).

| 로마자 | 횟수 | 파일:줄 (최대 3) | 문맥 한 조각 | 분류 | 이미 쓰이는 한국어 |
|---|--:|---|---|---|---|
| `Le Prodige` | 10 | `00-maps.jsonl:1249` · `2590` · `3271` (외 7) | 안녕하세요, 제가 바로 **Le Prodige**예요! | 인명(별명) | **르 프로디주** — 같은 대사의 `00-maps.jsonl:11820`이 이미 이렇게 옮겼다 (10:1로 로마자가 우세) |
| `Prímula` | 7 | `00-maps.jsonl:13146` · `13376` · `13388` (외 4) | \c[4]**Prímula:** 누가 이기든 중요한 건 참여하는 거 아니겠어요 | 인명(부활한 여왕) | **프리물라** — `names.json`의 `Primula` 항목, `14-trainer-names.jsonl:359` |
| `Auretosk` | 3 | `00-maps.jsonl:11350` · `12093` · `12095` | \c[6]**Auretosk:** 언제나 그랬듯 내 기지를 발휘하겠다. | 포켓몬명(창작 신격) | **아우레토스크** — 같은 인물 대사 15회 (`00-maps.jsonl:4326`, `10654`, `13475` 등) |
| `Briof` | 3 | `00-maps.jsonl:1161` · `10832` · `10833` | **Briof:** 무슨 일이냐, \PN? | 인명(상인) | **브리오프** — 자기소개 행 `00-maps.jsonl:10831` |
| `Milintercambios` | 3 | `00-maps.jsonl:5749` · `8049` · `8945` | 이런! 결국 **Milintercambios**에 광고를 올려야겠군. | 조직·서비스명(교환 게시판) | **교환 게시판** — 같은 원문의 `00-maps.jsonl:10173`이 이렇게 옮겼다 (3:1로 로마자가 우세) |
| `Dandelio` | 2 | `00-maps.jsonl:1131` · `1138` | **Dandelio:** 안녕하세요, \PN! | 인명(탈옥수) | **단델리오** — `00-maps.jsonl:32`, `7263`~`7270` |
| `Soldados` | 2 | `00-maps.jsonl:10464` · `11038` | **Soldados:** 예, 장군님! | 화자 라벨(일반명사) | **병사들** — 같은 라벨의 `00-maps.jsonl:10440`, `11018`, `11041` |
| `Alca` | 2 | `00-maps.jsonl:13925` · `13934` | \sh\c[9]**Alca:** 이것이 네 마지막 포켓몬 배틀이다! | 인명(최종 흑막) | **알카** — `names.json`, `14-trainer-names.jsonl:105`, 본문 다수 |
| `Barquero` | 1 | `00-maps.jsonl:3476` | **Barquero:** 여러분을 **가라마을** 근처에 내려드릴게요. | 화자 라벨(일반명사) | **뱃사공** — 같은 라벨 20회 (`00-maps.jsonl:222`, `3369`, `14210` 등) |
| `Dusknoir` | 1 | `00-maps.jsonl:6854` | **Dusknoir:** 찾던 것은 이미 얻지 않았나? | 포켓몬명(본가) | **야느와르몽** — 같은 화자 `00-maps.jsonl:6785`, `6798`, `6851` |
| `Melia` | 1 | `00-maps.jsonl:11039` | \sh\c[5]**Melia:** 플로에트! | 인명(여주인공) | **멜리아** — `names.json`, 본문 400여 회 |
| `Cornelio` | 1 | `00-maps.jsonl:12836` | \sh**Cornelio:** 새로운 세상은 우리의 것이다! | 인명 | **콘콤부르** — `names.json`, `14-trainer-names.jsonl:339` |
| `mademoiselle` | 1 | `00-maps.jsonl:3170` | *mademoiselle* **올리비에**, 이번 일에 대해… | 호칭 | **마드모아젤** — 같은 호칭 52회 |
| `Azoth` | 8 | `13-trainer-classes.jsonl:24` · `42` · `47` (외 5) | **Azoth** 연금술사 / **Azoth** 흡혈귀 | 조직(트레이너 클래스) | **아조스** — `glossary.md:75` 「Team Azoth → 팀 아조스」, 본문 다수 |
| `Flare` | 2 | `13-trainer-classes.jsonl:158` · `159` | **Flare** 신입 / **Flare** 보스 | 조직(트레이너 클래스) | **플레어** — `20-place-descs.jsonl:1` 「Laboratorio Flare → 플레어 연구소」. 본가 정식명은 「플레어단」 |
| `Céfira` | 2 | `23-script-texts.jsonl:5672` · `5673` | **Céfira** 도감 | 지방명 | **세피라** — 같은 파일 `23-script-texts.jsonl:5680` |

## 2. 대응하는 한국어 표기를 못 찾은 것 — 빈칸으로 둔다

| 로마자 | 횟수 | 파일:줄 | 문맥 한 조각 | 분류 | 이미 쓰이는 한국어 |
|---|--:|---|---|---|---|
| `Ciudad Porcelana` | 1 | `09-item-descs.jsonl:232` | **Ciudad Porcelana**의 명물. 포켓몬의 상태이상을 치료한다. | 지명 | (없음) |
| `Pueblo Caoba` | 1 | `09-item-descs.jsonl:236` | **Pueblo Caoba**의 명물 사탕. | 지명 | (없음) |
| `Gran Pantano` | 1 | `09-item-descs.jsonl:269` | 위장 무늬 몬스터볼. **Gran Pantano**에서만 쓴다. | 지명 | (없음) |
| `Gastesla` | 1 | `09-item-descs.jsonl:663` | **Gastesla**의 메가진화용 돌. | 포켓몬명(추정) | (없음) |
| `Lunaye` | 1 | `09-item-descs.jsonl:664` | **Lunaye**의 메가진화용 돌. | 포켓몬명(추정) | (없음) |
| `Narvalor` | 1 | `09-item-descs.jsonl:665` | **Narvalor**의 메가진화용 돌. | 포켓몬명(추정) | (없음) |
| `Constellar` | 1 | `06-move-descs.jsonl:728` | **Constellar**의 태양 폼과 달 폼을 전환한다. | 포켓몬명(추정) | (없음) |
| `Partidas Guardadas` | 2 | `00-maps.jsonl:238` · `14229` | 게임 폴더에 저장 데이터 접근용 바로가기("**Partidas Guardadas**") | 실제 폴더 이름 | (없음 — 게임 폴더의 실물 이름이라 번역하면 안내가 틀어진다) |

`09-item-descs`·`06-move-descs`의 네 항목(Gastesla·Lunaye·Narvalor·Constellar)은
`01-species.jsonl`에 같은 이름이 없다. 이 게임 본편 포켓몬이 아니라 보너스·미사용
데이터일 가능성이 있으나 확인하지 못했다.

## 3. 애매 — 판정하지 않고 담아 둔다

| 로마자 | 횟수 | 파일:줄 | 문맥 한 조각 | 왜 애매한가 |
|---|--:|---|---|---|
| `chateau` (소문자) | 2 | `00-maps.jsonl:1181` · `3254` | **삼채시티**의 거대한 *chateau*에 가본 적이… | 고유명이 아니라 이탤릭으로 강조한 프랑스어 보통명사다. 감탄·상용구 제외 규칙에 걸릴 수도, 「저택」으로 옮길 수도 있다. 2026-08-05에 `Chateau Rosillon`·`Chateau Lanto` 같은 **고유명** 쪽은 「…저택」으로 정리했다 |
| `Alca` (클래스 슬롯) | 1 | `13-trainer-classes.jsonl:195` | 값 자체가 `Alca` | 절13은 트레이너 클래스인데 값이 인명이다. 절14의 이름과 화면에서 이어 붙는 자리인지 확인이 필요하다 |
| `Mikolash` | 1 | `23-script-texts.jsonl:6564` | **La Isla de Mikolash**의 수수께끼를 밝혀라 | 철자가 다른 `Micolash`는 `14-trainer-names.jsonl:133`에서 **미콜라시**로 음차돼 있다. 같은 대상인지(블러드본 오마주) 확인 필요. 보너스 이스터에그 계열이라 4번 항목에도 걸린다 |
| `Anthony` · `Brumirage` · `rinkuuart` · `mralmagris` · `EricLostie` · `AbnayamiArt` · `therusan` · `Mothgosw` · `Ogost` · `JuanSegarra` · `Mapestudios` · `Kittybot` · `MrsLucy` · `Lilliacherryart` · `SiestaK` · `Almiart` · `Ankhell` · `CharaFantasy` · `HobCreativo` · `MRKSart` | 각 1~21 | `00-maps.jsonl:6282`·`6301`·`6308`·`11329`·`11331` 등 | \n작가: @**rinkuuart** / \n작가: **Anthony** | 도감 일러스트 작가 크레딧이다. `names.json`의 `keep` 명단에 `EricLostie`가 이미 올라 있어 크레딧은 유지가 기존 방침으로 보이나, 명단에 없는 이름이 대부분이다 |
| `Blyat` · `Dobro pozhalovat` | 3 | `00-maps.jsonl:10027` · `10544` · `12666` | \c[4]**센데라:** *Blyat*! 이 빌어먹을 대장간은 왜 이렇게 덥지! | 러시아어 감탄·인사다. 제외 규칙은 프랑스어 감탄을 말하는데, 같은 장치를 러시아계 인물에게 쓴 것인지 판정이 필요하다 |
| `Mamma mia` · `C'est nes pas` · `Ph'nglui … fhtagn` | 4 | `00-maps.jsonl:9119` · `9124` · `12809` · `8581` | Ph'nglui mglw'nafh Cthulhu R'lyeh… 르뤼에의 도시에서, 죽은 크툴루가… | 이탈리아어 감탄 / 프랑스어 상용구 오타 / 크툴루 주문(뒤에 한국어 번역이 이미 붙어 있다) |

## 4. 이미 판정된 것 — 손대지 않는 게 맞다

### 4-1. 프랑스어 감탄·상용구 (`share/번역표-README.md:187`)

> 대사에 섞인 프랑스어 감탄(monsieur, Sacrebleu ...)은 칼로스 지방의 정서를 담은
> 장치로 보고 그대로 두었습니다.

해당 낱말과 등장 횟수: `Bonjour` 30 · `vous` 25 · `Bon` 23 · `Sacrebleu` 20 ·
`plait` 20 · `Oui` 17 · `mon` 16 · `s'il` 16 · `D'accord` 14 · `Putain` 13 ·
`dieu` 10 · `la` 10 · `bien` 9 · `C'est` 9 · `Merci` 8 · `incroyable` 6 ·
`Merde` 6 · `cheri` 6 · `Magnifique` 5 · `garde` 5 · `Fantastique` 5 · 그 밖
`revoir` · `Enchanté` · `Bonsoir` · `Salut` · `Voilà` · `Zut alors` · `Non` ·
`Pardon` · `désolé` · `mignon` · `folie` · `troupe` 등.

**단, README와 실제 정본이 어긋나는 자리가 하나 있다.** README는 `monsieur`를
유지 대상의 본보기로 들지만, 정본은 이미 **무슈** 140회로 전량 음차했고 로마자
`monsieur`는 0회다(마지막 1행은 2026-08-05 커밋 `2e9be79`에서 정리됐다). 같은
결의 `madame`→**마담** 43회, `mademoiselle`→**마드모아젤** 52회도 마찬가지다.
호칭은 감탄이 아니라 이미 음차 쪽으로 굳었다는 뜻이라, README 문구를 고치든
방침을 다시 적든 한쪽으로 맞추는 게 낫다.

### 4-2. 보너스 콘텐츠 이스터에그 (`glossary.md`)

> 보너스 콘텐츠의 이스터에그 라틴명(Derringer·Makonawa·Missile·Monte Blues·
> Freestylers Studio)은 **원문 유지**(사용자 판정 2026-08-02).

`23-script-texts.jsonl:6520`~`6604`가 보너스 콘텐츠 도전과제 목록이고, 위 다섯
말고도 같은 성격의 팝컬처 오마주 이름이 줄줄이 들어 있다. **명시적으로 판정된 건
다섯뿐이라, 나머지는 같은 계열이라는 내 추정이다.**

같은 블록의 미판정 이름: `Arisca`(6524) · `Andy`(6538) · `Ciudad Bangles`(6542) ·
`Explosiv0`(6544) · `Nirvana`(6546) · `Waluigi`(6560) · `Ciudad Straits` ·
`Indiana`(6562) · `La Isla de Mikolash`(6564) · `Eminemcia`(6572) ·
`Tecnománticos`(6582) · `Freccia` · `Keroro`(6586) · `Pueblo Temptation` ·
`Snoopy`(6588) · `Base Lunar` · `Stain`(6594) · `Nexolimbo` · `Eva`(6596) ·
`Joshua`(6598) · `Baobab`(6600).

---

## 덤으로 눈에 띈 표기 갈라짐 (로마자 문제는 아니다)

조사 중에 드러난 것이라 함께 적어 둔다. 역시 고치지 않았다.

- **프리물라 29회 vs 프리뮬라 16회** — 같은 인물(부활한 여왕)이다. `names.json`과
  절14는 「프리물라」인데, 여왕을 서술하는 본문 계열(`00-maps.jsonl:1954`,
  `2217`, `3989`, `10795` 등)이 「프리뮬라」를 쓴다. 여기에 로마자 `Prímula` 7행이
  더 얹혀 세 갈래다.
- **뱃사공 20회 vs 바케로 1회**(`00-maps.jsonl:7230`) — 같은 화자 라벨 `Barquero`가
  한 자리만 음차로 갔다. 로마자로 남은 `00-maps.jsonl:3476`까지 세 갈래다.
