# 한 맵 안에서 화자가 갈리는 자리 — 판정 필요분 (2026-08-17)

정본 `translate/ko/00-maps.jsonl`의 (맵, 원문) 묶음을 귀속표
`translate/data/speaker-attr.jsonl.gz`와 (map, k)로 조인해, 자리가 둘 이상이면서
화자(`who`)가 갈리는 묶음을 뽑았다. 비어 있지 않은 화자가 둘 이상인 묶음이 **153**,
빈 화자를 갈래로 치면 196이다(재현: 이 문서 맨 아래 「센 법」).

갈래별로 **갈아야 한다 10 · 갈 필요 없다 73 · 판정 필요 70**이고, 아래는 판정 필요분 70 전량이다.
갈아야 한다 10은 `translate/ko/00-maps.loc.jsonl`에 좌표 항목으로 다 얹혀 있다 — 맵155 치유사 세 줄은
Z-73 1단에서, 맵25 마리아노 여섯 줄과 맵155 치유사 한 줄은 이번에 얹었다.

표 읽는 법: **자리**는 맵과 (이벤트, 명령) 쌍, **현행**은 지금 정본에 든 한 값,
**등재**는 페르소나 표(`translate/persona-table.jsonl`)의 버킷이다.
좌표 열쇠는 (맵, 이벤트, 명령)이라 페이지는 안 들어간다(Z-73 판정).

⚠ 70묶음 중 7묶음은 전투 호출(`pbTrainerBattle`) 대사다 — 좌표 조회 수술이 맵 대사
(`command_101`)와 선택지(`command_102`)에만 얹혀 있어 이 줄들은 갈라야 한다고 판정해도
지금 열쇠로는 못 간다. 자리는 맵25 마리아노·루시아노, 맵92 아르망·루이, 맵146 둘,
맵155 에바리스토·루크레시아, 맵322, 맵488이다.

## 등재 버킷은 갈리나 화자가 셋 이상이거나 반복 정형구다 (28묶음)

대부분 카페·호텔의 포켓몬 교환 창구와 배틀포인트 교환 창구다 — 같은 안내문을 맵 하나에서
서너 스프라이트가 나눠 읽는다. 2026-08-08에 교환 NPC 133줄을 페르소나대로 반말로 밀었다가
되돌린 자리가 여기이고, 지침이 이런 자리를 「맵 다수결로 정한다」로 잡아 두었다.
좌표가 서면 이제 갈 수는 있으나, 갈지 말지가 판정거리다.

| 맵 | 자리 (이벤트, 명령) | 화자 | 등재 | 원문 | 현행 |
|---|---|---|---|---|---|
| 63 Café Bohemien | 4·16, 5·18, 6·16 | burguesaow / cantanteow / mosqueterow | B2(사실·시설 설명 문장만 B3) / B2 / B1변형(공무·통보 문장은 B3) | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 63 Café Bohemien | 4·6, 5·7, 6·6 | burguesaow / cantanteow / mosqueterow | B2(사실·시설 설명 문장만 B3) / B2 / B1변형(공무·통보 문장은 B3) | ¡Cúidalo muy bien! | 귀여워해 줘! |
| 63 Café Bohemien | 4·10, 5·11, 6·10 | burguesaow / cantanteow / mosqueterow | B2(사실·시설 설명 문장만 B3) / B2 / B1변형(공무·통보 문장은 B3) | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 있지 않네. |
| 116 Restaurante Le Chonk | 13·16, 14·18, 15·16, 16·16, 17·16, 18·16 | burguesaow / burguesow / cantanteow / cazadorow / mosqueteraw / ninaSonadoraOW | B2(사실·시설 설명 문장만 B3) / B2(설명·선언은 B3, 자기 과시 대목은 반말 「~거다」 허용) / B2 / B1변형 / B1변형 / B1(어른 상대만 B2) | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 116 Restaurante Le Chonk | 13·6, 14·7, 15·6, 16·6, 17·6, 18·6 | burguesaow / burguesow / cantanteow / cazadorow / mosqueteraw / ninaSonadoraOW | B2(사실·시설 설명 문장만 B3) / B2(설명·선언은 B3, 자기 과시 대목은 반말 「~거다」 허용) / B2 / B1변형 / B1변형 / B1(어른 상대만 B2) | ¡Cúidalo muy bien! | 귀여워해 주세요! |
| 116 Restaurante Le Chonk | 13·10, 14·11, 15·10, 16·10, 17·10, 18·10 | burguesaow / burguesow / cantanteow / cazadorow / mosqueteraw / ninaSonadoraOW | B2(사실·시설 설명 문장만 B3) / B2(설명·선언은 B3, 자기 과시 대목은 반말 「~거다」 허용) / B2 / B1변형 / B1변형 / B1(어른 상대만 B2) | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 계시지 않네요. |
| 177 Café Soleil | 4·18, 5·18, 12·18 | burguesaow / lenador / mosqueterow | B2(사실·시설 설명 문장만 B3) / B1 / B1변형(공무·통보 문장은 B3) | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 177 Café Soleil | 4·12, 5·12, 12·12 | burguesaow / lenador / mosqueterow | B2(사실·시설 설명 문장만 B3) / B1 / B1변형(공무·통보 문장은 B3) | Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘. |
| 177 Café Soleil | 4·7, 5·7, 12·7 | burguesaow / lenador / mosqueterow | B2(사실·시설 설명 문장만 B3) / B1 / B1변형(공무·통보 문장은 B3) | ¡Cúidalo muy bien! | 귀여워해 줘! |
| 177 Café Soleil | 4·11, 5·11, 12·11 | burguesaow / lenador / mosqueterow | B2(사실·시설 설명 문장만 B3) / B1 / B1변형(공무·통보 문장은 B3) | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 있지 않네. |
| 178 Café Concordia | 4·16, 5·16, 6·16 | burguesaow / cantanteow / mosqueterow | B2(사실·시설 설명 문장만 B3) / B2 / B1변형(공무·통보 문장은 B3) | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 178 Café Concordia | 4·6, 5·6, 6·6 | burguesaow / cantanteow / mosqueterow | B2(사실·시설 설명 문장만 B3) / B2 / B1변형(공무·통보 문장은 B3) | ¡Cúidalo muy bien! | 귀여워해 줘! |
| 178 Café Concordia | 4·10, 5·10, 6·10 | burguesaow / cantanteow / mosqueterow | B2(사실·시설 설명 문장만 B3) / B2 / B1변형(공무·통보 문장은 B3) | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 있지 않네. |
| 179 Café Can Can | 6·17, 7·17, 8·17 | anciano / burguesaow / hombre1 | B4 / B2(사실·시설 설명 문장만 B3) / B1 | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 179 Café Can Can | 6·11, 7·11, 8·11 | anciano / burguesaow / hombre1 | B4 / B2(사실·시설 설명 문장만 B3) / B1 | Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘. |
| 179 Café Can Can | 6·6, 7·6, 8·6 | anciano / burguesaow / hombre1 | B4 / B2(사실·시설 설명 문장만 B3) / B1 | ¡Cúidalo muy bien! | 귀여워해 줘! |
| 179 Café Can Can | 6·10, 7·10, 8·10 | anciano / burguesaow / hombre1 | B4 / B2(사실·시설 설명 문장만 B3) / B1 | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 있지 않네. |
| 302 Café Pedrín | 4·16, 5·16, 6·16 | alquimista2OW / burguesaow / lenador | B2 / B2(사실·시설 설명 문장만 B3) / B1 | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 302 Café Pedrín | 4·6, 5·6, 6·6 | alquimista2OW / burguesaow / lenador | B2 / B2(사실·시설 설명 문장만 B3) / B1 | ¡Cúidalo muy bien! | 귀여워해 줘! |
| 302 Café Pedrín | 4·10, 5·10, 6·10 | alquimista2OW / burguesaow / lenador | B2 / B2(사실·시설 설명 문장만 B3) / B1 | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 있지 않네. |
| 308 Casa | 3·17, 4·17, 12·18 | mujer2 / obrerow / ranger | B1 / B1 / B2 | ¡Vaya! Al final tendré que poner un anuncio en Milintercambios. | 이런! 결국 교환 게시판에 광고라도 올려야겠군. |
| 395 Café Galanes | 4·18, 5·18, 12·18 | burguesaow2 / curanderaow / mosqueteraw | B2 / B1변형 / B1변형 | Bueno, otra vez será. | 그렇다면 다음 기회에. |
| 395 Café Galanes | 4·12, 5·12, 12·12 | burguesaow2 / curanderaow / mosqueteraw | B2 / B1변형 / B1변형 | Si te haces con ese Pokémon, ponlo en el primer lugar de tu equipo para que pueda verlo. | 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘. |
| 395 Café Galanes | 4·7, 5·7, 12·7 | burguesaow2 / curanderaow / mosqueteraw | B2 / B1변형 / B1변형 | ¡Cúidalo muy bien! | 귀여워해 줘! |
| 395 Café Galanes | 4·11, 5·11, 12·11 | burguesaow2 / curanderaow / mosqueteraw | B2 / B1변형 / B1변형 | ¡Vaya! Veo que no tienes uno. | 이런! 갖고 있지 않네. |
| 405 Gran Hotel Luminalia | 25·8, 25·18, 25·28, 26·8, 26·18, 26·28, 28·8, 28·18, 29·8, 29·18, 29·28 | burguesow / ilustrado / revolucionaria / revolucionario | B2(설명·선언은 B3, 자기 과시 대목은 반말 「~거다」 허용) / B2(사실 서술은 B3 혼재) / B1변형 / B1변형(흉흉한 시기만 격문투) | No tienes puntos suficientes. ¡Sigue combatiendo, que lo conseguirás! | 포인트가 부족하네요. 계속 배틀하다 보면 분명 얻을 수 있을 거예요! |
| 405 Gran Hotel Luminalia | 25·0, 26·0, 28·0, 29·0 | burguesow / ilustrado / revolucionaria / revolucionario | B2(설명·선언은 B3, 자기 과시 대목은 반말 「~거다」 허용) / B2(사실 서술은 B3 혼재) / B1변형 / B1변형(흉흉한 시기만 격문투) | ¡Buenos días! ¿Quieres cambiar tus <b>Puntos Batalla</b> por alguno de estos fantásticos premios? | 좋은 아침이에요! <b>배틀포인트</b>를 이 멋진 상품 중 하나로 교환하시겠어요? |
| 405 Gran Hotel Luminalia | 25·35, 26·35, 28·25, 29·35 | burguesow / ilustrado / revolucionaria / revolucionario | B2(설명·선언은 B3, 자기 과시 대목은 반말 「~거다」 허용) / B2(사실 서술은 B3 혼재) / B1변형 / B1변형(흉흉한 시기만 격문투) | ¡Vuelve cuando quieras! | 원할 때 언제든지 다시 오세요! |

## 좌표로 못 가른다 — 페이지만 다르다 (10묶음)

화자가 갈리는 두 자리의 (이벤트, 명령)이 같고 페이지만 다르다. 지금 열쇠로는 못 가른다 —
갈라야 한다면 소스 수술(페이지 반입)이 필요하다.

| 맵 | 자리 (이벤트, 명령) | 화자 | 등재 | 원문 | 현행 |
|---|---|---|---|---|---|
| 146 Bastión Pokémon | 6·0 | cazadorow / sanadoraow | B1변형 / B2(배틀 대사만 B1) | Buen trabajo, te deseo una larga y fructífera cacería. | 수고했다. 오랫동안 풍성한 사냥을 즐기길 바란다. |
| 223 Prisión del Olvido | 13·2 | Dandelio / acrilico82 | 없음 / 없음 | No soy más que un criminal, un ladronzuelo de tres al cuarto, un despojo de la sociedad. No hay nadie que me espere ahí  | 저는 그저 범죄자에, 하찮은 좀도둑, 사회의 찌꺼기일 뿐인걸요. 저 바깥에 절 기다려 주는 사람 따위는 없어요. 정말 단 한 명도요. |
| 223 Prisión del Olvido | 13·1 | Dandelio / acrilico82 | 없음 / 없음 | Yo he aprovechado todo el follón para escapar también, pero no me siento con fuerzas para continuar. | 저도 그 난리통을 틈타 탈출하긴 했는데, 계속 나아갈 기운이 전혀 안 나네요. |
| 225 Prisión del Olvido | 40·21 | 304 / 322 / 427 | 없음 / 없음 / 없음 | Hora de volver a tu celda. | 감옥으로 돌아갈 시간이다. |
| 225 Prisión del Olvido | 40·6 | 304 / 322 / 427 | 없음 / 없음 / 없음 | Y parece que se quiere dejar capturar. | 아무래도 잡혀주고 싶어 하는 것 같다. |
| 225 Prisión del Olvido | 40·5 | 304 / 322 / 427 | 없음 / 없음 / 없음 | ¡Es el mismo Pokémon que se te acercó hace un tiempo! | 얼마 전에 네게 다가왔던 바로 그 포켓몬이다! |
| 225 Prisión del Olvido | 40·20 | 304 / 322 / 427 | 없음 / 없음 / 없음 | ¡Sí! ¡Por fin vuelves a tener un Pokémon! | 좋았어! 드디어 다시 포켓몬을 갖게 되었다! |
| 225 Prisión del Olvido | 40·7 | 304 / 322 / 427 | 없음 / 없음 / 없음 | ¿Usas la Pokéball? | 몬스터볼을 사용할까? |
| 345 Balneario Oculto | 23·1 | Urano / payaso | voice-prompts / B1 | Cuando pase unos días en este balneario, podré volver al trabajo con una sonrisa imperecedera. | 이 온천에서 며칠 푹 쉬고 나면 결코 지워지지 않는 미소를 띠고 다시 일터로 돌아갈 수 있을 거다! |
| 345 Balneario Oculto | 23·0 | Urano / payaso | voice-prompts / B1 | Trabajo en el <b>Circo Sanguino</b>, el legendario espectáculo lleno de maravillas. Pero el estrés puede alcanzar hasta  | 난 경이로움으로 가득한 전설의 <b>상기노 서커스</b>에서 일하지! 하지만 늘 웃고 다니는 광대라도 스트레스는 쌓이거든... |

## 이름표 인물이 섞여 있다 (voice-prompts에는 버킷이 없다) (6묶음)

| 맵 | 자리 (이벤트, 명령) | 화자 | 등재 | 원문 | 현행 |
|---|---|---|---|---|---|
| 408 Pesadilla del Circo | 10·17, 10·88, 10·123, 10·135, 10·191, 10·294, 21·18, 21·89, 21·124, 21·136, 21·192, 21·295, 22·18, 22·89, 22·124, 22·136, 22·192, 22·295, 23·19, 23·90, 23·125, 23·137, 23·193, 23·296, 24·20, 24·91, 24·126, 24·138, 24·194, 24·297 | Melia / Siempreviva | voice-prompts / voice-prompts | \sh¡TAAAAAAAAL! | \sh키야아아아아! |
| 418 Gran Hotel Luminalia | 19·111, 19·112, 19·139 | Anturia / Cendera / Hibis / Rúpico / Siempreviva | voice-prompts / voice-prompts / voice-prompts / voice-prompts / voice-prompts | En ese caso, formalizaremos tu retirada del desafío. | 그렇다면 도전을 포기하는 것으로 처리하겠습니다. |
| 418 Gran Hotel Luminalia | 19·52, 19·53, 19·54, 19·80 | Anturia / Arrayán / Cendera / Hibis / Rúpico / Siempreviva | voice-prompts / voice-prompts / voice-prompts / voice-prompts / voice-prompts / voice-prompts | Vamos a curar a tus Pokémon. | 당신의 포켓몬을 치료해 드리겠습니다. |
| 418 Gran Hotel Luminalia | 19·49, 19·50, 19·51, 19·77, 19·107 | Anturia / Arrayán / Cendera / Hibis / Rúpico / Siempreviva | voice-prompts / voice-prompts / voice-prompts / voice-prompts / voice-prompts / voice-prompts | ¡Recibes 3 <b>Puntos Batalla</b>! | <b>배틀포인트</b> 3점을 획득했습니다! |
| 418 Gran Hotel Luminalia | 19·104, 19·105, 19·132 | Anturia / Cendera / Hibis / Rúpico / Siempreviva | voice-prompts / voice-prompts / voice-prompts / voice-prompts / voice-prompts | ¿Quieres continuar con los combates? | 배틀을 계속하시겠습니까? |
| 488 El Arma Definitiva | 33·19, 33·123 | Malvo / del linaje Rojo | voice-prompts / voice-prompts | ¡...! | ...! |

## 화자가 등재에 없다 (26묶음)

| 맵 | 자리 (이벤트, 명령) | 화자 | 등재 | 원문 | 현행 |
|---|---|---|---|---|---|
| 20 Bastión Pokémon | 11·17, 12·17, 13·17, 14·17, 15·17, 16·17, 17·17, 18·17, 19·17 | Mosquetera / Mosquetero | 없음 / 없음 | Bien hecho, Aspirante. Pero quiero que recuerdes algo. | 훌륭합니다, 후보생님. 하지만 한 가지 명심하십시오. |
| 20 Bastión Pokémon | 7·2, 8·2, 9·2 | Mosquetera / Mosquetero | 없음 / 없음 | Elige sabiamente... ¡o tendrás que enfrentarte a una versión más temible de mí! | 현명하게 선택해라... 그렇지 않으면 더 무서운 내 모습을 마주하게 될 테니! |
| 20 Bastión Pokémon | 11·6, 12·6, 14·6, 15·6, 17·6, 18·6 | Mosquetera / Mosquetero | 없음 / 없음 | Has elegido... mal. | 틀린... 답입니다. |
| 20 Bastión Pokémon | 13·6, 16·6, 19·6 | Mosquetera / Mosquetero | 없음 / 없음 | Has elegido... ¡bien! | 정답입니다! |
| 20 Bastión Pokémon | 5·0, 14·18, 15·18, 16·18 | Mosquetero / mosqueterow | 없음 / B1변형(공무·통보 문장은 B3) | La sabiduría humana se encierra por entero en estas dos palabras: ¡Confiar y esperar! | 인간의 모든 지혜는 이 두 단어에 담겨 있습니다. 바로 ‘믿음’과 ‘기다림’입니다! |
| 20 Bastión Pokémon | 4·0, 11·18, 12·18, 13·18 | Mosquetero / mosqueterow | 없음 / B1변형(공무·통보 문장은 B3) | ¡El orgullo de los que no pueden edificar es destruir! ¿Qué tipo de persona quieres ser tú? | 무언가를 창조하지 못하는 자의 자부심이란 결국 파괴에 불과합니다! 후보생님은 과연 어떤 사람이 되고 싶습니까? |
| 20 Bastión Pokémon | 6·0, 17·18, 18·18, 19·18 | Mosquetera / mosqueteraw | 없음 / B1변형 | ¡La pluma y la tinta son igual o más poderosas que la espada y la pokéball! | 펜과 잉크는 검과 몬스터볼만큼이나, 아니 그보다 더 강력하다! |
| 25 Pueblo Acrílico | 38·7, 38·15, 38·23, 41·7, 41·15, 41·23 | Luciano / Mariano | 없음 / 없음 | ¡Mamma mia! ¡Buen entrenamiento! | 맘마미아! 정말 좋은 훈련이었어! |
| 49 Casa | 4·2, 4·14 | Nácar / acrilico1 | 없음 / B2 | Me llamo <b>Nácar</b>, por cierto. ¡Es un placer! | 아 참, 제 이름은 <b>나카르</b>라고 해요. 만나서 반가워요! |
| 49 Casa | 4·1, 4·13 | Nácar / acrilico1 | 없음 / B2 | Si se te ocurre un lugar así, ¿podrías volver para avisarme? Creo que encajaría bien en una pequeña aldea. | 혹시 그런 곳이 떠오르면 다시 와서 알려주실 수 있나요? 작은 마을 같은 곳이면 잘 맞을 것 같아요. |
| 87 Bastión Pokémon | 12·0, 13·0, 14·0, 15·0, 16·0, 17·0, 18·0, 19·0, 20·0, 21·0, 22·0, 23·0, 24·0, 25·0, 26·0, 27·0, 28·0, 29·0, 30·0, 31·0, 32·0, 33·0, 34·0, 35·0, 36·0, 37·0, 38·0, 39·0, 40·0, 41·0, 42·0 | rayosAzulesV / rayosR / rayosRojosV / rayosV | 없음 / 없음 / 없음 / 없음 | ¡Una barrera eléctrica corta el paso! | 전기 장벽이 길을 막고 있다! |
| 89 Bastión Pokémon | 9·0, 10·0, 12·0, 13·0, 14·0, 15·0, 16·0, 17·0, 18·0, 19·0, 20·0, 21·0, 22·0, 23·0, 24·0, 25·0, 26·0, 27·0, 28·0, 29·0, 30·0, 31·0, 32·0, 33·0, 34·0, 35·0, 36·0, 37·0, 38·0, 39·0, 40·0, 41·0, 42·0, 43·0, 44·0, 45·0, 46·0, 47·0, 48·0 | rayosAzulesV / rayosR / rayosRojosV / rayosV | 없음 / 없음 / 없음 / 없음 | ¡Una barrera eléctrica corta el paso! | 전기 장벽이 길을 막고 있다! |
| 92 Chateau Lanto | 13·3, 14·3 | Armand / Louis | 없음 / 없음 | ¡Kiaaaaa! | 키아아아아! |
| 146 Bastión Pokémon | 5·52, 5·63, 5·74, 5·85, 5·96, 5·107, 11·52, 11·63, 11·74, 11·85, 11·96, 11·107, 12·52, 12·63, 12·74, 12·85, 12·96, 12·107, 13·52, 13·63, 13·74, 13·85, 13·96, 13·107, 14·52, 14·63, 14·74, 14·85, 14·96, 14·107, 15·52, 15·63, 15·74, 15·85, 15·96, 15·107 | Casandra / Edgard / Elvira / Elías / Keira / Selleck | 없음 / 없음 / 없음 / 없음 / 없음 / 없음 | La luna se tiñe roja sobre mí. | 내 머리 위로 달이 붉게 물들어 간다. |
| 146 Bastión Pokémon | 5·230, 5·241, 5·252, 11·230, 11·241, 11·252, 12·230, 12·241, 12·252, 13·230, 13·241, 13·252, 14·230, 14·241, 14·252, 15·230, 15·241, 15·252 | Dora / Neila / Yona | 없음 / 없음 / 없음 | ¡Regreso a la Sombra! | 그림자로의 귀환! |
| 155 Casa de Entrenamiento | 4·7, 4·15, 4·23, 5·7, 5·15, 5·23 | Evaristo / Lucrecia | 없음 / 없음 | ¡Buen entrenamiento! | 트레이닝 잘 하게! |
| 160 Ciudad Luminalia - Sur | 39·0, 39·14 | Revolucionaria / revolucionaria | 없음 / B1변형 | Espero que haya podido descansar bien estos últimos días, sé que ha tenido mucho trabajo. | 며칠간 푹 쉬셨기를 바라요. 그동안 일이 많으셨잖아요. |
| 160 Ciudad Luminalia - Sur | 39·2, 39·16 | Revolucionaria / revolucionaria | 없음 / B1변형 | Ya sabe, para negociar con la Regente de ese lugar y ganarse su apoyo a la Revolución. | 아시다시피 그곳 섭정과 협상해서 혁명을 지지하게 만들기 위해서죠. |
| 223 Prisión del Olvido | 13·3, 13·4 | Dandelio / acrilico82 | 없음 / 없음 | Así que, ¿para qué iba a querer escapar de esta isla? | 그러니 제가 이 섬에서 탈출해서 도대체 뭘 하겠어요? |
| 223 Prisión del Olvido | 13·4, 13·5 | Dandelio / acrilico82 | 없음 / 없음 | Me llamo <b>Dandelio</b>, por cierto. Antes de que me apresaran, vivía en <b>Pueblo Fresco</b>. | 참, 제 이름은 <b>단델리오</b>라고 해요. 잡혀 오기 전에는 <b>버들비마을</b>에 살고 있었어요. |
| 226 Prisión del Olvido | 25·0, 25·10 | Carabinera / carabinerow | 없음 / B2+B3(위협 시 B1변형) | El mismísimo Legislador <b>Mirra</b> te ha convocado para hablar contigo. | <b>미라</b> 입법관님께서 직접 너와 이야기를 나누고자 부르셨다. |
| 226 Prisión del Olvido | 25·1, 25·11 | Carabinera / carabinerow | 없음 / B2+B3(위협 시 B1변형) | Te está esperando en la <b>Sala de Audiencias</b>, ¡<i>dépêche-toi</i>! Dirígete ahí ahora mismo. | <b>접견실</b>에서 기다리고 계신다, <i>dépêche-toi</i>! 지금 당장 그쪽으로 가라. |
| 322 Bastión Pokémon | 25·112, 25·119, 25·126, 25·133, 25·144, 25·151, 25·158, 25·169, 25·176, 25·187 | Drumond / Hans / Vladimir / Vostok | 없음 / 없음 / 없음 / 없음 | ¡Jamás me había enfrentado a un oponente semejante! | 이런 상대와 겨뤄본 적은 단 한 번도 없었다! |
| 351 Cueva Psique | 2·15, 3·15, 4·15 | 480 / 481 / 482 | 없음 / 없음 / 없음 | ¡El Pokémon ha huido! | 포켓몬이 도망갔다! |
| 387 Maraña Oscura | 27·2, 28·2, 30·2, 31·2 | 168 / 922 | 없음 / 없음 | ¡WRYYYYYYY! | 크아아아악! |
| 388 Maraña Oscura | 15·2, 17·2, 18·2 | 168 / 922 | 없음 / 없음 | ¡WRYYYYYYY! | 크아아아악! |

## 센 법

```
# (맵, 원문) 묶음 × 자리 둘 이상 × 화자 갈림
norm = lambda s: re.sub(r'\s+', ' ', s).strip()   # 귀속표 k에 줄바꿈이 박혀 있다
# 00-maps.jsonl을 (map, norm(k)) → v로 읽고, speaker-attr.jsonl.gz를 같은 열쇠로 조인,
# 묶음 크기 2 이상이면서 {who} - {""} 의 크기가 2 이상인 것을 센다 → 153
# {who} 자체(빈 값 포함)의 크기가 2 이상이면 → 196
```

