# Z-65 배틀 20건 — 이벤트별 격 판정과 문안 제안

정본은 한 글자도 고치지 않았다. 아래는 제안이고 적용은 유지자 승인 뒤에 한다.

재현 경로 한 줄(각 이벤트의 전 행):
`python3 <스크래치패드>/evlines.py <맵> <이벤트>` — 귀속표(`translate/data/speaker-attr.jsonl.gz`)를
읽어 (맵, 원문)으로 `translate/ko/00-maps.jsonl` 줄번호와 현행 번역을 붙인다.
배틀 패배 대사(cmd 900)는 귀속표에 없어 `battle_mixed.md`의 정본 줄번호를 그대로 썼고,
값은 00-maps.jsonl에서 직접 읽어 대조했다.

---

## A. 고칠 것 없음 — 6이벤트

| # | 맵·이벤트 | 왜 안 고치나 |
|---|---|---|
| 5 | 맵359 Ruta 22 ev14 (payaso) | 줄11537은 **이야기 속 의사의 인용문**(「의사가 말하길 "…보러 가십시오"」). 화자의 격이 아니다. payaso 35행 전량이 하대이고 그 예외가 이 인용 두 줄뿐이다(줄11536·11538도 「말이야」·「말했지」로 하대 유지). persona-table의 payaso 비고가 같은 지적을 이미 적어 두었다. |
| 8 | 맵226 Prisión del Olvido ev41 (carabinerow) | **이미 처리됐다.** 배틀후 줄7416의 현행은 「…이 지경이 됐군. 나중에 다 정리되면 가르쳐 주겠나?」로 하대다 — `battle_mixed.md`의 「됐네요/주실래요」는 낡은 값이다. 커밋 7c03b68 `fix(z): prison guards stop speaking up to the prisoner`. 배틀중 줄7415는 격 표지가 없다. |
| 12 | 맵263 Torre Oscura P0 ev22 (lunatica) | 도발 줄8551의 존대는 **청자가 플레이어가 아니라 코스모그**다(기도문). 유지자가 fixlog에서 이 줄을 두 번 손봤고 두 번 다 「들리십니까」 존대를 유지했다. 배틀중·배틀후는 반말이고 그 청자는 플레이어다 — 청자가 갈린 자리이지 널뛰기가 아니다. |
| 13 | 맵264 Torre Oscura P1 ev22 (lunatico) | 존대·반말이 **한 줄 안에서 섞이는 것이 이 스프라이트의 연출**이고(persona-table lunatico 비고: 「어투 통일 게이트에서 걸리더라도 살려 둘 것」), 도발(줄8576 「도와줘요…배틀하지 마!」)과 배틀후(줄8578 「죄송해요…싶지 않았어」)가 **같은 방식으로 섞여 있다.** 배틀 전후가 달라지는 제보 증상이 아니다. |
| 17 | 맵292 Ruta 20 ev26 (eliteFractal) | 배틀중 줄9733의 합쇼체는 **청자가 센데라 대장**이다(「대장님, 기대에 부응하지 못했습니다!」). 도발·배틀후는 플레이어 상대 하대. 상관 보고의 격식이라 정상이다. eliteFractal 21행은 그 한 줄 빼고 전량 하대. |
| 19 | 맵298 Antigua Forja Inundada ev22 (druidaow) | 배틀중 줄9905·배틀후 줄9906이 둘 다 **전설 포켓몬에게 올리는 기도문**(「제르네아스, 이벨타르, 지가르데여! …주소서」). 청자가 신격이고 두 국면이 같은 격이다. 지침이 적은 오판 네 꼴 중 「명사 나열」에도 걸린다. |

---

## B. 고칠 것 있음 — 14이벤트 · 정본 17줄

정본 줄 기준 중복 제거: 맵25 ev38·ev41이 같은 4줄을 공유하므로 **이벤트 14 → 편집 줄 17**
(그중 1줄은 조건부). 원시 20이벤트 중 6건이 거짓 양성이었다.

### B-1. 맵25 Pueblo Acrílico ev38·ev41 (mariow·luigiow) — **반말로 통일** · 4줄

두 이벤트가 정본 줄을 통째로 공유한다(ev38 = mariow, ev41 = luigiow). 한 값밖에 못 준다.

격을 반말로 정한 근거 셋:
1. **같은 두 인물의 맵282 대사 9줄이 전량 반말이다**(줄9119~9128, 「마리아노와 루시아노
   형제다」·「보여주마」·「살아가겠어」). 몬스터볼 공장에서 만나 슈퍼 트레이너로 전업한
   뒤 맵25에 다시 서는 같은 인물이다.
2. **같은 원문의 다른 맵 번역이 이미 반말이다** — 맵155 ev4의 슈퍼 트레이닝 안내
   줄5413~5418(「시작하겠어?」·「내 포켓몬 팀을 연달아 쓰러뜨리면, 네 포켓몬은 특정
   능력치의 포인트를 빠르고 효율적으로 얻는다」).
3. 원문은 전량 `tú`이고 `usted` 표지(`le`·`su`·3인칭 활용)가 없다 — 격을 올릴 근거가 없다.

⚠ 여기만 갈림이 있다: persona-table이 mariow는 B2+B3(손님엔 해요체), luigiow는
B1(반말)로 서로 다르게 적어 두었다. 두 이벤트가 정본을 공유하므로 둘 중 하나만 산다.
해요체로 가는 선택도 가능하니 **이 한 건은 유지자가 뒤집을 수 있다.**

| 정본줄 | 원문 | 현행 | 제안 |
|--:|---|---|---|
| 1108 | ¿Qué entrenamiento te gustaría hacer? | 어떤 훈련을 하고 싶으신가요? | 어떤 훈련을 하고 싶어? |
| 1110 | ¿No? Pues tus Pokémon serán unos debiluchos. | 아니라고요? 그럼 당신 포켓몬들은 약골이 되고 말 텐데요. | 아니라고? 그럼 네 포켓몬들은 약골이 되고 말 텐데. |
| 1111 | Si derrotas de forma sucesiva a mis equipos Pokémon, tus Pokémon ganarán puntos extra en una característica determinada de forma rápida y eficiente. | 제 포켓몬 팀을 연달아 물리치시면, 당신의 포켓몬은 특정 능력치 포인트를 빠르고 효율적으로 추가 획득합니다. | 내 포켓몬 팀을 연달아 물리치면, 네 포켓몬은 특정 능력치 포인트를 빠르고 효율적으로 추가 획득해. |
| 1109 | ¡Mamma mia! ¡Buen entrenamiento! | 맘마미아! 정말 좋은 훈련이었네요! | 맘마미아! 정말 좋은 훈련이었어! |

손대지 않는 줄: 1107·1112·1113(이미 반말), 1183~1197(선택지).

### B-2. 맵140 Viejo Vánitas ev28·ev27 (sanadoraow) — **존대(해요체)로 통일** · 3줄

두 이벤트가 배틀후 줄4913·4914·4915를 공유한다(둘 다 존대라 손댈 것 없음).

근거: sanadoraow 73행 중 존대가 압도적이고(맵147·148·166·197·243·255·381·410 전량 해요체),
바니타스 치유사는 플레이어에게 치료를 파는 접객 역이다. 하대로 떨어진 자리는 배틀
국면 세 줄뿐이다. persona-table이 「배틀에 들어가면 반말로 짧게 끊는다」고 적었지만
그것이 바로 제보가 가리키는 증상이다.

| 정본줄 | 역할 | 원문 | 현행 | 제안 |
|--:|---|---|---|---|
| 4931 | ev28 도발 | Tengo que sanar a los Pokémon... aunque tenga que emplear mi sangre y dar mi vida en ello. | 내 피와 목숨을 바쳐야 한다 해도... 포켓몬들을 치료하겠어. | 제 피와 목숨을 바쳐야 한다 해도... 포켓몬들을 치료하겠어요. |
| 4932 | ev28 배틀중 | Esto me sobrepasa, ¡voy a llorar! | 더는 감당할 수 없어, 눈물이 나올 것 같아! | 더는 감당할 수 없어요, 눈물이 나올 것 같아요! |
| 4911 | ev27 배틀중 | ¡No! ¡Mi pobre Hypno! | 안 돼! 불쌍한 내 슬리퍼! | 안 돼요! 불쌍한 제 슬리퍼! |

### B-3. 낱줄 교정 11건

| # | 맵·이벤트 | 스프라이트 | 정한 격 | 근거 |
|---|---|---|---|---|
| 6 | 맵16 Cueva Grisalla ev9 | ladrona | 하대 | ladrona 37행 전량 하대(맵28·53·62·78·81·96·245·255·297). 배틀중만 존대로 튄다 |
| 7 | 맵46 Bosque Ladera ev10 | azothaow | 하대 | azothaow 37행이 협박 단정 하대로 고르다(맵88·147·148·166·466). 존대는 이 줄과 이름표 상속 오탐뿐 |
| 9 | 맵236 Fábrica de Pokéball ev4 | obrerow | 하대 | obrerow 65행 전량 하대(맵232·235·236·299·361·422·487) |
| 10 | 맵255 Pirineos de Kalos ev25 | ladrona | 하대 | 위 6번과 같다. 같은 맵 ev31도 하대 |
| 14 | 맵269 Ruta 14 ev19 | cocineroOW | 하대 | cocineroOW 58행 전량 하대. voices.md 집단 화자 「요리사 = 친근한 반말」(유지자 판정) |
| 15 | 맵270 Ruta 15 ev17 | ninaSonadoraOW | 하대 | voices.md Z-27 판정 「아이 스프라이트(nina·nino·ninaSonadora)는 플레이어를 또래로 본다 — 반말」 |
| 16 | 맵276 Bastión Pokémon ev24 | brujita | 하대(노파투) | voices.md 꼬마마녀 「존대 금지, 안투리아는 주어 존대로만」(2026-08-11 유지자 재판정). brujita 108행 전량 노파투 하대 |
| 18 | 맵298 Antigua Forja Inundada ev20 | druidaow | 하대 | druidaow 16행 전량 하대(맵298 ev21·22, 맵318, 맵319) |
| 20 | 맵318 Antigua Forja Inundada ev65 | druidaow | 하대 | 위와 같다 |
| 11 | 맵262 Torre Oscura P2 ev10 | lunatico | 하대 (**조건부**) | 아래 단서 참조 |

| # | 정본줄 | 역할 | 원문 | 현행 | 제안 |
|---|--:|---|---|---|---|
| 6 | 699 | 배틀중 | ¡Perdón! ¡Perdón! ¡Ya te dejo pasar! | 죄송해요! 죄송해요! 그냥 지나가게 해 드릴게요! | 미안해! 미안해! 그냥 지나가게 해 줄게! |
| 7 | 1946 | 배틀후 | Conforme pase el tiempo, más y más gente se irá uniendo al Team Azoth. ¡La historia está de nuestra parte! | 시간이 지날수록 점점 더 많은 사람이 아조스단에 합류할 거예요. 역사는 우리 편입니다! | 시간이 지날수록 점점 더 많은 사람이 아조스단에 합류할 거다. 역사는 우리 편이다! |
| 9 | 7900 | 배틀중 | ¡Se me ha aflojado una pieza! Pero no te preocupes, la próxima vez, todo estará bien ajustado. | 나사가 하나 풀려버렸네요! 하지만 걱정 마세요. 다음번엔 확실하게 조여둘 테니까요. | 나사가 하나 풀려버렸네! 하지만 걱정 마. 다음번엔 확실하게 조여둘 테니까. |
| 10 | 8307 | 배틀중 | ¡Me conformo con que me entregues a tus Pokémon más débiles! | 가장 약한 포켓몬이라도 내놓으신다면 만족하겠습니다! | 가장 약한 포켓몬이라도 내놓는다면 만족하겠어! |
| 11 | 8542 | 도발 | ¡Te doy la bienvenida a tu fiesta de no-cumpleaños? ¡Vienes a tomar el té! | 안-생일 파티에 오신 걸 환영해요! 차 마시러 왔구나! | 안-생일 파티에 온 걸 환영해! 차 마시러 왔구나! |
| 14 | 8791 | 배틀중 | Lo mío es el estudio de las setas, no el estudio de los combates Pokémon. | 제 전문은 버섯 연구지, 포켓몬 배틀 연구가 아니에요. | 내 전문은 버섯 연구지, 포켓몬 배틀 연구가 아니야. |
| 15 | 8805 | 도발 | Me encanta coleccionar peluches y figuras de mis Pokémon favoritos para poder hacer con ellos lo que quiera, ¿y a ti? | 저는 좋아하는 포켓몬 인형이나 피규어를 모아서 마음대로 가지고 노는 걸 정말 좋아해요. 당신은 어떠세요? | 나는 좋아하는 포켓몬 인형이나 피규어를 모아서 마음대로 가지고 노는 걸 정말 좋아해. 너는 어때? |
| 16 | 9000 | 배틀중 | Anturia... ¡he hecho todo lo que he podido! ¡Lo siento! | 안투리아님... 제가 할 수 있는 건 다 해봤어요! 죄송해요! | 안투리아님... 제가 할 수 있는 건 다 해봤느니라! 죄송하구나! |
| 18 | 9910 | 배틀중 | Con tu permiso... volveré a intentar dormir. | 실례가 안 된다면... 다시 잠을 청해보겠습니다. | 실례가 안 된다면... 다시 잠을 청해보겠다. |
| 20 | 10495 | 배틀중 | Tienes un espíritu de lucha feral, un equipo equilibrado y un Restaurar Todo en la mochila, por lo que veo. | 보아하니 야성적인 투지에, 균형 잡힌 팀, 가방엔 풀회복약까지 갖추고 있군요. | 보아하니 야성적인 투지에, 균형 잡힌 팀, 가방엔 풀회복약까지 갖추고 있구나. |

**11번(맵262 ev10)이 조건부인 까닭** — persona-table의 lunatico 비고가 「어투가 한 화자
안에서 흔들리는 것이 이 스프라이트의 연출이다. 어투 통일 게이트에서 걸리더라도 살려
둘 것」이라고 못 박는다. 다만 이 줄은 한 문장 안에서 「오신 걸 환영해요」와 「왔구나」가
부딪히고, 같은 이벤트의 배틀중·배틀후는 이미 반말이다. 또 유지자가 fixlog에서 lunatico
두 줄을 반말로 손본 이력이 있다(줄8524 「보세요→보라고」, 줄8579 「당신에게 말해주지
…태운다고요→나는…보았다」). 등재를 뒤집을지 유지자가 정할 자리라 제안만 올린다.

**16번 문안의 껄끄러운 데** — 「제가 …느니라」가 겹친다. 「제가」는 겸양 대명사라
존대 어미가 아니고 voices.md가 금한 것은 존대 어미이므로 그대로 두었지만,
「이 몸이 할 수 있는 건 다 해봤느니라」로 가는 쪽도 된다. 유지자 선택.
