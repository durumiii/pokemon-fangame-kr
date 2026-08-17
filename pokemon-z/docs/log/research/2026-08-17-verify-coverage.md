# verify.py 커버리지 실측 (2026-08-17)

## 절별 표

| 절 | 파일 | dat 꼴 | verify 검사(절 지정) | build.py assert | 오라클 | 오늘 실측 |
|---|---|---|---|---|---|---|
| 00 | maps | 맵별 해시 508 | check_unified(통일/갈림) | 맵 헤더·줄 수·자리별 키 문자열 | messages.dat 키 집합 | dat에만 0 · 정본에만 37 |
| 01 | species | 리스트 | check_canon(species) | 길이만 | canon.jsonl + messages.dat es | es 어긋남 0 |
| 02 | kinds | 리스트 | check_kinds(genera.jsonl) | 길이만 | genera.jsonl(번호) | 불일치 0 |
| 03 | entries | 리스트 | **없음** | 길이만 | 코퍼스 en 열 | 적중 207 · 불일치 9 |
| 04 | forms | 리스트 | **없음** | 길이만 | 없음(코퍼스 적중 0/46) | — |
| 05 | moves | 리스트 | check_canon(moves) | 길이만 | canon.jsonl | 불일치 0 |
| 06 | move-descs | 리스트 | **없음** | 길이만 | 코퍼스 es 열 | 적중 416 · 불일치 40 |
| 07 | items | 리스트 | check_canon(items) | 길이만 | canon.jsonl | 불일치 0 |
| 08 | item-plurals | 리스트 | **없음** | 길이만 | 없음(짧은 낱말, 코퍼스 오탐) | 적중 455 · 「불일치」6은 전부 오탐 |
| 09 | item-descs | 리스트 | **없음** | 길이만 | 코퍼스 es 열 | 적중 168 · 불일치 26 |
| 10 | abilities | 리스트 | check_canon(abilities) | 길이만 | canon.jsonl | 불일치 0 |
| 11 | ability-descs | 리스트 | **없음** | 길이만 | 코퍼스 es 열 | 적중 7 · 불일치 1 |
| 12 | types | 리스트 | check_canon(types) | 길이만 | canon.jsonl + PBS/types.txt | 불일치 0 |
| 13 | trainer-classes | 리스트 | **없음** | 길이만 | PBS/trainertypes.txt(3번째 필드) · 코퍼스 trtype | **미번역 1건(i=121 'Papa')** · trtype 불일치 2 |
| 14 | trainer-names | 해시 | **없음** | 줄 수·키 문자열 | PBS/trainers.txt(이름 집합) | PBS에만 0 · 원문 그대로 8건 |
| 15~17 | speech 3절 | 해시 | — | — | — | 정본·dat 모두 0줄 |
| 18 | regions | 리스트 | **없음** | 길이만 | messages.dat | 1줄, 일치 |
| 19 | place-names | 해시 | **없음** | 줄 수·키 문자열 | PBS/townmap.txt(키 집합만) | townmap 20개 전부 정본에 있음 |
| 20 | place-descs | 해시 | **없음** | 줄 수·키 문자열 | PBS/townmap.txt(키 집합만) | 같음 |
| 21 | map-names | 리스트 | **없음** | 길이만 | Data/MapInfos.rxdata | es 어긋남 0(2건은 dat 공백) |
| 22 | phone | 해시 | **없음** | 줄 수·키 문자열 | PBS/phone.txt | 19/19 일치 |
| 23 | script-texts | 해시 | check_ribbons(리본 키) · check_dat_and_sentinels(개수+파수3) | 줄 수·키 문자열 | 코퍼스(리본 밖은 미개척) | messages.dat에만 2키 |

전 절을 훑는 검사 둘 — check_names(고유명 변이 147개, ko/*.jsonl glob)와
check_ui_gsub(UI 치환표 53쌍 오폭)는 절을 안 가리지만 **값 쪽 검사**라 절별 오라클 대조가 아니다.

## 재현

- 절별 es/키 대조: `uv run /tmp/.../scratchpad/oracle_check.py`
- PBS 대조: `uv run /tmp/.../scratchpad/pbs_check.py`
- 미번역 스캔: `uv run /tmp/.../scratchpad/untr.py`
- 키 구멍: `uv run /tmp/.../scratchpad/gaps.py`
