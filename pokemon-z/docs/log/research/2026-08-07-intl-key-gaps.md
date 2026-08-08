# 번역표에 키가 없는 스크립트 문구 102종 (2026-08-07)

특성 전문가 화면에서 스페인어가 나온다는 제보를 좇다 나왔다. 그 문구는 `korean.dat`에 키
자체가 없어서 원문이 그대로 화면에 나왔다. 같은 자리가 더 있는지 전수로 셌다.

## 어떻게 셌나

게임 스크립트 265절의 `_INTL(...)` 리터럴 4,845개를 뽑아, 루비 리터럴 규칙대로 escape를
풀고(겹따옴표는 `\r\n`이 진짜 줄바꿈, 홑따옴표는 글자 그대로) `build.string_to_key`로
정규화한 뒤 절23 키 6,819개와 대조했다. 보간(`#{...}`)이 든 것과 세 글자 미만은 뺐다(182개).

재현: `uv run /tmp/gaps2.py` 꼴의 스크립트 — 절23 키 집합과 `_INTL` 리터럴을 맞대는 것이 전부다.

## 결과

**4,845개 중 102종이 번역표에 키가 없다.** 절별로는 이렇다.


| 절 | 종 | 성격 |
|---|---:|---|
| RandomMain | 29 | 랜덤라이저 메뉴 |
| PField_Field | 17 | 필드 상태이상·기절 안내 |
| PScreen_MysteryGift | 11 | 미스터리 기프트 |
| PokeBattle_BattleArena | 8 | 배틀 아레나 판정 |
| PItem_Items | 5 | 도구 사용·기술 습득 |
| PField_BerryPlants | 3 | 나무열매 |
| PScreen_EggHatching | 3 | 알 부화 |
| PMinigame_VoltorbFlip | 3 | 볼트롭 플립 |
| PSystem_Utilities NUEVO | 3 |  |
| Debug | 3 | 디버그 |
| Compiler | 3 | 컴파일 오류 |
| Pokemon_Evolution | 2 | 진화 |
| PScreen_Phone | 2 | 전화 |
| PScreen_HallOfFame | 2 | 명예의 전당 |
| Evolucion | 2 |  |
| Pokemon_MultipleForms | 1 |  |
| PScreen_Load | 1 |  |
| PScreen_PurifyChamber | 1 |  |
| PMinigame_Mining | 1 |  |
| Lente de la Verdad | 1 |  |
| Crafteo | 1 |  |

## 표본 (절별 앞 네 개)

**RandomMain**
```
  [X] Full Random
  [ ] Mapeo de habilidades
  [ ] Sin randomizar
  [ ] Full Random
```

**PField_Field**
```
  ¡{1} ha sobrevivido al envenenamiento!\ ⏎ ¡El veneno ha desaparecido!\\1
  {1} se ha desmayado...\\1
  \\w[]\\wm\\c[8]\\l[3]Tras la desafortunada derrota, {1} ha salido corriendo hacia un Centro Pokémon.
  \\w[]\\wm\\c[8]\\l[3]{1} ha salido corriendo hacia un Centro Pokémon para que su cansado y debilitado equipo P
```

**PScreen_MysteryGift**
```
  Buscando regalos en línea...\\wtnp[0]
  No se encontró ningún Regalo Misterioso en línea.\\wtnp[20]
  Regalo Misterioso en línea encontrado.\\wtnp[20]
  \\ts[]Gestionar Regalos Misteriosos (X=en línea).
```

**PokeBattle_BattleArena**
```
  ÁRBITRO: ¡{1} VS {2}! ⏎ ¡Que comience el combate!\\wtnp[20]
  ÁRBITRO: ¡Suficiente! ¡Ahora haremos las evaluaciones para determinar al ganador!\\wtnp[20]
  REFEREE: Judging category 1, Mind! ⏎ The Pokemon showing the most guts!\\wtnp[40]
  REFEREE: Judging category 2, Skill! ⏎ The Pokemon using moves the best!\\wtnp[40]
```

**PItem_Items**
```
  \\se[]¡{1} ha aprendido {2}!\\se[MoveLearnt]
  \\se[]1,\\wt[16] 2, y\\wt[16]...\\wt[16] ...\\wt[16] ... ¡Puf!\\se[balldrop]
  \\se[]{1} ha olvidado cómo usar {2}. Y... ¡{1} ha aprendido {3}!\\se[MoveLearnt]
  \\se[accesspc]MO iniciada.
```

**PField_BerryPlants**
```
  Has cosechado {1} bayas del arbusto de {2}.\\wtnp[30]
  Has cosechado una baya del arbusto de {1}.\\wtnp[30]
  {1} ha regado bien la tierra y ahora es más fértil.\\wtnp[40]
```

**PScreen_EggHatching**
```
  \\se[]¡{1} ha salido del huevo!\\wt[80]
  ...\1
  ... .... .....\1
```

**PMinigame_VoltorbFlip**
```
  \\me[Voltorb Flip Game Over]¡Oh no! ¡Terminaste con 0 Monedas!\\wtnp[50]
  \\se[VoltorbFlipLevelDown]Bajó a juego Nv. {1}!
  \\me[Voltorb Flip Win]¡Mesa limpia!\\wtnp[40]
```

**PSystem_Utilities NUEVO**
```
  ¡{1} ha obtenido un {2}!\\se[PokemonGet]\1
  {1} ha recibido un Pokémon de {2}.\\se[PokemonGet]\1
  {1} ha recibido un Pokémon.\\se[PokemonGet]\1
```

**Debug**
```
  Por favor, espera.\\wtnp[0]
  Todos los textos del juego se extrajeron y se guardaron en intl.txt.\1
  Para localizar el texto en un idioma en particular, traduzca todas las segundas líneas de cada par en el archi
```

**Compiler**
```
  \\G¡Aquí tienes!
  \\GNo tienes más espacio en la Mochila.
  \\GNo tienes el dinero suficiente.
```

**Pokemon_Evolution**
```
  \\se[]¡Oh, dios mío! ⏎ ¡{1} está evolucionando!\\^
  \\se[]¡Felicidades! ¡Tu {1} ha evolucionado en {2}!\\wt[80]
```

**PScreen_Phone**
```
  ......\\wt[5] ......\\1
  ¡Clic!\\wt[10] ⏎ ......\\wt[5] ......\\1
```

**PScreen_HallOfFame**
```
  ¡Te has hecho con la victoria!\\^
  \\se[accesspc]Acceso al Hall de la Fama concedido.
```

**Evolucion**
```
  \\se[]¡Mon Dieu! ⏎ ¡{1} está evolucionando!\\^
  \\se[]¡Enhorabuena! ¡Tu {1} ha evolucionado en {2}!\\wt[80]
```

**Pokemon_MultipleForms**
```
  \\se[]1,\\wt[4] 2,\\wt[4] y...\\wt[8] ...\\wt[8] ...\\wt[8] ¡Puf!\\se[balldrop]\1
```

**PScreen_Load**
```
  Borrando partida... ⏎ No cierres el juego...\\wtnp[0]
```

**PScreen_PurifyChamber**
```
  \\se[accesspc]Acceso a la Cámara de Purificación concedido.
```

**PMinigame_Mining**
```
  Un {1} fue obtenido.\\se[MiningItemGet]\\wtnp[30]
```

**Lente de la Verdad**
```
  ¡\\PN usó Lente de la Verdad!
```

**Crafteo**
```
  Guardas {1} en\ ⏎ el bolsillo <icon=bagPocket{2}>\\c[1]{3}\\c[0].
```

## 손대는 법

`translate/ko/23-script-texts.add.jsonl`에 `{"k": 원문, "v": 번역, "src": 절이름}`으로 얹고
빌드한 뒤 `export.py`로 본문에 접는다(오늘 특성 전문가 문구 셋을 그렇게 넣었다).

⚠ 제어열이 섞인 줄이 많다 — `\\se[…]`·`\\wt[16]`·`\\w[]`·`\\c[8]`·`\\l[3]`·`\\1`.
소리·대기·창 모양을 지시하는 것이라 **위치를 그대로 두고 사이의 말만 옮겨야** 한다.
번호 자리(`{1}`·`{2}`)도 순서를 지킨다.

