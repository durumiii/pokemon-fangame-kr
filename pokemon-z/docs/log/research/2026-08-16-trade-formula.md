# 교환 정형구 격 통일 — 조사·문안 제안 (2026-08-16, 정본 미수정)

정본 파일은 전부 `translate/ko/00-maps.jsonl`. 줄 번호는 2026-08-16 현재 실측.

## 1. 정형구가 걸린 맵 전수

교환 이벤트가 있는 맵은 32개(귀속표 실측). 그중 **한 맵에 교환 이벤트가 둘 이상이라
정형구를 나눠 쓰는 맵은 11개**다. 나머지 21맵은 이벤트 하나뿐이라 공유 충돌이 없다.

| 맵 | 이름 | 이벤트 | 스프라이트(원시명) | NPC 제 대사의 결 | 현행 정형구 격 | 다수결 | 판정 |
|---|---|---|---|---|---|---|---|
| 63 | Café Bohemien | 4,5,6 | cantanteow · mosqueterow · burguesaow | 해요 · 하게+반말 · 해요 | 존대 | 존2:하1 존대 | 일치 — 손대지 않음 |
| 116 | Restaurante Le Chonk | 13~18 | burguesaow · burguesow · cantanteow · mosqueteraw · cazadorow · ninaSonadoraOW | 해요 ×4 · 대화단정 ×2 | 존대 | 존4:하2 존대 | 일치 |
| 177 | Café Soleil | 4,5,12 | burguesaow · lenador · mosqueterow | 해요 · 반말 · 하게+단정 | **존대** | 존1:하2 **하대** | **어긋남 — 하대로** |
| 178 | Café Concordia | 4,5,6 | cantanteow · mosqueterow · burguesaow | 해요 · 하게+반말 · 해요 | 존대 | 존2:하1 존대 | 일치 |
| 179 | Café Can Can | 6,7,8 | burguesaow · hombre1 · anciano | 해요 · 반말 · 하게 | **존대** | 존1:하2 **하대** | **어긋남 — 하대로** |
| 302 | Café Pedrín | 4,5,6 | alquimista2OW · lenador · burguesaow | 해요 · 반말 · 해요 | **반말** | 존2:하1 **존대** | **어긋남 — 반대 방향** |
| 308 | Casa | 3,4,12 | obrerow · mujer2 · ranger | 반말 ×3 | 반말 | 하3 | 일치 |
| 395 | Café Galanes | 4,5,12 | burguesaow2 · curanderaow · mosqueteraw | 반말 · 하게 · 반말 | 반말 | 하3 | 일치 |
| 397 | Torre Maestra | 13,14 | monjaYantraAnciana · monjeYantra | 합쇼 ×2 | 합쇼 | — | 일치 |
| 409 | Casa | 14~17 | monjaYantra · monjeYantra | 합쇼 ×2 | 합쇼 | — | 일치 |
| 478 | Casa | 6,8,9 | mosqueteraw · hombre1 · lenador | 반말 ×3 | 반말 | 하3 | 일치 |

정형구 넉 줄 중 실제로 격이 실린 것은 셋이다. `Bueno, otra vez será.` →
「그렇다면 다음 기회에.」는 격 중립이고 `data/unified-phrases.jsonl`에 12맵 통일로
등재돼 있어 **어느 맵에서도 손대지 않는다.**

## 2. 맵179 Café Can Can — 문안 표본

세 NPC 중 둘이 하대다. 정형구만 해요체라 hombre1·anciano의 페이지에서 격이 튄다.

### (권장) 평대 반말 — 기존 반말 갈래 문안을 그대로 복제

| 줄 | 원문 | 현행 | 제안 |
|---|---|---|---|
| 6125 | `¡Cúidalo muy bien!` | 귀여워해 주세요! | 귀여워해 줘! |
| 6126 | `¡Vaya! Veo que no tienes uno.` | 이런! 갖고 계시지 않네요. | 이런! 갖고 있지 않네. |
| 6127 | `Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo.` | 그 포켓몬을 손에 넣으시면 볼 수 있게 선두에 세워서 보여 주세요. | 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘. |
| 6124 | `Estoy buscando un Rapidash, ¿lo cambiarías por mi Tepig?` (burguesaow, 같은 페이지 앞 대사) | 날쌩마를 찾고 있는데, 제 뚜꾸리와 교환할래요? | 날쌩마를 찾고 있는데, 내 뚜꾸리랑 교환할래? |

셋(6125~6127)은 맵302·313·395·478에 이미 서 있는 문안 그대로다 — 새 문형이 아니다.

### (대안) 하게체

| 줄 | 현행 | 제안 |
|---|---|---|
| 6125 | 귀여워해 주세요! | 귀여워해 주게! |
| 6126 | 이런! 갖고 계시지 않네요. | 이런! 갖고 있지 않구먼. |
| 6127 | 그 포켓몬을…보여 주세요. | 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 주게. |
| 6124 | 날쌩마를 찾고 있는데, 제 뚜꾸리와 교환할래요? | 날쌩마를 찾고 있는데, 내 뚜꾸리랑 바꾸지 않겠나? |

건드리지 않는 줄(참고): 6131·6132·6133(hombre1 반말) · 6134·6135·6136(anciano 하게) ·
6129·6130(burguesaow ev6 페이지1 혼잣말, 해요체) · 6128(다음 기회에, 통일 문구).

## 3. 맵177 Café Soleil — 문안 표본

하대 둘(lenador 반말, mosqueterow 반말+단정)에 하게체 화자가 없다. 평대 반말 하나뿐.

| 줄 | 원문 | 현행 | 제안 |
|---|---|---|---|
| 6080 | `¡Cúidalo muy bien!` | 귀여워해 주세요! | 귀여워해 줘! |
| 6081 | `¡Vaya! Veo que no tienes uno.` | 이런! 갖고 계시지 않네요. | 이런! 갖고 있지 않네. |
| 6082 | `Si te haces con ese Pokémon, …` | 그 포켓몬을 손에 넣으시면 볼 수 있게 선두에 세워서 보여 주세요. | 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘. |
| 6093 | `Estoy buscando un Misdreavus, ¿lo cambiarías por mi Chimchar?` (burguesaow, 같은 페이지 앞 대사) | 무우마를 찾고 있는데, 제 불꽃숭이와 교환하지 않을래요? | 무우마를 찾고 있는데, 내 불꽃숭이와 교환하지 않을래? |

건드리지 않는 줄: 6079(lenador 반말) · 6084·6085(lenador 잡담) · 6086·6087(mosqueterow) ·
6094(burguesaow 페이지1 혼잣말) · 6083(다음 기회에).

## 4. 맵302 Café Pedrín — 반대 방향의 어긋남

정형구가 반말인데 다수는 존대다(alquimista2OW 해요, burguesaow 해요, lenador 반말).
2026-08-12 `divergence-allowed` 등재가 302를 반말 갈래에 넣은 것이 다수결과 어긋난다.

| 줄 | 원문 | 현행 | 존대로 맞출 때 |
|---|---|---|---|
| 9966 | `¡Cúidalo muy bien!` | 귀여워해 줘! | 귀여워해 주세요! |
| 9967 | `¡Vaya! Veo que no tienes uno.` | 이런! 갖고 있지 않네. | 이런! 갖고 계시지 않네요. |
| 9965 | `Estoy buscando un Heatmor, …` (lenador, 같은 페이지 앞 대사) | 앤티골을 하나 찾고 있는데, 내 스코버니랑 안 바꿀래? | 앤티골을 하나 찾고 있는데, 제 스코버니랑 안 바꾸실래요? |
| 9968 | `Si te haces con un Heatmor, …` (lenador 전용, 자유 배정) | 앤티골을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘. | 앤티골을 손에 넣으시면 볼 수 있게 선두에 세워서 보여 주세요. |

## 5. 등재 파일에 따라오는 변경

- `translate/data/divergence-allowed.jsonl`
  - `¡Cúidalo muy bien!` — 존대 갈래 maps에서 177·179를 빼고 반말 갈래로 옮긴다.
  - `¡Vaya! Veo que no tienes uno.` — 같음.
  - `Si te haces con ese Pokémon, …` — 이 원문은 177·179·395·478 **네 맵뿐**이다.
    177·179가 반말로 가면 갈래가 하나로 합쳐지므로 **divergence 등재를 지우고
    `unified-phrases.jsonl`로 옮기는 것이 맞다.**
  - 302를 존대로 되돌리면 위 두 항목의 갈래 maps에서 302를 존대 쪽으로 옮긴다.
- `docs/ledger/voices.md` 「교환 NPC 정형 문구」 절 — 「179 카페 캉캉은 반말」이 이미
  적혀 있으나 정본은 존대다. 이번 반영이 그 판정을 실물에 맞추는 일이다.
