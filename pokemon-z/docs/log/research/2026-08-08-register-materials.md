# 귀족 NPC 격 손질 — 경위와 판정 재료 (2026-08-08)

## 왜 이 문서가 있나

**하려던 일** — 유지자 제보(「귀족들이 난데없이 ~거다! 하는 식으로 말을 마친다」)를 받아
귀족 스프라이트 NPC의 격이 한 페이지 안에서 섞인 자리를 정리하려 했다. 훑어 보니 26곳이었고,
그중 12곳의 원인은 여러 맵에 **복제된** 교환 정형 문구 네 계열이었다.

**어쩌다 조졌나** — 유지자는 복제된 문구를 자리마다 격에 맞게 나눠 쓰라고 했는데, 나는
원문이 전부 `tú`라는 것을 근거로 「나눌 게 없다」고 판단해 예순 자리를 반말 한 값으로 눌렀다.
교환 페이지 안의 존댓말 56줄도 함께 반말로 다시 썼다. 두 가지를 어겼다.

1. **짧은 NPC 대사의 말투 기준은 스프라이트 페르소나다.** 플레이어가 그 자리에서 보는 것은
   그림 하나뿐이라 이 프로젝트는 잡담 NPC의 말투를 그림으로 배정해 왔다. 나는 그 방침을
   모르는 채(가이드를 안 읽고) 작업했다.
2. **`tú`는 반말 근거가 아니다.** 스페인어의 일상 기본형이라 한국어 존대와 얼마든지 함께 간다.
   `speakers-register.md`의 「어투의 최종 근거는 원문의 격」은 이름표가 붙은 인물의 격 판정을
   다루는 절인데, 그것을 잡담 NPC까지 덮는 전 범위 규칙으로 읽었다.

**되돌린 것** — 교환 정형 문구 77줄과 교환 페이지 56줄을 손대기 전으로 물렸다(정본은
`85cac72` 시점). 유지자가 판정해 준 자리는 그대로 두거나 다시 넣었다.

**다시 할 때** — 티켓 Z-25(귀족 그룹의 격을 정본으로 세우기)와 Z-27(복제된 정형 문구를
페르소나별로 나눠 쓰기)이다. 아래 재료는 그 작업에 쓴다.

한 자리마다 **페이지의 모든 줄**을 원문·지금 정본·제안 순으로 싣는다. `⟨이름⟩`은 그 줄에
이름표가 붙어 화자가 갈리는 줄이다. 원문 격 신호는 그 페이지 전체에서 뽑은 낱말이다.

## A. 교환 NPC — 지금 정본과 되돌린 값

### A-1. 정형 문구 네 계열 — 복제 자리 목록

같은 스페인어가 맵마다 별개 줄로 복제돼 있다. 교환 페이지 57곳의 원문이 전부 `tú`라
반말로 통일하고, 본가 자구를 따랐다(오메가루비·알파사파이어가 `¡Cuida bien de X!`를
「X을 귀여워해 줘!」로, 파티 첫 자리를 「선두」로 옮긴다).

| 원문 | 지금 정본(되돌린 뒤) | 잘못 넣었던 값 | 쓰이는 맵 |
|---|---|---|---|
| `¡Cúidalo muy bien!` | 귀여워해 줘! | 꼭 잘 챙겨줘!  | 62, 63, 116, 135, 177, 178, 179, 302, 313, 395, 397, 409, 478 |
| `¡Vaya! Veo que no tienes uno.` | 이런! 아직 없구나. | 이런! 아직 안 갖고 있군. | 63, 83, 116, 135, 177, 178, 179, 302, 313, 338, 395, 478 |
| `¡Vaya! Al final tendré que poner un anuncio en Milintercambios.` | 이런! 결국 교환 게시판에 광고를 올려야겠군. | 이런! 결국 교환 게시판에 광고를 올려야겠군. | 163, 246, 273, 308 |
| `Si tienes un X, ponlo en el primer lugar de tu equipo…` (60여 줄, X는 포켓몬 이름) | 피죤투가 있다면 선두에 세워 두고 다시 와 줘. | 피죤투가 있다면 제가 잘 볼 수 있게 지니고 있는 포켓몬 맨 앞에 놓아주세요. | 교환 NPC 전 자리 |

### A-2. 교환 페이지에서 존댓말이던 56줄 — 페이지 전문

각 페이지의 원문 격 신호를 함께 싣는다. 「손대기 전」 칸이 비어 있으면 안 바뀐 줄이다.

**맵19 Casa · 이벤트20 · 그림 `mosqueteraw`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| ¡Intercambiar Pokémon es lo mejor! | 포켓몬 교환은 언제 해도 신난다니까! |  |
| Ahora estoy buscando un Mankey, ¿lo cambiarías por mi Abra? | 지금 망키를 구하는 중인데, 내 캐이시랑 바꾸지 않을래? |  |
| ¡Bien, veo que tienes un Mankey! ¡Hagamos el intercambio! | 좋아, 망키를 데리고 있잖아! 당장 교환하자! |  |
| Me encanta Mankey, ¡más vale fuerza que maña! | 난 망키가 정말 좋아. 잔재주보다는 역시 화끈한 힘이지! |  |
| Si tienes un Mankey, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 망키가 있다면 내가 잘 볼 수 있게 지니고 있는 포켓몬 맨 앞에 놓아줘. | 망키가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! ¿No te va lo de intercambiar Pokémon entonces? | 아이고, 아쉬워라! 포켓몬 교환은 안 내키는 거야? |  |

**맵30 Centro Pokémon · 이벤트15 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Pancham, ¿lo cambiarías por mi Cubchoo? Es un raro Pokémon de tipo Hielo. | 판짱을 구하는 중인데, 제 코고미와 교환하지 않으시겠어요? 제법 희귀한 얼음타입 포켓몬이에요. | 판짱을 구하는 중인데, 내 코고미와 교환하지 않을래? 제법 희귀한 얼음타입 포켓몬이야. |
| ¡Bien, veo que tienes un Pancham! ¡Hagamos el intercambio! | 어머, 판짱을 갖고 계시네요! 바로 교환하시죠! | 오, 판짱을 갖고 있구나! 바로 교환하자! |
| ¡Uy, qué cuco es Pancham! ¡Me encanta! | 어머나, 판짱이 정말 귀엽네요! 아주 마음에 들어요! | 우와, 판짱이 정말 귀엽네! 아주 마음에 들어. |
| Si tienes un Pancham, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 판짱이 있다면 잘 볼 수 있게 지닌 포켓몬의 첫 번째에 놓아주시죠. | 판짱이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! Tendré que adentrarme en la hierba alta, supongo... | 어머, 참 아쉽네요. 어쩔 수 없이 제가 직접 풀숲에 들어가 보는 수밖에요... | 아, 참 아쉽네. 어쩔 수 없이 내가 직접 풀숲에 들어가 보는 수밖에... |

**맵50 Casa · 이벤트1 · 그림 `gitano`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Rattata, ¿lo cambiarías por mi Yungoos? | 꼬렛을 찾고 있는데, 제 영구스와 교환하실래요? | 꼬렛을 찾고 있는데, 내 영구스와 교환할래? |
| ¡Bien, veo que tienes un Rattata! ¡Hagamos el intercambio! | 좋아요, 꼬렛을 갖고 계시네요! 교환해요! | 좋아, 꼬렛을 갖고 있구나! 교환하자! |
| ¡Me encantan los Rattata! Me recuerdan a mí. | 저는 꼬렛이 정말 좋아요! 제 모습을 보는 것 같거든요. | 난 꼬렛이 정말 좋아! 내 모습을 보는 것 같거든. |
| Si tienes un Rattata, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 꼬렛이 있다면 잘 볼 수 있게 지닌 포켓몬 맨 앞에 두세요. | 꼬렛이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! Tendré que adentrarme en la hierba alta, supongo... | 어머, 참 아쉽네요. 어쩔 수 없이 제가 직접 풀숲에 들어가 보는 수밖에요... | 아, 참 아쉽네. 어쩔 수 없이 내가 직접 풀숲에 들어가 보는 수밖에... |

**맵62 Casa · 이벤트23 · 그림 `nina`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Timburr, ¿lo cambiarías por mi Riolu? | 으랏차를 찾고 있는데, 내 리오르랑 바꿀래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Jo! ¡Pero si no lo tienes! | 치! 너 으랏차 없잖아! |  |
| Si te haces con un Timburr, ponlo en el primer lugar de tu equipo para que pueda verlo. | 으랏차를 잡으면 바로 볼 수 있게 지닌 포켓몬 첫 번째 자리에 두세요. | 으랏차를 얻거든 선두에 세워 두고 다시 와 줘. |
| ¡Jo! ¡Es que me encanta ese Pokémon! | 우와! 나 그 포켓몬 정말 좋아하거든! |  |

**맵63 Café Bohemien · 이벤트4 · 그림 `cantanteow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Gogoat. ¿lo cambiarías por mi Bulbasaur? | 고고트를 찾고 있어요! 제 이상해씨랑 교환하지 않을래요? | 고고트를 찾고 있어! 내 이상해씨랑 교환하지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Gogoat, ponlo en el primer lugar de tu equipo para que pueda verlo. | 고고트를 구하면 제가 볼 수 있게 지닌포켓몬 첫 번째 칸에 두세요! | 고고트를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵63 Café Bohemien · 이벤트5 · 그림 `mosqueterow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Rapidash, ¿lo cambiarías por mi Charmander? | 날쌩마를 찾고 있다. 내 파이리와 바꾸지 않겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Rapidash, ponlo en el primer lugar de tu equipo para que pueda verlo. | 날쌩마를 구하면 내가 볼 수 있게 지닌포켓몬 첫 번째 칸에 두도록 해라. | 날쌩마를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵63 Café Bohemien · 이벤트6 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Clawitzer, ¿lo cambiarías por mi Squirtle? | 블로스터를 찾고 있어요. 제 꼬부기와 바꾸시지 않겠어요? | 블로스터를 찾고 있어. 내 꼬부기와 바꾸지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Clawitzer, ponlo en el primer lugar de tu equipo para que pueda verlo. | 블로스터를 구하시면 제가 볼 수 있게 지닌포켓몬 첫 번째 칸에 두시죠. | 블로스터를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵77 Casa · 이벤트4 · 그림 `brujita`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Tinkatuff, ¿lo cambiarías por mi Impidimp? | 벼리짱을 찾고 있느니라, 내 메롱꿍과 바꿀 터이냐? |  |
| ¡Bien, veo que tienes un Tinkaton! ¡Hagamos el intercambio! | 오호라, 두드리짱을 가졌구나! 당장 교환을 진행하거라! |  |
| Gracias a la fuerza de Tinkaton, podré amartillar bien a esos malvados cazadores de brujas, ¡jijiji! | 두드리짱의 힘만 있으면 그 사악한 마녀 사냥꾼들을 제대로 두들겨 줄 수 있느니라, 히히히! |  |
| Si tienes un Tinkatuff, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 벼리짱이 있다면 내가 잘 볼 수 있도록 지닌포켓몬 맨 앞에 두거라. | 벼리짱이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Qué lástima! Me gusta Impidimp, pero no es lo suficientemente aguerrido como para defenderme de mis enemigos. | 안타깝구나! 메롱꿍도 좋아하지만 적들에게서 이 몸을 지키기엔 통 미흡하단 말이지. |  |

**맵83 Casa · 이벤트8 · 그림 `campesinaw`** — 격 신호 tú: `Tú`, `te haces`, `tienes`, `tu`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Necesitamos más Oinkologne si queremos que el negocio prospere. | 일이 잘되려면 퍼퓨돈이 더 있어야 하는데 말이야. |  |
| ¿Tú tienes un Oinkologne? ¡Te lo cambio por mi Lickitung! | 너 퍼퓨돈 있어? 내 내루미랑 바꾸지 않을래? |  |
| ¡Gracias! Me has intercambiado un buen ejemplar. | 고마워! 정말 멋진 애로 바꿔 줬네. |  |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Oinkologne, ponlo en el primer lugar de tu equipo para que pueda verlo. | 퍼퓨돈을 잡게 되면 내가 볼 수 있게 지닌포켓몬 제일 앞에 두어 줘. | 퍼퓨돈을 얻거든 선두에 세워 두고 다시 와 줘. |
| ¿No? ¡A este paso nos quedaremos sin trufas! | 안 바꿀 거야? 이대로 가다간 송로버섯이 다 떨어지고 말 텐데! |  |

**맵93 Casa · 이벤트25 · 그림 `burguesow`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Me gustaría tener un Flabebe, es un Pokémon que se ha puesto de moda en la alta sociedad. | 플라베베를 하나 구하고 싶군요. 상류층 사이에서 아주 유행하는 포켓몬이거든요. | 플라베베를 하나 구하고 싶군. 상류층 사이에서 아주 유행하는 포켓몬이거든. |
| Si encuentras uno, ¿lo cambiarías por mi Cutiefly? | 혹시 한 마리 찾게 되면 제 에블리랑 교환하시겠어요? | 혹시 한 마리 찾게 되면 내 에블리랑 교환할래? |
| ¡Eh, tienes un Flabebe! ¡Intercambiemos nuestros Pokémon! | 어라, 플라베베를 가지고 있잖아! 어서 나랑 교환하자고! |  |
| ¡<i>Trés bien</i>! ¡Por fin tengo este Pokémon! | <i>Très bien</i>! 마침내 이 포켓몬을 손에 넣었거다! |  |
| Si tienes un Flabebe, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 플라베베가 있다면 잘 볼 수 있게 지닌포켓몬의 맨 앞에 놓아주세요. | 플라베베가 있다면 선두에 세워 두고 다시 와 줘. |
| ¿En serio? Voy a ser el hazmerreir de en las fiestas. | 정말인가요? 이러다 파티에서 웃음거리가 되고 말겠어요. | 정말인가? 이러다 파티에서 웃음거리가 되고 말겠군. |

**맵105 Transición · 이벤트9 · 그림 `ilustrado`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Fearow, ¿lo cambiarías por mi Farfetch'd? | 깨비드릴조를 찾고 있는데, 제 파오리와 교환해 주시겠어요? | 깨비드릴조를 찾고 있는데, 내 파오리와 교환해 주겠어? |
| ¡Bien, veo que tienes un Fearow! ¡Hagamos el intercambio! | 좋아요, 깨비드릴조를 갖고 계시네요! 교환해요! | 좋아, 깨비드릴조를 갖고 있구나! 교환하자! |
| ¡Gracias! No subestimes a Farfetch'd, puede convertirse en un temible Pokémon si le equipas un Palo. | 고마워요! 파오리를 얕보지 마세요, 대파를 지니게 하면 무시무시한 포켓몬이 될 수 있답니다. | 고마워! 파오리를 얕보지 마, 대파를 지니게 하면 무시무시한 포켓몬이 될 수 있거든. |
| Si tienes un Fearow, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 깨비드릴조가 있다면 잘 볼 수 있게 지닌포켓몬의 첫 번째에 놓아주세요. | 깨비드릴조가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! Siento si te he molestado. | 이런, 아쉽네요! 귀찮게 해드렸다면 죄송해요. | 이런, 아쉽네! 귀찮게 했다면 미안해. |

**맵116 Restaurante Le Chonk · 이벤트13 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Bellossom. ¿lo cambiarías por mi Chikorita? | 아르코를 구하고 있는데, 제 치코리타와 교환하지 않으실래요? | 아르코를 구하고 있는데, 내 치코리타와 교환하지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Bellossom, ponlo en el primer lugar de tu equipo para que pueda verlo. | 아르코를 구하면 볼 수 있게 지닌 포켓몬의 첫 번째 자리에 두세요. | 아르코를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵116 Restaurante Le Chonk · 이벤트14 · 그림 `burguesow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Pyroar, ¿lo cambiarías por mi Cyndaquil? | 화염레오를 찾고 있는데, 제 브케인과 교환하시겠어요? | 화염레오를 찾고 있는데, 내 브케인과 교환할래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Pyroar, ponlo en el primer lugar de tu equipo para que pueda verlo. | 화염레오를 얻으셨다면 지니고 있는 포켓몬 맨 앞에 두어서 보여주세요. | 화염레오를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵116 Restaurante Le Chonk · 이벤트15 · 그림 `cantanteow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Ludicolo, ¿lo cambiarías por mi Totodile? | 지금 로파파를 찾고 있어요! 제 리아코랑 교환하지 않을래요? | 지금 로파파를 찾고 있어! 내 리아코랑 교환하지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Ludicolo, ponlo en el primer lugar de tu equipo para que pueda verlo. | 혹시 로파파를 구하면 지닌 포켓몬 맨 앞에 두고 와서 보여주세요! | 혹시를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵116 Restaurante Le Chonk · 이벤트16 · 그림 `mosqueteraw`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Gastrodon, ¿lo cambiarías por mi Mudkip? | 트리토돈을 찾고 있다. 내 물짱이랑 교환할래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Gastrodon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 트리토돈을 구하게 되면, 내가 볼 수 있게 지닌 포켓몬 첫 번째 자리에 둬라. | 트리토돈을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵116 Restaurante Le Chonk · 이벤트17 · 그림 `cazadorow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Arcanine, ¿lo cambiarías por mi Torchic? | 윈디를 찾고 있다. 내 아차모랑 바꾸겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Arcanine, ponlo en el primer lugar de tu equipo para que pueda verlo. | 윈디를 구하게 되면, 내가 볼 수 있게 지닌 포켓몬 첫 번째 자리에 둬라. | 윈디를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵116 Restaurante Le Chonk · 이벤트18 · 그림 `ninaSonadoraOW`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Whimsicott, ¿lo cambiarías por mi Treecko? | 엘풍을 찾고 있는데, 제 나무지기와 교환해 주시겠어요? | 엘풍을 찾고 있는데, 내 나무지기와 교환해 주겠어? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Whimsicott, ponlo en el primer lugar de tu equipo para que pueda verlo. | 엘풍을 구하면 볼 수 있게 지닌 포켓몬의 첫 번째 자리에 두세요. | 엘풍을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵117 Casa · 이벤트14 · 그림 `lenador`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Forretress, ¿lo cambiarías por mi Shuckle? | 나 쏘콘을 찾고 있는데, 혹시 내 단단지랑 바꿔 주지 않을래? |  |
| ¡Bien, veo que tienes un Forretress! ¡Hagamos el intercambio! | 오, 쏘콘을 갖고 있구나! 바로 교환하자! |  |
| ¡Gracias! Shuckle es un Pokémon muy útil, pero yo no sé usarlo. ¡A ver si me va mejor con Forretress! | 고마워! 단단지는 정말 유용한 포켓몬이지만 난 다루기 어렵더라고. 쏘콘이랑은 더 잘 맞았으면 좋겠다! |  |
| Si tienes un Forretress, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 쏘콘이 있다면 잘 볼 수 있게 파티 첫 번째 자리에 두어 봐. | 쏘콘이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! Tendré que entrenar un Pineco para que evoluciona en Forretress. Qué palo... | 으아, 아쉽다! 피콘을 키워서 쏘콘으로 진화시켜야겠어. 귀찮게 됐네... |  |

**맵135 Casa · 이벤트8 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Mantine. ¿lo cambiarías por mi Tangrowth? | 만타인을 찾고 있어요. 제 덩쿠림보와 교환하시겠어요? | 만타인을 찾고 있어. 내 덩쿠림보와 교환할래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Mantine, ponlo en el primer lugar de tu equipo para que pueda verlo. | 만타인을 잡게 되면 제가 볼 수 있도록 지닌 포켓몬의 맨 앞자리에 두세요. | 만타인을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵163 Ciudad Luminalia - Norte · 이벤트16 · 그림 `burguesow`** — 격 신호 tú: `tienes`, `tu`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Oye, ¿tienes por casualidad uno de esos Electivire? | 저기, 혹시 에레키블을 한 마리 가지고 계신가요? | 저기, 혹시 에레키블을 한 마리 가지고 있어? |
| ¿No te gustaría cambiarlo por mi Magmortar? | 제 마그마번과 교환해 보지 않으시겠어요? | 내 마그마번과 교환해 보지 않을래? |
| ¡Bien, veo que tienes un Electivire! ¡Hagamos el intercambio! | 좋군요, 에레키블을 가지고 계시네요! 교환하도록 해요! | 좋군, 에레키블을 가지고 있구나! 교환하자! |
| ¡Qué bien! ¡Siempre me ha encantado Darmanitan! | 정말 좋네요! 전 항상 불비달마를 정말 좋아했거든요! | 정말 좋아! 난 항상 불비달마를 정말 좋아했거든! |
| Si tienes un Electivire, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 에레키블을 가지고 있다면 잘 볼 수 있게 지닌포켓몬의 맨 앞에 놓아 주세요. | 에레키블이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |  |

**맵176 Casa · 이벤트6 · 그림 `nino`** — 격 신호 tú: `Cambiarías`, `tienes`, `tu` · usted: `Cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| ¡Me apasionan los Pokémon de tipo Bicho! Por eso busco coleccionarlos todos. | 저는 벌레타입 포켓몬이 너무 좋아요! 그래서 전부 모으려고 하거든요. | 난 벌레타입 포켓몬이 너무 좋아! 그래서 전부 모으려고 하거든. |
| ¿Cambiarías un Scyther por un Heracross? Un bicho por un bicho. | 스라크를 헤라크로스랑 교환해 주실 수 있나요? 벌레끼리 바꾸는 거예요. | 스라크를 헤라크로스랑 교환해 줄 수 있어? 벌레끼리 바꾸는 거야. |
| ¡Bien, veo que tienes un Scyther! ¡Hagamos el intercambio! | 와, 스라크를 갖고 계시네요! 교환해요! | 와, 스라크를 갖고 있구나! 교환하자! |
| Me encanta Scyther, ¡ahora tengo que pensar en qué evolucionarlo! | 스라크는 정말 좋아요. 이제 어떤 포켓몬으로 진화시킬지 고민해 봐야겠어요! | 스라크는 정말 좋아. 이제 어떤 포켓몬으로 진화시킬지 고민해 봐야겠어! |
| Si tienes un Scyther, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 스라크가 있으시다면, 잘 볼 수 있게 지닌포켓몬의 첫 번째에 놓아주세요. | 스라크가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! Me va a costar mucho hacerme con todos los Pokémon bicho. | 이런, 정말 아쉽네요! 벌레타입 포켓몬을 전부 모으기는 쉽지 않겠어요. | 이런, 정말 아쉽네! 벌레타입 포켓몬을 전부 모으기는 쉽지 않겠어. |

**맵177 Café Soleil · 이벤트4 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Misdreavus, ¿lo cambiarías por mi Chimchar? | 무우마를 찾고 있답니다. 제 불꽃숭이와 교환하시겠어요? | 무우마를 찾고 있어. 내 불꽃숭이와 교환할래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵177 Café Soleil · 이벤트5 · 그림 `lenador`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Clamperl, ¿lo cambiarías por mi Piplup? | 내가 진주몽을 하나 찾고 있는데, 내 팽도리랑 바꾸지 않을래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵177 Café Soleil · 이벤트12 · 그림 `mosqueterow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Makuhita, ¿lo cambiarías por mi Turtwig? | 내가 마크탕을 찾고 있는데, 내 모부기와 바꾸지 않겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵178 Café Concordia · 이벤트4 · 그림 `cantanteow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Tropius. ¿lo cambiarías por mi Rowlet? | 트로피우스를 찾고 있어요! 제 나몰빼미와 교환하지 않으실래요? | 트로피우스를 찾고 있어! 내 나몰빼미와 교환하지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Tropius, ponlo en el primer lugar de tu equipo para que pueda verlo. | 트로피우스를 구하시면 제가 볼 수 있게 지닌 포켓몬의 첫 번째 자리에 두세요! | 트로피우스를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵178 Café Concordia · 이벤트5 · 그림 `mosqueterow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Chandelure, ¿lo cambiarías por mi Litten? | 샹델라를 찾고 있는데, 내 냐오불이랑 바꾸지 않겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Chandelure, ponlo en el primer lugar de tu equipo para que pueda verlo. | 샹델라를 구하면 내가 볼 수 있게 지닌 포켓몬의 첫 번째 자리에 두고 와라. | 샹델라를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵178 Café Concordia · 이벤트6 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Sharpedo, ¿lo cambiarías por mi Popplio? | 샤크니아를 찾고 있답니다. 제 누리공과 교환하지 않으시겠어요? | 샤크니아를 찾고 있어. 내 누리공과 교환하지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Sharpedo, ponlo en el primer lugar de tu equipo para que pueda verlo. | 샤크니아를 구하시면 알아볼 수 있게 지닌 포켓몬의 첫 번째 자리에 두시지요. | 샤크니아를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵179 Café Can Can · 이벤트6 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Rapidash, ¿lo cambiarías por mi Tepig? | 날쌩마를 찾고 있는데, 제 뚜꾸리와 교환하시겠어요? | 날쌩마를 찾고 있는데, 내 뚜꾸리와 교환할래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵179 Café Can Can · 이벤트7 · 그림 `hombre1`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Masquerain, ¿lo cambiarías por mi Oshawott? | 비나방을 찾고 있는데, 내 수댕이랑 바꿀래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵179 Café Can Can · 이벤트8 · 그림 `anciano`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Wormadam, ¿lo cambiarías por mi Snivy? | 도롱마담을 찾고 있다네, 내 주리비얀과 바꾸지 않겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵180 Casa · 이벤트8 · 그림 `mujer2`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Me encanta Aromatisse, ¿lo cambiarías por mi Slurpuff? | 난 프레프티르가 정말 좋던데, 혹시 내 나루림이랑 바꿀래? |  |
| ¡Bien, veo que tienes un Slurpuff! ¡Hagamos el intercambio! | 어, 나루림을 갖고 있네! 그럼 나랑 교환하자! |  |
| ¡Gracias! ¡Qué bonito es mi nuevo y flamante Aromatisse! | 고마워! 새로 생긴 내 멋진 프레프티르, 정말 예쁘다! |  |
| Si tienes un Aromatisse, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 프레프티르가 있다면 잘 볼 수 있게 지닌포켓몬의 맨 앞에 놓아줘. | 프레프티르가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué lástima! ¿Y cómo me hago con ese precioso Pokémon? | 아이쿠, 아쉬워라! 그럼 저 예쁜 포켓몬은 어떻게 구해야 하지? |  |

**맵185 Casa · 이벤트15 · 그림 `gitana`** — 격 신호 tú: `Tienes`, `tienes`, `tu` · usted: `su`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| ¿Tienes un Kadabra? ¿Te gustaría cambiarlo por mi Kirlia? | 흠... 그렇군... 윤겔라를 가지고 있나? 내 킬리아와 교환하지 않겠나? |  |
| ¡Qué guay! ¡Pues a intercambiar se ha dicho! | 신난다! 그럼 당장 교환하자! |  |
| Kirlia puede evolucionar a dos formas distintas dependiendo de su género y del método que decidas usar para evolucionarlo. ¡Buena suerte! | 킬리아는 성별과 진화시키는 방식에 따라 두 가지 다른 모습으로 진화할 수 있지. 행운을 빈다! |  |
| Si tienes un Kadabra, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 윤겔라가 있다면 내가 잘 볼 수 있게 지닌포켓몬 첫 번째 자리에 두거라. | 윤겔라가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué mala suerte la mía! | 흠... 내 운이 없었군! |  |

**맵246 Casa · 이벤트12 · 그림 `mosqueteraw`** — 격 신호 tú: `tienes`, `tu`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Oye, ¿tienes por casualidad uno de esos Trevenant? | 이봐, 혹시 대로트 한 마리 없어? |  |
| ¿No te gustaría cambiarlo por mi GOURGEIST? | 내 펌킨인이랑 교환하지 않을래? |  |
| ¡Bien, veo que tienes un Trevenant! ¡Hagamos el intercambio! | 좋아, 대로트를 갖고 있구나! 당장 교환하자! |  |
| ¡Qué bien! ¡Siempre me ha encantado Trevenant! | 신난다! 난 늘 대로트가 정말 좋았거든! |  |
| Si tienes un Trevenant, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 대로트가 있다면 잘 볼 수 있게 지닌포켓몬 맨 앞에 놓아다오. | 대로트가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |  |

**맵273 Centro Pokémon · 이벤트3 · 그림 `burguesaow`** — 격 신호 tú: `tienes`, `tu`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Oye, ¿tienes por casualidad uno de esos Pidgeot? | 저기, 혹시 피죤투를 갖고 계신가요? | 저기, 혹시 피죤투를 갖고 있어? |
| ¿No te gustaría cambiarlo por mi Squawkabilly? | 제 시비꼬랑 교환하지 않으시겠어요? | 내 시비꼬랑 교환하지 않을래? |
| ¡Bien, veo que tienes un Pidgeot! ¡Hagamos el intercambio! | 어머, 피죤투가 있으시네요! 어서 교환해요! | 오, 피죤투가 있구나! 어서 교환하자! |
| ¡Qué bien! Ese Squawkabilly era demasiado ruidoso para mi ritmo de vida tranquilo. | 잘됐네요! 그 시비꼬는 제 차분한 삶에 비하면 너무 시끄러웠거든요. | 잘됐어! 그 시비꼬는 내 차분한 삶에 비하면 너무 시끄러웠거든. |
| Si tienes un Pidgeot, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 피죤투가 있다면 제가 잘 볼 수 있게 지니고 있는 포켓몬 맨 앞에 놓아주세요. | 피죤투가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |  |

**맵302 Café Pedrín · 이벤트4 · 그림 `alquimista2OW`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Victreebel. ¿lo cambiarías por mi Grookey? | 우츠보트를 찾고 있어요. 제 흥나숭과 교환해 주시지 않을래요? | 우츠보트를 찾고 있어. 내 흥나숭과 교환해 주지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Victreebel, ponlo en el primer lugar de tu equipo para que pueda verlo. | 우츠보트를 잡으시면 제가 볼 수 있게 지닌포켓몬 첫 번째 자리에 두세요. | 우츠보트를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵302 Café Pedrín · 이벤트5 · 그림 `lenador`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Heatmor, ¿lo cambiarías por mi Scorbunny? | 앤티골을 하나 찾고 있는데, 내 스코버니랑 안 바꾸겠어? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Heatmor, ponlo en el primer lugar de tu equipo para que pueda verlo. | 앤티골을 구하게 되면 내가 볼 수 있게 지닌포켓몬 첫 번째에 놓아주라. | 앤티골을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵302 Café Pedrín · 이벤트6 · 그림 `burguesaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Bruxish, ¿lo cambiarías por mi Sobble? | 치갈기를 찾고 있는데, 제 울머기랑 교환하지 않으시겠어요? | 치갈기를 찾고 있는데, 내 울머기랑 교환하지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Bruxish, ponlo en el primer lugar de tu equipo para que pueda verlo. | 치갈기를 구하시면 제가 볼 수 있게 지닌포켓몬 첫 번째 자리에 두세요. | 치갈기를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵308 Casa · 이벤트3 · 그림 `obrerow`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Anorith, ¿lo cambiarías por mi Tyrunt? | 아노딥스를 찾고 있는데, 내 티고라스랑 교환할래? |  |
| ¡Bien, veo que tienes un Anorith! ¡Hagamos el intercambio! | 좋아, 아노딥스를 갖고 있구나! 어서 교환하자고! |  |
| ¡Qué bien! ¡Ya me quedan menos Pokémon para completar la Pokédex! | 신난다! 이제 도감 완성까지 남은 포켓몬이 줄었어! |  |
| Si tienes un Anorith, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 아노딥스가 있다면 잘 볼 수 있게 지닌포켓몬 첫 번째 자리에 둬 봐. | 아노딥스가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |  |

**맵308 Casa · 이벤트4 · 그림 `mujer2`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Kabuto, ¿lo cambiarías por mi Amaura? | 투구를 찾고 있는데, 내 아마루스랑 교환할래? |  |
| ¡Bien, veo que tienes un Kabuto! ¡Hagamos el intercambio! | 좋아, 투구를 갖고 있구나! 어서 교환하자. |  |
| Los Pokémon prehistóricos son increíbles, ¿verdad? | 고대 포켓몬은 정말 대단하지 않니? |  |
| Si tienes un Kabuto, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 투구가 있다면 잘 볼 수 있게 지닌포켓몬 첫 번째 자리에 둬 봐. | 투구가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |  |

**맵308 Casa · 이벤트12 · 그림 `ranger`** — 격 신호 tú: `tienes`, `tu`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Oye, ¿tienes por casualidad uno de esos Magmortar? | 저기, 혹시 마그마번 가지고 계세요? | 저기, 혹시 마그마번 가지고 있어? |
| ¿No te gustaría cambiarlo por mi Electivire? |  제 에레키블이랑 교환하지 않으실래요? |  내 에레키블이랑 교환하지 않을래? |
| ¡Bien, veo que tienes un Magmortar! ¡Hagamos el intercambio! | 와, 마그마번을 가지고 계시네요! 어서 교환해요! | 와, 마그마번을 가지고 있구나! 어서 교환하자! |
| ¡Qué bien! ¡Siempre me ha encantado Darmanitan! | 정말 좋네요! 전 항상 불비달마를 정말 좋아했거든요! | 정말 좋아! 난 항상 불비달마를 정말 좋아했거든! |
| Si tienes un Magmortar, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 마그마번이 있다면 잘 볼 수 있게 지닌포켓몬 첫 번째 자리에 두세요. | 마그마번이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고를 올려야겠군. |  |

**맵313 Casa · 이벤트11 · 그림 `revolucionaria`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Kingambit, ¿lo cambiarías por mi Krookodile? | 대도각참을 찾는다. 내 악비아르와 바꾸지 않겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con un Krookodile, ponlo en el primer lugar de tu equipo para que pueda verlo. | 악비아르를 얻거든 내가 볼 수 있게 지닌포켓몬 첫 번째에 두어라. | 악비아르를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵338 Campamento de Crisanto · 이벤트10 · 그림 `mosqueteraw`** — 격 신호 tú: `Cambiarías`, `tienes` · usted: `Cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Esto me da algo de vergüenza, pero... No he logrado preparar a mi Pokémon a tiempo para la batalla. | 이거 좀 부끄러운데... 배틀 시간에 맞춰서 포켓몬을 준비 못 했거든. |  |
| Así que necesito un Pokémon fuerte y evolucionado urgentemente o no tendré nada que hacer... | 당장 강하고 진화한 포켓몬이 필요해, 안 그러면 아무것도 못 하고 끝장나겠어... |  |
| ¿Cambiarías un Aggron tuyo por mi Riolu? | 너 혹시 보스로라 가지고 있어? 내 리오르랑 바꾸지 않을래? |  |
| ¡Gracias! ¡Me salvas de una buena! | 고마워! 덕분에 완전히 살았어! |  |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| ¡Pues a ver qué hago ahora! Seguramente acabarán conmigo en seguida. | 아 이제 어쩌지! 이러다간 순식간에 당하고 말겠는데. |  |
| ¡Pues a ver qué hago ahora! Seguramente acabarán conmigo en seguida. | 아 이제 어쩌지! 이러다간 순식간에 당하고 말겠는데. |  |

**맵360 Pueblo Sanguino · 이벤트34 · 그림 `nina`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| No me gusta mi Pokémon... ¿Me lo cambiarías por un Morpeko, si lo tienes? | 내 포켓몬이 마음에 안 들어... 혹시 모르페코 있으면 나랑 바꾸지 않을래? |  |
| ¡Qué guay! ¡Pues a intercambiar se ha dicho! | 신난다! 그럼 당장 교환하자! |  |
| Morpeko me parece mucho más chulo que Pachirisu. ¡Gracias por cambiármelo! | 모르페코가 파치리스보다 훨씬 멋진 것 같아. 바꿔줘서 고마워! |  |
| Si tienes un Morpeko, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 모르페코가 있으면 잘 볼 수 있게 지닌포켓몬 제일 앞에 놓아줘. | 모르페코가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué mala suerte la mía! | 흠... 내 운이 없었군! |  |

**맵378 Carpa · 이벤트7 · 그림 `gitano`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Para mi próxima actuación, me vendría bien un Pokémon aterrador como Glalie. | 다음 공연에는 얼음귀신처럼 무시무시한 포켓몬이 있으면 좋을 것 같아요. | 다음 공연에는 얼음귀신처럼 무시무시한 포켓몬이 있으면 좋을 것 같아. |
| Si tienes uno, ¿lo cambiarías por mi Eiscue? | 혹시 있으시다면 제 빙큐보와 교환하시겠어요? | 혹시 있다면 내 빙큐보와 교환할래? |
| ¡Fantástico! ¡Pues a intercambiar se ha dicho! | 멋지네요! 그럼 어서 교환해요! | 멋져! 그럼 어서 교환하자! |
| Gracias a Glalie, podré preparar mi próximo espectáculo de máscaras y rostros aterradores. | 얼음귀신 덕분에 무서운 가면과 얼굴을 선보일 다음 공연을 준비할 수 있겠어요. | 얼음귀신 덕분에 무서운 가면과 얼굴을 선보일 다음 공연을 준비할 수 있겠어. |
| Si tienes un Glalie, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 얼음귀신이 있다면, 잘 볼 수 있게 지니고 있는 포켓몬 맨 앞에 두세요. | 얼음귀신이 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué mala suerte la mía! | 흠... 내 운이 없었군! |  |

**맵395 Café Galanes · 이벤트4 · 그림 `burguesaow2`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Scrafty, ¿lo cambiarías por mi Fuecoco? | 곤율거니를 찾고 있어요, 혹시 제 뜨아거랑 바꾸지 않으실래요? | 곤율거니를 찾고 있어, 혹시 내 뜨아거랑 바꾸지 않을래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵395 Café Galanes · 이벤트5 · 그림 `curanderaow`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Heliolisk, ¿lo cambiarías por mi Quaxly? | 일레도리자드를 찾고 있다만... 내 꾸왁스랑 바꾸지 않겠나? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵395 Café Galanes · 이벤트12 · 그림 `mosqueteraw`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Kecleon, ¿lo cambiarías por mi Sprigatito? | 켈리몬을 찾고 있는데, 내 나오하랑 바꾸지 않을래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵397 Torre Maestra · 이벤트13 · 그림 `monjaYantraAnciana`** — 격 신호 tú: `cambiarías`, `te haces`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Grumpig, ¿lo cambiarías por mi Alakazam? | 저는 피그킹을 찾고 있습니다. 제 후딘과 교환하시겠습니까? | 난 피그킹을 찾고 있어. 내 후딘과 교환할래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| Si te haces con un Grumpig, ponlo en el primer lugar de tu equipo para que pueda verlo. | 피그킹을 얻게 되시면 제가 볼 수 있도록 지닌포켓몬의 첫 번째 자리에 두어 주십시오. | 피그킹을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵397 Torre Maestra · 이벤트14 · 그림 `monjeYantra`** — 격 신호 tú: `cambiarías`, `te haces`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Wyrdeer, ¿lo cambiarías por mi Bronzong? | 저는 신비록을 찾고 있습니다. 제 동탁군과 교환하시겠습니까? | 난 신비록을 찾고 있어. 내 동탁군과 교환할래? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| Si te haces con un Wyrdeer, ponlo en el primer lugar de tu equipo para que pueda verlo. | 신비록을 얻게 되시면 제가 볼 수 있도록 지닌포켓몬의 첫 번째 자리에 두어 주십시오. | 신비록을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵409 Casa · 이벤트14 · 그림 `monjaYantra`** — 격 신호 tú: `cambiarías`, `te haces`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Throh, ¿lo cambiarías por mi Hitmonchan? | 던지미를 찾고 있는데, 제 홍수몬과 교환해 주시겠습니까? | 던지미를 찾고 있는데, 내 홍수몬과 교환해 주겠어? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| Si te haces con un Throh, ponlo en el primer lugar de tu equipo para que pueda verlo. | 던지미를 얻게 되면, 제가 볼 수 있도록 지닌포켓몬 첫 번째 자리에 놓아주십시오. | 던지미를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵409 Casa · 이벤트15 · 그림 `monjeYantra`** — 격 신호 tú: `cambiarías`, `te haces`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Sawk, ¿lo cambiarías por mi Hitmonlee? | 타격귀를 찾고 있는데, 제 시라소몬과 교환해 주시겠습니까? | 타격귀를 찾고 있는데, 내 시라소몬과 교환해 주겠어? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| Si te haces con un Sawk, ponlo en el primer lugar de tu equipo para que pueda verlo. | 타격귀를 얻게 되면, 제가 볼 수 있도록 지닌포켓몬 첫 번째 자리에 놓아주십시오. | 타격귀를 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵409 Casa · 이벤트16 · 그림 `monjeYantra`** — 격 신호 tú: `cambiarías`, `te haces`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Hariyama, ¿lo cambiarías por mi Hitmontop? | 하리뭉을 찾고 있는데, 제 카포에라와 교환해 주시겠습니까? | 하리뭉을 찾고 있는데, 내 카포에라와 교환해 주겠어? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| Si te haces con un Hariyama, ponlo en el primer lugar de tu equipo para que pueda verlo. | 하리뭉을 얻게 되면, 제가 볼 수 있도록 지닌포켓몬 첫 번째 자리에 놓아주십시오. | 하리뭉을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵409 Casa · 이벤트17 · 그림 `monjaYantra`** — 격 신호 tú: `cambiarías`, `te haces`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Machamp, ¿lo cambiarías por mi Annihilape? | 괴력몬을 찾고 있는데, 제 저승갓숭과 교환해 주시겠습니까? | 괴력몬을 찾고 있는데, 내 저승갓숭과 교환해 주겠어? |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| Si te haces con un Machamp, ponlo en el primer lugar de tu equipo para que pueda verlo. | 괴력몬을 얻게 되면, 제가 볼 수 있도록 지닌포켓몬 첫 번째 자리에 놓아주십시오. | 괴력몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵463 Centro Pokémon · 이벤트17 · 그림 `obrerow`** — 격 신호 tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Cetitan, ¿lo cambiarías por mi Eiscue? | 나 우락고래를 찾고 있는데, 내 빙큐보랑 바꿀래? |  |
| ¡Qué guay! ¡Pues a intercambiar se ha dicho! | 신난다! 그럼 당장 교환하자! |  |
| ¡Menos mal! No me gustaba nada ese Pokémon. | 살았다! 그 포켓몬은 진짜 별로였거든. |  |
| Si tienes un Cetitan, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 우락고래가 있으면 잘 볼 수 있게 파티 맨 앞에 둬 봐. | 우락고래가 있다면 선두에 세워 두고 다시 와 줘. |
| ¡Vaya, qué mala suerte la mía! | 흠... 내 운이 없었군! |  |

**맵478 Casa · 이벤트6 · 그림 `mosqueteraw`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Stonjourner, ¿lo cambiarías por mi Chespin? | 돌헨진을 찾고 있는데, 내 도치마론이랑 바꾸지 않을래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵478 Casa · 이벤트8 · 그림 `hombre1`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Annihilape, ¿lo cambiarías por mi Fennekin? | 저승갓숭을 찾고 있다. 내 푸호꼬랑 바꾸지 않을래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

**맵478 Casa · 이벤트9 · 그림 `lenador`** — 격 신호 tú: `cambiarías`, `te haces`, `tienes`, `tu` · usted: `cambiaría`

| 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|
| Estoy buscando un Malamar, ¿lo cambiarías por mi Froakie? | 칼라마네로를 찾고 있는데, 내 개구마르랑 바꾸지 않을래? |  |
| ¡Cúidalo muy bien! | 꼭 잘 챙겨줘!  | 귀여워해 줘! |
| ¡Vaya! Veo que no tienes uno. | 이런! 아직 안 갖고 있군. | 이런! 아직 없구나. |
| Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 얻거든 내가 볼 수 있게 지닌 포켓몬 첫 번째에 놓아줘. | 그 포켓몬을 얻거든 선두에 세워 두고 다시 와 줘. |
| Bueno, otra vez será. | 그렇다면 다음 기회에. |  |

## B. 개별 자리 — 페이지 전문

유지자가 판정해 준 자리는 이미 들어가 있다. 「잘못 넣었던 값」 칸은 내가 원문 `tú`를
근거로 반말로 밀었다가 물린 값이다 — 참고용이다.

**맵12 Chateau Merlot · 이벤트17 페이지0 · 그림 `burguesow` · 장면 잡담**

원문 격 신호 — tú: `tú` · usted: `su`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | ¿Seguro que hace bien el <i>monsieur</i> <b>Merlot</b> dejando ir a su hija de viaje? | <i>무슈</i> <b>메를로</b>가 딸을 여행 보내는 게 과연 현명한 처사일까요? |  |
| 2 | Entre tú y yo, esa muchacha no es la vela más luminosa del candelabro. | 우리끼리 얘기지만, 그 처자는 머리가 그리 잘 돌아가는 편이 아니거든요. | 우리끼리 얘기지만, 그 처자는 머리가 그리 잘 돌아가는 편이 아니거든. |

**맵38 Chateau Rosillon · 이벤트6 페이지0 · 그림 `burguesow` · 장면 잡담**

원문 격 신호 — tú: `Míralos`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Menudas vistas, ¿no? Míralos, todos haciendo sus quehaceres como autómatas, como pequeñas criaturas predecibles... | 훌륭한 전망이죠? 저들을 보세요. 다들 자동인형이나 예측 가능한 작은 생물처럼 자기 할 일을 하고 있네요... |  |
| 2 | ¡Eh! ¡Me están quitando el sitio! | 이봐요! 내 자리를 뺏고 있잖아요! | 어이! 내 자리를 뺏고 있잖냐! |

**맵297 Ciudad Fluxus · 이벤트59 페이지0 · 그림 `burguesow` · 장면 대화**

원문 격 신호 — tú: `cambiarías`, `tienes` · usted: `cambiaría`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Pareces alguien con cierta maña en la fabricación de Pokéball. Voy a proponerte un lucrativo negocio. | 몬스터볼을 만드는 데 꽤 수완이 있으시군요. 짭짤한 거래를 제안해 드리죠. |  |
| 2 | ¿Me cambiarías una Ultra Ball Casera por una Ocaso Ball? | 수제 하이퍼볼 하나를 다크볼 하나와 바꾸시겠습니까? |  |
| 3 | ¡Pues trato cerrado! Aquí tienes. | 거래 성사군요! 여기 있습니다. |  |
| 4 | Te cambiaré las Ocaso Balls que hagan falta siempre que me traigas más de esas Ultra Balls Caseras. | 그 수제 하이퍼볼을 더 가져다주신다면, 필요한 만큼 얼마든지 다크볼로 바꿔 드리겠습니다. |  |
| 5 | ¡Pero si no tienes nada, muerto de hambre! | 이런, 가진 게 아무것도 없잖습니까. 빈털터리시군! | 뭐야, 가진 게 아무것도 없잖아. 거지 녀석이! |
| 6 | ¡Pero si no tienes nada, muerta de hambre! | 이런, 가진 게 아무것도 없잖습니까. 빈털터리시군! | 뭐야, 가진 게 아무것도 없잖아. 거지 녀석이! |
| 7 | Entiendo. A mí me parecía un trato justo, dado que las Ocaso Balls son poco frecuentes. | 알겠습니다. 다크볼이 귀하다는 점을 고려하면 공정한 거래라 생각했습니다만. |  |

**맵307 Centro Pokémon · 이벤트3 페이지0 · 그림 `burguesow` · 장면 잡담**

원문 격 신호 — tú: `Has llegado`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | ¿Has llegado a usar a uno de esos Marowak? Por lo visto, portan restos de Steelix a modo de armadura. | 저 텅구리들을 써본 적이 있나요? 보아하니 강철톤의 잔해를 갑옷처럼 두르고 있더군요. |  |
| 2 | Además, si llevan equipado el objeto Cola Plúmbea, atacarán con mucha más fuerza. | 게다가 느림보꼬리를 지니게 하면 훨씬 더 강력하게 공격하게 될 거예요. | 게다가 느림보꼬리를 지니게 하면 훨씬 더 강력하게 공격하게 될 거다. |

**맵331 Pueblo Mosaico · 이벤트5 페이지0 · 그림 `burguesow` · 장면 대화**

⟨유죄 판결을 받은 남성⟩ 줄과 그 뒤 두 줄은 그 사람 말이고 원문이 `le digo`·`su Furfrou`라 존대가 맞다 — 제안 없음

원문 격 신호 —  · usted: `le digo`, `su`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | <i>Excuse moi</i>, joven, esto es una ejecución privada. | <i>Excuse-moi</i>, 젊은이. 이건 비공개 처형이에요. |  |
| 2 | ¿Ves a ese pérfido hombre que está sobre el cadalso? ¡Me robó a mi Pokémon y se deshizo de él! | 처형대 위에 서 있는 저 비열한 사내가 보이나요? 내 포켓몬을 훔치고는 내다 버렸지 뭡니까! |  |
| 3 | Y no era un Pokémon cualquiera, no. ¡Se trataba de un Furfrou varicolor! Una extrema rareza que me costó lo suyo. | 그저 그런 포켓몬이 아니었습니다. 색이 다른 트리미앙이었다고요! 엄청난 희귀종이라 손에 넣느라 거금을 들인 녀석이란 말입니다. |  |
| 4 | El castigo por tan altísimo delito no puede ser sino otro que la muerte. | 이런 중죄에 내릴 처벌이란 사형 말고는 없는 법입니다. |  |
| 5 ⟨Hombre sentenciado⟩ | <b>Hombre sentenciado:</b> Por última vez, le digo que yo no he sido. | <b>유죄 판결을 받은 남성:</b> 마지막으로 말씀드리는데, 정말 제가 아니었습니다. |  |
| 6 | Vi a su Furfrou por la <b>Ruta 20</b> y jugué un poco con él. ¡Pero después le perdí de vista! | <b>20번도로</b>에서 그쪽 트리미앙을 보고 잠시 같이 놀아 준 것뿐이에요. 하지만 그러다 놓치고 말았다고요! |  |
| 7 | Seguramente aún siga deambulando por ahí. | 분명 아직도 그 근처를 헤매고 있을 겁니다. |  |
| 8 | ¡Mentiras y más mentiras! Voy a disfrutar golosamente de esta ejecución. | 거짓말에 또 거짓말이군! 이번 처형은 아주 즐겁게 감상해 주지. |  |

**맵331 Pueblo Mosaico · 이벤트7 페이지0 · 그림 `burguesow` · 장면 컷신**

⟨브리오프⟩ 줄과 그가 자기소개하는 세 줄은 다른 화자다 — 제안 없음

원문 격 신호 — tú: `Mira`, `Sabes`, `Tú`, `intervienes`, `prepárate`, `sabes` · usted: `podéis`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | ¡Qué casualidad más conveniente! Resulta que aparece mi Furfrou justo cuando intervienes tú. | 참 편리한 우연이로군요! 하필 네가 개입하자마자 내 트리미앙이 나타나다니. |  |
| 2 | ¿Acaso eras tú la persona culpable? ¿Sabes lo que he tenido que esforzarme para conseguir un huevo de Furfrou con estas características? | 혹시 네 녀석이 범인이었나? 이런 특징을 가진 트리미앙 알을 얻으려고 내가 얼마나 공을 들였는지 아느냐? |  |
| 3 | No toleraré que atenten contra mi honor, ¡prepárate para recibir tu castigo! | 내 명예를 더럽히는 짓은 용납하지 않겠어요. 응분의 벌을 받을 준비나 해라! |  |
| 4 | Mira, ¿sabes qué? Tú y tu compinche podéis quedaros con el dichoso Furfrou. | 이봐요, 그 지긋지긋한 트리미앙은 너랑 네 패거리가 가지시지요. |  |
| 5 | Haré que mis sirvientes trabajen día y noche para sacar más huevos de Furfrou. ¡Pronto tendré toda una jauría de Pokémon varicolor! ¡Jo, jo, jo! | 하인들을 밤낮없이 일하게 해서 트리미앙 알을 더 뽑아내면 그만이다. 곧 색이 다른 포켓몬 무리를 거느리게 될 거다! 조, 조, 조! |  |
| 6 ⟨Hombre sentenciado⟩ | <b>Hombre sentenciado:</b> ¡Eh, me has salvado de un buen apuro! | <b>유죄 판결을 받은 남성:</b> 어이, 덕분에 큰 곤경에서 벗어났네! |  |
| 7 | No sé qué pasa últimamente con el mundo, que el despotismo y la barbarie campan a sus anchas más que nunca. | 요즘 세상이 어떻게 돌아가는 건지, 전횡과 야만이 그 어느 때보다 기승을 부리는군요. |  |
| 8 | ¡Y parecía que todo eso había quedado atrás! | 그런 야만적인 일은 이제 다 끝난 줄 알았는데 말입니다! |  |
| 9 | En fin, me llamo <b>Briof</b> y soy un comerciante de artículos raros. Me disponía a trasladarme a <b>Pueblo Acrílico</b> cuando pasó todo este lío. | 어쨌든 제 이름은 <b>브리오프</b>이고 희귀품을 다루는 상인입니다. 이 소동이 터졌을 때 막 <b>아크릴리코마을</b>로 떠나려던 참이었지요. |  |
| 10 ⟨Briof⟩ | <b>Briof:</b> No te preocupes por el Furfrou, yo cuidaré de él. | <b>브리오프:</b> 트리미앙은 걱정하지 마, 내가 보살펴줄 테니. |  |
| 11 ⟨Briof⟩ | <b>Briof:</b> En fin, ¡pásate por mi tienda de <b>Pueblo Acrílico</b> y te haré un precio especial, camarada! | <b>브리오프:</b> 아무튼 <b>아크릴리코마을</b>에 있는 내 가게에 들러 주게, 친구! 특별가로 해줌세! |  |

**맵93 Casa · 이벤트25 페이지0 · 그림 `burguesow` · 장면 잡담**

교환 NPC라 이미 반말로 통일됐다. 남은 것은 「손에 넣었거다」 오타 하나

원문 격 신호 — tú: `cambiarías`, `tienes`, `tu` · usted: `cambiaría`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Me gustaría tener un Flabebe, es un Pokémon que se ha puesto de moda en la alta sociedad. | 플라베베를 하나 구하고 싶군요. 상류층 사이에서 아주 유행하는 포켓몬이거든요. | 플라베베를 하나 구하고 싶군. 상류층 사이에서 아주 유행하는 포켓몬이거든. |
| 2 | Si encuentras uno, ¿lo cambiarías por mi Cutiefly? | 혹시 한 마리 찾게 되면 제 에블리랑 교환하시겠어요? | 혹시 한 마리 찾게 되면 내 에블리랑 교환할래? |
| 3 | ¡Eh, tienes un Flabebe! ¡Intercambiemos nuestros Pokémon! | 어라, 플라베베를 가지고 있잖아! 어서 나랑 교환하자고! |  |
| 4 | ¡<i>Trés bien</i>! ¡Por fin tengo este Pokémon! | <i>Très bien</i>! 마침내 이 포켓몬을 손에 넣었거다! |  |
| 5 | Si tienes un Flabebe, ponlo en el primer lugar de tu equipo para que pueda verlo bien. | 플라베베가 있다면 잘 볼 수 있게 지닌포켓몬의 맨 앞에 놓아주세요. | 플라베베가 있다면 선두에 세워 두고 다시 와 줘. |
| 6 | ¿En serio? Voy a ser el hazmerreir de en las fiestas. | 정말인가요? 이러다 파티에서 웃음거리가 되고 말겠어요. | 정말인가? 이러다 파티에서 웃음거리가 되고 말겠군. |

## C. 아직 제안을 못 세운 자리

**맵162 Ciudad Luminalia - Oeste · 이벤트10 페이지0 · 그림 `burguesaow` · 장면 잡담**

원문이 상인들을 3인칭으로만 말해 tú/usted가 안 드러난다. 지금은 첫 줄 반말·둘째 줄 존대

원문 격 신호 — tú: `Tienen`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Yo no tengo problema con que estos individuos feriantes de <b>Pueblo Profano</b> se ganen la vida, pero... | <b>프로파노마을</b>에서 온 저 축제 상인들이 밥벌이하는 것까진 상관없습니다만... | <b>프로파노마을</b>에서 온 저 축제 상인들이 밥벌이하는 것까진 상관 안 하겠는데... |
| 2 | ¿Tienen que hacerlo en mi barrio? ¿Tan cerca de mi casa? | 하필 우리 동네에서 해야 하나요? 우리 집 바로 앞에서? |  |

### 오탐이라 본 넷 — 손대지 않는 게 맞는지

**맵36 Chateau Rosillon · 이벤트10 페이지0 · 그림 `burguesaow` · 장면 잡담**

둘째 줄만 존대. 첫 줄은 「~다니...」 감탄 종결이라 격이 안 드러난다고 봤다

원문 격 신호 — (없음)

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Ser Aspirante, poder viajar por toda la región forjando un vínculo irrompible con los Pokémon que vas conociendo... | 후보생이 되어 지방 전체를 누비며 만나는 포켓몬들과 끊을 수 없는 유대를 맺는다니... |  |
| 2 | ¡Ojalá me hubiera pillado más joven! | 조금만 더 젊었을 때 이런 일을 경험했으면 좋았을 텐데요! |  |

**맵297 Ciudad Fluxus · 이벤트18 페이지0 · 그림 `burguesow` · 장면 잡담**

위와 같은 꼴

원문 격 신호 — tú: `tienen` · usted: `su`

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Así que las famosas <b>12 medallas de Regente</b> que se distribuyen por toda la región se fabrican en esta ciudad... | 지방 전역에 지급되는 저 유명한 <b>섭정 배지 12개</b>가 바로 이 도시에서 만들어진다니... |  |
| 2 | Me pregunto qué secretos habrá en su fabricación y por qué tienen unas runas tan peculiares grabadas en ellas. | 제작 과정에 어떤 비밀이 숨겨져 있는지, 왜 저렇게 독특한 룬 문자가 새겨진 것인지 궁금하군요. |  |

**맵190 Palacio Luminalia · 이벤트29 페이지0 · 그림 `burguesaow2` · 장면 잡담**

반말로 잡힌 줄이 화자의 말이 아니라 인용된 옛 속담이다

원문 격 신호 — (없음)

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | ¿Has venido a protegerme? ¡Por favor, no permitas que me hagan ningún daño! | 날 지켜주러 온 건가요? 제발 다치지 않게 해주세요! |  |
| 2 | ... | ... |  |
| 3 | ¿Viejas leyendas en el palacio? No sé de qué nos sirve eso ahora... | 궁전에 전해지는 옛 전설이요? 그게 지금 무슨 소용이 있겠어요... |  |
| 4 | Pero sí, conozco una. Una especie de dicho extraño que se decía antaño. | 그래도 하나 알고 있긴 해요. 옛날부터 전해지던 이상한 속담 같은 건데요. |  |
| 5 | "Siéntate en la silla maldita y usa el talismán. Con las sombras te encontrarás". | “저주받은 의자에 앉아 부적을 사용하라. 그리하면 그림자들을 만나리라.” |  |
| 6 | Y ahora, por favor, ¡encárgate de esos revolucionarios! | 자, 이제 제발 저 혁명가들을 처리해 주세요! |  |

**맵190 Palacio Luminalia · 이벤트37 페이지0 · 그림 `burguesaow2` · 장면 잡담**

반말로 잡힌 줄이 괄호 지문이다

원문 격 신호 — (없음)

| # | 원문 | 지금 정본 | 잘못 넣었던 값 |
|---|---|---|---|
| 1 | Mi... mi Pokémon me protegerá de cualquier peligro, ¿verdad? ¿VERDAD? | 내... 내 포켓몬이 어떤 위험에서도 절 지켜주겠죠? 그렇죠?! |  |
| 2 | (Parece estar muy alterada para hablar) | (너무 동요해서 대화할 수 없는 것 같다) |  |

