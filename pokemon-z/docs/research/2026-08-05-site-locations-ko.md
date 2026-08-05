# 사이트 포켓몬 위치표 — 한국어판

2026-08-05 작성. pokemonzfangame.com의 포켓몬 위치 안내 페이지를 크롤해 포켓몬 이름과
지명을 우리 한글패치 표기로 바꾼 것이다. 공략을 보면서 게임 화면의 이름으로 바로 찾으라고 만들었다.
조건 문구는 게임 화면 문구가 아니라 공략 설명문이라 간결한 평서로 옮겼다.

행 수 1108. 원표 3칸(번호·포켓몬·입수 방법)에 한국어 칸을 더했다.

## 어떻게 뽑았는지

손으로 옮긴 자리는 없다. 이름은 전부 표 조회로 바꿨다.

1. 페이지를 받는다(11개, 각 200~380KB).
   `curl -sL -A "Mozilla/5.0" https://pokemonzfangame.com/<슬러그>/ -o <슬러그>.html`
   슬러그는 `gen-1-pokemon-locations`, `gen-2`~`gen-9-pokemon-location`,
   `all-legendary-pokemon-locations`, `all-new-fakemon-locations`.
2. `<tr>`에서 `<td>` 3칸을 뽑는다. 머리글 행(`<th>`)은 버린다. 모든 페이지가 같은
   3칸 구조(번호 · 포켓몬 · 입수 방법)라 페이지별 예외 처리가 필요 없었다.
3. **포켓몬 이름**: `translate/canon/canon.jsonl`의 species 도메인에서 `en` → `ko`.
   여기서 안 잡히는 팬게임 자체 종은 `translate/ko/01-species.jsonl`의 `es` → `v`로
   한 번 더 본다(페이크몬은 원문 이름이 영어 표기와 같다).
4. **지명**: `docs/research/2026-08-05-place-name-table.jsonl`의 `site_en` → `ko`.
   사이트가 한 곳을 여러 이름으로 부르는 변형도 전부 열쇠로 쓴다. 긴 이름부터 맞춰
   `Grisalla Cave`가 `Grisalla City`로 잘못 잡히지 않게 했다.
5. **도구·기술 이름**: 같은 canon 파일의 items·moves 도메인에서 `en` → `ko`.
   화석 4종·왕의징표석·진화의 돌이 여기서 풀린다.
6. **인물 이름**: `translate/ko/00-maps.jsonl`의 퀘스트 문구는 고유명사를 `<b>`로 감싸고
   있다. 원문과 번역문의 `<b>` 짝 수가 같은 줄만 골라 짝지어 대조표를 만들었다
   (크리산토·이시도라·사프라 등). 이 방식은 짝 수가 어긋나는 줄을 버리므로 오정렬이 없다.
7. **조건 문구**: 문형 규칙 120여 개(진화·교배·교환·포획·화석·위치 수식어)를 순서대로
   적용한다. 순서가 중요하다 — 지명을 먼저 바꾸고, 문형, 도구·기술, 마지막에 포켓몬
   이름과 인물 이름을 바꾼다. 긴 이름부터 맞춰 `Grisalla Cave`가 `Grisalla City`로
   잘못 잡히지 않게 했고, `Ancient Power`(기술)가 `Ancient`(수식어)로 깨지지 않게 했다.
8. 조사(을/를·와/과·이/가)는 규칙이 만든 자리에만 표시자를 심고 앞 글자 받침으로 고른다.
9. 조회로 안 풀린 것은 원문을 그대로 두고 「미해결」 절에 모았다. 추측으로 채우지 않았다.

## 위치표

### 1세대 (151행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 001 | 이상해씨 | Bulbasaur | 카페 보에미엔 / 올레오시티 | Café Bohemie / Óleo City | 고고트와 교환 — 카페 보에미엔 (올레오시티) |
| 002 | 이상해풀 | Ivysaur |  |  | 이상해씨를 18레벨까지 키우면 진화 |
| 003 | 이상해꽃 | Venusaur |  |  | 이상해풀을 45레벨까지 키우면 진화 |
| 004 | 파이리 | Charmander | 카페 보에미엔 / 올레오시티 | Café Bohemie / Óleo City | 날쌩마와 교환 — 카페 보에미엔 (올레오시티) |
| 005 | 리자드 | Charmeleon |  |  | 파이리를 18레벨까지 키우면 진화 |
| 006 | 리자몽 | Charizard |  |  | 리자드를 45레벨까지 키우면 진화 |
| 007 | 꼬부기 | Squirtle | 카페 보에미엔 / 올레오시티 | Café Bohemie / Óleo City | 블로스터와 교환 — 카페 보에미엔 (올레오시티) |
| 008 | 어니부기 | Wartortle |  |  | 꼬부기를 18레벨까지 키우면 진화 |
| 009 | 거북왕 | Blastoise |  |  | 어니부기를 45레벨까지 키우면 진화 |
| 010 | 캐터피 | Caterpie |  |  | 버터플 교배로 얻는다 |
| 011 | 단데기 | Metapod |  |  | 캐터피를 9레벨까지 키우면 진화 |
| 012 | 버터플 | Butterfree | 미르시티 - 서쪽 | West Luminalia City | 미르시티 - 서쪽 |
| 013 | 뿔충이 | Weedle |  |  | 독침붕 교배로 얻는다 |
| 014 | 딱충이 | Kakuna |  |  | 뿔충이를 9레벨까지 키우면 진화 |
| 015 | 독침붕 | Beedrill | 미르시티 - 서쪽 | West Luminalia City | 미르시티 - 서쪽 |
| 016 | 구구 | Pidgey | 2번도로 | Route 2 | 2번도로 |
| 017 | 피죤 | Pidgeotto |  |  | 구구를 18레벨까지 키우면 진화 |
| 018 | 피죤투 | Pidgeot | 휴게소 | Service Station | 휴게소 또는 진화: 피죤 — 36레벨 |
| 019 | 꼬렛 | Rattata | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 020 | 레트라 | Raticate |  |  | 꼬렛을 20레벨까지 키우면 진화 |
| 021 | 깨비참 | Spearow | 4번도로 | Route 4 | 4번도로 |
| 022 | 깨비드릴조 | Fearow |  |  | 깨비참을 20레벨까지 키우면 진화 |
| 023 | 아보 | Ekans | 비닐로마을 | Vinyl Town | 비닐로마을 |
| 024 | 아보크 | Arbok | 12번도로 | Route 12 | 12번도로 또는 진화: 아보 — 22레벨 |
| 025 | 피카츄(Z) | Pikachu (Z) | 3번도로 / 아크릴리코마을 | Route 3 / Acrylic Town | 3번도로 또는 — 아크릴리코마을 |
| 026 | 라이츄(Z) | Raichu (Z) |  |  | 피카츄 Z에게 천둥의돌 사용 |
| 027 | 모래두지 | Sandshrew | 5번도로 | Route 5 | 5번도로 |
| 028 | 고지 | Sandslash |  |  | 모래두지를 22레벨까지 키우면 진화 |
| 029 | 니드런♀ | Nidoran♀ | 2번도로 | Route 2 | 2번도로 |
| 030 | 니드리나 | Nidorina |  |  | 니드런♀를 16레벨까지 키우면 진화 |
| 031 | 니드퀸 | Nidoqueen |  |  | 니드리나에게 달의돌 사용 |
| 032 | 니드런♂ | Nidoran♂ | 2번도로 | Route 2 | 2번도로 |
| 033 | 니드리노 | Nidorino |  |  | 니드런♂를 16레벨까지 키우면 진화 |
| 034 | 니드킹 | Nidoking |  |  | 니드리노에게 달의돌 사용 |
| 035 | 삐삐 | Clefairy | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 |
| 036 | 픽시 | Clefable |  |  | 삐삐에게 달의돌 사용 |
| 037 | 식스테일 | Vulpix | 7번도로 | Route 7 | 7번도로 (2부) |
| 038 | 나인테일 | Ninetales |  |  | 식스테일에게 불꽃의돌 사용 |
| 039 | 푸린 | Jigglypuff | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 040 | 푸크린 | Wigglytuff | 포켓몬마을 | Pokémon Villa | 포켓몬마을 또는 진화: 푸린 — 달의돌 사용 |
| 041 | 주뱃 | Zubat | 그리사야 동굴 / 빛나는 동굴 | Grisalla Cave / Refulgent Cave | 그리사야 동굴 또는 빛나는 동굴 |
| 042 | 골뱃 | Golbat | 남부 카타콤 | Southern Catacombs | 남부 카타콤 또는 진화: 주뱃 — 22레벨 |
| 043 | 뚜벅쵸 | Oddish | 올레오시티 | Óleo City | 올레오시티 |
| 044 | 냄새꼬 | Gloom |  |  | 뚜벅쵸를 21레벨까지 키우면 진화 |
| 045 | 라플레시아 | Vileplume |  |  | 냄새꼬에게 리프의돌 사용 |
| 046 | 파라스(Z) | Paras (Z) | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 047 | 파라섹트(Z) | Parasect (Z) | 옛 바니타스 | Old Vanitas | 옛 바니타스 또는 진화: 파라스 (Z) — 22레벨 |
| 048 | 콘팡 | Venonat | 7번도로 | Route 7 | 7번도로 (1부) |
| 049 | 도나리 | Venomoth |  |  | 콘팡을 31레벨까지 키우면 진화 |
| 050 | 디그다 | Diglett |  |  | 닥트리오 교배로 얻는다 |
| 051 | 닥트리오 | Dugtrio | 끝의 동굴 | Terminus Cave | 끝의 동굴 |
| 052 | 나옹 | Meowth | 백단시티 | Novarte City | 백단시티 |
| 053 | 페르시온 | Persian |  |  | 나옹을 28레벨까지 키우면 진화 |
| 054 | 고라파덕 | Psyduck | 1번도로 / 2번도로 | Route 1 / Route 2 | 1번도로 또는 2번도로 |
| 055 | 골덕 | Golduck |  |  | 고라파덕을 30레벨까지 키우면 진화 |
| 056 | 망키 | Mankey | 비닐로마을 | Vinyl Town | 비닐로마을 |
| 057 | 성원숭 | Primeape |  |  | 망키를 28레벨까지 키우면 진화 |
| 058 | 가디 | Growlithe | 왕들의 성소 | Kings’ Sanctuary | 왕들의 성소 |
| 059 | 윈디 | Arcanine |  |  | 가디에게 불꽃의돌 사용 |
| 060 | 발챙이 | Poliwag | 1번도로 | Route 1 | 1번도로 |
| 061 | 슈륙챙이 | Poliwhirl | 13번도로 | Route 13 | 13번도로 또는 진화: 발챙이 — 22레벨 |
| 062 | 강챙이 | Poliwrath |  |  | 슈륙챙이에게 물의돌 사용 |
| 063 | 캐이시 | Abra | 콜라주마을 | Collage Town | 콜라주마을 |
| 064 | 윤겔라 | Kadabra | 13번도로 | Route 13 | 13번도로 또는 진화: 캐이시 — 16레벨 |
| 065 | 후딘 | Alakazam | 서부 카타콤 | Western Catacombs | 서부 카타콤 또는 진화: 윤겔라 — 45레벨 |
| 066 | 알통몬 | Machop | 프로파노마을 | Profane Town | 프로파노마을 |
| 067 | 근육몬 | Machoke | 프로파노마을 | Profane Town | 프로파노마을 또는 진화: 알통몬 — 16레벨 |
| 068 | 괴력몬 | Machamp |  |  | 근육몬을 45레벨까지 키우면 진화 |
| 069 | 모다피 | Bellsprout | 콜라주마을 | Collage Town | 콜라주마을 |
| 070 | 우츠동 | Weepinbell | 15번도로 | Route 15 | 15번도로 또는 진화: 모다피 — 21레벨 |
| 071 | 우츠보트 | Victreebel |  |  | 우츠동에게 리프의돌 사용 |
| 072 | 왕눈해 | Tentacool | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 073 | 독파리 | Tentacruel | 해저 | Seafloor | 해저 또는 진화: 왕눈해 — 30레벨 |
| 074 | 꼬마돌 | Geodude | 음침한 동굴 | Gloomy Cave | 음침한 동굴 |
| 075 | 데구리 | Graveler | 음침한 동굴 | Gloomy Cave | 음침한 동굴 또는 진화: 꼬마돌 — 25레벨 |
| 076 | 딱구리 | Golem |  |  | 데구리를 45레벨까지 키우면 진화 |
| 077 | 포니타 | Ponyta | 12번도로 | Route 12 | 12번도로 |
| 078 | 날쌩마 | Rapidash | 12번도로 | Route 12 | 12번도로 또는 진화: 포니타 — 40레벨 |
| 079 | 야돈 | Slowpoke | 그리사야 동굴 / 음침한 동굴 / 비닐로마을 | Grisalla Cave / Gloomy Cave / Vinyl Town | 그리사야 동굴, 음침한 동굴, 또는 비닐로마을 |
| 080 | 야도란 | Slowbro | 19번도로 | Route 19 | 19번도로 또는 진화: 야돈 — 37레벨 |
| 081 | 코일 | Magnemite | 올레오시티 / 빛나는 동굴 | Óleo City / Refulgent Cave | 올레오시티 또는 빛나는 동굴 |
| 082 | 레어코일 | Magneton |  |  | 코일에게 천둥의돌 사용 |
| 083 | 파오리 | Farfetch’d | 13번도로 / 19번도로 / 왕들의 성소 | Route 13 / Route 19 / Kings’ Sanctuary | 13번도로, 19번도로, 또는 왕들의 성소 |
| 084 | 두두 | Doduo |  |  | 두트리오 교배로 얻는다 |
| 085 | 두트리오 | Dodrio | 16번도로 | Route 16 | 16번도로 |
| 086 | 쥬쥬 | Seel | 18번도로 | Route 18 | 18번도로 |
| 087 | 쥬레곤 | Dewgong |  |  | 쥬쥬를 34레벨까지 키우면 진화 |
| 088 | 질퍽이 | Grimer | 올레오시티 | Óleo City | 올레오시티 |
| 089 | 질뻐기 | Muk |  |  | 질퍽이를 32레벨까지 키우면 진화 |
| 090 | 셀러 | Shellder | 리엔소마을 | Canvas Town | 리엔소마을 (리엔소마을) |
| 091 | 파르셀 | Cloyster |  |  | 셀러에게 물의돌 사용 |
| 092 | 고오스 | Gastly | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 093 | 고우스트 | Haunter | 프로파노 늪 / 5번도로 | Profane Swamp / Route 5 | 프로파노 늪, 5번도로 묘지 이벤트, 또는 진화: 고오스 — 25레벨 |
| 094 | 팬텀 | Gengar | 포켓몬 요새 | Vanitas Bastion | 포켓몬 요새 또는 진화: 고우스트 — 45레벨 |
| 095 | 롱스톤 | Onix | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 |
| 096 | 슬리프 | Drowzee | 3번도로 | Route 3 | 3번도로 |
| 097 | 슬리퍼 | Hypno | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 또는 진화: 슬리프 — 26레벨 |
| 098 | 크랩 | Krabby | 리엔소마을 | Canvas Town | 리엔소마을 (리엔소마을) |
| 099 | 킹크랩 | Kingler |  |  | 크랩을 28레벨까지 키우면 진화 |
| 100 | 찌리리공 | Voltorb | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 |
| 101 | 붐볼 | Electrode | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 또는 진화: 찌리리공 — 30레벨 |
| 102 | 아라리 | Exeggcute | 9번도로 | Route 9 | 9번도로 |
| 103 | 나시 | Exeggutor | 몬테산토섬 | Montesanto Island | 몬테산토섬 또는 진화: 아라리 — 리프의돌 사용 |
| 104 | 탕구리(Z) | Cubone (Z) | 음침한 동굴 | Gloomy Cave | 음침한 동굴 |
| 105 | 텅구리(Z) | Marowak (Z) | 음침한 동굴 | Gloomy Cave | 음침한 동굴 또는 진화: 탕구리 (Z) — 28레벨 |
| 106 | 시라소몬 | Hitmonlee |  |  | 배루키를 23레벨까지 키우면 진화 (공격이 방어보다 높을 때) |
| 107 | 홍수몬 | Hitmonchan |  |  | 배루키를 23레벨까지 키우면 진화 (공격이 방어보다 낮을 때) |
| 108 | 내루미 | Lickitung | 21번도로 | Route 21 | 21번도로 |
| 109 | 또가스 | Koffing | 불탄 공방 | Burned Workshop | 불탄 공방 |
| 110 | 또도가스 | Weezing |  |  | 또가스를 30레벨까지 키우면 진화 |
| 111 | 뿔카노 | Rhyhorn | 10번도로 | Route 10 | 10번도로 |
| 112 | 코뿌리 | Rhydon | 휴게소 | Service Station | 휴게소 또는 진화: 뿔카노 — 30레벨 |
| 113 | 럭키 | Chansey | 이설시티 | Fractal City | 이설시티 |
| 114 | 덩쿠리 | Tangela | 5번도로 | Route 5 | 5번도로 |
| 115 | 캥카 | Kangaskhan | 13번도로 | Route 13 | 13번도로 |
| 116 | 쏘드라 | Horsea | 11번도로 | Route 11 | 11번도로 |
| 117 | 시드라 | Seadra |  |  | 쏘드라를 32레벨까지 키우면 진화 |
| 118 | 콘치 | Goldeen |  |  | 왕콘치 교배로 얻는다 |
| 119 | 왕콘치 | Seaking | 16번도로 | Route 16 | 16번도로 |
| 120 | 별가사리 | Staryu | 로시욘 저택 | Chateau Rosillon | 로시욘 저택 |
| 121 | 아쿠스타 | Starmie | 향전시티 | Fluxus City | 향전시티 |
| 122 | 마임맨 | Mr. Mime | 기남시티 / 올레오시티 | Batik City / Óleo City | 기남시티 and 올레오시티 |
| 123 | 스라크 | Scyther | 8번도로 | Route 8 | 8번도로 |
| 124 | 루주라 | Jynx | 이설시티 | Fractal City | 이설시티 |
| 125 | 에레브 | Electabuzz | 폭풍 언덕 | Storm Hill | 폭풍 언덕 |
| 126 | 마그마 | Magmar | 불탄 공방 | Burned Workshop | 불탄 공방 |
| 127 | 쁘사이저 | Pinsir | 8번도로 | Route 8 | 8번도로 |
| 128 | 켄타로스 | Tauros | 21번도로 | Route 21 | 21번도로 |
| 129 | 잉어킹 | Magikarp | 향전시티 | Fluxus City | 잠수 — 향전시티 |
| 130 | 갸라도스 | Gyarados | 24번도로 | Route 24 | 24번도로 또는 진화: 잉어킹 — 20레벨 |
| 131 | 라프라스 | Lapras | 프로스트케이브 | Frozen Grotto | 프로스트케이브 |
| 132 | 메타몽 | Ditto | 5번도로 | Route 5 | 5번도로 |
| 133 | 이브이 | Eevee | 포켓몬마을 | Pokémon Villa | 포켓몬마을 또는 스카프를 돌려준 뒤 — 이시도라 |
| 134 | 샤미드 | Vaporeon |  |  | 이브이에게 물의돌 사용 |
| 135 | 쥬피썬더 | Jolteon |  |  | 이브이에게 천둥의돌 사용 |
| 136 | 부스터 | Flareon |  |  | 이브이에게 불꽃의돌 사용 |
| 137 | 폴리곤(Z) | Porygon (Z) | 불탄 공방 | Burned Workshop | 불탄 공방 |
| 138 | 암나이트 | Omanyte | 페트로 동굴 / 배롱마을 | Petro Cave / Mosaic Town | 페트로 동굴에서 화석을 얻어 다음에서 되살린다 — 배롱마을 |
| 139 | 암스타 | Omastar |  |  | 암나이트를 35레벨까지 키우면 진화 |
| 140 | 투구 | Kabuto | 페트로 동굴 / 배롱마을 | Petro Cave / Mosaic Town | 페트로 동굴에서 화석을 얻어 다음에서 되살린다 — 배롱마을 |
| 141 | 투구푸스 | Kabutops |  |  | 투구를 35레벨까지 키우면 진화 |
| 142 | 프테라 | Aerodactyl | 페트로 동굴 / 배롱마을 | Petro Cave / Mosaic Town | 페트로 동굴에서 화석을 얻어 다음에서 되살린다 — 배롱마을 |
| 143 | 잠만보 | Snorlax | 25번도로 | Route 25 | 25번도로 또는 진화: 먹고자 친밀도로 진화 |
| 144 | 프리져 | Articuno | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 |
| 145 | 썬더 | Zapdos | 폭풍 언덕 | Storm Hill | 폭풍 언덕 |
| 146 | 파이어 | Moltres | 불타는 구렁 | Burning Abyss / Fiery Chasm | 불타는 구렁 (불타는 구렁 / Sima Ardiente) |
| 147 | 미뇽 | Dratini | 18번도로 | Route 18 | 18번도로 |
| 148 | 신뇽 | Dragonair |  |  | 미뇽을 30레벨까지 키우면 진화 |
| 149 | 망나뇽 | Dragonite | 23번도로 | Route 23 | 23번도로 또는 진화: 신뇽 — 55레벨 |
| 150 | 뮤츠 | Mewtwo | 플레어 연구소 | Flare Laboratory | 플레어 연구소 (전설 위치 안내 참고) |
| 151 | 뮤 | Mew | 탈라시아 동굴 | Talasia Cave | 탈라시아 동굴 |

### 2세대 (100행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 152 | 치코리타 | Chikorita | 레스토랑 르 총크 / 보데곤마을 | Lechonk Restaurant / Bodegón Town | 아르코와 교환 — 레스토랑 르 총크 (보데곤마을) |
| 153 | 베이리프 | Bayleef |  |  | 치코리타를 18레벨까지 키우면 진화 |
| 154 | 메가니움 | Meganium |  |  | 베이리프를 45레벨까지 키우면 진화 |
| 155 | 브케인 | Cyndaquil | 레스토랑 르 총크 / 보데곤마을 | Lechonk Restaurant / Bodegón Town | 날쌩마와 교환 — 레스토랑 르 총크 (보데곤마을) |
| 156 | 마그케인 | Quilava |  |  | 브케인을 18레벨까지 키우면 진화 |
| 157 | 블레이범 | Typhlosion |  |  | 마그케인을 45레벨까지 키우면 진화 |
| 158 | 리아코 | Totodile | 레스토랑 르 총크 / 보데곤마을 | Lechonk Restaurant / Bodegón Town | 로파파와 교환 — 레스토랑 르 총크 (보데곤마을) |
| 159 | 엘리게이 | Croconaw |  |  | 리아코를 18레벨까지 키우면 진화 |
| 160 | 장크로다일 | Feraligatr |  |  | 엘리게이를 45레벨까지 키우면 진화 |
| 161 | 꼬리선 | Sentret |  |  | 다꼬리 교배로 얻는다 |
| 162 | 다꼬리 | Furret | 21번도로 | Route 21 | 21번도로 |
| 163 | 부우부 | Hoothoot | 3번도로 | Route 3 | 3번도로 |
| 164 | 야부엉 | Noctowl |  |  | 부우부를 24레벨까지 키우면 진화 |
| 165 | 레디바 | Ledyba | 그리사야시티 | Grisalla City | 그리사야시티 |
| 166 | 레디안 | Ledian |  |  | 레디바를 21레벨까지 키우면 진화 |
| 167 | 페이검 | Spinarak | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 168 | 아리아도스 | Ariados | 북부 카타콤 | Northern Catacombs | 북부 카타콤 또는 진화: 페이검 — 21레벨 |
| 169 | 크로뱃 | Crobat | 포켓몬 요새 | Bastion Vanitas | 포켓몬 요새 또는 진화: 골뱃 친밀도로 진화 |
| 170 | 초라기 | Chinchou | 빛나는 동굴 / 아크릴리코마을 | Glittering Cave / Acrylic Town | 빛나는 동굴 또는 아크릴리코마을 |
| 171 | 랜턴 | Lanturn |  |  | 초라기를 27레벨까지 키우면 진화 |
| 172 | 피츄 | Pichu |  |  | 피카츄/라이츄 교배로 얻는다 |
| 173 | 삐 | Cleffa |  |  | 픽시 교배로 얻는다 |
| 174 | 푸푸린 | Igglybuff |  |  | 푸크린 교배로 얻는다 |
| 175 | 토게피 | Togepi | 레스토랑 르 총크 | Lechonk Restaurant | 수은열쇠 봉인문 안쪽 — 레스토랑 르 총크 |
| 176 | 토게틱 | Togetic |  |  | 진화: 토게피 친밀도로 진화 |
| 177 | 네이티 | Natu | 왕들의 성소 | Sanctuary of Kings | 왕들의 성소 |
| 178 | 네이티오 | Xatu |  |  | 네이티를 28레벨까지 키우면 진화 |
| 179 | 메리프 | Mareep | 1번도로 | Route 1 | 1번도로 |
| 180 | 보송송 | Flaaffy |  |  | 메리프를 15레벨까지 키우면 진화 |
| 181 | 전룡 | Ampharos |  |  | 보송송을 30레벨까지 키우면 진화 |
| 182 | 아르코 | Bellossom |  |  | 냄새꼬에게 태양의돌 사용 |
| 183 | 마릴 | Marill | 비닐로마을 | Vinyl Town | 비닐로마을 |
| 184 | 마릴리 | Azumarill | 티에라우니다 동굴 | Earthbound Grotto | 티에라우니다 동굴 또는 진화: 마릴 — 18레벨 |
| 185 | 꼬지모 | Sudowoodo | 떠도는 숲 | Wandering Forest | 떠도는 숲 |
| 186 | 왕구리 | Politoed | 후늬시티 | Romantis City | 후늬시티 또는 진화: 슈륙챙이 by leveling up once — 왕의징표석 낮에 사용 |
| 187 | 통통코 | Hoppip | 비닐로마을 / 백단시티 | Vinyl Town / Novarte City | 비닐로마을 또는 백단시티 |
| 188 | 두코 | Skiploom |  |  | 통통코를 18레벨까지 키우면 진화 |
| 189 | 솜솜코 | Jumpluff |  |  | 두코를 27레벨까지 키우면 진화 |
| 190 | 에이팜 | Aipom | 프로파노마을 | Profane Town | 프로파노마을 |
| 191 | 해너츠 | Sunkern | 5번도로 | Route 5 | 5번도로 |
| 192 | 해루미 | Sunflora | 5번도로 | Route 5 | 5번도로 또는 진화: 해너츠 — 태양의돌 사용 |
| 193 | 왕자리 | Yanma | 9번도로 | Route 9 | 9번도로 |
| 194 | 우파 | Wooper | 3번도로 / 음침한 동굴 / 그리사야 동굴 | Route 3 / Murky Cave / Grisalla Cave | 3번도로, 음침한 동굴, 또는 그리사야 동굴 |
| 195 | 누오 | Quagsire | 음침한 동굴 | Murky Cave | 음침한 동굴 또는 진화: 우파 — 20레벨 |
| 196 | 에브이 | Espeon |  |  | 진화: 이브이 친밀도로 진화 낮에 |
| 197 | 블래키 | Umbreon |  |  | 진화: 이브이 친밀도로 진화 밤에 |
| 198 | 니로우 | Murkrow | 비탈 숲 / 옛 바니타스 / 6번도로 | Hillside Forest / Old Vanitas / Route 6 | 비탈 숲, 옛 바니타스, 또는 6번도로 |
| 199 | 야도킹 | Slowking | 아쥐르만 | Azure Bay | 아쥐르만 또는 진화: 야돈 — 물의돌 사용 |
| 200 | 무우마 | Misdreavus | 북부 카타콤 | Northern Catacombs | 북부 카타콤 |
| 201 | 안농 | Unown | 서부 카타콤 | Western Catacombs | 서부 카타콤 |
| 202 | 마자용 | Wobbuffet | 티에라우니다 동굴 | Earthbound Grotto | 티에라우니다 동굴 |
| 203 | 키링키 | Girafarig | 6번도로 | Route 6 | 6번도로 |
| 204 | 피콘 | Pineco | 4번도로 | Route 4 | 4번도로 |
| 205 | 쏘콘 | Forretress |  |  | 피콘을 31레벨까지 키우면 진화 |
| 206 | 노고치 | Dunsparce | 그리사야시티 / 이설시티 | Grisalla City / Fractal City | 그리사야시티 또는 이설시티 |
| 207 | 글라이거 | Gligar | 7번도로 북쪽 / 10번도로 / 20번도로 | Route 7 Part 1 / Route 10 / Route 20 | 7번도로 북쪽, 10번도로, 또는 20번도로 |
| 208 | 강철톤 | Steelix | 불타는 구렁 | Fiery Chasm | 불타는 구렁 또는 진화: 롱스톤 — 42레벨 |
| 209 | 블루 | Snubbull | 그리사야시티 | Grisalla City | 그리사야시티 |
| 210 | 그랑블루 | Granbull |  |  | 블루를 23레벨까지 키우면 진화 |
| 211 | 침바루 | Qwilfish | 13번도로 / 14번도로 | Route 13 / Route 14 | 13번도로 and 14번도로 |
| 212 | 핫삼 | Scizor |  |  | 스라크를 42레벨까지 키우면 진화 |
| 213 | 단단지 | Shuckle | 끝의 동굴 | Resolution Cave | 끝의 동굴 |
| 214 | 헤라크로스 | Heracross | 15번도로 | Route 15 | 15번도로 또는 교환: 스라크 — 남쪽 미르시티 |
| 215 | 포푸니 | Sneasel | 6번도로 | Route 6 | 6번도로 |
| 216 | 깜지곰 | Teddiursa | 6번도로 | Route 6 | 6번도로 |
| 217 | 링곰 | Ursaring | 16번도로 | Route 16 | 16번도로 또는 진화: 깜지곰 — 30레벨 |
| 218 | 마그마그 | Slugma |  |  | 마그카르고 교배로 얻는다 |
| 219 | 마그카르고 | Magcargo | 불타는 구렁 | Fiery Chasm | 불타는 구렁 |
| 220 | 꾸꾸리 | Swinub | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 |
| 221 | 메꾸리 | Piloswine | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 또는 진화: 꾸꾸리 — 33레벨 |
| 222 | 코산호 | Corsola | 몬테산토섬 | Montesanto Island | 몬테산토섬 (동굴) |
| 223 | 총어 | Remoraid | 세르티호섬 | Certijo Island | 세르티호섬 |
| 224 | 대포무노 | Octillery | 티에라우니다 동굴 | Earthbound Grotto | 티에라우니다 동굴 또는 진화: 총어 — 25레벨 |
| 225 | 딜리버드 | Delibird | 칼로스 피레네 / 프로스트케이브 | Kalos Pyrenees / Frozen Grotto | 칼로스 피레네 또는 프로스트케이브 |
| 226 | 만타인 | Mantine | 11번도로 | Route 11 | 11번도로 |
| 227 | 무장조 | Skarmory | 이설시티 | Fractal City | 이설시티 |
| 228 | 델빌 | Houndour | 3번도로 | Route 3 | 3번도로 |
| 229 | 헬가 | Houndoom |  |  | 델빌을 24레벨까지 키우면 진화 |
| 230 | 킹드라 | Kingdra |  |  | 시드라를 50레벨까지 키우면 진화 |
| 231 | 코코리 | Phanpy | 폭풍 언덕 | Storm Hill | 폭풍 언덕 |
| 232 | 코리갑 | Donphan |  |  | 코코리를 25레벨까지 키우면 진화 |
| 233 | 폴리곤2(Z) | Porygon2 (Z) |  |  | 폴리곤 (Z)를 30레벨까지 키우면 진화 |
| 234 | 노라키 | Stantler | 왕들의 성소 | Sanctuary of Kings | 왕들의 성소 |
| 235 | 루브도 | Smeargle | 끝의 동굴 | Resolution Cave | 끝의 동굴 (지니아 임무) |
| 236 | 배루키 | Tyrogue |  |  | Barracks 보상 (3rd Delinquent) |
| 237 | 카포에라 | Hitmontop |  |  | 배루키를 23레벨까지 키우면 진화 (공격과 방어가 같을 때) |
| 238 | 뽀뽀라 | Smoochum |  |  | 루주라 교배로 얻는다 |
| 239 | 에레키드 | Elekid | 백단시티 | Novarte City | 백단시티 |
| 240 | 마그비 | Magby | 불탄 공방 | Burned Workshop | 불탄 공방 |
| 241 | 밀탱크 | Miltank | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 |
| 242 | 해피너스 | Blissey |  |  | 럭키를 친밀도로 진화 |
| 243 | 라이코 | Raikou | 빛나는 동굴 | Glittering Cave | 빛나는 동굴 (파도타기 필요) |
| 244 | 앤테이 | Entei | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 (파도타기 필요) |
| 245 | 스이쿤 | Suicune | 음침한 동굴 | Murky Cave | 음침한 동굴 (파도타기 필요) |
| 246 | 애버라스 | Larvitar | 끝의 동굴 | Resolution Cave | 끝의 동굴 (아래층) |
| 247 | 데기라스 | Pupitar | 끝의 동굴 | Resolution Cave | 끝의 동굴 또는 진화: 애버라스 — 30레벨 |
| 248 | 마기라스 | Tyranitar |  |  | 데기라스를 55레벨까지 키우면 진화 |
| 249 | 루기아 | Lugia | 해저 / 가라마을 | Seafloor / Petroglifo | 해저 가라마을 |
| 250 | 칠색조 | Ho-Oh | 15번도로 | Route 15 | 15번도로 (얀트라 사건 이후) |
| 251 | 세레비 | Celebi | 비탈 숲 | Hillside Forest | 비탈 숲 (얀트라 사건 이후) |

### 3세대 (135행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 252 | 나무지기 | Treecko | 레스토랑 르 총크 / 보데곤마을 | Lechonk Restaurant / Bodegón Town | 엘풍과 교환 — 레스토랑 르 총크 (보데곤마을) |
| 253 | 나무돌이 | Grovyle |  |  | 나무지기를 18레벨까지 키우면 진화 |
| 254 | 나무킹 | Sceptile |  |  | 나무돌이를 45레벨까지 키우면 진화 |
| 255 | 아차모 | Torchic | 레스토랑 르 총크 / 보데곤마을 | Lechonk Restaurant / Bodegón Town | 윈디와 교환 — 레스토랑 르 총크 (보데곤마을) |
| 256 | 영치코 | Combusken |  |  | 아차모를 18레벨까지 키우면 진화 |
| 257 | 번치코 | Blaziken |  |  | 영치코를 45레벨까지 키우면 진화 |
| 258 | 물짱이 | Mudkip | 레스토랑 르 총크 / 보데곤마을 | Lechonk Restaurant / Bodegón Town | 트리토돈과 교환 — 레스토랑 르 총크 (보데곤마을) |
| 259 | 늪짱이 | Marshtomp |  |  | 물짱이를 18레벨까지 키우면 진화 |
| 260 | 대짱이 | Swampert |  |  | 늪짱이를 45레벨까지 키우면 진화 |
| 261 | 포챠나 | Poochyena | 비닐로마을 | Vinyl Town | 비닐로마을 |
| 262 | 그라에나 | Mightyena | 15번도로 | Route 15 | 15번도로 또는 진화: 포챠나 — 18레벨 |
| 263 | 지그제구리 | Zigzagoon | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 264 | 직구리 | Linoone | 옛 바니타스 | Old Vanitas | 옛 바니타스 또는 진화: 지그제구리 — 20레벨 |
| 265 | 개무소 | Wurmple |  |  | 뷰티플라이/독케일 교배 |
| 266 | 실쿤 | Silcoon |  |  | 개무소를 7레벨까지 키우면 진화 |
| 267 | 뷰티플라이 | Beautifly | 떠도는 숲 | Wandering Forest | 떠도는 숲 |
| 268 | 카스쿤 | Cascoon |  |  | 개무소를 7레벨까지 키우면 진화 |
| 269 | 독케일 | Dustox | 떠도는 숲 | Wandering Forest | 떠도는 숲 |
| 270 | 연꽃몬 | Lotad | 2번도로 / 비탈 숲 | Route 2 / Hillside Forest | 2번도로 또는 비탈 숲 |
| 271 | 로토스 | Lombre | 5번도로 | Route 5 | 5번도로 또는 진화: 연꽃몬 — 14레벨 |
| 272 | 로파파 | Ludicolo | 21번도로 | Route 21 | 21번도로 또는 진화: 로토스 — 물의돌 사용 |
| 273 | 도토링 | Seedot | 2번도로 | Route 2 | 2번도로 |
| 274 | 잎새코 | Nuzleaf | 프로파노마을 | Profane Town | 프로파노마을 |
| 275 | 다탱구 | Shiftry |  |  | 잎새코에게 리프의돌 사용 |
| 276 | 테일로 | Taillow | 8번도로 | Route 8 | 8번도로 |
| 277 | 스왈로 | Swellow |  |  | 테일로를 22레벨까지 키우면 진화 |
| 278 | 갈모매 | Wingull | 삼채시티 | Relief City | 삼채시티 |
| 279 | 패리퍼 | Pelipper |  |  | 갈모매를 25레벨까지 키우면 진화 |
| 280 | 랄토스 | Ralts | 8번도로 / 그리사야시티 | Route 8 / Grisalla City | 8번도로 또는 그리사야시티 |
| 281 | 킬리아 | Kirlia | 8번도로 | Route 8 | 8번도로 또는 진화: 랄토스 — 20레벨 |
| 282 | 가디안 | Gardevoir |  |  | 킬리아를 30레벨까지 키우면 진화 |
| 283 | 비구술 | Surskit | 4번도로 / 비탈 숲 | Route 4 / Hillside Forest | 4번도로 또는 비탈 숲 |
| 284 | 비나방 | Masquerain | 옛 바니타스 | Old Vanitas | 옛 바니타스 또는 진화: 비구술 — 25레벨 |
| 285 | 버섯꼬 | Shroomish | 콜라주마을 | Collage Town | 콜라주마을 |
| 286 | 버섯모 | Breloom |  |  | 버섯꼬를 23레벨까지 키우면 진화 |
| 287 | 게을로 | Slakoth |  |  | 발바로/게을킹 교배 |
| 288 | 발바로 | Vigoroth | 떠도는 숲 | Wandering Forest | 떠도는 숲 |
| 289 | 게을킹 | Slaking |  |  | 발바로를 36레벨까지 키우면 진화 |
| 290 | 토중몬 | Nincada | 로시욘 저택 | Chateau Rosillon Garden | 로시욘 저택 |
| 291 | 아이스크 | Ninjask |  |  | 토중몬을 20레벨까지 키우면 진화 |
| 292 | 껍질몬 | Shedinja |  |  | 토중몬가 진화할 때 파티에 빈자리와 몬스터볼이 있어야 한다 |
| 293 | 소곤룡 | Whismur | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 (아래층) |
| 294 | 노공룡 | Loudred |  |  | 소곤룡을 18레벨까지 키우면 진화 |
| 295 | 폭음룡 | Exploud | 25번도로 | Route 25 | 25번도로 또는 진화: 노공룡 — 40레벨 |
| 296 | 마크탕 | Makuhita |  |  | 하리뭉 교배 |
| 297 | 하리뭉 | Hariyama | 12번도로 | Route 12 | 12번도로 |
| 298 | 루리리 | Azurill |  |  | 마릴/마릴리 교배 |
| 299 | 코코파스 | Nosepass | 빛나는 동굴 | Glittering Cave | 빛나는 동굴 |
| 300 | 에나비 | Skitty | 4번도로 | Route 4 | 4번도로 |
| 301 | 델케티 | Delcatty |  |  | 에나비에게 달의돌 사용 |
| 302 | 깜까미 | Sableye | 티에라우니다 동굴 | Earthbound Grotto | 티에라우니다 동굴 |
| 303 | 입치트 | Mawile | 16번도로 / 음침한 동굴 | Route 16 / Gloomy Cave | 16번도로 또는 음침한 동굴 |
| 304 | 가보리 | Aron |  |  | 갱도라 교배 |
| 305 | 갱도라 | Lairon | 끝의 동굴 | Terminus Cave | 끝의 동굴 |
| 306 | 보스로라 | Aggron | 칼로스 동부 전투 | East Kalos Battle | 칼로스 동부 전투 또는 진화: 갱도라 — 42레벨 |
| 307 | 요가랑 | Meditite | 기남시티 / 그리사야 동굴 | Batik City / Grisalla Cave | 기남시티 또는 그리사야 동굴 |
| 308 | 요가램 | Medicham | 기남시티 | Batik City | 기남시티 또는 진화: 요가랑 — 37레벨 |
| 309 | 썬더라이 | Electrike | 9번도로 | Route 9 | 9번도로 |
| 310 | 썬더볼트 | Manectric |  |  | 썬더라이를 26레벨까지 키우면 진화 |
| 311 | 플러시 | Plusle | 13번도로 / 빛나는 동굴 | Route 13 / Glittering Cave | 13번도로 또는 빛나는 동굴 |
| 312 | 마이농 | Minun | 13번도로 / 빛나는 동굴 | Route 13 / Glittering Cave | 13번도로 또는 빛나는 동굴 |
| 313 | 볼비트 | Volbeat | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 314 | 네오비트 | Illumise | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 315 | 로젤리아 | Roselia | 8번도로 | Route 8 | 8번도로 또는 진화: 꼬몽울 — 20레벨 |
| 316 | 꼴깍몬 | Gulpin | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 317 | 꿀꺽몬 | Swalot | 13번도로 | Route 13 | 13번도로 또는 진화: 꼴깍몬 — 28레벨 |
| 318 | 샤프니아 | Carvanha |  |  | 샤크니아 교배 |
| 319 | 샤크니아 | Sharpedo | 23번도로 | Route 23 | 23번도로 |
| 320 | 고래왕자(Z) | Wailmer (Z) | 11번도로 | Route 11 | 11번도로 |
| 321 | 고래왕(Z) | Wailord (Z) |  |  | 고래왕자 (Z)를 40레벨까지 키우면 진화 |
| 322 | 둔타 | Numel | 10번도로 | Route 10 | 10번도로 |
| 323 | 폭타 | Camerupt | 10번도로 | Route 10 | 10번도로 또는 진화: 둔타 — 33레벨 |
| 324 | 코터스 | Torkoal | 19번도로 | Route 19 | 19번도로 |
| 325 | 피그점프 | Spoink | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 326 | 피그킹 | Grumpig | 18번도로 | Route 18 | 18번도로 또는 진화: 피그점프 — 32레벨 |
| 327 | 얼루기 | Spinda | 16번도로 | Route 16 | 16번도로 |
| 328 | 톱치 | Trapinch |  |  | 비브라바/플라이곤 교배 |
| 329 | 비브라바(Z) | Vibrava (Z) | 떠도는 숲 | Wandering Forest | 떠도는 숲 |
| 330 | 플라이곤(Z) | Flygon (Z) |  |  | 비브라바 (Z)를 45레벨까지 키우면 진화 |
| 331 | 선인왕 | Cacnea |  |  | 밤선인 교배 |
| 332 | 밤선인 | Cacturne | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 333 | 파비코 | Swablu | 2번도로 | Route 2 | 2번도로 |
| 334 | 파비코리 | Altaria |  |  | 파비코를 35레벨까지 키우면 진화 |
| 335 | 쟝고 | Zangoose | 삼채시티 | Relief City | 삼채시티 |
| 336 | 세비퍼 | Seviper | 삼채시티 | Relief City | 삼채시티 |
| 337 | 루나톤 | Lunatone | 물에 잠긴 대장간 | Flooded Forge | 물에 잠긴 대장간 |
| 338 | 솔록 | Solrock | 물에 잠긴 대장간 | Flooded Forge | 물에 잠긴 대장간 |
| 339 | 미꾸리 | Barboach | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 |
| 340 | 메깅 | Whiscash | 12번도로 | Route 12 | 12번도로 또는 진화: 미꾸리 — 30레벨 |
| 341 | 가재군 | Corphish | 6번도로 | Route 6 | 6번도로 |
| 342 | 가재장군 | Crawdaunt | 상기나 해안 | Bloodshore Coast | 상기나 해안 또는 진화: 가재군 — 30레벨 |
| 343 | 오뚝군 | Baltoy |  |  | 점토도리 교배 |
| 344 | 점토도리 | Claydol | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 345 | 릴링 | Lileep | 배롱마을 | Mosaic Town | 화석을 되살린다 — 배롱마을 |
| 346 | 릴리요 | Cradily |  |  | 릴링을 40레벨까지 키우면 진화 |
| 347 | 아노딥스 | Anorith | 배롱마을 | Mosaic Town | 화석을 되살린다 — 배롱마을 |
| 348 | 아말도 | Armaldo |  |  | 아노딥스를 40레벨까지 키우면 진화 |
| 349 | 빈티나 | Feebas | 로시욘 저택 | Chateau Rosillon | 로시욘 저택 |
| 350 | 밀로틱 | Milotic | 사라시티 | Yantra City | 사라시티 또는 진화: 빈티나 — 37레벨 |
| 351 | 캐스퐁 | Castform | 18번도로 | Route 18 | 18번도로 |
| 352 | 켈리몬 | Kecleon | 로시욘 저택 | Chateau Rosillon Garden | 로시욘 저택 |
| 353 | 어둠대신 | Shuppet | 폭풍 언덕 | Storm Hill | 폭풍 언덕 |
| 354 | 다크펫 | Banette | 포켓몬마을 | Pokémon Village | 포켓몬마을 또는 진화: 어둠대신 — 32레벨 |
| 355 | 해골몽 | Duskull |  |  | 미라몽 교배 |
| 356 | 미라몽 | Dusclops | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 357 | 트로피우스 | Tropius | 11번도로 | Route 11 | 11번도로 |
| 358 | 치렁 | Chimecho | 티에라우니다 동굴 | Earthbound Grotto | 티에라우니다 동굴 |
| 359 | 앱솔 | Absol | 18번도로 / 번영의 성소 | Route 18 / Prosperity Sanctuary | 18번도로 또는 번영의 성소 |
| 360 | 마자 | Wynaut |  |  | 마자용 교배 |
| 361 | 눈꼬마 | Snorunt | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 |
| 362 | 얼음귀신 | Glalie | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 또는 진화: 눈꼬마 — 42레벨 |
| 363 | 대굴레오 | Spheal |  |  | 씨레오/씨카이저 교배 |
| 364 | 씨레오 | Sealeo | 프로스트케이브 | Frozen Grotto | 프로스트케이브 |
| 365 | 씨카이저 | Walrein | 18번도로 | Route 18 | 18번도로 또는 진화: 씨레오 — 44레벨 |
| 366 | 진주몽 | Clamperl | 세르티호섬 | Certijo Island | 세르티호섬 |
| 367 | 헌테일 | Huntail | 해저 | Seafloor | 해저 또는 진화: 진주몽 — 어둠의돌 사용 |
| 368 | 분홍장이 | Gorebyss | 해저 | Seafloor | 해저 또는 진화: 진주몽 — 물의돌 사용 |
| 369 | 시라칸 | Relicanth | 해저 | Petroglifo Seafloor | 해저 |
| 370 | 사랑동이 | Luvdisc | 22번도로 | Route 22 | 22번도로 |
| 371 | 아공이 | Bagon | 삼채시티 | Relief City | 삼채시티 |
| 372 | 쉘곤 | Shelgon |  |  | 아공이를 30레벨까지 키우면 진화 |
| 373 | 보만다 | Salamence |  |  | 쉘곤을 50레벨까지 키우면 진화 |
| 374 | 메탕 | Beldum | 미르 신시가지 - 남쪽 | South Luminalia Expansions | 미르 신시가지 - 남쪽 |
| 375 | 메탕구 | Metang | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 또는 진화: 메탕 — 20레벨 |
| 376 | 메타그로스 | Metagross | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 또는 진화: 메탕구 — 45레벨 |
| 377 | 레지락 | Regirock | 끝의 동굴 | Terminus Cave | 끝의 동굴 |
| 378 | 레지아이스 | Regice | 프로스트케이브 | Frozen Grotto | 프로스트케이브 |
| 379 | 레지스틸 | Registeel | 불타는 구렁 | Scorched Chasm | 불타는 구렁 |
| 380 | 라티아스 | Latias | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 (얀트라 사건 이후) |
| 381 | 라티오스 | Latios | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 (얀트라 사건 이후) |
| 382 | 가이오가 | Kyogre | 향전시티 | Fluxus City Lake | 향전시티 (얀트라 사건 이후) |
| 383 | 그란돈 | Groudon | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 (얀트라 사건 이후) |
| 384 | 레쿠쟈 | Rayquaza | 버려진 등대 | Route 23 Lighthouse | 버려진 등대 |
| 385 | 지라치 | Jirachi | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 (얀트라 사건 이후) |
| 386 | 테오키스 | Deoxys | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 (얀트라 사건 이후) |

### 4세대 (107행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 387 | 모부기 | Turtwig |  |  | 마크탕과 교환 — 남쪽 미르시티 Café |
| 388 | 수풀부기 | Grotle |  |  | 모부기를 18레벨까지 키우면 진화 |
| 389 | 토대부기 | Torterra |  |  | 수풀부기를 45레벨까지 키우면 진화 |
| 390 | 불꽃숭이 | Chimchar |  |  | 무우마와 교환 — 남쪽 미르시티 Café |
| 391 | 파이숭이 | Monferno |  |  | 불꽃숭이를 18레벨까지 키우면 진화 |
| 392 | 초염몽 | Infernape |  |  | 파이숭이를 45레벨까지 키우면 진화 |
| 393 | 팽도리 | Piplup |  |  | 진주몽과 교환 — 남쪽 미르시티 Café |
| 394 | 팽태자 | Prinplup |  |  | 팽도리를 18레벨까지 키우면 진화 |
| 395 | 엠페르트 | Empoleon |  |  | 팽태자를 45레벨까지 키우면 진화 |
| 396 | 찌르꼬 | Starly |  |  | 찌르버드/찌르호크 교배 |
| 397 | 찌르버드 | Staravia | 로시욘 저택 | Chateau Rosillon | 로시욘 저택 |
| 398 | 찌르호크 | Staraptor |  |  | 찌르버드를 34레벨까지 키우면 진화 |
| 399 | 비버니(Z) | Bidoof (Z) | 1번도로 | Route 1 | 1번도로 |
| 400 | 비버통(Z) | Bibarel (Z) | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 또는 진화: 비버니 (Z) — 16레벨 |
| 401 | 귀뚤뚜기(Z) | Kricketot (Z) | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 402 | 귀뚤톡크(Z) | Kricketune (Z) |  |  | 귀뚤뚜기 (Z)를 17레벨까지 키우면 진화 |
| 403 | 꼬링크 | Shinx | 4번도로 | Route 4 | 4번도로 |
| 404 | 럭시오 | Luxio | 삼채시티 | Relief City | 삼채시티 또는 진화: 꼬링크 — 16레벨 |
| 405 | 렌트라 | Luxray |  |  | 럭시오를 30레벨까지 키우면 진화 |
| 406 | 꼬몽울 | Budew | 4번도로 | Route 4 | 4번도로 |
| 407 | 로즈레이드 | Roserade |  |  | 로젤리아에게 빛의돌 사용 |
| 408 | 두개도스 | Cranidos | 배롱마을 | Mosaic Town | 화석을 되살린다 — 배롱마을 |
| 409 | 램펄드 | Rampardos |  |  | 두개도스를 30레벨까지 키우면 진화 |
| 410 | 방패톱스 | Shieldon | 배롱마을 | Mosaic Town | 화석을 되살린다 — 배롱마을 |
| 411 | 바리톱스 | Bastiodon |  |  | 방패톱스를 30레벨까지 키우면 진화 |
| 412 | 도롱충이 | Burmy |  |  | 도롱마담의 알 |
| 413 | 도롱마담 | Wormadam | 8번도로 | Route 8 | 8번도로 |
| 414 | 나메일 | Mothim |  |  | 수컷 도롱충이를 20레벨까지 키우면 진화 |
| 415 | 세꿀버리 | Combee | 콜라주마을 | Collage Town | 콜라주마을 |
| 416 | 비퀸 | Vespiquen |  |  | 세꿀버리를 21레벨까지 키우면 진화 |
| 417 | 파치리스 | Pachirisu | 6번도로 | Route 6 | 6번도로 |
| 418 | 브이젤 | Buizel | 6번도로 | Route 6 | 6번도로 |
| 419 | 플로젤 | Floatzel | 배롱마을 | Mosaic Town | 배롱마을 또는 진화: 브이젤 — 26레벨 |
| 420 | 체리버 | Cherubi | 1번도로 | Route 1 | 1번도로 |
| 421 | 체리꼬 | Cherrim |  |  | 체리버를 18레벨까지 키우면 진화 |
| 422 | 깝질무 | Shellos | 11번도로 | Route 11 | 11번도로 |
| 423 | 트리토돈 | Gastrodon | 11번도로 | Route 11 | 11번도로 또는 진화: 깝질무 — 30레벨 |
| 424 | 겟핸보숭 | Ambipom |  |  | 에이팜이 더블어택을 배운 상태로 진화 |
| 425 | 흔들풍손 | Drifloon | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 426 | 둥실라이드 | Drifblim | 22번도로 | Route 22 | 22번도로 또는 진화: 흔들풍손 — 28레벨 |
| 427 | 이어롤 | Buneary |  |  | 이어롭 교배 |
| 428 | 이어롭 | Lopunny | 8번도로 / 란토 저택 | Route 8 / Chateau Lanto | 8번도로 (부근 — 란토 저택) |
| 429 | 무우마직 | Mismagius |  |  | 무우마에게 어둠의돌 사용 |
| 430 | 돈크로우 | Honchkrow |  |  | 니로우에게 어둠의돌 사용 |
| 431 | 나옹마 | Glameow | 미르시티 - 서쪽 | West Luminalia City | 미르시티 - 서쪽 |
| 432 | 몬냥이 | Purugly | 미르시티 | Luminalia City | 미르시티 또는 진화: 나옹마 — 28레벨 |
| 433 | 랑딸랑 | Chingling | 티에라우니다 동굴 | Earthbound Grotto | 티에라우니다 동굴 |
| 434 | 스컹뿡 | Stunky | 9번도로 / 옛 바니타스 | Route 9 / Old Vanitas Sewers | 9번도로 또는 옛 바니타스 |
| 435 | 스컹탱크 | Skuntank |  |  | 스컹뿡을 34레벨까지 키우면 진화 |
| 436 | 동미러 | Bronzor | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 |
| 437 | 동탁군 | Bronzong |  |  | 동미러를 33레벨까지 키우면 진화 |
| 438 | 꼬지지 | Bonsly |  |  | 꼬지모 교배 |
| 439 | 흉내내 | Mime Jr. | 올레오시티 | Oleo City | 올레오시티 |
| 440 | 핑복 | Happiny |  |  | 럭키/해피너스 교배 |
| 441 | 페라페 | Chatot | 몬테산토섬 | Montesanto Island | 몬테산토섬 |
| 442 | 화강돌 | Spiritomb | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 |
| 443 | 딥상어동 | Gible |  |  | 한바이트/한카리아스 교배 |
| 444 | 한바이트 | Gabite | 미르 신시가지 - 남쪽 | South Luminalia Expansions | 미르 신시가지 - 남쪽 |
| 445 | 한카리아스 | Garchomp |  |  | 한바이트를 48레벨까지 키우면 진화 |
| 446 | 먹고자 | Munchlax | 바니타스 텃밭 | Vanitas Orchard | 바니타스 텃밭 이벤트 |
| 447 | 리오르 | Riolu | 4번도로 | Route 4 | 4번도로 |
| 448 | 루카리오 | Lucario |  |  | 친밀도를 올린 뒤 낮에 레벨 업 |
| 449 | 히포포타스 | Hippopotas |  |  | 하마돈 교배 |
| 450 | 하마돈 | Hippowdon | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 451 | 스콜피 | Skorupi | 15번도로 | Route 15 | 15번도로 |
| 452 | 드래피온 | Drapion | 포켓몬 요새 | Bastion Vanitas | 포켓몬 요새 또는 진화: 스콜피 — 32레벨 |
| 453 | 삐딱구리 | Croagunk | 3번도로 | Route 3 | 3번도로 |
| 454 | 독개굴 | Toxicroak |  |  | 삐딱구리를 33레벨까지 키우면 진화 |
| 455 | 무스틈니 | Carnivine | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 456 | 형광어 | Finneon |  |  | 네오라이트 교배 |
| 457 | 네오라이트 | Lumineon | 해저 | Acrylic Town Seafloor | 해저 |
| 458 | 타만타 | Mantyke |  |  | 만타인 교배 |
| 459 | 눈쓰개 | Snover | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 |
| 460 | 눈설왕 | Abomasnow | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 또는 진화: 눈쓰개 — 40레벨 |
| 461 | 포푸니라 | Weavile | 18번도로 | Route 18 | 18번도로 또는 진화: 포푸니 — 38레벨 |
| 462 | 자포코일 | Magnezone |  |  | 레어코일을 45레벨까지 키우면 진화 |
| 463 | 내룸벨트 | Lickilicky |  |  | 내루미가 구르기를 배운 상태로 진화 |
| 464 | 거대코뿌리 | Rhyperior |  |  | 코뿌리를 45레벨까지 키우면 진화 |
| 465 | 덩쿠림보 | Tangrowth |  |  | 덩쿠리가 원시의힘을 배운 상태로 진화 |
| 466 | 에레키블 | Electivire |  |  | 에레브를 50레벨까지 키우면 진화 |
| 467 | 마그마번 | Magmortar |  |  | 마그마를 50레벨까지 키우면 진화 |
| 468 | 토게키스 | Togekiss |  |  | 토게틱에게 빛의돌 사용 |
| 469 | 메가자리 | Yanmega |  |  | 왕자리가 원시의힘을 배운 상태로 진화 |
| 470 | 리피아 | Leafeon |  |  | 이브이에게 리프의돌 사용 |
| 471 | 글레이시아 | Glaceon |  |  | 이브이에게 각성의돌 사용 |
| 472 | 글라이온 | Gliscor | 20번도로 | Route 20 | 20번도로 또는 진화: 글라이거 — 42레벨 |
| 473 | 맘모꾸리 | Mamoswine | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 또는 진화: 메꾸리 — 배운 기술: 원시의힘 |
| 474 | 폴리곤Z(Z) | Porygon-Z (Z) |  |  | 폴리곤2 (Z)를 50레벨까지 키우면 진화 |
| 475 | 엘레이드 | Gallade |  |  | 킬리아에게 각성의돌 사용 |
| 476 | 대코파스 | Probopass |  |  | 코코파스를 40레벨까지 키우면 진화 |
| 477 | 야느와르몽 | Dusknoir |  |  | 미라몽을 45레벨까지 키우면 진화 |
| 478 | 눈여아 | Froslass | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 또는 진화: 암컷 눈꼬마 — 각성의돌 사용 |
| 479 | 로토무 | Rotom | 후늬시티 | Romantis City | 후늬시티 (오른쪽 위) |
| 480 | 유크시 | Uxie | 프시케 동굴 / 15번도로 | Psyche Cave / Route 15 | 프시케 동굴에 들른 뒤 — 15번도로 |
| 481 | 엠라이트 | Mesprit | 프시케 동굴 / 12번도로 | Psyche Cave / Route 12 | 프시케 동굴에 들른 뒤 — 12번도로 |
| 482 | 아그놈 | Azelf | 프시케 동굴 / 9번도로 | Psyche Cave / Route 9 | 프시케 동굴에 들른 뒤 — 9번도로 (위쪽) |
| 483 | 디아루가 | Dialga | 떠도는 숲 | Wandering Forest | 떠도는 숲 (얀트라 사건 이후) |
| 484 | 펄기아 | Palkia | 미르 신시가지 - 동쪽 | East Luminalia Expansions | 미르 신시가지 - 동쪽 (얀트라 사건 이후) |
| 485 | 히드런 | Heatran | 불타는 구렁 | Scorched Chasm | 불타는 구렁 |
| 486 | 레지기가스 | Regigigas | 21번도로 | Route 21 | 21번도로 (호연 레지 3마리 필요) |
| 487 | 기라티나 | Giratina | 22번도로 | Route 22 | 22번도로 (얀트라 사건 이후) |
| 488 | 크레세리아 | Cresselia | 세뇨리알 대성당 | Manorial Cathedral | 세뇨리알 대성당 (봉인된 문) |
| 489 | 피오네 | Phione |  |  | 마나피 교배 |
| 490 | 마나피 | Manaphy | 해저 | Acrylic Town Ocean Floor | 해저 |
| 491 | 다크라이 | Darkrai | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 (봉인된 문) |
| 492 | 쉐이미 | Shaymin | 떠도는 숲 | Wandering Forest | 떠도는 숲 (얀트라 사건 이후) |
| 493 | 아르세우스 | Arceus |  |  | 차원문 만난 곳 — 크리산토 |

### 5세대 (156행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 494 | 비크티니 | Victini | 레비아탄 요새 | Fort Leviatan | 레비아탄 요새 (얀트라 사건 이후) |
| 495 | 주리비얀 | Snivy | 미르시티 - 서쪽 | West Luminalia | 도롱마담과 교환 — 미르시티 - 서쪽 Café |
| 496 | 샤비 | Servine |  |  | 주리비얀을 18레벨까지 키우면 진화 |
| 497 | 샤로다 | Serperior |  |  | 샤비를 45레벨까지 키우면 진화 |
| 498 | 뚜꾸리 | Tepig | 미르시티 - 서쪽 | West Luminalia | 날쌩마와 교환 — 미르시티 - 서쪽 Café |
| 499 | 차오꿀 | Pignite |  |  | 뚜꾸리를 18레벨까지 키우면 진화 |
| 500 | 염무왕 | Emboar |  |  | 차오꿀을 45레벨까지 키우면 진화 |
| 501 | 수댕이 | Oshawott | 미르시티 - 서쪽 | West Luminalia | 비나방과 교환 — 미르시티 - 서쪽 Café |
| 502 | 쌍검자비 | Dewott |  |  | 수댕이를 18레벨까지 키우면 진화 |
| 503 | 대검귀 | Samurott |  |  | 쌍검자비를 45레벨까지 키우면 진화 |
| 504 | 보르쥐 | Patrat |  |  | 보르그 교배 |
| 505 | 보르그 | Watchog | 21번도로 | Route 21 | 21번도로 |
| 506 | 요테리 | Lillipup | 콜라주마을 | Collage Town | 콜라주마을 |
| 507 | 하데리어 | Herdier |  |  | 요테리를 16레벨까지 키우면 진화 |
| 508 | 바랜드 | Stoutland |  |  | 하데리어를 32레벨까지 키우면 진화 |
| 509 | 쌔비냥 | Purrloin | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 510 | 레파르다스 | Liepard | 15번도로 | Route 15 | 15번도로 |
| 511 | 야나프 | Pansage | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 512 | 야나키 | Simisage |  |  | 사용: 리프의돌 |
| 513 | 바오프 | Pansear | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 514 | 바오키 | Simisear |  |  | 사용: 불꽃의돌 |
| 515 | 앗차프 | Panpour | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 516 | 앗차키 | Simipour |  |  | 사용: 물의돌 |
| 517 | 몽나 | Munna | 8번도로 | Route 8 | 8번도로 |
| 518 | 몽얌나 | Musharna |  |  | 사용: 달의돌 |
| 519 | 콩둘기 | Pidove |  |  | 유토브 교배 |
| 520 | 유토브 | Tranquill | 미르시티 | Luminalia City | 미르시티 |
| 521 | 켄호로우 | Unfezant |  |  | 유토브를 32레벨까지 키우면 진화 |
| 522 | 줄뮤마 | Blitzle | 로시욘 저택 | Chateau Rosillon | 로시욘 저택 |
| 523 | 제브라이카 | Zebstrika |  |  | 줄뮤마를 27레벨까지 키우면 진화 |
| 524 | 단굴 | Roggenrola | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 |
| 525 | 암트르 | Boldore | 티에라우니다 동굴 | Unity Cave | 티에라우니다 동굴 또는 진화: — 23레벨 |
| 526 | 기가이어스 | Gigalith | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 또는 진화: — 40레벨 |
| 527 | 또르박쥐 | Woobat | 남부 카타콤 | Southern Catacombs | 남부 카타콤 또는 Dark Cave |
| 528 | 맘박쥐 | Swoobat |  |  | Dark Cave 또는 친밀도 |
| 529 | Drillbur | Drillbur | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 |
| 530 | 몰드류 | Excadrill | 끝의 동굴 | Terminus Cave | 끝의 동굴 또는 진화: — 31레벨 |
| 531 | 다부니 | Audino | 21번도로 | Route 21 | 21번도로 |
| 532 | 으랏차 | Timburr | 콜라주마을 | Collage Town | 콜라주마을 |
| 533 | 토쇠골 | Gurdurr | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 또는 진화: — 23레벨 |
| 534 | 노보청 | Conkeldurr |  |  | 진화: 토쇠골 — 45레벨 |
| 535 | 동챙이 | Tympole | 4번도로 | Route 4 | 4번도로 |
| 536 | 두까비 | Palpitoad | 14번도로 | Route 14 | 14번도로 또는 진화: — 21레벨 |
| 537 | 두빅굴 | Seismitoad | 14번도로 | Route 14 | 14번도로 또는 진화: — 36레벨 |
| 538 | 던지미 | Throh | 7번도로 남쪽 | Route 7 South | 7번도로 남쪽 |
| 539 | 타격귀 | Sawk | 7번도로 남쪽 | Route 7 South | 7번도로 남쪽 |
| 540 | 두르보 | Sewaddle |  |  | 두르쿤/모아머 교배 |
| 541 | 두르쿤 | Swadloon | 16번도로 | Route 16 | 16번도로 |
| 542 | 모아머 | Leavanny |  |  | 친밀도 진화 |
| 543 | 마디네 | Venipede |  |  | 휠구/펜드라 교배 |
| 544 | 휠구 | Whirlipede | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 |
| 545 | 펜드라 | Scolipede | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 또는 진화: — 30레벨 |
| 546 | 소미안 | Cottonee | 올레오시티 | Olea City | 올레오시티 |
| 547 | 엘풍 | Whimsicott |  |  | 태양의돌 |
| 548 | 치릴리 | Petilil |  |  | 코인 400개 — Sanguine 카지노 |
| 549 | 드레디어(Z) | Lilligant (Z) |  |  | 태양의돌 |
| 550 | 배쓰나이 | Basculin | 15번도로 | Route 15 | 15번도로 |
| 551 | 깜눈크 | Sandile |  |  | 악비르/악비아르 교배 |
| 552 | 악비르 | Krokorok | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 553 | 악비아르 | Krookodile |  |  | 40레벨에 진화 |
| 554 | 달막화 | Darumaka | 불타는 구렁 | Fiery Chasm | 불타는 구렁 |
| 555 | 불비달마 | Darmanitan | 불타는 구렁 | Fiery Chasm | 불타는 구렁 또는 진화: — 35레벨 |
| 556 | 마라카치 | Maractus | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 557 | 돌살이 | Dwebble |  |  | Dark Cave |
| 558 | 암팰리스 | Crustle |  |  | Dark Cave 또는 진화: — 32레벨 |
| 559 | 곤율랭 | Scraggy |  |  | 곤율거니 교배 |
| 560 | 곤율거니 | Scrafty | 22번도로 | Route 22 | 22번도로 |
| 561 | 심보러 | Sigilyph | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 562 | 데스마스(Z) | Yamask (Z) | 10번도로 | Route 10 | 10번도로 |
| 563 | 데스니칸(Z) | Cofagrigus (Z) |  |  | 34레벨에 진화 |
| 564 | 프로토가 | Tirtouga | 배롱마을 | Mosaic Town | 화석 되살리기 — 배롱마을 |
| 565 | 늑골라 | Carracosta |  |  | 37레벨에 진화 |
| 566 | 아켄 | Archen | 배롱마을 | Mosaic Town | 화석 되살리기 — 배롱마을 |
| 567 | 아케오스 | Archeops |  |  | 37레벨에 진화 |
| 568 | 깨봉이 | Trubbish |  |  | 더스트나 교배 |
| 569 | 더스트나 | Garbodor | 미르 지하묘지 / 옛 바니타스 | Luminalia Crypts / Old Vanitas | 미르 지하묘지 또는 옛 바니타스 |
| 570 | 조로아 | Zorua |  |  | 조로아크 교배 |
| 571 | 조로아크 | Zoroark | 상기노 서커스 / 비탈 숲 | Sanguine Circus / Hillside Forest | 상기노 서커스 / 비탈 숲 |
| 572 | 치라미 | Minccino |  |  | 치라치노 교배 |
| 573 | 치라치노 | Cinccino | 19번도로 | Route 19 | 19번도로 |
| 574 | 고디탱 | Gothita |  |  | 고디보미 교배 |
| 575 | 고디보미 | Gothorita | 14번도로 | Route 14 | 14번도로 |
| 576 | 고디모아젤(Z) | Gothitelle (Z) |  |  | 38레벨에 진화 |
| 577 | 유니란(Z) | Solosis (Z) | 옛 바니타스 | Old Vanitas | 옛 바니타스 |
| 578 | 듀란(Z) | Duosion (Z) | 옛 바니타스 | Old Vanitas | 옛 바니타스 또는 진화: — 25레벨 |
| 579 | 란쿨루스(Z) | Reuniclus (Z) | 20번도로 | Route 20 | 20번도로 또는 진화: — 38레벨 |
| 580 | 꼬지보리 | Ducklett | 그리사야시티 | Grisalla City | 그리사야시티 |
| 581 | 스완나 | Swanna |  |  | 30레벨에 진화 |
| 582 | 바닐프티 | Vanillite | 17번도로 | Route 17 | 17번도로 |
| 583 | 바닐리치 | Vanillish | 17번도로 | Route 17 | 17번도로 또는 진화: — 25레벨 |
| 584 | 배바닐라 | Vanilluxe |  |  | 40레벨에 진화 |
| 585 | 사철록 | Deerling | 6번도로 | Route 6 | 6번도로 |
| 586 | 바라철록 | Sawsbuck |  |  | 32레벨에 진화 |
| 587 | 에몽가 | Emolga | 올레오시티 | Olea City | 올레오시티 |
| 588 | 딱정곤 | Karrablast | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 589 | 슈바르고 | Escavalier |  |  | 32레벨에 진화 |
| 590 | 깜놀버슬 | Foongus | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 591 | 뽀록나 | Amoonguss | 포켓몬마을 | Pokémon Villa | 포켓몬마을 또는 진화: — 36레벨 |
| 592 | 탱그릴 | Frillish | 15번도로 | Route 15 | 15번도로 |
| 593 | 탱탱겔 | Jellicent | 호수 밑바닥 | Lake Depths | 호수 밑바닥 또는 진화: — 35레벨 |
| 594 | 맘복치 | Alomomola | 호수 밑바닥 | Route 16 Lake Depth | 호수 밑바닥 |
| 595 | 파쪼옥 | Joltik | 옛 도서관 | Ancient Library | 옛 도서관 |
| 596 | 전툴라 | Galvantula |  |  | 32레벨에 진화 |
| 597 | 철시드 | Ferroseed |  |  | 너트령 교배 |
| 598 | 너트령 | Ferrothorn | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 |
| 599 | 기어르 | Klink | 빛나는 동굴 | Luminous Cave | 빛나는 동굴 |
| 600 | 기기어르 | Klang | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 또는 진화: — 25레벨 |
| 601 | 기기기어르 | Klinklang |  |  | 40레벨에 진화 |
| 602 | 저리어 | Tynamo | 빛나는 동굴 | Luminous Cave | 빛나는 동굴 |
| 603 | 저리릴 | Eelektrik | 물에 잠긴 옛 대장간 | Old Flooded Forge | 물에 잠긴 옛 대장간 또는 진화: — 30레벨 |
| 604 | 저리더프 | Eelektross |  |  | 천둥의돌 |
| 605 | 리그레 | Elgyem |  |  | 교배 |
| 606 | 벰크 | Beheeyem | 23번도로 | Route 23 | 23번도로 |
| 607 | 불켜미 | Litwick | 옛 도서관 | Ancient Library | 옛 도서관 |
| 608 | 램프라 | Lampent | 옛 바니타스 | Old Vanitas | 옛 바니타스 또는 진화: — 34레벨 |
| 609 | 샹델라 | Chandelure |  |  | 어둠의돌 |
| 610 | 터검니 | Axew | 왕들의 성소 | Kings’ Sanctuary | 왕들의 성소 |
| 611 | 액슨도 | Fraxure |  |  | 30레벨에 진화 |
| 612 | 액스라이즈 | Haxorus |  |  | 48레벨에 진화 |
| 613 | 코고미 | Cubchoo |  |  | 툰베어 교배 |
| 614 | 툰베어 | Beartic | 17번도로 | Route 17 | 17번도로 |
| 615 | 프리지오 | Cryogonal | 프로스트케이브 | Frozen Cave | 프로스트케이브 |
| 616 | 쪼마리 | Shelmet | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 617 | 어지리더 | Accelgor |  |  | 32레벨에 진화 |
| 618 | 메더 | Stunfisk | 프로파노마을 | Profane Town | 프로파노마을 |
| 619 | 비조푸 | Mienfoo |  |  | 비조도 교배 |
| 620 | 비조도 | Mienshao | 23번도로 | Route 23 | 23번도로 |
| 621 | 크리만 | Druddigon | 끝의 동굴 | Terminus Cave | 끝의 동굴 |
| 622 | 골비람 | Golett | 옛 도서관 | Ancient Library | 옛 도서관 |
| 623 | 골루그 | Golurk | 물에 잠긴 옛 대장간 | Old Flooded Forge | 물에 잠긴 옛 대장간 또는 진화: — 35레벨 |
| 624 | 자망칼 | Pawniard | 왕들의 성소 | Kings’ Sanctuary | 왕들의 성소 |
| 625 | 절각참 | Bisharp |  |  | 30레벨에 진화 |
| 626 | 버프론 | Bouffalant | 21번도로 | Route 21 | 21번도로 |
| 627 | 수리둥보 | Rufflet | 23번도로 | Route 23 | 23번도로 |
| 628 | 워글 | Braviary | 23번도로 | Route 23 | 23번도로 또는 진화: — 35레벨 |
| 629 | 벌차이 | Vullaby | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 630 | 버랜지나 | Mandibuzz | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 또는 진화: — 35레벨 |
| 631 | 앤티골 | Heatmor | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 |
| 632 | 아이앤트 | Durant | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 |
| 633 | 모노두 | Deino |  |  | 디헤드/삼삼드래 교배 |
| 634 | 디헤드 | Zweilous | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 |
| 635 | 삼삼드래 | Hydreigon | 비춤의 동굴 / 25번도로 | Reflection Cave / Route 25 | 비춤의 동굴 또는 25번도로 |
| 636 | 활화르바 | Larvesta | 세르티호섬 | Certijo Island | 세르티호섬 |
| 637 | 불카모스 | Volcarona |  |  | 55레벨에 진화 |
| 638 | 코바르온 | Cobalion | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 (이벤트 이후) |
| 639 | 테라키온 | Terrakion | 13번도로 | Route 13 | 13번도로 (이벤트 이후) |
| 640 | 비리디온 | Virizion | 비탈 숲 | Hillside Forest | 비탈 숲 (이벤트 이후) |
| 641 | 토네로스 | Tornadus |  |  | Dark Cave (얀트라 사건 이후) |
| 642 | 볼트로스 | Thundurus | 빛나는 동굴 | Luminous Cave | 빛나는 동굴 |
| 643 | 레시라무 | Reshiram | 로시욘 저택 | Chateau Rosillon | 로시욘 저택 (얀트라 사건 이후) |
| 644 | 제크로무 | Zekrom | 란토 저택 | Chateau Lanto | 란토 저택 (얀트라 사건 이후) |
| 645 | 랜드로스 | Landorus | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 (얀트라 사건 이후) |
| 646 | 큐레무 | Kyurem | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 |
| 647 | 케르디오 | Keldeo | 배롱마을 | Mosaic Town | 배롱마을 (이벤트 이후) |
| 648 | 메로엣타 | Meloetta | 미르시티 - 서쪽 | West Luminalia | 미르시티 - 서쪽 (얀트라 사건 이후) |
| 649 | 게노세크트 | Genesect | 불탄 공방 | Burned Workshop | 불탄 공방 (얀트라 사건 이후) |

### 6세대 (72행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 650 | 도치마론 | Chespin | 옥유마을 | Crómlech | 돌헨진 — 옥유마을과 교환 |
| 651 | 도치보구 | Quilladin |  |  | 도치마론을 18레벨까지 키우면 진화 |
| 652 | 브리가론(Z) | Chesnaught (Z) |  |  | 도치보구를 45레벨까지 키우면 진화 |
| 653 | 푸호꼬 | Fennekin | 옥유마을 | Crómlech | 저승갓숭 — 옥유마을과 교환 |
| 654 | 테르나 | Braixen |  |  | 푸호꼬를 18레벨까지 키우면 진화 |
| 655 | 마폭시(Z) | Delphox (Z) |  |  | 테르나를 45레벨까지 키우면 진화 |
| 656 | 개구마르 | Froakie | 옥유마을 | Crómlech | 칼라마네로 — 옥유마을과 교환 |
| 657 | 개굴반장 | Frogadier |  |  | 개구마르를 18레벨까지 키우면 진화 |
| 658 | 개굴닌자(Z) | Greninja (Z) |  |  | 개굴반장을 45레벨까지 키우면 진화 |
| 659 | 파르빗 | Bunnelby | 비닐로마을 | Vinyl Town | 비닐로마을 |
| 660 | 파르토 | Diggersby |  |  | 파르빗을 20레벨까지 키우면 진화 |
| 661 | 화살꼬빈 | Fletchling | 1번도로 | Route 1 | 1번도로 |
| 662 | 불화살빈 | Fletchinder | 5번도로 | Route 5 | 5번도로 또는 진화: at Lv. 17 |
| 663 | 파이어로 | Talonflame |  |  | 35레벨에 진화 |
| 664 | 분이벌레 | Scatterbug | 1번도로 | Route 1 | 1번도로 |
| 665 | 분떠도리 | Spewpa |  |  | 9레벨에 진화 |
| 666 | 비비용 | Vivillon |  |  | 16레벨에 진화 |
| 667 | 레오꼬 | Litleo | 2번도로 | Route 2 | 2번도로 |
| 668 | 화염레오 | Pyroar | 13번도로 | Route 13 | 13번도로 또는 진화: at Lv. 30 |
| 669 | 플라베베 | Flabébé | 그리사야시티 | Grisalla City | 그리사야시티 |
| 670 | 플라엣테 | Floette |  |  | 19레벨에 진화 |
| 671 | 플라제스 | Florges |  |  | 사용: Day Stone |
| 672 | 메이클 | Skiddo | 2번도로 | Route 2 | 2번도로 |
| 673 | 고고트 | Gogoat | 칼로스 동부 전투 | East Kalos Battle | 칼로스 동부 전투 또는 진화: at Lv. 32 |
| 674 | 판짱 | Pancham | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 675 | 부란다 | Pangoro |  |  | 32레벨에 진화 |
| 676 | 트리미앙 | Furfrou | 8번도로 | Route 8 | 8번도로 |
| 677 | 냐스퍼 | Espurr | 5번도로 / 번영의 성소 | Route 5 / Prosperity Sanctuary | 5번도로 또는 번영의 성소 |
| 678 | 냐오닉스 | Meowstic | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 또는 진화: at Lv. 25 |
| 679 | 단칼빙 | Honedge | 남쪽 감시탑 | South Watchtower | 남쪽 감시탑 |
| 680 | 쌍검킬 | Doublade |  |  | 35레벨에 진화 |
| 681 | 킬가르도 | Aegislash | 칼로스 동부 전투 | East Kalos Battle | 칼로스 동부 전투 또는 Night Stone |
| 682 | 슈쁘 | Spritzee | 4번도로 | Route 4 | 4번도로 |
| 683 | 프레프티르 | Aromatisse |  |  | 27레벨에 진화 |
| 684 | 나룸퍼프 | Swirlix |  |  | 나루림 교배 |
| 685 | 나루림 | Slurpuff | 미르시티 - 서쪽 | West Luminalia | 교환: 프레프티르 — 미르시티 - 서쪽 |
| 686 | 오케이징 | Inkay |  |  | 칼라마네로 교배 |
| 687 | 칼라마네로 | Malamar | 몬테산토섬 | Montesanto Island | 몬테산토섬 (동굴) |
| 688 | 거북손손 | Binacle | 11번도로 | Route 11 | 11번도로 |
| 689 | 거북손데스 | Barbaracle | 11번도로 | Route 11 | 11번도로 또는 진화: at Lv. 39 |
| 690 | 수레기 | Skrelp | 9번도로 | Route 9 | 9번도로 |
| 691 | 드래캄 | Dragalge | 14번도로 | Route 14 | 14번도로 또는 진화: at Lv. 35 |
| 692 | 완철포 | Clauncher | 빛나는 동굴 | Glittering Cave | 빛나는 동굴 |
| 693 | 블로스터 | Clawitzer | 몬테산토섬 | Montesanto Island | 몬테산토섬 또는 진화: at Lv. 35 |
| 694 | 목도리키텔 | Helioptile |  |  | 일레도리자드 교배 |
| 695 | 일레도리자드 | Heliolisk | 미르 신시가지 - 남쪽 | South Luminalia Expansions | 미르 신시가지 - 남쪽 |
| 696 | 티고라스 | Tyrunt | 배롱마을 | Mosaic Town | 교환: 아노딥스 — 배롱마을 |
| 697 | 견고라스 | Tyrantrum |  |  | 39레벨에 진화 |
| 698 | 아마루스 | Amaura | 배롱마을 | Mosaic Town | 교환: 릴링 — 배롱마을 |
| 699 | 아마루르가 | Aurorus |  |  | 39레벨에 진화 |
| 700 | 님피아 | Sylveon |  |  | 사용: Day Stone |
| 701 | 루차불 | Hawlucha | 10번도로 | Route 10 | 10번도로 |
| 702 | 데덴네 | Dedenne | 9번도로 | Route 9 | 9번도로 |
| 703 | 멜리시 | Carbink | 물에 잠긴 대장간 / 티에라우니다 동굴 | Flooded Forge / Tierraunida Grotto | 물에 잠긴 대장간 또는 티에라우니다 동굴 |
| 704 | 미끄메라 | Goomy | 프로파노 늪 | Profane Swamp | 프로파노 늪 |
| 705 | 미끄네일 | Sliggoo | 14번도로 | Route 14 | 14번도로 또는 진화: at Lv. 30 |
| 706 | 미끄래곤 | Goodra |  |  | 50레벨에 진화 |
| 707 | 클레피 | Klefki | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 |
| 708 | 나목령 | Phantump | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 709 | 대로트 | Trevenant | 16번도로 | Route 16 | 16번도로 또는 진화: at Lv. 38 |
| 710 | 호바귀 | Pumpkaboo | 15번도로 | Route 15 | 15번도로 (2부) |
| 711 | 펌킨인 | Gourgeist | 15번도로 | Route 15 | 15번도로 또는 진화: at Lv. 37 |
| 712 | 꽁어름 | Bergmite | 17번도로 / 프로스트케이브 / 칼로스 피레네 | Route 17 / Frost Cavern / Kalos Pyrenees | 17번도로, 프로스트케이브, 또는 칼로스 피레네 |
| 713 | 크레베이스 | Avalugg |  |  | 37레벨에 진화 |
| 714 | 음뱃 | Noibat | 북부 카타콤 | Northern Catacombs | 북부 카타콤 |
| 715 | 음번 | Noivern |  |  | 42레벨에 진화 |
| 716 | 제르네아스 | Xerneas | 깊은 샘 | Deep Spring | 깊은 샘 (엔딩 후) |
| 717 | 이벨타르 | Yveltal | 서커스의 악몽 | Circus Nightmare | 서커스의 악몽 (엔딩 후) |
| 718 | 지가르데 | Zygarde | 프리즘타워 | Prism Tower | 프리즘타워 (엔딩 후) |
| 719 | 디안시 | Diancie | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 |
| 720 | 후파 | Hoopa |  |  | 코인 1400개 — Sanguine 카지노 |
| 721 | 볼케니온 | Volcanion | 미르시티 - 서쪽 | West Luminalia | 미르시티 - 서쪽 신시가지 Pokémon Center |

### 7세대 (88행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 722 | 나몰빼미 | Rowlet |  |  | 교환: 트로피우스 — 미르시티 동쪽 Café |
| 723 | 빼미스로우 | Dartrix |  |  | 진화: 나몰빼미 — 18레벨 |
| 724 | 모크나이퍼 | Decidueye |  |  | 진화: 빼미스로우 — 45레벨 |
| 725 | 냐오불 | Litten |  |  | 교환: 샹델라 — 미르시티 서쪽 Café |
| 726 | 냐오히트 | Torracat |  |  | 진화: 냐오불 — 18레벨 |
| 727 | 어흥염 | Incineroar |  |  | 진화: 냐오히트 — 45레벨 |
| 728 | 누리공 | Popplio |  |  | 교환: 샤크니아 — 미르시티 서쪽 Café |
| 729 | 키요공 | Brionne |  |  | 진화: 누리공 — 18레벨 |
| 730 | 누리레느 | Primarina |  |  | 진화: 키요공 — 45레벨 |
| 731 | 콕코구리 | Pikipek |  |  | 왕큰부리 교배 |
| 732 | 크라파 | Trumbeak |  |  | 진화: 콕코구리 — 14레벨 |
| 733 | 왕큰부리 | Toucannon | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 734 | 영구스 | Yungoos |  |  | 형사구스 교배 |
| 735 | 형사구스 | Gumshoos | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 736 | 턱지충이 | Grubbin | 5번도로 | Route 5 | 5번도로 |
| 737 | 전지충이 | Charjabug |  |  | 진화: 턱지충이 — 20레벨 |
| 738 | 투구뿌논 | Vikavolt |  |  | 진화: 전지충이 — 36레벨 |
| 739 | 오기지게 | Crabrawler | 11번도로 | Route 11 | 11번도로 |
| 740 | 모단단게 | Crabominable |  |  | 진화: 오기지게 — 36레벨 |
| 741 | 춤추새 | Oricorio | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 742 | 에블리 | Cutiefly | 백단시티 | Novarte City | 백단시티에서 플라베베와 교환 |
| 743 | 에리본 | Ribombee | 19번도로 | Route 19 | 19번도로 |
| 744 | 암멍이 | Rockruff | 9번도로 | Route 9 | 9번도로 |
| 745 | 루가루암 | Lycanroc |  |  | 진화: 암멍이 — 25레벨 |
| 746 | 약어리 | Wishiwashi | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 747 | 시마사리 | Mareanie |  |  | 더시마사리 교배 |
| 748 | 더시마사리 | Toxapex | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 749 | 머드나기 | Mudbray | 9번도로 | Route 9 | 9번도로 |
| 750 | 만마드 | Mudsdale | 9번도로 | Route 9 | 9번도로 또는 진화로 얻는다 |
| 751 | 물거미 | Dewpider | 폭풍 언덕 / 그리사야시티 | Storm Hill / Grisalla City | 폭풍 언덕 또는 그리사야시티 |
| 752 | 깨비물거미 | Araquanid | 22번도로 | Route 22 | 22번도로 또는 진화로 얻는다 |
| 753 | Formantis | Formantis | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 754 | 라란티스 | Lurantis | 몬테산토섬 | Isle Montesanto | 몬테산토섬 또는 진화로 얻는다 |
| 755 | 자마슈 | Morelull | 3번도로 / 비탈 숲 | Route 3 / Hillside Forest | 3번도로 또는 비탈 숲 |
| 756 | 마셰이드 | Shiinotic |  |  | 진화: 자마슈 — 24레벨 |
| 757 | 야도뇽 | Salandit |  |  | 염뉴트 교배 |
| 758 | 염뉴트 | Salazzle | 포켓몬 요새 | Vanitas Town (Pokémon Bastion) | 포켓몬 요새 |
| 759 | 포곰곰 | Stufful | 22번도로 | Route 22 | 22번도로 |
| 760 | 이븐곰 | Bewear | 22번도로 | Route 22 | 22번도로 또는 진화로 얻는다 |
| 761 | 달콤아 | Bounsweet |  |  | 달무리나/달코퀸 교배 |
| 762 | 달무리나 | Steenee | 16번도로 | Route 16 | 16번도로 |
| 763 | 달코퀸 | Tsareena |  |  | 달무리나가 짓밟기를 배운 상태로 진화 |
| 764 | 큐아링 | Comfey | 세르티호섬 | Certijo Isle | 세르티호섬 |
| 765 | 하랑우탄 | Oranguru | 세르티호섬 | Certijo Isle | 세르티호섬 |
| 766 | 내던숭이 | Passimian | 세르티호섬 | Certijo Isle | 세르티호섬 |
| 767 | 꼬시레 | Wimpod | 삼채시티 | Relieve City | 삼채시티 |
| 768 | 갑주무사 | Golisopod | 몬테산토섬 | Isle Montesanto | 몬테산토섬 또는 진화로 얻는다 |
| 769 | 모래꿍 | Sandygast | 11번도로 | Route 11 | 11번도로 |
| 770 | 모래성이당 | Palossand | 상기나 해안 | Sanguina Coast | 상기나 해안 또는 진화로 얻는다 |
| 771 | 해무기 | Pyukumuku | 11번도로 | Route 11 | 11번도로 |
| 772 | 타입:널 | Type: Null | 얀트라 농장 / 24번도로 | Yantra Ranch / Route 24 | 얀트라 농장 (24번도로) |
| 773 | 실버디 | Silvally |  |  | 친밀도 진화로 얻는다 |
| 774 | 메테노 | Minior | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 |
| 775 | 자말라 | Komala | 몬테산토섬 | Isle Montesanto | 몬테산토섬 |
| 776 | 폭거북스 | Turtonator | 불타는 구렁 | Fiery Chasm | 불타는 구렁 |
| 777 | 토게데마루 | Togedemaru | 불탄 공방 | Burned Workshop | 불탄 공방 |
| 778 | 따라큐 | Mimikyu |  |  | Profano Witch 이벤트 |
| 779 | 치갈기 | Bruxish | 향전시티 / 8번도로 | Fluxus City / Route 8 | 향전시티 또는 8번도로 |
| 780 | 할비롱 | Drampa | 9번도로 | Route 9 | 9번도로 |
| 781 | 타타륜 | Dhelmise | 해저 | Acrylic Town Seafloor | 해저 |
| 782 | 짜랑꼬 | Jangmo-o |  |  | 짜랑고우 교배 |
| 783 | 짜랑고우 | Hakamo-o | 몬테산토섬 / 휴게소 | Isle Montesanto / Service Station | 몬테산토섬 또는 휴게소 |
| 784 | 짜랑고우거 | Kommo-o |  |  | 진화: 짜랑고우 — 45레벨 |
| 785 | 카푸꼬꼬꼭 | Tapu Koko | 몬테산토섬 | Isle Montesanto | 몬테산토섬 (이후 — 로토 이벤트) |
| 786 | 카푸나비나 | Tapu Lele | 몬테산토섬 | Isle Montesanto | 몬테산토섬 (이후 — 로토 이벤트) |
| 787 | 카푸브루루 | Tapu Bulu | 몬테산토섬 | Isle Montesanto | 몬테산토섬 (이후 — 로토 이벤트) |
| 788 | 카푸느지느 | Tapu Fini | 몬테산토섬 | Isle Montesanto | 몬테산토섬 (이후 — 로토 이벤트) |
| 789 | 코스모그 | Cosmog | 세르티호섬 / 옛 바니타스 | Certijo Isle / Old Vanitas | 세르티호섬 또는 옛 바니타스 (얀트라 사건 이후) |
| 790 | 코스모움 | Cosmoem |  |  | 진화: 코스모그 — 45레벨 |
| 791 | 솔가레오 | Solgaleo |  |  | 진화: 코스모움 (Day Stone) |
| 792 | 루나아라 | Lunala |  |  | 진화: 코스모움 (Night Stone) |
| 793 | 텅비드 | Nihilego | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 794 | 매시붕 | Buzzwole | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 795 | 페로코체 | Pheromosa | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 796 | 전수목 | Xurkitree | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 797 | 철화구야 | Celesteela | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 798 | 종이신도 | Kartana | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 799 | 악식킹 | Guzzlord | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 800 | 네크로즈마 | Necrozma | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 |
| 801 | 마기아나 | Magearna | 백단시티 | Novarte City | 백단시티 (이후 — Mechanical Heart) |
| 802 | 마샤도 | Marshadow | 상기나 해안 | Sanguina Coast | 상기나 해안 (얀트라 사건 이후) |
| 803 | 베베놈 | Poipole | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 804 | 아고용 | Naganadel |  |  | 진화: 베베놈 (용의파동) |
| 805 | 차곡차곡 | Stakataka | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 806 | 두파팡 | Blacephalon | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 |
| 807 | 제라오라 | Zeraora | 휴게소 | Service Station | 휴게소 (위층) |
| 808 | 멜탄 | Meltan |  |  | 코인 700개와 교환 — Sanguino 카지노 |
| 809 | 멜메탈 | Melmetal |  |  | 친밀도 진화로 얻는다 |

### 8세대 (96행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 810 | 흥나숭 | Grookey |  |  | 우츠보트 — Fluxus Café와 교환 |
| 811 | 채키몽 | Thwackey |  |  | 흥나숭을 18레벨까지 키우면 진화 |
| 812 | 고릴타 | Rillaboom |  |  | 채키몽을 45레벨까지 키우면 진화 |
| 813 | 염버니 | Scorbunny |  |  | 앤티골 — Fluxus Café와 교환 |
| 814 | 래비풋 | Raboot |  |  | 염버니를 18레벨까지 키우면 진화 |
| 815 | 에이스번 | Cinderace |  |  | 래비풋을 45레벨까지 키우면 진화 |
| 816 | 울머기 | Sobble |  |  | 치갈기 — Fluxus Café와 교환 |
| 817 | 누겔레온 | Drizzile |  |  | 울머기를 18레벨까지 키우면 진화 |
| 818 | 인텔리레온 | Inteleon |  |  | 누겔레온을 45레벨까지 키우면 진화 |
| 819 | 탐리스 | Skwovet |  |  | 요씽리스. 교배로 얻는다 |
| 820 | 요씽리스 | Greedent | 16번도로 | Route 16 | 16번도로 |
| 821 | 파라꼬 | Rookidee |  |  | 파크로우. 교배로 얻는다 |
| 822 | 파크로우 | Corvisquire | 12번도로 | Route 12 | 12번도로 |
| 823 | 아머까오 | Corviknight |  |  | 파크로우를 38레벨까지 키우면 진화 |
| 824 | 두루지벌레 | Blipbug | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 825 | 레돔벌레 | Dottler |  |  | 두루지벌레를 10레벨까지 키우면 진화 |
| 826 | 이올브 | Orbeetle |  |  | 레돔벌레를 30레벨까지 키우면 진화 |
| 827 | 훔처우 | Nickit | 3번도로 | Route 3 | 3번도로 |
| 828 | 폭슬라이 | Thievul | 프로파노마을 | Profane Town | 프로파노마을 또는 진화: 훔처우 — 18레벨 |
| 829 | 꼬모카 | Gossifleur |  |  | 백솜모카. 교배로 얻는다 |
| 830 | 백솜모카 | Eldegoss | 20번도로 | Route 20 | 20번도로 |
| 831 | 우르 | Wooloo | 9번도로 | Route 9 | 9번도로 |
| 832 | 배우르 | Dubwool | 9번도로 | Route 9 | 9번도로 또는 진화: 우르 — 24레벨 |
| 833 | 깨물부기 | Chewtle | 5번도로 | Route 5 | 5번도로 |
| 834 | 갈가부기 | Drednaw | 버들비마을 | Fresh Town | 버들비마을 또는 진화: 깨물부기 — 24레벨 |
| 835 | 멍파치 | Yamper | 백단시티 | Novarte City | 백단시티 |
| 836 | 펄스멍 | Boltund |  |  | 멍파치를 25레벨까지 키우면 진화 |
| 837 | 탄동 | Rolycoly | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 |
| 838 | 탄차곤 | Carkol |  |  | Dark Cave 또는 진화: 탄동 — 18레벨 |
| 839 | 석탄산 | Coalossal |  |  | 탄차곤을 40레벨까지 키우면 진화 |
| 840 | 과사삭벌레 | Applin | 7번도로 북쪽 | Route 7 North | 7번도로 북쪽 |
| 841 | 애프룡 | Flapple |  |  | 과사삭벌레에게 리프의돌 사용 |
| 842 | 단지래플 | Appletun |  |  | 과사삭벌레에게 태양의돌 사용 |
| 843 | 모래뱀 | Silicobra |  |  | 사다이사. 교배로 얻는다 |
| 844 | 사다이사 | Sandaconda | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 845 | 윽우지 | Cramorant | 23번도로 | Route 23 | 23번도로 |
| 846 | 찌로꼬치 | Arrokuda |  |  | 꼬치조. 교배로 얻는다 |
| 847 | 꼬치조 | Barraskewda | 가라마을 / 해저 | Petroglyph Town / Seafloor | 가라마을 해저 |
| 848 | 일레즌 | Toxel | 5번도로 | Route 5 | 5번도로 |
| 849 | 스트린더 | Toxtricity |  |  | 일레즌을 30레벨까지 키우면 진화 |
| 850 | 태우지네 | Sizzlipede |  |  | 다태우지네. 교배로 얻는다 |
| 851 | 다태우지네 | Centiskorch | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 |
| 852 | 때때무노 | Clobbopus | 가라마을 | Petroglyph Town | 가라마을 |
| 853 | 케오퍼스 | Grapploct |  |  | 때때무노를 40레벨까지 키우면 진화 |
| 854 | 데인차 | Sinistea | 옛 도서관 / 올레오시티 | Old Library / Oleum City | 옛 도서관 (올레오시티) |
| 855 | 포트데스 | Polteageist |  |  | 데인차에게 Night Stone 사용 |
| 856 | 몸지브림 | Hatenna |  |  | 손지브림/브리무음. 교배로 얻는다 |
| 857 | 손지브림 | Hattrem | 6번도로 | Route 6 | 6번도로 |
| 858 | 브리무음 | Hatterene |  |  | 손지브림을 42레벨까지 키우면 진화 |
| 859 | 메롱꿍 | Impidimp | 7번도로 | Route 7 | 벼리짱 민가 — 7번도로와 교환 |
| 860 | 쏘겨모 | Morgrem | 옛 바니타스 | Old Vanitas | 옛 바니타스 또는 진화: 메롱꿍 — 32레벨 |
| 861 | 오롱털 | Grimmsnarl |  |  | 쏘겨모를 42레벨까지 키우면 진화 |
| 862 | 가로막구리 | Obstagoon |  |  | 직구리를 35레벨까지 키우면 진화 |
| 863 | 나이킹 | Perrserker | 25번도로 | Route 25 | 25번도로 또는 진화: 나옹 — Night Stone. 사용 |
| 864 | 산호르곤 | Cursola |  |  | 코산호에게 Night Stone 사용 |
| 865 | 창파나이트(Z) | Sirfetch’d (Z) |  |  | 진화: 파오리 — Hard Bread. 사용 |
| 866 | 마임꽁꽁 | Mr. Rime | 기남시티 | Batik City | 기남시티 또는 진화: 마임맨 — 각성의돌. 사용 |
| 867 | 데스판 | Runerigus | 25번도로 | Route 25 | 25번도로 또는 진화: 데스마스 — Night Stone. 사용 |
| 868 | 마빌크 | Milcery | 8번도로 / 란토 저택 | Route 8 / Chateau Lanto | 8번도로 (란토 저택 화면) |
| 869 | 마휘핑 | Alcremie | 8번도로 | Route 8 | 8번도로 또는 진화: 마빌크 — 달의돌. 사용 |
| 870 | 대여르 | Falinks | 세르티호섬 | Certijo Island | 세르티호섬 |
| 871 | 찌르성게 | Pincurchin | 11번도로 | Route 11 | 11번도로 |
| 872 | 누니머기 | Snom | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 |
| 873 | 모스노우 | Frosmoth | 칼로스 피레네 / 이설시티 | Kalos Pyrenees / Fractal City | 칼로스 피레네 또는 이설시티 |
| 874 | 돌헨진 | Stonjourner | 25번도로 | Route 25 | 25번도로 |
| 875 | 빙큐보 | Eiscue | 상기노마을 | Sanguino Town | 교환: 모르페코 — 상기노마을 |
| 876 | 에써르 | Indeedee | 미르 신시가지 - 남쪽 | South Luminalia Expansions | 미르 신시가지 - 남쪽 |
| 877 | 모르페코 | Morpeko | 12번도로 | Route 12 | 12번도로 |
| 878 | 끼리동 | Cufant | 휴게소 | Service Station | 휴게소 |
| 879 | 대왕끼리동 | Copperajah | 휴게소 | Service Station | 휴게소 또는 진화: 끼리동 — 34레벨 |
| 880 | 파치래곤 | Dracozolt | 배롱마을 | Mosaic City | 배롱마을에서 조개화석과 교환 |
| 881 | 파치르돈 | Arctozolt | 배롱마을 | Mosaic City | 배롱마을에서 껍질화석과 교환 |
| 882 | 어래곤 | Dracovish | 배롱마을 | Mosaic City | 배롱마을에서 뿌리화석과 교환 |
| 883 | 어치르돈 | Arctovish | 배롱마을 | Mosaic City | 배롱마을에서 발톱화석과 교환 |
| 884 | 두랄루돈 | Duraludon | 미르 신시가지 - 남쪽 | South Luminalia Expansions | 미르 신시가지 - 남쪽 |
| 885 | 드라꼰 | Dreepy | 22번도로 | Route 22 | 22번도로 |
| 886 | 드래런치 | Drakloak |  |  | 드라꼰을 50레벨까지 키우면 진화 |
| 887 | 드래펄트 | Dragapult |  |  | 드래런치를 60레벨까지 키우면 진화 |
| 888 | 자시안 | Zacian | 왕들의 성소 | Kings’ Sanctuary | 왕들의 성소 (얀트라 사건 이후) |
| 889 | 자마젠타 | Zamazenta | 왕들의 성소 | Kings’ Sanctuary | 왕들의 성소 (얀트라 사건 이후) |
| 890 | 무한다이노 | Eternatus | 서부 카타콤 | Western Catacombs | 서부 카타콤 (퍼즐을 푼 뒤) |
| 891 | 치고마 | Kubfu | 사라시티 | Yantra City | 사라시티 |
| 892 | 우라오스 | Urshifu |  |  | 치고마를 친밀도로 진화 |
| 893 | 자루도 | Zarude | 20번도로 | Route 20 | 20번도로 (얀트라 사건 이후) |
| 894 | 레지에레키 | Regieleki | 대박람회 | Grand Exhibition | 대박람회 (얀트라 사건 이후) |
| 895 | 레지드래고 | Regidrago | 17번도로 | Route 17 | On 17번도로 |
| 896 | 블리자포스 | Glastrier | 이설시티 | Fractal City | 이설시티 |
| 897 | 레이스포스 | Spectrier | 어둠의 탑 | Dark Tower | 어둠의 탑 (얀트라 사건 이후) |
| 898 | 버드렉스 | Calyrex | 바니타스 텃밭 | Vanitas Orchard | 바니타스 텃밭 (얀트라 사건 이후) |
| 903 | 사마자르 | Kleavor |  |  | 스라크가 바위깨기를 배운 상태로 진화 |
| 904 | 신비록 | Wyrdeer |  |  | 노라키를 40레벨까지 키우면 진화 |
| 905 | 대쓰여너 | Basculegion |  |  | 배쓰나이를 40레벨까지 키우면 진화 |
| 906 | 장침바루 | Overqwil |  |  | 침바루가 독압정을 배운 상태로 진화 |
| 907 | 포푸니크 | Sneasler |  |  | 포푸니가 독찌르기를 배운 상태로 진화 |
| 994 | 다투곰 | Ursaluna |  |  | 링곰을 45레벨까지 키우면 진화 |
| 995 | 러브로스 | Enamorus | 페트로 동굴 | Petro Cave | 페트로 동굴, (얀트라 사건 이후) |

### 9세대 (95행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 909 | 나오하 | Sprigatito | 카페 갈라네스 | Galanes Café | At 카페 갈라네스 for a 켈리몬 |
| 910 | 나로테 | Floragato |  |  | 나오하를 18레벨까지 키우면 진화 |
| 911 | 마스카나 | Meowscarada |  |  | 나로테를 45레벨까지 키우면 진화 |
| 912 | 뜨아거 | Fuecoco | 카페 갈라네스 | Galanes Café | At 카페 갈라네스 for a 곤율거니 |
| 913 | 악뜨거 | Crocalor |  |  | 뜨아거를 18레벨까지 키우면 진화 |
| 914 | 라우드본 | Skeledirge |  |  | 악뜨거를 45레벨까지 키우면 진화 |
| 915 | 꾸왁스 | Quaxly | 카페 갈라네스 | Galanes Café | At 카페 갈라네스 for a 일레도리자드 |
| 916 | 아꾸왁 | Quaxwell |  |  | 꾸왁스를 18레벨까지 키우면 진화 |
| 917 | 웨이니발 | Quaquaval |  |  | 아꾸왁을 45레벨까지 키우면 진화 |
| 918 | 맛보돈 | Lechonk | 9번도로 | Route 9 | 9번도로 |
| 919 | 퍼퓨돈 | Oinkologne | 9번도로 | Route 9 | 9번도로 또는 진화: 맛보돈 — 18레벨 |
| 920 | 노고고치 | Dudunsparce | 24번도로 | Route 24 | 24번도로 또는 진화: 노고치 — 37레벨 |
| 921 | 타랜툴라 | Tarountula |  |  | 트래피더. 교배로 얻는다 |
| 922 | 트래피더 | Spidops | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 923 | 콩알뚜기 | Nymble | 비탈 숲 | Hillside Forest | 비탈 숲 |
| 924 | 엑스레그 | Lokix |  |  | 콩알뚜기를 24레벨까지 키우면 진화 |
| 925 | 구르데 | Rellor | 6번도로 | Route 6 | 6번도로 |
| 926 | 베라카스 | Rabsca |  |  | 구르데를 30레벨까지 키우면 진화 |
| 927 | 망망이 | Greavard | 6번도로 | Route 6 | 6번도로 |
| 928 | 묘두기 | Houndstone |  |  | 망망이를 30레벨까지 키우면 진화 |
| 929 | 하느라기 | Flittle | 3번도로 | Route 3 | 3번도로 |
| 930 | 클레스퍼트라 | Espathra |  |  | 하느라기를 35레벨까지 키우면 진화 |
| 931 | 키키링 | Farigiraf |  |  | 키링키를 40레벨까지 키우면 진화 |
| 932 | 어써러셔 | Dondozo | 16번도로 | Route 16 | 물속 — 16번도로 |
| 933 | 가비루사 | Veluza | 가라마을 | Petroglifo Town | 물속 — 가라마을 |
| 934 | 맨돌핀 | Finizen | 아크릴리코마을 | Acrílico Town | 물속 — 아크릴리코마을 |
| 935 | 돌핀맨 | Palafin | 아크릴리코마을 | Acrílico Town | 물속 — 아크릴리코마을 또는 진화: 맨돌핀 — 38레벨 |
| 936 | 미니브 | Smoliv |  |  | 올리뇨/올리르바. 교배로 얻는다 |
| 937 | 올리뇨 | Dolliv | 8번도로 | Route 8 | 8번도로 |
| 938 | 올리르바 | Arboliva |  |  | 올리뇨를 35레벨까지 키우면 진화 |
| 939 | 캡싸이 | Capsakid | 왕들의 성소 | Kings’ Sanctuary | 왕들의 성소 |
| 940 | 스코빌런 | Scovillain |  |  | 캡싸이에게 불꽃의돌 사용 |
| 941 | 빈나두 | Tadbulb | 빛나는 동굴 | Shimmering Cave | 빛나는 동굴 |
| 942 | 찌리배리 | Bellibolt |  |  | 빈나두에게 천둥의돌 사용 |
| 943 | 부르롱 | Varoom |  |  | Revaroom. 교배로 얻는다 |
| 944 | Revaroom | Revaroom | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 |
| 945 | 꿈트렁 | Orthworm | 휴게소 | Service Station | 휴게소 |
| 946 | 두리쥐 | Tandemaus |  |  | 사프라 보상 (이후 — Restaurant) |
| 947 | 파밀리쥐 | Maushold |  |  | 두리쥐를 25레벨까지 키우면 진화 |
| 948 | 터벅고래 | Cetoddle |  |  | 우락고래. 교배로 얻는다 |
| 949 | 우락고래 | Cetitan | 프로스트케이브 | Frozen Grotto | 프로스트케이브 |
| 950 | 드니차 | Frigibax | 프로스트케이브 | Frozen Grotto | 프로스트케이브 |
| 951 | 드니꽁 | Arctibax |  |  | 드니차를 35레벨까지 키우면 진화 |
| 952 | 드닐레이브 | Baxcalibur |  |  | 드니꽁을 54레벨까지 키우면 진화 |
| 953 | 싸리용 | Tatsugiri | 16번도로 | Route 16 | 물속 — 16번도로 |
| 954 | 모토마 | Cyclizar | 휴게소 | Service Station | 휴게소 |
| 955 | 빠모 | Pawmi | 2번도로 | Route 2 | 2번도로 |
| 956 | 빠모트 | Pawmo |  |  | 빠모를 18레벨까지 키우면 진화 |
| 957 | 빠르모트 | Pawmot |  |  | 빠모트를 친밀도로 진화 |
| 958 | 찌리비 | Wattrel | 백단시티 / 11번도로 | Novarte City / Route 11 | 백단시티 또는 11번도로 |
| 959 | 찌리비크 | Kilowattrel | 11번도로 | Route 11 | 11번도로 또는 진화: 찌리비 — 25레벨 |
| 960 | 떨구새 | Bombirdier | 14번도로 | Route 14 | 14번도로 |
| 961 | 시비꼬 | Squawkabilly | 후늬시티 | Romantis City | 피죤투 — 후늬시티와 교환 |
| 962 | Flamingo | Flamingo | 세르티호섬 | Certijo Island | 세르티호섬 |
| 963 | 절벼게 | Klawf | 10번도로 | Route 10 | 10번도로 |
| 964 | 베베솔트 | Nacli |  |  | 스태솔트/콜로솔트. 교배 |
| 965 | 스태솔트 | Naclstack | 휴게소 | Service Station | 휴게소 |
| 966 | 콜로솔트 | Garganacl | 칼로스 동부 전투 | East Kalos Battle | 칼로스 동부 전투 또는 진화: 스태솔트 — 38레벨 |
| 967 | 초롱순 | Glimmet | 북부 카타콤 | Northern Catacombs | 북부 카타콤 |
| 968 | 킬라플로르 | Glimmora | 북부 카타콤 | Northern Catacombs | 북부 카타콤 또는 진화: 초롱순 — 35레벨 |
| 969 | 땃쭈르 | Shroodle |  |  | 태깅구르. 교배로 얻는다 |
| 970 | 태깅구르 | Grafaiai | 14번도로 | Route 14 | 14번도로 |
| 971 | 쫀도기 | Fidough | 2번도로 | Route 2 | 2번도로 |
| 972 | 바우첼 | Dachsbun |  |  | 쫀도기를 26레벨까지 키우면 진화 |
| 973 | 오라티프 | Maschiff | 폭풍 언덕 | Storm Hill | 폭풍 언덕 |
| 974 | 마피티프 | Mabosstiff |  |  | 오라티프를 30레벨까지 키우면 진화 |
| 975 | 그푸리 | Bramblin |  |  | 공푸리 교배로 얻는다 |
| 976 | 공푸리 | Brambleghast | 24번도로 | Route 24 | 24번도로 |
| 977 | 모으령 | Gimmighoul | 8번도로 | Route 8 | 8번도로 |
| 978 | 타부자고 | Gholdengo |  |  | 모으령을 50레벨까지 키우면 진화 |
| 979 | 어리짱 | Tinkatink | 5번도로 | Route 5 | 5번도로 |
| 980 | 벼리짱 | Tinkatuff |  |  | 어리짱을 24레벨까지 키우면 진화 |
| 981 | 두드리짱 | Tinkaton |  |  | 벼리짱을 38레벨까지 키우면 진화 |
| 982 | 카르본 | Charcadet | 7번도로 | Route 7 | 북쪽 7번도로 |
| 983 | 카디나르마 | Armarouge |  |  | 카르본에게 불꽃의돌 사용 |
| 984 | 파라블레이즈 | Ceruledge |  |  | 카르본에게 어둠의돌 사용 |
| 985 | 대도각참 | Kingambit |  |  | 절각참을 42레벨까지 키우면 진화 |
| 986 | 토오 | Clodsire | 프로파노 늪 | Profane Swamp | 프로파노 늪 또는 진화: 우파 — 배운 기술: 독찌르기 |
| 987 | 저승갓숭 | Annihilape |  |  | 성원숭을 45레벨까지 키우면 진화 |
| 988 | 총지엔 | Wo-Chien | 북부 카타콤 | Northern Catacombs | 북부 카타콤 |
| 989 | 파오젠 | Chien-Pao | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 990 | 딩루 | Ting-Lu | 동부 카타콤 | Eastern Catacombs | 동부 카타콤 |
| 991 | 위유이 | Chi-Yu | 서부 카타콤 | Western Catacombs | 서부 카타콤 |
| 992 | 코라이돈 | Koraidon | 번영의 성소 / 드루이드의 방 | Prosperity Sanctuary / druidic cave | 번영의 성소 안쪽 — 드루이드의 방 |
| 993 | 미라이돈 | Miraidon | 몬스터볼 공장 | Poké Ball Factory | 몬스터볼 공장 |
| 999 | 과미르 | Dipplin |  |  | 과사삭벌레를 28레벨까지 키우면 진화 |
| 1000 | 조타구 | Okidogi | 프로파노 늪 | Profane Swamp | 프로파노 늪, (얀트라 사건 이후) |
| 1001 | 이야후 | Munkidori | 프로파노 늪 | Profane Swamp | 프로파노 늪, (얀트라 사건 이후) |
| 1002 | 기로치 | Fezandipiti | 프로파노 늪 | Profane Swamp | 프로파노 늪, (얀트라 사건 이후) |
| 1003 | 오거폰 | Ogerpon | 16번도로 | Route 16 | On 16번도로, (얀트라 사건 이후) |
| 1004 | 그우린차 | Sinistcha |  |  | 데인차에게 리프의돌 사용 |
| 1005 | 브리두라스 | Archaludon | 미르 신시가지 | Luminalia Expansions | 미르 신시가지 또는 진화: 두랄루돈 — 55레벨 |
| 1006 | 과미드라 | Hydrapple |  |  | 과미르를 50레벨까지 키우면 진화 |
| 1016 | 테라파고스 | Terapagos | 물에 잠긴 옛 대장간 | Abandoned Forge | 물에 잠긴 옛 대장간 (얀트라 사건 이후) |
| 1017 | 복숭악동 | Pecharunt | 프로파노 늪 | Profane Swamp | 프로파노 늪, 나무 위, (얀트라 사건 이후) |

### 전설 (90행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 1 | 라이코 | Raikou | 빛나는 동굴 | Shimmering Cave | 최북단 — 빛나는 동굴 (파도타기 길) |
| 2 | 앤테이 | Entei | 그리사야 동굴 | Grisalla Cave | 가장 깊은 곳 — 그리사야 동굴 |
| 3 | 스이쿤 | Suicune | 음침한 동굴 | Gloomy Cave | 가장 깊은 곳 — 음침한 동굴 |
| 4 | 크레세리아 | Cresselia | 세뇨리알 대성당 | Manorial Cathedral | 세뇨리알 대성당 (Mercuric Key 문) |
| 5 | 다크라이 | Darkrai | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 (왼쪽 위) |
| 6 | 레지락 | Regirock |  |  | Endgame Cave 퍼즐 바위 |
| 7 | 레지아이스 | Regice | 프로스트케이브 | Frozen Grotto | 프로스트케이브 (Lens Truth) |
| 8 | 레지스틸 | Registeel | 불타는 구렁 | Burning Abyss | 불타는 구렁 — Prison Island |
| 9 | 레지기가스 | Regigigas | 아틀라스 동굴 / 21번도로 | Atlas Cavern / Route 21 | 아틀라스 동굴 (21번도로) |
| 10 | 마기아나 | Magearna | 백단시티 | Novarte City | 화석 되살리기 — 백단시티 (Mechanical Heart) |
| 11 | 유크시 | Uxie | 15번도로 / 프시케 동굴 | Route 15 / Psyche Cave | 15번도로 작은 섬 ((도주 이후) 프시케 동굴) |
| 12 | 엠라이트 | Mesprit | 12번도로 | Route 12 | 12번도로 남쪽 작은 섬 |
| 13 | 아그놈 | Azelf | 9번도로 | Route 9 | 9번도로 조수 섬 |
| 14 | 코바르온 | Cobalion | 몬스터볼 공장 | Poke Ball Factory | 몬스터볼 공장 바깥 정원 |
| 15 | 테라키온 | Terrakion | 12번도로 | Route 12 | 12번도로 가장 왼쪽 |
| 16 | 비리디온 | Virizion | 비탈 숲 | Hillside Forest | 비탈 숲 오른쪽 |
| 17 | 케르디오 | Keldeo | 배롱마을 | Mosaic Town | 배롱마을 산악 구역 |
| 18 | 마나피 | Manaphy | 아크릴리코마을 | Acrylic Town | 앞바다 — 아크릴리코마을 (잠수 길) |
| 19 | 피오네 | Phione | 5번도로 | Route 5 | 교배: 마나피 — 메타몽 (5번도로 키우미집) 사용 |
| 20 | 카푸꼬꼬꼭 | Tapu Koko | 몬테산토섬 | Montesanto Island | 몬테산토섬 입구 |
| 21 | 카푸나비나 | Tapu Lele | 몬테산토섬 | Montesanto Island | 몬테산토섬 왼쪽 위 |
| 22 | 카푸브루루 | Tapu Bulu | 몬테산토섬 | Montesanto Island | 몬테산토섬 오른쪽 위 |
| 23 | 카푸느지느 | Tapu Fini | 몬테산토섬 | Montesanto Island | 몬테산토섬 오른쪽 아래 |
| 24 | 프리져 | Articuno | 칼로스 피레네 | Pyrenees | 칼로스 피레네 풀언덕 |
| 25 | 썬더 | Zapdos | 폭풍 언덕 | Storm Hill | 폭풍 언덕 남쪽 |
| 26 | 파이어 | Moltres | 불타는 구렁 | Burning Abyss | 불타는 구렁 내부 |
| 27 | 뮤츠 | Mewtwo | 플레어 연구소 | Flare Laboratory | 플레어 연구소 (M Embryo) |
| 28 | 뮤 | Mew | 탈라시아 동굴 | Talasia Cave | 탈라시아 동굴 퍼즐 |
| 29 | 루기아 | Lugia | 해저 | Petroglifo Seafloor | 해저 |
| 30 | 칠색조 | Ho-Oh | 15번도로 | Route 15 | 15번도로 강길 |
| 31 | 세레비 | Celebi | 비탈 숲 | Hillside Forest | 비탈 숲 샛길 |
| 32 | 라티아스 | Latias | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 |
| 33 | 라티오스 | Latios | 번영의 성소 | Prosperity Sanctuary | 번영의 성소 |
| 34 | 가이오가 | Kyogre |  |  | 물속 — Fluxus 호수 |
| 35 | 그란돈 | Groudon | 망각의 감옥 | Prison of Oblivion | 망각의 감옥 출구 |
| 36 | 레쿠쟈 | Rayquaza | 버려진 등대 | Abandoned Lighthouse | 버려진 등대 꼭대기 |
| 37 | 지라치 | Jirachi | 아크릴리코마을 | Acrylic Town | 아크릴리코마을 |
| 38 | 테오키스 | Deoxys | 수수께끼의 장소 | Mysterious Place | 수수께끼의 장소 (station 문) |
| 39 | 디아루가 | Dialga | 떠도는 숲 | Wandering Forest | 떠도는 숲 퍼즐 |
| 40 | 펄기아 | Palkia | 미르 신시가지 | Luminalia Extensions | 동쪽 미르 신시가지 |
| 41 | 히드런 | Heatran | 불타는 구렁 | Burning Abyss | 불타는 구렁 왼쪽 길 |
| 42 | 기라티나 | Giratina | 22번도로 / 상기노마을 | Route 22 / Sanguine Town | 22번도로 직전 — 상기노마을 |
| 43 | 쉐이미 | Shaymin | 떠도는 숲 | Wandering Forest | 떠도는 숲 석상 이벤트 |
| 44 | 아르세우스 | Arceus | 창기둥 | Spear Pillar | 창기둥 차원문 이벤트 |
| 45 | 비크티니 | Victini | 레비아탄 요새 | Fort Leviathan | 레비아탄 요새 우리 |
| 46 | 토네로스 | Tornadus | 음침한 동굴 | Gloomy Cave | 음침한 동굴 파도타기 구역 |
| 47 | 볼트로스 | Thundurus | 빛나는 동굴 | Shimmering Cave | 빛나는 동굴 길 |
| 48 | 랜드로스 | Landorus | 그리사야 동굴 | Grisalla Cave | 그리사야 동굴 호수 |
| 49 | 레시라무 | Reshiram | 로시욘 저택 | Chateau Rosillon | 로시욘 저택 발코니 |
| 50 | 제크로무 | Zekrom | 란토 저택 | Chateau Lanto | 란토 저택 |
| 51 | 큐레무 | Kyurem | 칼로스 피레네 | Kalos Pyrenees | 칼로스 피레네 길 |
| 52 | 메로엣타 | Meloetta | 미르시티 - 서쪽 | West Luminalia | 미르시티 - 서쪽 |
| 53 | 게노세크트 | Genesect | 불탄 공방 | Burned Workshop | 불탄 공방 |
| 54 | 디안시 | Diancie | 비춤의 동굴 | Reflection Cave | 비춤의 동굴 숨은 문 |
| 55 | 후파 | Hoopa | 상기노마을 | Sanguine Town | 상기노마을 카지노 |
| 56 | 볼케니온 | Volcanion | 미르시티 - 서쪽 | West Luminalia | 미르시티 - 서쪽 이벤트 |
| 57 | 타입:널 | Type: Null | 얀트라 농장 | Yantra Farm | 얀트라 농장 |
| 58 | 실버디 | Silvally | 얀트라 농장 | Yantra Farm | 얀트라 농장 (진화) |
| 59 | 코스모그 | Cosmog | 세르티호섬 / 옛 바니타스 | Certijo Island / Old Vanitas | 세르티호섬 / 옛 바니타스 |
| 60 | 코스모움 | Cosmoem |  |  | 진화로 얻는다 코스모그 |
| 61 | 솔가레오 | Solgaleo |  |  | 진화로 얻는다 계열 |
| 62 | 루나아라 | Lunala |  |  | 진화로 얻는다 계열 |
| 63 | 네크로즈마 | Necrozma | 미르 지하묘지 | Luminalia Crypts | 미르 지하묘지 중앙 |
| 64 | 마샤도 | Marshadow | 상기나 해안 | Sanguine Coast | 상기나 해안 |
| 65 | 제라오라 | Zeraora | 휴게소 | Service Station | 휴게소 계단 |
| 66 | 자시안 | Zacian | 왕들의 성소 | Kings Sanctuary | 왕들의 성소 |
| 67 | 자마젠타 | Zamazenta | 5번도로 | Route 5 | 5번도로 바위 오르막 |
| 68 | 무한다이노 | Eternatus | 서부 카타콤 | Western Catacombs | 서부 카타콤 퍼즐 |
| 69 | 자루도 | Zarude | 20번도로 | Route 20 | 20번도로 늪 |
| 70 | 레지에레키 | Regieleki | 배롱마을 | Mosaic Town | 배롱마을 박람회 |
| 71 | 레지드래고 | Regidrago | 17번도로 | Route 17 | 17번도로 |
| 72 | 블리자포스 | Glastrier | 이설시티 | Fractal City | 이설시티 계단 |
| 73 | 레이스포스 | Spectrier | 어둠의 탑 | Dark Tower | 어둠의 탑 방 |
| 74 | 버드렉스 | Calyrex | 바니타스 텃밭 | Vanitas Orchard | 바니타스 텃밭 |
| 75 | 총지엔 | Wo-Chien | 북부 카타콤 | Northern Catacombs | 북부 카타콤 |
| 76 | 파오젠 | Chien-Pao | 남부 카타콤 | Southern Catacombs | 남부 카타콤 |
| 77 | 딩루 | Ting-Lu | 동부 카타콤 | Eastern Catacombs | 동부 카타콤 |
| 78 | 위유이 | Chi-Yu | 서부 카타콤 | Western Catacombs | 서부 카타콤 |
| 79 | 코라이돈 | Koraidon | 드루이드의 방 | Druidic Chamber | 드루이드의 방 |
| 80 | 미라이돈 | Miraidon | 몬스터볼 공장 | Poke Ball Factory | 몬스터볼 공장 |
| 81 | 러브로스 | Enamorus | 페트로 동굴 | Petro Cave | 페트로 동굴 |
| 82 | 조타구 | Okidogi | 프로파노 늪 | Profane Swamp | 프로파노 늪 NE |
| 83 | 이야후 | Munkidori | 프로파노 늪 | Profane Swamp | 프로파노 늪 굴 |
| 84 | 기로치 | Fezandipiti | 프로파노 늪 | Profane Swamp | 프로파노 늪 비행 구역 |
| 85 | 오거폰 | Ogerpon | 16번도로 | Route 16 | 16번도로 |
| 86 | 테라파고스 | Terapagos | 물에 잠긴 대장간 | Flooded Forge | 옛 물에 잠긴 대장간 |
| 87 | 복숭악동 | Pecharunt | 깊은 굴 | Deep Burrow | 깊은 굴 |
| 88 | 제르네아스 | Xerneas | 깊은 샘 | Deep Spring | 깊은 샘 |
| 89 | 이벨타르 | Yveltal | 서커스의 악몽 | Circus Nightmare | 서커스의 악몽 |
| 90 | 지가르데 | Zygarde | 프리즘타워 | Prism Tower | 프리즘타워 꼭대기 |

### 페이크몬 (18행)

| 번호 | 포켓몬(한국어) | 원표 영어명 | 출현 장소(한국어) | 원표 장소 표기 | 조건·비고(한국어) |
|---|---|---|---|---|---|
| 899 | 제피레온 | Cefireon | 몬테산토섬 | Montesanto Island | 진화: 이브이 — Wind Feather. (완주: 몬테산토섬) 사용 |
| 900 | Maidible (Mega Mawile) | Maidible (Mega Mawile) |  |  | 입치트를 45레벨까지 키우면 진화 |
| 901 | Zippectre (Mega Banette) | Zippectre (Mega Banette) |  |  | 다크펫을 40레벨까지 키우면 진화 |
| 902 | Soundow (Mega Audino) | Soundow (Mega Audino) |  |  | 다부니를 40레벨까지 키우면 진화 |
| 908 | Missigno | Missigno | 궁극병기 | Ultimate Weapon | 안쪽에서 포획 — 궁극병기 |
| 996 | Cherriller | Cherriller |  |  | 체리꼬를 32레벨까지 키우면 진화 |
| 997 | 로얄레온 | Royaleon | 세르티호섬 | Certijo Island | 진화: 이브이 — Royal Wig. (세르티호섬) 사용 |
| 998 | 고르마우스 | Gourmaus |  |  | 파밀리쥐를 38레벨까지 키우면 진화 |
| 1007 | 할콤바테 | Halcombate |  |  | 루차불을 55레벨까지 키우면 진화 |
| 1008 | 세르두플라 | Serdupla |  |  | 세비퍼를 52레벨까지 키우면 진화 |
| 1009 | 장굴 | Zanghoul |  |  | 쟝고를 52레벨까지 키우면 진화 |
| 1010 | 프레이징크스 | Freyjynx |  |  | 루주라를 65레벨까지 키우면 진화 |
| 1011 | 포베토 | Fobeto |  |  | 슬리퍼를 65레벨까지 키우면 진화 |
| 1012 | 콘스텔라 | Constellar |  |  | 진화: 솔록 또는 루나톤 (둘 다 파티에 넣고 레벨 업) |
| 1013 | 루보른 | Luvourne |  |  | 사랑동이를 60레벨까지 키우면 진화 |
| 1014 | 마롤리에 | Marolier |  |  | 텅구리를 65레벨까지 키우면 진화 |
| 1015 | 수드라실 | Sudrasil |  |  | 꼬지모를 70레벨까지 키우면 진화 |
| 1018 | 아우레토스크 | Auretosk |  |  | 스토리 끝 |

## 미해결

조회표로 풀리지 않아 원문을 그대로 둔 자리다.

**포켓몬 이름 9종** — `Cherriller`, `Drillbur`, `Flamingo`, `Formantis`, `Maidible (Mega Mawile)`, `Missigno`, `Revaroom`, `Soundow (Mega Audino)`, `Zippectre (Mega Banette)`

**영어가 남은 조건 문구 40행**(서로 다른 문구 39종). 대부분 사이트가 붙인 퀘스트·이벤트 이름이라 우리 정본에 대응어가 없다.

- `사용: Day Stone` (2행)
- `불타는 구렁 (불타는 구렁 / Sima Ardiente)`
- `후늬시티 또는 진화: 슈륙챙이 by leveling up once — 왕의징표석 낮에 사용`
- `Barracks 보상 (3rd Delinquent)`
- `남부 카타콤 또는 Dark Cave`
- `Dark Cave 또는 친밀도`
- `코인 400개 — Sanguine 카지노`
- `Dark Cave`
- `Dark Cave 또는 진화: — 32레벨`
- `Dark Cave (얀트라 사건 이후)`
- `칼로스 동부 전투 또는 Night Stone`
- `코인 1400개 — Sanguine 카지노`
- `미르시티 - 서쪽 신시가지 Pokémon Center`
- `Profano Witch 이벤트`
- `진화: 코스모움 (Day Stone)`
- `진화: 코스모움 (Night Stone)`
- `백단시티 (이후 — Mechanical Heart)`
- `코인 700개와 교환 — Sanguino 카지노`
- `우츠보트 — Fluxus Café와 교환`
- `앤티골 — Fluxus Café와 교환`
- `치갈기 — Fluxus Café와 교환`
- `Dark Cave 또는 진화: 탄동 — 18레벨`
- `데인차에게 Night Stone 사용`
- `25번도로 또는 진화: 나옹 — Night Stone. 사용`
- `코산호에게 Night Stone 사용`
- `진화: 파오리 — Hard Bread. 사용`
- `25번도로 또는 진화: 데스마스 — Night Stone. 사용`
- `Revaroom. 교배로 얻는다`
- `사프라 보상 (이후 — Restaurant)`
- `세뇨리알 대성당 (Mercuric Key 문)`
- `Endgame Cave 퍼즐 바위`
- `프로스트케이브 (Lens Truth)`
- `불타는 구렁 — Prison Island`
- `화석 되살리기 — 백단시티 (Mechanical Heart)`
- `플레어 연구소 (M Embryo)`
- `물속 — Fluxus 호수`
- `수수께끼의 장소 (station 문)`
- `진화: 이브이 — Wind Feather. (완주: 몬테산토섬) 사용`
- `진화: 이브이 — Royal Wig. (세르티호섬) 사용`

이 중 다음 셋은 조회로 풀리는지 확인했으나 근거가 없어 남겼다.

- `Dark Cave` — 지명 대응표에서도 미해결로 남긴 자리다. `Cueva Lóbrega`(음침한 동굴)로 보이나 확인 못 했다.
- `Night Stone` / `Day Stone` — 우리 07절에 `Piedra Noche`(어둠의돌)·`Piedra Día`(빛의돌)가 있지만,
  사이트가 `Dusk Stone`도 따로 쓰기 때문에 같은 도구인지 확정하지 못했다.
- `Hard Bread` / `Royal Wig` / `Wind Feather` — 팬게임 자체 도구. 영어 이름만으로는 원문을 못 찾았다.
