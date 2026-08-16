# 전투 종료 대사 357행이 시야에 든 뒤 — 사람이 볼 목록 (2026-08-16)

Z-60 구현으로 `pbTrainerBattle`의 셋째 인자 대사가 귀속표에 들어왔다. 귀속표는
19,310행에서 19,834행이 됐고(+524), 정본 기준 357행이 새로 시야에 들었다. 이 문서는
그 뒤에 사람이 판정할 자리를 모은 것이다 — 말투가 어긋나 보이는 자리와, 층이 지문·
시스템(N)으로 잡힌 70행.

무엇으로 쟀나. 화자는 호출 인자(`PBTrainers::<직함>`, `"<이름>"`)에서 그대로 왔고
근거는 `how="전투호출"`이다. 평소 급은 `register.py`의 방식 그대로 **이름표가 붙은
줄(`how="태그"`)만** 세어 정했다 — 전투 대사는 평소 급 계산에 안 들어간다.
급 판정은 같은 파일의 `axis()`(존대/하대 두 축)를 썼다.

재현. 귀속표를 다시 만들고(`cd translate && uv run speaker.py scan` → 19,834행) 전투
갈래만 세면 522가 나온다.

```sh
cd translate && uv run python -c "import gzip,json; \
rows=[json.loads(l) for l in gzip.open('data/speaker-attr.jsonl.gz','rt',encoding='utf-8')]; \
print(sum(1 for r in rows if r['how']=='전투호출'))"
```

어긋남 표는 `register.py`의 `dominant()`(평소 급)와 `axis()`(그 줄의 급)를 그대로
불러 `how="전투호출"` 행에 견준 것이다. `uv run register.py scan`도 이제 이 행들을
검사하지만, 그쪽은 표본 3줄 미만·평소 비율 0.7 미만·이중말투를 빼고 세어 일곱 자리만
남긴다. 이 문서는 유지자가 직접 보라는 목록이라 그 걸름망을 걷고 열다섯을 다 실었다.

## 1. 말투가 어긋나 보이는 자리

522개 전투 대사 중 화자의 평소 급이 잡히는 것은 **119행**이고, 그중 **15행**이 평소
급과 어긋난다. 15행은 인물·문구로 접으면 **11묶음**이다(같은 대사가 여러 이벤트에
복제된 자리가 있다 — 정본은 한 줄이라 고치면 함께 바뀐다).

⚠ 어긋남은 관측이지 처방이 아니다. 아래 네 부류가 섞여 있다.

- **어미를 고칠 자리** — 존대로 일관하던 인물이 전투 종료 대사에서만 반말이 된다.
  볼프람이 그 전형이다(평소 존대 0.85, 54줄).
- **원문이 실제로 격을 바꾸는 자리** — 패배 순간 가면이 벗겨지는 연출이면 원문도
  격을 바꾼다. 란토 맵190(미르 궁전)은 원문이 대문자 절규(`¡TE ODIO CON TODAS LAS CÉLULAS…`)라
  한국어 반말이 오히려 맞다.
- **반대 방향으로 어긋난 자리** — 아우레와 사프라는 평소 하대인데 전투 대사만
  존대다. 아우레의 원문은 `sois`·`merecéis`로 여전히 상대를 낮춰 부르는데 번역만
  합쇼체가 됐다. 아우레는 이중말투 명단이라 지금 검사에는 안 걸린다.
- **평소 급 자체가 갈리는 자리** — 히비스(0.51)·미미(0.5)는 이름표 줄부터 존대와
  하대가 반반이라 「평소 급」이라 부를 것이 없다. 이 둘은 어긋남의 근거가 약하다.

이중말투가 정체성이라 `register.py`가 검사에서 빼는 인물(란토·센데라·아우레)은 표에
표시했다. 지금 상태로도 검사에 안 걸리는 자리다.

| 자리 | 인물 | 직함 | 평소 급 | 이 대사 | 이중말투 명단 |
|---|---|---|---|---|---|
| 맵90(백단 아카데미) ev38 p2:93 | 볼프람(Wolfram) | 아조스단 연금술사 | 존대 0.85(54줄) | 하대 | 아니오 |
| 맵90(백단 아카데미) ev40 p2:91 | 볼프람(Wolfram) | 아조스단 연금술사 | 존대 0.85(54줄) | 하대 | 아니오 |
| 맵90(백단 아카데미) ev35 p2:92 | 볼프람(Wolfram) | 아조스단 연금술사 | 존대 0.85(54줄) | 하대 | 아니오 |
| 맵90(백단 아카데미) ev41 p2:92 | 볼프람(Wolfram) | 아조스단 연금술사 | 존대 0.85(54줄) | 하대 | 아니오 |
| 맵112(란토 저택) ev4 p0:254 | 란토(Lanto) | 무슈 | 존대 0.77(132줄) | 하대 | 예 — 검사 밖 |
| 맵166(카두코 구호소) ev4 p0:24 | 볼프람(Wolfram) | 아조스단 연금술사 | 존대 0.85(54줄) | 하대 | 아니오 |
| 맵190(미르 궁전) ev77 p0:93 | 란토(Lanto) | 무슈 | 존대 0.77(132줄) | 하대 | 예 — 검사 밖 |
| 맵266(어둠의 탑) ev28 p0:81 | 히비스(Hibis) | 섭정 | 존대 0.51(55줄) | 하대 | 아니오 |
| 맵266(어둠의 탑) ev28 p1:56 | 히비스(Hibis) | 섭정 | 존대 0.51(55줄) | 하대 | 아니오 |
| 맵322(포켓몬 요새) ev1 p0:51 | 센데라(Cendera) | 섭정 | 존대 0.77(26줄) | 하대 | 예 — 검사 밖 |
| 맵378(천막) ev13 p1:18 | 미미(Mimi) | 타로술사 | 존대 0.5(10줄) | 하대 | 아니오 |
| 맵418(미르 그랜드 호텔) ev19 p0:54 | 히비스(Hibis) | 섭정 | 존대 0.51(55줄) | 하대 | 아니오 |
| 맵418(미르 그랜드 호텔) ev19 p3:14 | 사프라(Zafra) | 섭정 | 하대 1.0(33줄) | 존대 | 아니오 |
| 맵424(마스터타워) ev5 p0:201 | 콘콤부르(Cornelio) | 수도승 스승 | 존대 0.89(9줄) | 하대 | 아니오 |
| 맵488(최종병기) ev24 p0:38 | 아우레(Aure) | 영원의 왕 | 하대 0.57(87줄) | 존대 | 예 — 검사 밖 |

#### 볼프람(Wolfram) — 맵90(백단 아카데미) ev38 p2:93 · 맵90(백단 아카데미) ev40 p2:91 · 맵90(백단 아카데미) ev35 p2:92 · 맵90(백단 아카데미) ev41 p2:92

같은 대사가 4자리에 복제돼 있다. 정본은 한 줄이라 고치면 함께 바뀐다. 아래는 첫 자리의 페이지다.

평소 존대 0.85(54줄) · 이 대사 하대 · 장면 컷신 · 페이지 층 PS · 그림 `없음` · 직함 `WOLFRAM1`(아조스단 연금술사)

- (앞 2줄 생략)
- `31` 아! <i>Merde</i>! 문을 닫는 걸 깜빡했군!
  - es: ¡Ah! ¡<i>Merde</i>! ¡Había olvidado cerrar la puerta!
- … 다른 화자 4줄 생략
- `58` 조용히 하세요! 이것 때문에 엄청난 골칫거리가 생겼잖아요...
  - es: ¡Silencio! Esto me acaba de meter en un buen lío...
- `90` <b>사핀</b>의 문서를 <b>아조스단</b>에 넘기기만 하면 평생 팔자를 고칠 수 있었는데, 그런데 이제...
  - es: Solo tenía que venderle los documentos de <b>Sapin</b> al <b>Team Azoth</b> y mi vida estaría solucionada para siempre, pero ahora...
- `91` 어쩔 수 없군요, 당신 입을 확실하게 봉해 드려야겠습니다!
  - es: No me dejas otra salida, ¡tendré que asegurarme tu silencio y discreción!
- `93` **[전투 종료 대사]** 내가 긴장해서 진 것뿐이다! 마음만 먹으면 널 짓밟아 버릴 수 있다고!
  - es: ¡Solo me has derrotado porque estaba nervioso! ¡Que conste que te doy mil patadas en todo!
- … 다른 화자 3줄 생략
- `131` 죄... 죄송합니다! 빚이 산더미처럼 쌓여 있어서 어쩔 수 없었어요!
  - es: ¡Lo... lo siento! ¡Es que estoy hasta arriba de deudas!
- `132` <b>아조스단</b>이 그 문서의 대가로 엄청난 거금을 약속했단 말입니다.
  - es: El <b>Team Azoth</b> me ha pagado una inmensa cantidad de dinero por los documentos.
- (뒤 7줄 생략)

#### 란토(Lanto) — 맵112(란토 저택) ev4 p0:254

평소 존대 0.77(132줄) · 이 대사 하대 · **이중말투 명단이라 지금도 검사 밖** · 장면 컷신 · 페이지 층 PS · 그림 `없음` · 직함 `LANTO1`(무슈)

- (앞 15줄 생략)
- `192` 그런데 그분이 나타나 제게 색다른 것을 보여주셨죠! 그토록 불가능하고... 아름다운 꿈을... 제게 다시 감정을 느끼게 해 준 꿈을요!
  - es: Pero entonces aparece ella... ¡y me ofrece algo distinto! ¡Un sueño tan imposible... tan bello... con el que vuelvo a sentir algo!
- … 다른 화자 13줄 생략
- `236` \c[0] 이 머리 나쁜 멍청이들은 절대 이해하지 못할 겁니다. 제가 장난감처럼 싹 부숴버리게 해주십시오!
  - es: \c[0] Estos zotes de mente obtusa jamás lo entenderán. ¡Permítame romperlos como si fueran mis juguetitos!
- … 다른 화자 2줄 생략
- `253` \c[0] <i>Merci beaucoup</i>! 우선 \PN, 당신과 신나게 놀아볼까요!
  - es: \c[0] ¡<i>Merci beaucoup</i>! ¡Voy a empezar divirtiéndome con \PN!
- `254` **[전투 종료 대사]** 뭐라고?! 이게 무슨 소리야?! 네가 내 장난감이 되어야 한단 말이다!
  - es: ¡¿Cómo?! ¡¿Qué significa esto?! ¡Se supone que tienes que ser mi juguete!
- `265` \c[0] 어떻게... 어떻게...!
  - es: \c[0] ¡Pero... pero...!
- `266` \sh비열한 쓰레기 주제에 감히 내 저택에서 나에게 수치심을 주다니?
  - es: \sh¿CÓMO TE ATREVES A HUMILLARME EN MI PROPIA CASA, ESCORIA MISERABLE?
- `267` 내 가문의 모든 것을 걸고 맹세하건대, 널 가만두지...!
  - es: ¡Te juro por todo mi linaje que te voy a...!
- (뒤 10줄 생략)

#### 볼프람(Wolfram) — 맵166(카두코 구호소) ev4 p0:24

평소 존대 0.85(54줄) · 이 대사 하대 · 장면 컷신 · 페이지 층 PS · 그림 `없음` · 직함 `WOLFRAM2`(아조스단 연금술사)

- `20` 아악! 또 당신이군요!
  - es: ¡Aah! ¡Eres tú otra vez!
- `21` 왜 제 뒤에서 나타나는 건가요? 저를 놀라게 하려던 건가요?
  - es: ¿Por qué apareces por mi espalda? ¿Pretendías asustarme?
- `22` 유감스럽지만 이번엔 <b>백단시티</b> 때처럼 되진 않을 거랍니다. 이번에 제 덫에 걸려든 건 바로 당신이라고요!
  - es: Pues siento decirte que esto no será como en <b>Ciudad Novarte</b>, ¡esta vez eres tú el que ha caído en mis redes!
- `24` **[전투 종료 대사]** 말도 안 돼! 내 계략은 네 포켓몬 팀을 전멸시키도록 설계된 거였는데!
  - es: ¡Imposible! ¡Mis artimañas habían sido diseñados para acabar con tu equipo Pokémon!

#### 란토(Lanto) — 맵190(미르 궁전) ev77 p0:93

평소 존대 0.77(132줄) · 이 대사 하대 · **이중말투 명단이라 지금도 검사 밖** · 장면 컷신 · 페이지 층 PS · 그림 `없음` · 직함 `LANTO2`(무슈)

- (앞 2줄 생략)
- `73` \c[0] 이 궁전 전체와 왕가 녀석들이 똥더미가 됐을 때, 그 위에 처음으로 올라가서 소리칠 수탉은 바로 나다.
  - es: \c[0] Cuando todo este palacio y la familia real queden reducidos a un montón de estiércol, yo seré el gallo que se sube encima para cacarear.
- `80` \c[0] 그건 그렇고, 이번엔 너희를 지켜줄 그 꼬마 친구도 없는 모양이구나.
  - es: \c[0] En cualquier caso, veo que ahora ya no está vuestra amiguita para defenderos.
- `81` 알아둬, 난 예전의 <i>무슈</i> <b>란토</b>가 아니라는 걸. <b>알카</b> 님 밑에서 단련을 쌓았거든.
  - es: Tenéis que saber que ya no soy el <i>monsieur</i> <b>Lanto</b> de siempre. He entrenado con mi señora <b>Alca</b>.
- `82` 그러니 이제 남은 건...
  - es: Lo cual me lleva a lo siguiente...
- `89` \sh\c[2]<b>란토:</b>\c[0] 내 마음대로 너희를 짓밟고 흔적도 없이 없애버리는 것뿐이다! 지금 여기서!
  - es: \sh\c[2]<b>Lanto:</b>\c[0] ¡Pienso profanaros y obliteraros como me plazca! ¡Aquí y ahora!
- `93` **[전투 종료 대사]** 안 돼! 안 돼! 그만 좀 이겨! 내 온몸의 세포 하나하나가 너를 증오해!
  - es: ¡NO! ¡NO! ¡Deja de ganarme! ¡TE ODIO CON TODAS LAS CÉLULAS DE MI CUERPO!
- `130` \sh\c[2]<b>란토:</b>\c[0] 그만! 당장 그만해!
  - es: \sh\c[2]<b>Lanto:</b>\c[0] ¡BASTA! ¡YA BASTA!
- `131` 이런 역겨운 쓰레기들한테 두 번 다시 질 순 없어!
  - es: ¡No pienso volver a perder contra tan repugnante escoria!
- `132` 내 포켓몬들이 쓰러졌어도... 그놈들 없이 내 손으로 해내 주마!
  - es: Aunque mis Pokémon queden fuera de combate... ¡me las puedo apañar sin ellos!
- (뒤 7줄 생략)

#### 히비스(Hibis) — 맵266(어둠의 탑) ev28 p0:81 · 맵266(어둠의 탑) ev28 p1:56

같은 대사가 2자리에 복제돼 있다. 정본은 한 줄이라 고치면 함께 바뀐다. 아래는 첫 자리의 페이지다.

평소 존대 0.51(55줄) · 이 대사 하대 · 장면 컷신 · 페이지 층 PS · 그림 `없음` · 직함 `LIDER7`(섭정)

- (앞 11줄 생략)
- `31` \c[0] 나는 <b>역전 배틀</b> 분야에서 몇 안 되는 전문가 중 한 명이다.
  - es: \c[0] Soy uno de los pocos especialistas que existen en el arte de los <b>combates inversos</b>.
- `45` \c[0] 그렇다. <b>역전 배틀</b>이란 타입의 약점과 내성이 반대로 뒤바뀌는 배틀이지.
  - es: \c[0] Así es. Un <b>combate inverso</b> es aquel en el que las debilidades y resistencias de tipos se invierten.
- `46` 그런데도 내게 도전하겠는가? 아니면 준비할 시간이 몇 분 더 필요한가?
  - es: Aún así, ¿quieres desafiarme? ¿O necesitas unos minutos más para prepararte?
- … 다른 화자 2줄 생략
- `62` \c[0] 나중에 경고하지 않았다고 하지 마라.
  - es: \c[0] Luego no digas que no te lo advertí.
- `81` **[전투 종료 대사]** 뭐라고? 내 메가진화의 힘으로도 부족했단 말인가? 대체 정체가 무엇이냐?
  - es: ¿Cómo? ¿El poder de mi megaevolución no fue suficiente? ¿Quién eres exactamente?
- `100` \c[0] 내 계산이 너를 과소평가했던 것이 분명하구나.
  - es: \c[0] Está claro que mis cálculos te habían subestimado.
- `101` 나는 여전히 섭정이니, 이제 배지를 내주어야 할 때겠지?
  - es: Sigo siendo un Regente, ahora es cuando tengo que darte la medalla, ¿verdad?
- `102` 아깝군! 배지의 기묘한 문양이 내 초능력을 증폭하는 데 유용했거늘.
  - es: ¡Una lástima! Su extraño grabado me estaba sirviendo para amplificar mis poderes psíquicos.
- (뒤 14줄 생략)

#### 센데라(Cendera) — 맵322(포켓몬 요새) ev1 p0:51

평소 존대 0.77(26줄) · 이 대사 하대 · **이중말투 명단이라 지금도 검사 밖** · 장면 컷신 · 페이지 층 PS · 그림 `cenderaow` · 직함 `LIDER10`(섭정)

- … 다른 화자 9줄 생략
- `51` **[전투 종료 대사]** 말도 안 돼...! 내가 패배하다니, 그것도 내 영지에서! 이래서 입법관 님이 너를 그토록 두려워했던 건가?
  - es: ¡Es... es imposible! ¡Jamás había sido derrotada y menos en mi propio terreno! ¿Es por esto que el Legislador te teme tanto?
- … 다른 화자 24줄 생략

#### 미미(Mimi) — 맵378(천막) ev13 p1:18

평소 존대 0.5(10줄) · 이 대사 하대 · 장면 컷신 · 페이지 층 PS · 그림 `없음` · 직함 `TAROTISTA`(타로술사)

- `6` 내... 내 카드를 찾아다 준 거야?
  - es: ¿Has... has conseguido mis cartas?
- `14` <i>Bon</i>, 이제 내-내가 저지른 이 실수를 목격한 증인을 없애기만 하면 돼.
  - es: <i>Bon</i>, ahora so-solo tengo que eliminar a los testigos de este estropicio que he ca-causado.
- `15` 나-너무 나쁘게 생각하진 마, 하지만... 널 어-없애는 수밖에 없어!
  - es: No te lo to-tomes a mal, pero... ¡No me que-queda más remedio que eliminarte!
- `16` 울-울 준비나 해!
  - es: ¡Prepárate pa-para llorar!
- `18` **[전투 종료 대사]** 안 돼! 날 울리다니!
  - es: ¡Nooo! ¡Me has hecho llorar!
- `29` 흑흑! 내 서커스 인생은 끝이야! <b>시엠프레비바</b> 스승님의 제자가 되려고 얼마나 고생했는데.
  - es: ¡Snif! ¡Se acabó mi carrera circense! Con lo que me había costado convertirme en aprendiz de la maestra <b>Siempreviva</b>.
- `30` 솔직히 말하면 여기 온 뒤로 불행한 일만 계속 일어나긴 했어. 게다가 더 피곤하고, 병에도 자주 걸리는 것 같거든.
  - es: Aunque, para ser sincera, desde que estoy aquí no paran de ocurrirme desgracias. Y a demás me noto más cansada, y me pongo enferma más veces.
- `35` 기후가 더 건강에 좋은 곳을 찾아보는 게 좋을지도 모르겠어. 바닷가 같은 곳...
  - es: Supongo que podría buscar un lugar con un clima más sano. A la orilla del mar...
- (뒤 2줄 생략)

#### 히비스(Hibis) — 맵418(미르 그랜드 호텔) ev19 p0:54

평소 존대 0.51(55줄) · 이 대사 하대 · 장면 컷신 · 페이지 층 PS · 그림 `carabinerow` · 직함 `LIDER7R`(섭정)

- … 다른 화자 2줄 생략
- `39` 내가 아직 네 상대가 되지 못하는구나. 하지만 언젠가 형세를 뒤집기 위해 계속 검무를 연마하겠다.
  - es: Sigo sin ser rival para ti. Pero seguiré practicando la danza de la espada para cambiar las tornas algún día.
- … 다른 화자 1줄 생략
- `51` 어떤 왕과 시골 농부들이 <b>칼로스</b> 땅을 채우든, 정신을 탐구하고자 하는 나의 열망은 결코 변하지 않을 것입니다.
  - es: Da igual qué reyes y campesinos pueblan las tierras de <b>Kalos</b>, mi deseo por el estudio de la mente seguirá intacto.
- `52` 특히 \PN, 그대처럼 명석한 정신에는 여전히 흥미가 끌리는군요. 지난번에는 내 손을 벗어났지만, 이번엔 아주 다를 겁니다.
  - es: En especial me sigue interesando una mente tan preclara como la tuya, \PN. Me eludiste a última vez, pero ahora será muy distinto.
- `54` **[전투 종료 대사]** 네 마음은 여전히 내 손가락 사이로 연기처럼 빠져나가는구나. 참으로 설명할 수 없는 현상이다.
  - es: Tu mente se me sigue escapando como humo entre las manos. Es un fenómeno inexplicable.
- `62` 나의 연구와 실험이 필요한 곳이라면 어디든 계속 기여할 생각입니다. 언젠가 모든 것을 이해하고, 나아가 지배할 수 있게 될 날이 오겠지요.
  - es: Seguiré aportando mis estudios y experimentos allá donde se requieran. Algún día podré comprenderlo todo, y por tanto también controlarlo.
- `77` <b>배틀포인트</b> 3점을 획득했습니다!
  - es: ¡Recibes 3 <b>Puntos Batalla</b>!
- `80` 당신의 포켓몬을 치료해 드리겠습니다.
  - es: Vamos a curar a tus Pokémon.
- (뒤 3줄 생략)

#### 사프라(Zafra) — 맵418(미르 그랜드 호텔) ev19 p3:14

평소 하대 1.0(33줄) · 이 대사 존대 · 장면 컷신 · 페이지 층 PS · 그림 `carabinerow` · 직함 `LIDER4R`(섭정)

- `11` 꺄아! 다시 만나서 정말 기뻐, \PN! 내 식당은 그 어느 때보다 잘되고 있고 곧 이 지방 다른 곳에도 지점을 낼 거지만, 배틀할 시간은 언제든 뺄 수 있어!
  - es: ¡Aaay! ¡Qué ilusión me hace volver a verte, \PN! A mi restaurante le va mejor que nunca y pronto abriré en otros puntos de la región, pero siempre saco tiempo para un buen combate.
- `13` 이번엔 내가 어떤 걸 준비해 왔는지 볼래?
  - es: ¿Quieres ver lo que te he cocinado esta vez?
- `14` **[전투 종료 대사]** 배틀도 요리와 같아서, 감동을 끌어내려면 재료의 양과 질을 정교하게 조율할 줄 알아야 해요.
  - es: Los combates, al igual que la cocina, consisten en saber mezclar los ingredientes en cantidad y calidad para provocar emociones.
- `21` 식당에 더 자주 들러 줘, 알았지? 적어도 날 보러라도 와. 넌 내 마음속 영원한 특별 손님이니까!
  - es: Pásate más de vez en cuando por el restaurante, ¿vale? Al menos para venir a verme. Siempre serás un comensal especial en mi corazón.
- … 다른 화자 2줄 생략
- `27` 내 마음속 빙산을 깨부수다니 칭찬할 만합니다. 대적자로서 당신을 인정하겠습니다.
  - es: Resquebrajar el iceberg que tengo por corazón es muy meritorio. Tienes mi respeto como oponente.
- (뒤 1줄 생략)

#### 콘콤부르(Cornelio) — 맵424(마스터타워) ev5 p0:201

평소 존대 0.89(9줄) · 이 대사 하대 · 장면 컷신 · 페이지 층 PS · 그림 `meliaTS` · 직함 `GRANMONJE`(수도승 스승)

- (앞 13줄 생략)
- `176` 그리고 <b>알카</b>는 우리에게 그 길을 보여주었습니다!
  - es: ¡Y <b>Alca</b> nos ha mostrado el camino para hacerlo!
- `177` 공격하십시오!
  - es: ¡Atacadles!
- `180` 용서하십시오, 콘콤부르 스승님!
  - es: ¡Perdóname, Maestro Cornelio!
- `188` 용서하십시오, 콘콤부르 스승님!
  - es: ¡Perdóname, Maestro Cornelio!
- `200` \sh<b>콘콤부르:</b> 새로운 세상은 우리의 것이다! 당장 무릎을 꿇어라!
  - es: \sh<b>Cornelio:</b> ¡El nuevo mundo nos pertenece a nosotros! ¡Postraos ahora mismo!
- `201` **[전투 종료 대사]** 말도 안 돼! 우리가 더 우월하고, 더 진화했거늘!
  - es: ¡Imposible! ¡Somos mejores, más evolucionados!
- `209` 말-말도 안 돼! <b>얀트라 교단</b>은... 영원하다! 우리는 전설의 포켓몬에게 선택받은 자들이다!
  - es: ¡Im-imposible! ¡La <b>Orden Yantra</b>... es eterna! ¡Somos los elegidos de los Pokémon legendarios!
- … 다른 화자 2줄 생략

#### 아우레(Aure) — 맵488(최종병기) ev24 p0:38

평소 하대 0.57(87줄) · 이 대사 존대 · **이중말투 명단이라 지금도 검사 밖** · 장면 컷신 · 페이지 층 PS · 그림 `aureow2` · 직함 `ALTOMANDOF2`(영원의 왕)

- (앞 1줄 생략)
- `27` \c[0] 나의 새로운 영역에 온 것을 환영하마! 저 <b>알카</b> 녀석이 이 안에 나만의 공방을 지을 수 있도록 허락해 주었거든.
  - es: \c[0] ¡Te doy la bienvenida a mis nuevos dominios! Esa <b>Alca</b> me ha concedido el permiso para construir mi propio taller aquí dentro.
- `29` 하지만 그 녀석의 생색이 녀석 자신의 파멸을 부를 것이다! 이 안에서 녀석을 무찌를 새로운 장치를 만들어낼 생각이니까. 그리고 나 자신이 직접 <b>최종병기</b>와 그 신성한 힘을 지배하겠다!
  - es: ¡Pero su condescendencia será su perdición! Pues aquí dentro pienso forjar un nuevo artefacto que me permitirá derrotarla. ¡Y entonces yo mismo tomaré el control del <b>Arma Definitiva</b> y de sus poderes divinos!
- `31` 이 가련한 세상에 혼돈을 풀어놓을 테다. 분쟁, 무질서, 엔트로피... 그 모든 것이 강자들을 오르게 하고 우리를 진정으로 진화시킬 것이다.
  - es: Pienso desatar el caos en este infeliz mundo. Conflicto, desorden, entropía... Todo ello permitirá que los más fuertes se impongan y evolucionemos de forma verdadera.
- `33` 태초부터 지가르데가 우리를 복종시키려 했던 이 조화와 균형이란... 세상의 흐름을 정체시키고 새로운 시대의 탄생을 가로막는 함정에 불과하지.
  - es: Esta armonía, este equilibrio al que nos ha intentado someter Zygarde desde los albores de los tiempos... No es más que una trampa para estancar el curso de las cosas y permitir el nacimiento de nuevas eras.
- `35` 인간의 무지함 속에 갇힌 <b>알카</b>는 그걸 알지 못한다. 그렇기에 녀석은 실패할 것이고, 나 <b>아우레</b>는 너희 모두의 위에 서게 될 것이다!
  - es: Eso es algo que <b>Alca</b>, en su supina ignorancia humana, desconoce. ¡Y por eso fracasará mientras que yo, <b>Aure</b>, me alzaré sobre todos vosotros!
- `38` **[전투 종료 대사]** 신의 거처에서조차 신에게 감히 도전하다니, 그 오만함은 어디까지입니까? 너희 인간들은 비열하기 짝이 없으니 심연 속으로 던져져야 마땅합니다!
  - es: ¿Hasta dónde llega tu arrogancia que te permites incluso desafiar a un dios en su propia casa? ¡Los seres humanos sois despreciables y merecéis ser arrojados al abismo!
- `47` \c[0] 너에게 느끼는 이 경멸을 표현할 단어는 인간의 언어에도, 포켓몬의 언어에도 존재하지 않는다. 미개한 놈! 겁쟁이 녀석!
  - es: \c[0] No existen palabras en lengua humana o Pokémon para expresar el desprecio que te tengo. ¡Salvaje! ¡Pusilánime!
- `48` 그렇다고 이 정도 찰나의 상심 때문에 멈출 생각은 없다. <b>알카</b>가 내 의도를 눈치채지 못하는 한 내 계획은 얼마든지 계속 꾸며나갈 수 있으니까.
  - es: Igualmente no pienso detenerme por una contrariedad de este calibre. Puedo seguir maquinando mis planes mientras <b>Alca</b> no descubra mis intenciones.
- `50` 인간이란 이래서 좋다니까, 어처구니없는 거짓말에도 언제나 다시 속아 넘어가 주니 말이다! 크크크!
  - es: Eso es lo bueno de los seres humanos, ¡siempre se les puede volver a engañar con cualquier tontería! ¡Je, je, je!
- (뒤 3줄 생략)

## 2. N층 70행 — 21페이지를 열어 봤다

전투 대사 524행의 층은 PC 285 · PS 169 · **N 70**이다. N은 「지문·시스템」 자리라
사람 말이 거기 있으면 결함이다. 21페이지를 전부 열어 봤다.

| 자리 | 그림 | 행 | 무엇 |
|---|---|--:|---|
| 맵146(포켓몬 요새) ev5·11·12·13·14·15 p0 | 없음 | 54 | 사냥꾼·치유사·마녀 아홉과 잇달아 싸우는 자리. 전부 사람 말 |
| 맵234(15번도로) ev14·15·18·20 p0 | 없음 | 4 | 레인저 넷의 패배 대사. 전부 사람 말 |
| 맵237(16번도로) ev5·7 p0 | 없음 | 2 | 레인저 둘의 패배 대사. 전부 사람 말 |
| 맵303(끝의 동굴) ev44 p0 | `235` | 2 | 지니아의 대사. 이벤트 그림이 루브도(전국도감 235번) |
| 맵263(어둠의 탑 P0) ev46 p0~p5 | `trchar00N_5` | 6 | 도플갱어. 원문이 `...` 하나뿐 |
| 맵262(어둠의 탑 P2) ev27 p0 | 없음 | 1 | 자루 괴물. 원문이 `¡...!` |
| 맵261(기남 여관) ev19 p0 | `flecha` | 1 | 악몽 속 괴물. 원문이 `a xd`(제작자 낙서) |

**70행 중 62행이 사람 말이다.** 나머지 여덟은 말줄임표와 낙서라 번역할 것이 없다.
N 판정 자체가 틀린 것은 아니다 — 그 판정은 **페이지**에 붙는 것이고, 페이지에는 사람
그림도 이름표도 없다. 다만 전투 대사는 층과 무관하게 화자가 호출 인자로 확정되므로,
**이 행들에 한해서는 `cls="N"`을 「화자 없음」으로 읽으면 안 된다.**

### 그림이 없는 열세 페이지

`@character_name`이 비었고 `@tile_id`도 0이며 `@trigger`가 1(플레이어 접촉)이다
(맵146(포켓몬 요새) 여섯 · 맵234(15번도로) 넷 · 맵237(16번도로) 둘 · 맵262(어둠의 탑 P2) 하나를 하나하나 확인했다). 눈에 보이는
그림이 없는 **밟으면 발동하는 자리**다 — 플레이어가 그 칸을 밟으면 대사가 뜨고
전투가 시작된다. 그림이 없으니 `person_sprite()`가 사람으로 볼 재료가 애초에 없다.

### 표본 — 맵146(포켓몬 요새) ev5(사냥터)

아홉 명과 잇달아 싸우는 자리다. 도전 대사 하나에 전투 종료 대사가 아홉이라, 종료
대사는 사람마다 다르지 않고 직함별로 한 벌씩만 있다.

- `50` 앞으로 나아가려면 싸워야 하니까… 자, 사냥을 시작해 보자!
  - es: Vas a tener que combatir para avanzar, así que... ¡demos comienzo a la cacería!
- `52` **[전투 종료]** 엘리아스(사냥꾼) — 내 머리 위로 달이 붉게 물들어 간다.
  - es: La luna se tiñe roja sobre mí.
- `63`·`107` 에드가르·셀렉(사냥꾼) — 같은 문구
- `74`·`85`·`96` **[전투 종료]** 엘비라·카산드라·케이라(치유사) — 같은 문구
- `166` 팀의 포켓몬 여럿이 상태 이상에 걸렸다!
- `201` 행운이 당신 편이군요, 후보생! 당신의 포켓몬을 치료해 주겠습니다.
- `228` 후, 후, 후! 불운이 네게 닥치길!
- `230`·`241`·`252` **[전투 종료]** 요나·도라·네일라(꼬마마녀) — 그림자로의 귀환!
  - es: ¡Regreso a la Sombra!

### 표본 — 15번도로·16번도로의 레인저 여섯

밟으면 발동하는 자리라 도전 대사와 전투 종료 대사가 한 쌍으로 붙어 있다. 여섯 쌍
전부 두 대사의 격이 서로 맞는다 — 이쪽은 고칠 것이 없어 보인다.

- 맵234(15번도로) ev18 알베르(레인저) — 「입어보니 아주 근사한걸요!」 / 「제가 졌을지는 몰라도, 여전히 당신보다 잘생겼어요.」
- 맵234(15번도로) ev14 마리안느(레인저) — 「우린 포켓몬 레인저다! …더럽히러 온 거냐?」 / 「놀라게 해서 미안해. 아니, 잠깐만. 그건 네가 해야 할 말이잖아.」
- 맵234(15번도로) ev20 닉스(레인저) — 「…누리도록 보장하는 것입니다.」 / 「…패배의 아픔쯤은 아무것도 아닙니다.」
- 맵234(15번도로) ev15 침(레인저) — 「제 기술, 어떠셨나요?」 / 「어쩌면 저는 레인저에 적합하지 않은 걸지도 모르겠네요...」
- 맵237(16번도로) ev5 티스만(레인저) — 「이제 그 대가를 치르게 될 거다!」 / 「내 머릿속에서는 내가 실제보다 더 멋져 보이는데...」
- 맵237(16번도로) ev7 안토니오(레인저) — 「정말 어쩔 수가 없다니까요!」 / 「비록 졌지만, 소름이 돋을 정도로 전율이 흘렀어요.」

## 3. 유지자에게 올리는 물음

1. **이 357행을 트레이너 재번역 배치에 태울 것인가.** 지금은 안 탄다 — 새 행이
   `kind="battle"`이라 `batch_trainers.py`가 집는 `kind="text"`에 안 걸린다.
   태우려면 그쪽 필터를 열면 된다.
2. **말투 수선의 범위.** 위 15행 중 어디까지가 고칠 자리인가. 특히 격을 바꾸는 것이
   연출인 자리(란토·아우레)를 손댈지.
3. **이름표가 없는 트레이너 403행**은 평소 급이 없어 어긋남 표에 아예 안 잡힌다.
   표본으로 본 레인저 여섯 쌍은 도전과 종료의 격이 맞았으나 전수로 본 것은 아니다.
   이쪽까지 볼 것인지.
