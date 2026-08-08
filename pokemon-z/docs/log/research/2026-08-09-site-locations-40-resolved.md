# 사이트 위치표 영어 잔존 40행 — 열쇠 실측과 해소 (2026-08-09)

[2026-08-05 위치표](2026-08-05-site-locations-ko.md) 「미해결」 절의 후속. 열쇠 셋을
게임 원본(PBS)으로 실측해 40행 중 17행을 풀었고, 2차 훑기로 나머지의 절반에 후보를
달았다. 조사는 서브에이전트(sonnet) 보고를 부모가 재현 경로로 재검증해 승격했다.

## 열쇠 셋 (전부 실측)

- **Dark Cave = 음침한 동굴**(`Cueva Lóbrega`, 맵 45·200·201). 동굴 지명 20종 중
  「어둡다」 뜻은 이것뿐(배제법). 재현: `grep -i cueva translate/ko/21-map-names.jsonl`
- **Night Stone = Dusk Stone = 어둠의돌**(`Piedra Noche`, 도구 18) ·
  **Day Stone = 빛의돌**(`Piedra Día`, 도구 20, 내부명 SHINYSTONE). 사이트가 같은
  돌을 두 영명으로 섞어 썼다. 위치표의 해당 포켓몬(나옹·데인차·코산호·데스마스·
  코스모움)의 진화 조건이 게임 `PBS/pokemon.txt`에서 전부 DUSKSTONE/SHINYSTONE으로
  일치. 재현: `grep -n "Item,DUSKSTONE" "/mnt/d/Game/Pokemon Z/V2.18/PBS/pokemon.txt"`
- **팬게임 자체 도구 셋** — Hard Bread = **딱딱한빵**(`Pan Duro`, 806 — 설명문이
  파오리를 직접 언급) · Royal Wig = **귀족가발**(`Peluca Regia`, 764) · Wind
  Feather = **바람깃털**(`Pluma Eólica`, 533). 이브이 진화표(pokemon.txt 3739행:
  ROYALEON←귀족가발, CEFIREON←바람깃털)와 파오리→SIRFETCHD(딱딱한빵)가 위치표
  행과 일치. 재현: `grep -n "PANDURO\|PELUCAREGIA\|PLUMAEOLICA" ".../PBS/items.txt"`

## 풀린 17행 (기계 치환)

| 전 | 후 |
|---|---|
| 남부 카타콤 또는 Dark Cave | 남부 카타콤 또는 음침한 동굴 |
| Dark Cave 또는 친밀도 | 음침한 동굴 또는 친밀도 |
| Dark Cave | 음침한 동굴 |
| Dark Cave 또는 진화: — 32레벨 | 음침한 동굴 또는 진화: — 32레벨 |
| Dark Cave (얀트라 사건 이후) | 음침한 동굴 (얀트라 사건 이후) |
| Dark Cave 또는 진화: 탄동 — 18레벨 | 음침한 동굴 또는 진화: 탄동 — 18레벨 |
| 칼로스 동부 전투 또는 Night Stone | 칼로스 동부 전투 또는 어둠의돌 |
| 진화: 코스모움 (Day Stone) | 진화: 코스모움 (빛의돌) |
| 진화: 코스모움 (Night Stone) | 진화: 코스모움 (어둠의돌) |
| 데인차에게 Night Stone 사용 | 데인차에게 어둠의돌 사용 |
| 25번도로 또는 진화: 나옹 — Night Stone. 사용 | 25번도로 또는 진화: 나옹 — 어둠의돌 사용 |
| 코산호에게 Night Stone 사용 | 코산호에게 어둠의돌 사용 |
| 25번도로 또는 진화: 데스마스 — Night Stone. 사용 | 25번도로 또는 진화: 데스마스 — 어둠의돌 사용 |
| 진화: 파오리 — Hard Bread. 사용 | 진화: 파오리 — 딱딱한빵 사용 |
| Revaroom. 교배로 얻는다 | 부르르룸. 교배로 얻는다 |
| 진화: 이브이 — Wind Feather. (완주: 몬테산토섬) 사용 | 진화: 이브이 — 바람깃털 사용 (완주: 몬테산토섬) |
| 진화: 이브이 — Royal Wig. (세르티호섬) 사용 | 진화: 이브이 — 귀족가발 사용 (세르티호섬) |

## 2차 훑기 — 남은 21행의 후보 (확정도 표기)

정본 대조로 자구가 잡힌 것(실측):

- `Mercuric Key` = **수은열쇠**(`Llave Mercúrica`, 도구 758) → 「세뇨리알 대성당 (수은열쇠 문)」
- `Lens Truth` = **진실의렌즈**(`Lente de la Verdad`, 도구 666) → 「프로스트케이브 (진실의렌즈)」
- `Sanguine/Sanguino 카지노` — 마을명은 **상기노**(Pueblo Sanguino) → 「상기노 카지노」
- `Sima Ardiente` = **불타는 구렁**(이미 병기돼 있던 행 — 주석만 정리하면 됨)
- `Pokémon Center` → **포켓몬센터** (일반 명사)

2차 실측 승격(2026-08-09 같은 날 재조사):

- `Fluxus Café` = **카페 페드린**(맵 302) — 위치표의 교환 내용(우츠보트↔흥나숭)과
  같은 교환 대사가 맵 302에 있다. 사이트는 향전시티(Ciudad Fluxus) 소재라 그렇게
  불렀을 뿐이다. 재현: 00-maps에서 「제 흥나숭과 교환」이 든 맵 번호 조회 → 302.
- `Mechanical Heart` = **기계심장**(`Corazón Mecánico`, 도구 866) — 마기아나 부활
  재료로 문맥 일치. 첫 훑기의 「병기의 심장」 후보는 오답이었다(도구표 확인으로 기각).
- `Restaurant`(사프라 보상) = **레스토랑 르 총크**(보데곤마을) — 사프라 퀘스트 대사가
  「Restaurante Le Chonk」를 직접 언급한다(00-maps).

- `Barracks` = **총사 병영** — 유지자 판정(2026-08-09, 실기 지식): 총사 병영에서
  받는 퀘스트가 맞고 보상 배루키도 거기서 받는다. 「3rd Delinquent」는 그 퀘스트의
  세 번째 불량배.

정황상 후보(추정 — 승격 전 확인 필요):

- `Fluxus 호수` — 향전시티의 호수(가이오가 자리). 별도 맵명이 있는지 조사 중.

미확인(대응어 못 찾음 — 사이트 자체 명명일 공산):

`3rd Delinquent` · `Profano Witch 이벤트` · `Endgame Cave` · `Prison Island` ·
`M Embryo` · `station 문` · `by leveling up once`(문형 잔존)

## 반영 자리

위치표의 배포면은 유지자 스프레드시트 「사이트 위치표(한국어)」 탭이다 — 위 표를
그쪽에 반영하는 것은 유지자 몫. 이 문서와 2026-08-05 원본은 기록층이라 원본은
고치지 않는다.
