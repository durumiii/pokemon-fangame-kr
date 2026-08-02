# namudex — 나무위키 도감 설명 추출 보고

- 원본: HuggingFace `heegyu/namuwiki` / `namuwiki_20210301.parquet` (문서 867,024개)
- 종 이름 후보로 걸러낸 문서 1,147개 중 `[anchor(앵커-도감 설명)]`을 가진 문서 541개
- 파싱 성공 문서 539개, 원시 행 10119개, 전개 후 14487행
- 종 수 895 (도감번호 기준)

## 판본별 커버리지 (폼 주석 없는 행만)

| 판본 | 종 수 |
|---|---|
| x | 715 |
| omega-ruby | 713 |
| y | 712 |
| alpha-sapphire | 710 |
| black | 648 |
| white | 648 |
| black-2 | 646 |
| white-2 | 646 |
| diamond | 492 |
| heartgold | 492 |
| pearl | 492 |
| platinum | 492 |
| soulsilver | 492 |
| shield | 431 |
| sword | 416 |
| ultra-sun | 396 |
| ultra-moon | 395 |
| ruby | 385 |
| sapphire | 385 |
| emerald | 384 |
| firered | 384 |
| leafgreen | 384 |
| go | 322 |
| moon | 297 |
| sun | 297 |
| crystal | 250 |
| gold | 250 |
| silver | 250 |
| lets-go-eevee | 152 |
| lets-go-pikachu | 151 |
| blue | 150 |
| green | 150 |
| red | 150 |
| yellow | 150 |

## 판본 라벨 사전 (원문 → 전개)

| 원문 라벨 | 등장 | 전개 |
|---|---|---|
| `X` | 715 | x |
| `Y` | 711 | y |
| `실드` | 678 | shield |
| `소드` | 652 | sword |
| `울트라문` | 428 | ultra-moon |
| `울트라썬` | 426 | ultra-sun |
| `5세대` | 343 | black, white, black-2, white-2 |
| `포켓몬 GO` | 334 | go |
| `문` | 328 | moon |
| `썬` | 327 | sun |
| `DPPt` | 274 | diamond, pearl, platinum |
| `크리스탈` | 250 | crystal |
| `OR` | 248 | omega-ruby |
| `AS` | 247 | alpha-sapphire |
| `금/HG` | 246 | gold, heartgold |
| `은/SS` | 246 | silver, soulsilver |
| `기라티나` | 213 | platinum |
| `에메랄드` | 202 | emerald |
| `루비/OR` | 195 | ruby, omega-ruby |
| `사파이어/AS` | 193 | sapphire, alpha-sapphire |
| `RSE/ORAS` | 181 | ruby, sapphire, emerald, omega-ruby, alpha-sapphire |
| `블랙` | 156 | black |
| `화이트` | 156 | white |
| `레츠고! 피카츄/이브이` | 152 | lets-go-pikachu, lets-go-eevee |
| `BW2` | 151 | black-2, white-2 |
| `펄기아` | 151 | pearl |
| `청/LG` | 150 | blue, leafgreen |
| `피카츄` | 150 | yellow |
| `적/녹/FR` | 149 | red, green, firered |
| `디아루가` | 149 | diamond |
| `블랙 2` | 147 | black-2 |
| `화이트 2` | 147 | white-2 |
| `BW` | 145 | black, white |
| `HGSS` | 143 | heartgold, soulsilver |
| `파이어레드/리프그린` | 130 | firered, leafgreen |
| `리프그린` | 93 | leafgreen |
| `파이어레드` | 92 | firered |
| `하트골드/소울실버` | 91 | heartgold, soulsilver |
| `오메가루비` | 89 | omega-ruby |
| `알파사파이어` | 89 | alpha-sapphire |
| `디아루가/펄기아` | 61 | diamond, pearl |
| `사파이어` | 9 | sapphire |
| `LG` | 8 | leafgreen |
| `FR` | 8 | firered |
| `루비` | 7 | ruby |
| `하트골드` | 6 | heartgold |
| `소울실버` | 6 | soulsilver |
| `하트골드·소울실버` | 4 | heartgold, soulsilver |
| `다이아몬드` | 4 | diamond |
| `플라티나` | 4 | platinum |
| `블랙·화이트 2` | 3 | black-2, white-2 |
| `펄` | 3 | pearl |
| `디이루가` | 2 | diamond |
| `포켓몬GO` | 2 | go |
| `FR/LG` | 2 | firered, leafgreen |
| `FRLG` | 2 | firered, leafgreen |
| `3세대` | 2 | ruby, sapphire, emerald |
| `블랙/화이트` | 2 | black, white |
| `BW/BW2` | 2 | black, white, black-2, white-2 |
| `금` | 2 | gold |
| `은` | 2 | silver |
| `적/녹/FR/썬` | 1 | red, green, firered, sun |
| `레츠고 이브이` | 1 | lets-go-eevee |
| `XY` | 1 | x, y |
| `금/하트골드` | 1 | gold, heartgold |
| `은/소울실버` | 1 | silver, soulsilver |
| `다이아몬드/펄` | 1 | diamond, pearl |
| `금/HG/LG` | 1 | gold, heartgold, leafgreen |
| `은/SS/FR` | 1 | silver, soulsilver, firered |
| `디아루가·펄기아` | 1 | diamond, pearl |
| `펄/플라티나` | 1 | pearl, platinum |

## 파싱 실패 유형

| 유형 | 건수 | 설명 |
|---|---|---|
| empty | 306 | 본문 칸이 비어 있는 행(예: `포켓몬 GO` 미기재) |
| no-species | 194 | 위 머리 실패로 종이 안 잡힌 상태의 데이터 행 |
| header | 49 | 폼 전용 절 머리(메가·지우개굴닌자 등) — 도감번호가 없어 종을 못 붙임 |

## 한계

- 덤프 시점이 **2021-03-01**이다. `heegyu/namuwiki`에 올라온 원본 스냅숏이 그것 하나뿐이라
  요청받은 2022년판이 아니다. 그래서 `source_name`은 `fan_wiki_namuwiki_20210301`으로 적었다.
- 도감번호 899 이상(9세대·전설의섬 이후 추가분)은 덤프에 문서가 없다.
- 898 이하인데 빠진 종 16개: 140, 718, 741, 745, 849, 854, 855, 875, 876, 877, 891, 892, 893, 894, 895, 898
  대부분 절 머리가 도감번호 없이 폼 이름(우라오스 일격의 태세 등)으로만 서 있어 종을 못 붙인 것이다.
  140 투구는 투구푸스 문서 안에서 머리 없이 첫 블록으로 들어 있어 오귀속을 피하려고 버렸다.
- `note`가 붙은 행은 폼 한정 설명이다(메가·거다이맥스·지역폼·크기폼 등).
  같은 (종, 판본)에 주석 없는 행이 이미 있으면 그쪽이 기본형이다.
- 텍스트는 공식 전사와 팬 번역이 섞여 있다. 나무위키 원문 그대로이고 검수하지 않았다.

## 재현

```sh
uv run --with huggingface_hub python -c "from huggingface_hub import hf_hub_download as d; print(d('heegyu/namuwiki','namuwiki_20210301.parquet',repo_type='dataset'))"
uv run namu_filter.py <parquet> namu_poke.jsonl   # 제목 필터
uv run namu_emit.py namu_poke.jsonl namudex.jsonl namudex-report.md
```

스크립트 사본: `mod/z/translate/reference/tools/`
