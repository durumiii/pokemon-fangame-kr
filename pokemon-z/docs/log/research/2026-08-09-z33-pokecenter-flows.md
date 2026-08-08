# 2026-08-09 — Z-33 포켓몬센터 회복 대사 전문 표

Z-33 「회복 대사 묶음 처리」의 판정 재료. 제보 `3:61`이 요구한 것이 낱건 수정이 아니라
「이런 걸 묶어서 처리할 방법」이라, 흩어진 자리를 전수로 뜨고 슬롯별 빈도를 세었다.

⚠ **이 표는 통일 전 상태다.** 같은 날 네 슬롯을 각각 한 문장으로 모았으므로(113행)
지금 정본의 값과 다르다 — 무엇을 왜 그렇게 정했는지는
[quality 원장](../../ledger/quality.md)의 「포켓몬센터 회복 대사」 절.

**본가 대조 결과는 이 흐름이 이식 대상이 아님을 말한다.** 본가 포켓몬센터는 접수와
완료 두 마디로 끝나고 「기다려 주세요」 단계 자체가 없다(오메가루비·스칼렛 계열
코퍼스 실측, `잠시만 기다` 검색 0건). 이 게임의 네 마디는 스페인어 원문부터 창작이라
공식 자구를 그대로 옮길 대상이 없다 — 정할 것은 우리 표준이다.

실측: `translate/ko/00-maps.jsonl` 전수 스캔(부분/완전 일치, 공백 정규화 `re.sub(r'\s+',' ',s).strip()` 적용). 화자는 귀속표 `translate/data/speaker-attr.jsonl.gz`를 같은 정규화로 조인. 슬롯을 가진 맵 36개.

## 요약

### 슬롯별 자리 수 · 서로 다른 번역 가짓수

(자리 수 = 정본에 등장한 (map,k,v) 줄 개수. 가짓수 = norm(v) 기준 서로 다른 문자열 수)

| 슬롯 | 자리 수 | 다른 번역 가짓수 |
|---|---|---|
| 인사 | 36 | 32 |
| 대기 | 35 | 2 |
| 완료 | 36 | 21 |
| 응대 | 34 | 7 |

### 인사 슬롯 번역 빈도표 (내림차순)

| 번역 | 맵(자리) 수 |
|---|---|
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? | 3 |
| ... 어머나! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? | 3 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 치료의 기적을 일으키죠. 지닌 포켓몬을 회복시키시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 치료의 기적을 보여드릴게요. 지닌 포켓몬을 치료하시겠어요? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 완벽한 회복을 보장해 드린답니다. 지닌 포켓몬을 치료하시겠어요? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 건강의 기적을 만드는 곳이죠. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| ... 어머! <i>Bonsoir</i>! 포켓몬센터에 오신 걸 환영해요. 건강의 기적을 만드는 곳이죠. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 만들어 낸답니다. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| ... 어머나! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 만들어 낸답니다. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 의술의 기적을 선보이죠. 지니신 포켓몬을 치료하시겠습니까? | 1 |
| ...어머나! 포켓몬센터에 오신 걸 환영해요. 저희는 의술의 기적을 선보이죠. 지니신 포켓몬을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 선보이죠. 포켓몬들을 치료하시겠습니까? | 1 |
| ... 어머! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 선보이죠. 포켓몬들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요, 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 회복시키시겠습니까? | 1 |
| ... 어머나! 포켓몬센터에 오신 것을 환영해요, 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 회복시키시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요! 완벽한 치료를 약속해 드리죠. 포켓몬들을 치료하시겠습니까? | 1 |
| ... 어머나! 포켓몬센터에 오신 것을 환영해요! 완벽한 치료를 약속해 드리죠. 포켓몬들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 의료 기적을 만들어내죠. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| ... 어머! 포켓몬센터에 오신 것을 환영해요. 저희는 의료 기적을 만들어내죠. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 치료의 기적을 선보이는 곳이죠. 포켓몬들을 치료하시겠습니까? | 1 |
| 포켓몬센터에 오신 것을 환영해요! 저희는 의료의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 의료의 기적을 보여드리죠. 포켓몬들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 우리는 의료의 기적을 만들어 내죠. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요, 치료의 기적을 일으키는 곳이죠. 동행 포켓몬을 치료하시겠어요? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 치료의 기적을 보여드리는 곳이죠. 포켓몬들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영합니다. 저희는 건강의 기적을 만듭니다. 포켓몬들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어 내죠. 지닌 포켓몬을 치료하시겠습니까? | 1 |
| 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 행하죠. 포켓몬들을 치료하시겠습니까? | 1 |
| 포켓몬센터에 오신 것을 환영해요. 치료의 기적을 선보여 드리지요. 팀을 치료하시겠습니까? | 1 |
| 포켓몬센터에 오신 것을 환영해요! 저희는 건강의 기적을 만들어내죠. 팀을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 훌륭한 치료를 제공해 드린답니다. 동료들을 치료하시겠습니까? | 1 |
| <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요! 저희는 기적을 일으키듯 건강하게 치료해 드린답니다. 포켓몬들을 치료하시겠어요? | 1 |

### 대기 슬롯 번역 빈도표 (내림차순)

| 번역 | 맵(자리) 수 |
|---|---|
| 잠시 시간이 걸릴 거예요. | 34 |
| 잠시만 기다려 주세요. | 1 |

### 완료 슬롯 번역 빈도표 (내림차순)

| 번역 | 맵(자리) 수 |
|---|---|
| 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! | 8 |
| 치료 완료! 필요할 때 언제든 또 들러 주세요! | 4 |
| 치료를 마쳤어요! 도움이 필요할 때 언제든 다시 찾아주세요! | 3 |
| 치료를 마쳤습니다. 필요할 때 언제든 또 들러 주세요! | 2 |
| 치료 완료예요! 필요할 때 언제든 다시 오세요. | 2 |
| 치료가 끝났습니다! 필요하실 때 언제든 또 찾아주세요! | 2 |
| 치료를 마쳤습니다. 필요할 때 언제든 다시 찾아주세요! | 1 |
| 치료가 끝났어요. 필요하실 때 언제든 다시 찾아주세요! | 1 |
| 치료가 끝났어요! 도움이 필요하면 언제든 다시 오세요! | 1 |
| 치료 완료예요! 필요할 때 또 와주세요! | 1 |
| 치료 완료! 필요할 때 언제든 또 오세요! | 1 |
| 치료가 끝났습니다. 필요하실 때 언제든 또 들러 주세요! | 1 |
| 치료가 끝났어요! 도움이 필요하시면 언제든 또 찾아주세요! | 1 |
| 치료를 마쳤어요. 필요할 때 언제든 다시 오세요! | 1 |
| 치료가 끝났습니다, 필요할 때 언제든 다시 찾아주세요! | 1 |
| 치료 완료했습니다. 필요하실 때 언제든 또 이용해 주세요! | 1 |
| 치료가 끝났어요! 필요할 때 언제든 다시 오세요! | 1 |
| 임무 완료! 필요할 때 언제든 다시 들러 주세요! | 1 |
| 치료를 마쳤습니다. 필요할 때 언제든 다시 오세요! | 1 |
| 치료가 끝났습니다. 필요할 때 언제든 다시 찾아주세요! | 1 |
| 치료가 끝났어요. 도움이 필요할 때 언제든 다시 들러 주세요! | 1 |

### 응대 슬롯 번역 빈도표 (내림차순)

| 번역 | 맵(자리) 수 |
|---|---|
| 언제든 정성껏 모시겠습니다. | 21 |
| 정성을 다해 모시겠습니다. | 6 |
| 언제든 이용해 주십시오. | 3 |
| 언제든 말씀만 하십시오. | 1 |
| 항상 정성을 다하겠습니다. | 1 |
| 언제든 말씀해 주십시오. | 1 |
| 늘 곁에 있겠습니다. | 1 |

### 스프라이트가 nurse가 아닌 맵

| 맵 | 이름 | 스프라이트 |
|---|---|---|
| 68 | 큰 집 (Casa Grande) | enfermera2G |
| 193 | 미르 궁전 (Palacio Luminalia) | enfermera |
| 197 | 카두코 구호소 (Hospicio Caduco) | enfermera2G |
| 345 | 비밀 온천 (Balneario Oculto) | kimono |
| 356 | 포켓몬마을 (Villa Pokemon) | 242 |
| 463 | 포켓몬센터 (Centro Pokémon) | burguesaow2 |

## 맵별 전문

### 맵 3 — 리엔소마을 (Pueblo Lienzo)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료! 필요할 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 정성을 다해 모시겠습니다. |

### 맵 10 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 치료의 기적을 일으키죠. 지닌 포켓몬을 회복시키시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤어요! 도움이 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 18 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 치료의 기적을 보여드릴게요. 지닌 포켓몬을 치료하시겠어요? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤습니다. 필요할 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 25 — 아크릴리코마을 (Pueblo Acrílico)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤습니다. 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 정성을 다해 모시겠습니다. |

(정본 인덱스 간격: [49, 50, 52] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 30 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 완벽한 회복을 보장해 드린답니다. 지닌 포켓몬을 치료하시겠어요? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요. 필요하실 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 35 — 로시욘 저택 (Chateau Rosillon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 도움이 필요하면 언제든 다시 오세요! |
| 응대 | Estamos a tu servicio. | 언제든 말씀만 하십시오. |

### 맵 60 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 건강의 기적을 만드는 곳이죠. 지닌 포켓몬을 치료하시겠습니까? |
| 인사 | ... ¡Uy! ¡<i>Bonsoir</i>!Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머! <i>Bonsoir</i>! 포켓몬센터에 오신 걸 환영해요. 건강의 기적을 만드는 곳이죠. 지닌 포켓몬을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [19, 20, 21, 22, 24] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 68 — 큰 집 (Casa Grande)   · 스프라이트: enfermera2G · who: enfermera2G
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료예요! 필요할 때 또 와주세요! |
| 응대 | Estamos a tu servicio. | 정성을 다해 모시겠습니다. |

### 맵 82 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 만들어 낸답니다. 지닌 포켓몬을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머나! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 만들어 낸답니다. 지닌 포켓몬을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료예요! 필요할 때 언제든 다시 오세요. |
| 응대 | Estamos a tu servicio. | 언제든 이용해 주십시오. |

(정본 인덱스 간격: [15, 16, 17, 18, 20] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 104 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머나! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료! 필요할 때 언제든 또 오세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [7, 8, 9, 10, 12] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 114 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 의술의 기적을 선보이죠. 지니신 포켓몬을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ...어머나! 포켓몬센터에 오신 걸 환영해요. 저희는 의술의 기적을 선보이죠. 지니신 포켓몬을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났습니다. 필요하실 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [16, 17, 18, 19, 21] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 134 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 선보이죠. 포켓몬들을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머! 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 선보이죠. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료예요! 필요할 때 언제든 다시 오세요. |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [16, 17, 18, 19, 21] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 142 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머나! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤습니다. 필요할 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [8, 9, 10, 11, 13] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 164 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요, 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 회복시키시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머나! 포켓몬센터에 오신 것을 환영해요, 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 회복시키시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 항상 정성을 다하겠습니다. |

(정본 인덱스 간격: [8, 9, 10, 11, 13] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 174 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요! 완벽한 치료를 약속해 드리죠. 포켓몬들을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머나! 포켓몬센터에 오신 것을 환영해요! 완벽한 치료를 약속해 드리죠. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 도움이 필요하시면 언제든 또 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [17, 18, 19, 20, 22] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 175 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 의료 기적을 만들어내죠. 지닌 포켓몬을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머! 포켓몬센터에 오신 것을 환영해요. 저희는 의료 기적을 만들어내죠. 지닌 포켓몬을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시만 기다려 주세요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났습니다! 필요하실 때 언제든 또 찾아주세요! |
| 응대 | Estamos a tu servicio. | 정성을 다해 모시겠습니다. |

(정본 인덱스 간격: [16, 17, 18, 19, 21] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 193 — 미르 궁전 (Palacio Luminalia)   · 스프라이트: enfermera · who: enfermera
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤어요. 필요할 때 언제든 다시 오세요! |
| 응대 | Estamos a tu servicio. | 언제든 말씀해 주십시오. |

### 맵 197 — 카두코 구호소 (Hospicio Caduco)   · 스프라이트: enfermera2G · who: enfermera2G
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났습니다, 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 정성을 다해 모시겠습니다. |

### 맵 239 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 치료의 기적을 선보이는 곳이죠. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료했습니다. 필요하실 때 언제든 또 이용해 주세요! |
| 응대 | Estamos a tu servicio. | 늘 곁에 있겠습니다. |

### 맵 259 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | 포켓몬센터에 오신 것을 환영해요! 저희는 의료의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 오세요! |
| 응대 | Estamos a tu servicio. | 정성을 다해 모시겠습니다. |

### 맵 273 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 의료의 기적을 보여드리죠. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료! 필요할 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 295 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 우리는 의료의 기적을 만들어 내죠. 지닌 포켓몬을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 임무 완료! 필요할 때 언제든 다시 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 307 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요, 치료의 기적을 일으키는 곳이죠. 동행 포켓몬을 치료하시겠어요? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 311 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 치료의 기적을 보여드리는 곳이죠. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료! 필요할 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 338 — 크리산토의 캠프 (Campamento de Crisanto)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤습니다. 필요할 때 언제든 다시 오세요! |
| 응대 | (없음) | (없음) |

### 맵 345 — 비밀 온천 (Balneario Oculto)   · 스프라이트: kimono · who: kimono
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 356 — 포켓몬마을 (Villa Pokemon)   · 스프라이트: 242 · who: 242
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | (없음) | (없음) |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났습니다! 필요하실 때 언제든 또 찾아주세요! |
| 응대 | (없음) | (없음) |

### 맵 357 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 인사 | ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | ... 어머나! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

(정본 인덱스 간격: [12, 13, 14, 15, 17] — 슬롯 사이에 다른 대사가 끼어 있을 수 있음)

### 맵 360 — 상기노마을 (Pueblo Sanguino)   · 스프라이트:  · who: 
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영합니다. 저희는 건강의 기적을 만듭니다. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났습니다. 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 394 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어 내죠. 지닌 포켓몬을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요. 도움이 필요할 때 언제든 다시 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 399 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | 포켓몬센터에 오신 걸 환영해요. 저희는 의료의 기적을 행하죠. 포켓몬들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 405 — 미르 그랜드 호텔 (Gran Hotel Luminalia)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | 포켓몬센터에 오신 것을 환영해요. 치료의 기적을 선보여 드리지요. 팀을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 429 — 미르 그랜드 호텔 (Gran Hotel Luminalia)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | 포켓몬센터에 오신 것을 환영해요! 저희는 건강의 기적을 만들어내죠. 팀을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료가 끝났어요! 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 452 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요. 저희는 훌륭한 치료를 제공해 드린답니다. 동료들을 치료하시겠습니까? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료 완료! 필요할 때 언제든 또 들러 주세요! |
| 응대 | Estamos a tu servicio. | 언제든 이용해 주십시오. |

### 맵 463 — 포켓몬센터 (Centro Pokémon)   · 스프라이트: burguesaow2 · who: burguesaow2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres curar a tu equipo? | <i>Bonjour</i>! 포켓몬센터에 오신 걸 환영해요! 저희는 기적을 일으키듯 건강하게 치료해 드린답니다. 포켓몬들을 치료하시겠어요? |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤어요! 도움이 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 정성껏 모시겠습니다. |

### 맵 504 — 리엔소마을 (Pueblo Lienzo)   · 스프라이트: enfermera2 · who: enfermera2
| 슬롯 | 원문 | 현행 번역 |
|---|---|---|
| 인사 | (없음) | (없음) |
| 대기 | Esto llevará un rato. | 잠시 시간이 걸릴 거예요. |
| 완료 | Misión cumplida, ¡vuelve cuando lo necesites! | 치료를 마쳤어요! 도움이 필요할 때 언제든 다시 찾아주세요! |
| 응대 | Estamos a tu servicio. | 언제든 이용해 주십시오. |
