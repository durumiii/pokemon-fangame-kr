# 격 손질 확인 요청 (2026-08-08)

귀족 NPC의 존대·반말이 한 이벤트 안에서 부딪히던 자리를 훑은 결과다. **원문의 격**
(`tú`/`usted`/`vos`)을 근거로 갈랐고, 원문에 격 신호가 없는 자리는 판정을 비워 뒀다.

## 1. 이미 정본에 넣은 것 — 물리려면 말해 주세요

### 1-1. 교환 NPC 정형 문구 (커밋 `63bbd93`)

교환 페이지 57곳의 원문이 **전부 `tú`**였다(`cambiarías`·`tienes`·`te haces`·`tu equipo`,
usted 신호 0). 그래서 격을 나누지 않고 반말로 통일하고, 문구는 본가 자구를 따랐다 —
오메가루비·알파사파이어가 `¡Cuida bien de X!`를 「X을 귀여워해 줘!」로 옮기고 파티
첫 자리를 「선두」라 부른다.

| 원문 | 옛 번역 | 새 번역 |
|---|---|---|
| `¡Cúidalo muy bien!` | 꼭 잘 챙겨 주기를! | 귀여워해 줘! |
| `¡Vaya! Veo que no tienes uno.` | 이런! 아직 없다니... | 이런! 아직 없구나. |
| `¡Vaya! Al final tendré que poner un anuncio en Milintercambios.` | 이런... 결국 교환 게시판에 광고를 올릴 수밖에. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |
| `Si tienes un Pidgeot, ponlo en el primer lugar de tu equipo para que pueda verlo bien.` | 피죤투가 있다면 잘 보이게 지닌 포켓몬 맨 앞에 놓아 주기를. | 피죤투가 있다면 선두에 세워 두고 다시 와 줘. |

### 1-2. 교환 페이지 안에서 존댓말이던 56줄

| 옛 번역 | 새 번역 |
|---|---|
| 판짱을 구하는 중인데, 제 코고미와 교환하지 않으시겠어요? 제법 희귀한 얼음타입 포켓몬이에요. | 판짱을 구하는 중인데, 내 코고미와 교환하지 않을래? 제법 희귀한 얼음타입 포켓몬이야. |
| 어머, 판짱을 갖고 계시네요! 바로 교환하시죠! | 오, 판짱을 갖고 있구나! 바로 교환하자! |
| 어머나, 판짱이 정말 귀엽네요! 아주 마음에 들어요! | 우와, 판짱이 정말 귀엽네! 아주 마음에 들어. |
| 어머, 참 아쉽네요. 어쩔 수 없이 제가 직접 풀숲에 들어가 보는 수밖에요... | 아, 참 아쉽네. 어쩔 수 없이 내가 직접 풀숲에 들어가 보는 수밖에... |
| 꼬렛을 찾고 있는데, 제 영구스와 교환하실래요? | 꼬렛을 찾고 있는데, 내 영구스와 교환할래? |
| 좋아요, 꼬렛을 갖고 계시네요! 교환해요! | 좋아, 꼬렛을 갖고 있구나! 교환하자! |
| 저는 꼬렛이 정말 좋아요! 제 모습을 보는 것 같거든요. | 난 꼬렛이 정말 좋아! 내 모습을 보는 것 같거든. |
| 고고트를 찾고 있어요! 제 이상해씨랑 교환하지 않을래요? | 고고트를 찾고 있어! 내 이상해씨랑 교환하지 않을래? |
| 블로스터를 찾고 있어요. 제 꼬부기와 바꾸시지 않겠어요? | 블로스터를 찾고 있어. 내 꼬부기와 바꾸지 않을래? |
| 플라베베를 하나 구하고 싶군요. 상류층 사이에서 아주 유행하는 포켓몬이거든요. | 플라베베를 하나 구하고 싶군. 상류층 사이에서 아주 유행하는 포켓몬이거든. |
| 혹시 한 마리 찾게 되면 제 에블리랑 교환하시겠어요? | 혹시 한 마리 찾게 되면 내 에블리랑 교환할래? |
| 정말인가요? 이러다 파티에서 웃음거리가 되고 말겠어요. | 정말인가? 이러다 파티에서 웃음거리가 되고 말겠군. |
| 깨비드릴조를 찾고 있는데, 제 파오리와 교환해 주시겠어요? | 깨비드릴조를 찾고 있는데, 내 파오리와 교환해 주겠어? |
| 좋아요, 깨비드릴조를 갖고 계시네요! 교환해요! | 좋아, 깨비드릴조를 갖고 있구나! 교환하자! |
| 고마워요! 파오리를 얕보지 마세요, 대파를 지니게 하면 무시무시한 포켓몬이 될 수 있답니다. | 고마워! 파오리를 얕보지 마, 대파를 지니게 하면 무시무시한 포켓몬이 될 수 있거든. |
| 이런, 아쉽네요! 귀찮게 해드렸다면 죄송해요. | 이런, 아쉽네! 귀찮게 했다면 미안해. |
| 아르코를 구하고 있는데, 제 치코리타와 교환하지 않으실래요? | 아르코를 구하고 있는데, 내 치코리타와 교환하지 않을래? |
| 화염레오를 찾고 있는데, 제 브케인과 교환하시겠어요? | 화염레오를 찾고 있는데, 내 브케인과 교환할래? |
| 지금 로파파를 찾고 있어요! 제 리아코랑 교환하지 않을래요? | 지금 로파파를 찾고 있어! 내 리아코랑 교환하지 않을래? |
| 엘풍을 찾고 있는데, 제 나무지기와 교환해 주시겠어요? | 엘풍을 찾고 있는데, 내 나무지기와 교환해 주겠어? |
| 만타인을 찾고 있어요. 제 덩쿠림보와 교환하시겠어요? | 만타인을 찾고 있어. 내 덩쿠림보와 교환할래? |
| 저기, 혹시 에레키블을 한 마리 가지고 계신가요? | 저기, 혹시 에레키블을 한 마리 가지고 있어? |
| 제 마그마번과 교환해 보지 않으시겠어요? | 내 마그마번과 교환해 보지 않을래? |
| 좋군요, 에레키블을 가지고 계시네요! 교환하도록 해요! | 좋군, 에레키블을 가지고 있구나! 교환하자! |
| 정말 좋네요! 전 항상 불비달마를 정말 좋아했거든요! | 정말 좋아! 난 항상 불비달마를 정말 좋아했거든! |
| 저는 벌레타입 포켓몬이 너무 좋아요! 그래서 전부 모으려고 하거든요. | 난 벌레타입 포켓몬이 너무 좋아! 그래서 전부 모으려고 하거든. |
| 스라크를 헤라크로스랑 교환해 주실 수 있나요? 벌레끼리 바꾸는 거예요. | 스라크를 헤라크로스랑 교환해 줄 수 있어? 벌레끼리 바꾸는 거야. |
| 와, 스라크를 갖고 계시네요! 교환해요! | 와, 스라크를 갖고 있구나! 교환하자! |
| 스라크는 정말 좋아요. 이제 어떤 포켓몬으로 진화시킬지 고민해 봐야겠어요! | 스라크는 정말 좋아. 이제 어떤 포켓몬으로 진화시킬지 고민해 봐야겠어! |
| 이런, 정말 아쉽네요! 벌레타입 포켓몬을 전부 모으기는 쉽지 않겠어요. | 이런, 정말 아쉽네! 벌레타입 포켓몬을 전부 모으기는 쉽지 않겠어. |
| 무우마를 찾고 있답니다. 제 불꽃숭이와 교환하시겠어요? | 무우마를 찾고 있어. 내 불꽃숭이와 교환할래? |
| 트로피우스를 찾고 있어요! 제 나몰빼미와 교환하지 않으실래요? | 트로피우스를 찾고 있어! 내 나몰빼미와 교환하지 않을래? |
| 샤크니아를 찾고 있답니다. 제 누리공과 교환하지 않으시겠어요? | 샤크니아를 찾고 있어. 내 누리공과 교환하지 않을래? |
| 날쌩마를 찾고 있는데, 제 뚜꾸리와 교환하시겠어요? | 날쌩마를 찾고 있는데, 내 뚜꾸리와 교환할래? |
| 저기, 혹시 피죤투를 갖고 계신가요? | 저기, 혹시 피죤투를 갖고 있어? |
| 제 시비꼬랑 교환하지 않으시겠어요? | 내 시비꼬랑 교환하지 않을래? |
| 어머, 피죤투가 있으시네요! 어서 교환해요! | 오, 피죤투가 있구나! 어서 교환하자! |
| 잘됐네요! 그 시비꼬는 제 차분한 삶에 비하면 너무 시끄러웠거든요. | 잘됐어! 그 시비꼬는 내 차분한 삶에 비하면 너무 시끄러웠거든. |
| 우츠보트를 찾고 있어요. 제 흥나숭과 교환해 주시지 않을래요? | 우츠보트를 찾고 있어. 내 흥나숭과 교환해 주지 않을래? |
| 치갈기를 찾고 있는데, 제 울머기랑 교환하지 않으시겠어요? | 치갈기를 찾고 있는데, 내 울머기랑 교환하지 않을래? |
| 저기, 혹시 마그마번 가지고 계세요? | 저기, 혹시 마그마번 가지고 있어? |
|  제 에레키블이랑 교환하지 않으실래요? |  내 에레키블이랑 교환하지 않을래? |
| 와, 마그마번을 가지고 계시네요! 어서 교환해요! | 와, 마그마번을 가지고 있구나! 어서 교환하자! |
| 다음 공연에는 얼음귀신처럼 무시무시한 포켓몬이 있으면 좋을 것 같아요. | 다음 공연에는 얼음귀신처럼 무시무시한 포켓몬이 있으면 좋을 것 같아. |
| 혹시 있으시다면 제 빙큐보와 교환하시겠어요? | 혹시 있다면 내 빙큐보와 교환할래? |
| 멋지네요! 그럼 어서 교환해요! | 멋져! 그럼 어서 교환하자! |
| 얼음귀신 덕분에 무서운 가면과 얼굴을 선보일 다음 공연을 준비할 수 있겠어요. | 얼음귀신 덕분에 무서운 가면과 얼굴을 선보일 다음 공연을 준비할 수 있겠어. |
| 곤율거니를 찾고 있어요, 혹시 제 뜨아거랑 바꾸지 않으실래요? | 곤율거니를 찾고 있어, 혹시 내 뜨아거랑 바꾸지 않을래? |
| 저는 피그킹을 찾고 있습니다. 제 후딘과 교환하시겠습니까? | 난 피그킹을 찾고 있어. 내 후딘과 교환할래? |
| 저는 신비록을 찾고 있습니다. 제 동탁군과 교환하시겠습니까? | 난 신비록을 찾고 있어. 내 동탁군과 교환할래? |

### 1-3. 유지자 판정대로 넣은 셋

| 원문 | 옛 번역 | 새 번역 |
|---|---|---|
| `Bien, ¡ahora tú!` | 자, 이제 네 차례야! | 자, 이제 그쪽 차례예요! |
| `Mmm... tu \v[66]... déjame verlo...` | 음... 네 \v[66]... 한번 볼게... | 음... 그 \v[66]... 한번 볼게요... |

## 2. 판정이 필요한 자리 — 페이지 전문

각 자리의 원문을 그대로 싣는다. 격 신호가 되는 낱말을 함께 적었다.

### 2-1. 처형 구경꾼 (원문 `tú` — 지금 번역이 존대라 어긋난다)

맵331(Pueblo Mosaico) 이벤트5 페이지0 · 격 신호: `joven`(젊은이라 부름) · `¿Ves…?` · `Me robó` — 전부 tú. 다만 「유죄 판결을 받은 남성」은 `le digo`로 usted를 쓴다(그 줄은 존대가 맞다)

- `<i>Excuse moi</i>, joven, esto es una ejecución privada.`
  → <i>Excuse-moi</i>, 젊은이. 이건 비공개 처형이에요.
- `¿Ves a ese pérfido hombre que está sobre el cadalso? ¡Me robó a mi Pokémon y se deshizo de él!`
  → 처형대 위에 서 있는 저 비열한 사내가 보이나요? 내 포켓몬을 훔치고는 내다 버렸지 뭡니까!
- `Y no era un Pokémon cualquiera, no. ¡Se trataba de un Furfrou varicolor! Una extrema rareza que me costó lo suyo.`
  → 그저 그런 포켓몬이 아니었습니다. 색이 다른 트리미앙이었다고요! 엄청난 희귀종이라 손에 넣느라 거금을 들인 녀석이란 말입니다.
- `El castigo por tan altísimo delito no puede ser sino otro que la muerte.`
  → 이런 중죄에 내릴 처벌이란 사형 말고는 없는 법입니다.
- `<b>Hombre sentenciado:</b> Por última vez, le digo que yo no he sido.`
  → <b>유죄 판결을 받은 남성:</b> 마지막으로 말씀드리는데, 정말 제가 아니었습니다.
- `Vi a su Furfrou por la <b>Ruta 20</b> y jugué un poco con él. ¡Pero después le perdí de vista!`
  → <b>20번도로</b>에서 그쪽 트리미앙을 보고 잠시 같이 놀아 준 것뿐이에요. 하지만 그러다 놓치고 말았다고요!
- `Seguramente aún siga deambulando por ahí.`
  → 분명 아직도 그 근처를 헤매고 있을 겁니다.
- `¡Mentiras y más mentiras! Voy a disfrutar golosamente de esta ejecución.`
  → 거짓말에 또 거짓말이군! 이번 처형은 아주 즐겁게 감상해 주지.

### 2-2. 트리미앙 주인 (원문 `tú` — 존대와 반말이 섞여 있다)

맵331(Pueblo Mosaico) 이벤트7 페이지0 · 격 신호: `intervienes tú` · `¿eras tú…?` · `prepárate` — tú. 페이지 끝의 브리오프는 다른 화자다

- `¡Qué casualidad más conveniente! Resulta que aparece mi Furfrou justo cuando intervienes tú.`
  → 참 편리한 우연이로군요! 하필 네가 개입하자마자 내 트리미앙이 나타나다니.
- `¿Acaso eras tú la persona culpable? ¿Sabes lo que he tenido que esforzarme para conseguir un huevo de Furfrou con estas características?`
  → 혹시 네 녀석이 범인이었나? 이런 특징을 가진 트리미앙 알을 얻으려고 내가 얼마나 공을 들였는지 아느냐?
- `No toleraré que atenten contra mi honor, ¡prepárate para recibir tu castigo!`
  → 내 명예를 더럽히는 짓은 용납하지 않겠어요. 응분의 벌을 받을 준비나 해라!
- `Mira, ¿sabes qué? Tú y tu compinche podéis quedaros con el dichoso Furfrou.`
  → 이봐요, 그 지긋지긋한 트리미앙은 너랑 네 패거리가 가지시지요.
- `Haré que mis sirvientes trabajen día y noche para sacar más huevos de Furfrou. ¡Pronto tendré toda una jauría de Pokémon varicolor! ¡Jo, jo, jo!`
  → 하인들을 밤낮없이 일하게 해서 트리미앙 알을 더 뽑아내면 그만이다. 곧 색이 다른 포켓몬 무리를 거느리게 될 거다! 조, 조, 조!
- `<b>Hombre sentenciado:</b> ¡Eh, me has salvado de un buen apuro!`
  → <b>유죄 판결을 받은 남성:</b> 어이, 덕분에 큰 곤경에서 벗어났네!
- `No sé qué pasa últimamente con el mundo, que el despotismo y la barbarie campan a sus anchas más que nunca.`
  → 요즘 세상이 어떻게 돌아가는 건지, 전횡과 야만이 그 어느 때보다 기승을 부리는군요.
- `¡Y parecía que todo eso había quedado atrás!`
  → 그런 야만적인 일은 이제 다 끝난 줄 알았는데 말입니다!
- `En fin, me llamo <b>Briof</b> y soy un comerciante de artículos raros. Me disponía a trasladarme a <b>Pueblo Acrílico</b> cuando pasó todo este lío.`
  → 어쨌든 제 이름은 <b>브리오프</b>이고 희귀품을 다루는 상인입니다. 이 소동이 터졌을 때 막 <b>아크릴리코마을</b>로 떠나려던 참이었지요.
- `<b>Briof:</b> No te preocupes por el Furfrou, yo cuidaré de él.`
  → <b>브리오프:</b> 트리미앙은 걱정하지 마, 내가 보살펴줄 테니.
- `<b>Briof:</b> En fin, ¡pásate por mi tienda de <b>Pueblo Acrílico</b> y te haré un precio especial, camarada!`
  → <b>브리오프:</b> 아무튼 <b>아크릴리코마을</b>에 있는 내 가게에 들러 주게, 친구! 특별가로 해줌세!

### 2-3. 메를로 저택 손님 (원문 `tú`)

맵12(Chateau Merlot) 이벤트17 페이지0 · 격 신호: `Entre tú y yo` — tú. 지금은 앞줄만 존대다

- `¿Seguro que hace bien el <i>monsieur</i> <b>Merlot</b> dejando ir a su hija de viaje?`
  → <i>무슈</i> <b>메를로</b>가 딸을 여행 보내는 게 과연 현명한 처사일까요?
- `Entre tú y yo, esa muchacha no es la vela más luminosa del candelabro.`
  → 우리끼리 얘기지만, 그 처자는 머리가 그리 잘 돌아가는 편이 아니거든.

### 2-4. 로시용 저택 손님 (원문 `tú`)

맵38(Chateau Rosillon) 이벤트6 페이지0 · 격 신호: `Míralos` — tú 명령형. 지금은 앞줄만 존대다

- `Menudas vistas, ¿no? Míralos, todos haciendo sus quehaceres como autómatas, como pequeñas criaturas predecibles...`
  → 훌륭한 전망이죠? 저들을 보세요. 다들 자동인형이나 예측 가능한 작은 생물처럼 자기 할 일을 하고 있네요...
- `¡Eh! ¡Me están quitando el sitio!`
  → 어이! 내 자리를 뺏고 있잖냐!

### 2-5. 몬스터볼 상인 (원문 `tú`)

맵297(Ciudad Fluxus) 이벤트59 페이지0 · 격 신호: `proponerte` · `¿Me cambiarías?` · `Aquí tienes` · `Te cambiaré` — 전부 tú. 지금은 다섯 줄이 존대다

- `Pareces alguien con cierta maña en la fabricación de Pokéball. Voy a proponerte un lucrativo negocio.`
  → 몬스터볼을 만드는 데 꽤 수완이 있으시군요. 짭짤한 거래를 제안해 드리죠.
- `¿Me cambiarías una Ultra Ball Casera por una Ocaso Ball?`
  → 수제 하이퍼볼 하나를 다크볼 하나와 바꾸시겠습니까?
- `¡Pues trato cerrado! Aquí tienes.`
  → 거래 성사군요! 여기 있습니다.
- `Te cambiaré las Ocaso Balls que hagan falta siempre que me traigas más de esas Ultra Balls Caseras.`
  → 그 수제 하이퍼볼을 더 가져다주신다면, 필요한 만큼 얼마든지 다크볼로 바꿔 드리겠습니다.
- `¡Pero si no tienes nada, muerto de hambre!`
  → 뭐야, 가진 게 아무것도 없잖아. 거지 녀석이!
- `¡Pero si no tienes nada, muerta de hambre!`
  → 뭐야, 가진 게 아무것도 없잖아. 거지 녀석이!
- `Entiendo. A mí me parecía un trato justo, dado que las Ocaso Balls son poco frecuentes.`
  → 알겠습니다. 다크볼이 귀하다는 점을 고려하면 공정한 거래라 생각했습니다만.

### 2-6. 포켓몬센터 손님 (원문 `tú`)

맵307(Centro Pokémon) 이벤트3 페이지0 · 격 신호: `¿Has llegado a usar…?` — tú. 지금은 앞줄만 존대다

- `¿Has llegado a usar a uno de esos Marowak? Por lo visto, portan restos de Steelix a modo de armadura.`
  → 저 텅구리들을 써본 적이 있나요? 보아하니 강철톤의 잔해를 갑옷처럼 두르고 있더군요.
- `Además, si llevan equipado el objeto Cola Plúmbea, atacarán con mucha más fuerza.`
  → 게다가 느림보꼬리를 지니게 하면 훨씬 더 강력하게 공격하게 될 거다.

### 2-7. 미르시티 서쪽 주민 (원문에 격 신호 없음)

맵162(Ciudad Luminalia - Oeste) 이벤트10 페이지0 · 상인들을 3인칭으로만 말해 tú/usted가 드러나지 않는다 — 어느 쪽으로 세울지 판정이 필요하다

- `Yo no tengo problema con que estos individuos feriantes de <b>Pueblo Profano</b> se ganen la vida, pero...`
  → <b>프로파노마을</b>에서 온 저 축제 상인들이 밥벌이하는 것까진 상관 안 하겠는데...
- `¿Tienen que hacerlo en mi barrio? ¿Tan cerca de mi casa?`
  → 하필 우리 동네에서 해야 하나요? 우리 집 바로 앞에서?

### 2-8. 플라베베 수집가 — 오타 한 자리

맵93(Casa) 이벤트25 페이지0 · 교환 NPC라 이미 반말로 통일됐다. 「손에 넣었거다!」가 오타로 보인다(「넣었군!」?)

- `Me gustaría tener un Flabebe, es un Pokémon que se ha puesto de moda en la alta sociedad.`
  → 플라베베를 하나 구하고 싶군. 상류층 사이에서 아주 유행하는 포켓몬이거든.
- `Si encuentras uno, ¿lo cambiarías por mi  Cutiefly?`
  → 혹시 한 마리 찾게 되면 내 에블리랑 교환할래?
- `¡Eh, tienes un Flabebe! ¡Intercambiemos  nuestros Pokémon!`
  → 어라, 플라베베를 가지고 있잖아! 어서 나랑 교환하자고!
- `¡<i>Trés bien</i>! ¡Por fin tengo este Pokémon!`
  → <i>Très bien</i>! 마침내 이 포켓몬을 손에 넣었거다!
- `Si tienes un Flabebe, ponlo en el primer  lugar de tu equipo para que pueda verlo bien.`
  → 플라베베가 있다면 선두에 세워 두고 다시 와 줘.
- `¿En serio? Voy a ser el hazmerreir de en las fiestas.`
  → 정말인가? 이러다 파티에서 웃음거리가 되고 말겠군.

## 3. 오탐이라 본 자리 — 손대지 않는 게 맞는지 확인

### 3-1. 로시용 저택 (감탄 종결)

맵36(Chateau Rosillon) 이벤트10 페이지0 · 「~다니...」로 끝나 격이 드러나지 않는다고 봤다

- `Ser Aspirante, poder viajar por toda la región forjando un vínculo irrompible con los Pokémon que vas conociendo...`
  → 후보생이 되어 지방 전체를 누비며 만나는 포켓몬들과 끊을 수 없는 유대를 맺는다니...
- `¡Ojalá me hubiera pillado más joven!`
  → 조금만 더 젊었을 때 이런 일을 경험했으면 좋았을 텐데요!

### 3-2. 플룩수스시티 주민 (감탄 종결)

맵297(Ciudad Fluxus) 이벤트18 페이지0 · 위와 같다

- `Así que las famosas <b>12 medallas de Regente</b> que se distribuyen por toda la región se fabrican en esta ciudad...`
  → 지방 전역에 지급되는 저 유명한 <b>섭정 배지 12개</b>가 바로 이 도시에서 만들어진다니...
- `Me pregunto qué secretos habrá en su fabricación y por qué tienen unas runas tan peculiares grabadas en ellas.`
  → 제작 과정에 어떤 비밀이 숨겨져 있는지, 왜 저렇게 독특한 룬 문자가 새겨진 것인지 궁금하군요.

### 3-3. 궁전 귀부인 — 인용된 속담

맵190(Palacio Luminalia) 이벤트29 페이지0 · 반말로 잡힌 줄이 화자의 말이 아니라 인용된 옛 속담이다

- `¿Has venido a protegerme? ¡Por favor, no permitas que me hagan ningún daño!`
  → 날 지켜주러 온 건가요? 제발 다치지 않게 해주세요!
- `...`
  → ...
- `¿Viejas leyendas en el palacio? No sé de qué nos sirve eso ahora...`
  → 궁전에 전해지는 옛 전설이요? 그게 지금 무슨 소용이 있겠어요...
- `Pero sí, conozco una. Una especie de dicho extraño que se decía antaño.`
  → 그래도 하나 알고 있긴 해요. 옛날부터 전해지던 이상한 속담 같은 건데요.
- `"Siéntate en la silla maldita y usa el talismán. Con las sombras te encontrarás".`
  → “저주받은 의자에 앉아 부적을 사용하라. 그리하면 그림자들을 만나리라.”
- `Y ahora, por favor, ¡encárgate de esos revolucionarios!`
  → 자, 이제 제발 저 혁명가들을 처리해 주세요!

### 3-4. 겁먹은 귀부인 — 괄호 지문

맵190(Palacio Luminalia) 이벤트37 페이지0 · 반말로 잡힌 줄이 괄호 지문이라 화자 말이 아니다

- `Mi... mi Pokémon me protegerá de cualquier peligro, ¿verdad? ¿VERDAD?`
  → 내... 내 포켓몬이 어떤 위험에서도 절 지켜주겠죠? 그렇죠?!
- `(Parece estar muy alterada para hablar)`
  → (너무 동요해서 대화할 수 없는 것 같다)

