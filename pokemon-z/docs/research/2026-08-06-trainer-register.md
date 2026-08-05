# 트레이너 개시·패배 말투 정합 (2026-08-06)

대상은 `docs/research/2026-08-06-speaker-table_trainer.md`의 84줄. 고친 파일은
`translate/ko/00-maps.jsonl` 하나뿐이고, 원문 칸(`k`)은 건드리지 않았다.

## 판정의 뼈대

원문 격을 전수 판독한 결과, **플레이어를 `usted`로 부르는 자리는 84줄 어디에도 없다.**
개시·패배 양쪽 모두 2인칭이 나올 때는 예외 없이 `tú`(`te`·`tu`·`tus`·`has`·`eres`·
`vienes`·`prepárate`·`déjame … -te`)다. `su`·`le`가 잡힌 여덟 자리는 전부 3인칭이었다 —
`su llamada`(포켓몬의 부름, 41:26), `Monsieur Lanto tiene`(91:14), `su cacofonía`(264:24),
`su guardia`(센데라의 근위대, 292:26), `el precio de las mismas … sus`(몬스터볼, 236:2),
`no le has gustado al regente`(히소포에게, 69:61), `No le hagas daño a mi pobre
Murkrow`(니로우에게, 70:11). 유일한 혼재는 39:36 마리오의 개시 한 줄로,
`¿Le gusta la biblioteca?`와 `¿puedo ayudarte?`가 한 문장 안에 섞여 있다.

따라서 **개시와 패배의 원문 격이 실제로 갈린 자리는 없었다.** 한국어가 갈린 것은 전부
번역 쪽 문제이고, 어느 쪽으로 맞출지는 원문 격이 아니라 직군·인물 판정이 정했다
(`translate/persona-table.jsonl`, `translate/voices.md`). `tú`뿐이라고 해서 반말로 내리지는
않았다 — 부르주아·집사장·수도승·레인저처럼 표에 존대 판정이 있는 직군은 존대로 모았다.

## 결과 요약

| 갈래 | 줄 수 |
|---|--:|
| 고침 | 69 (jsonl 실제 수정 행 67 — 155:5=155:4, 282:3=282:4가 같은 행을 공유) |
| 보류 | 7 |
| 손댈 것 없음(선행 sweep이 이미 정합) | 8 |

## 고친 자리

「격」 칸은 개시/패배 순. `—`는 그 줄에 2인칭이 안 나온다는 뜻(1인칭 감탄·독백·격언).

| 맵:이벤트 | 트레이너 | 격(개시/패배) | 판정 | 고친 문구 |
|---|---|---|---|---|
| 14:22 | CAMPESINO/Jean | tú(`vienes`,`darte`) / — | 반말 (campesinow=반말) | 졌지만, 정말 자랑스러워! |
| 27:10 | BURGUESA/Amarna | — / — | 해요체 (burguesaow=해요체) | 저처럼 품격 있는 여성한테 이렇게 무례하다니요! |
| 35:40 | METRE/Maurice | tú(`colarte`,`te daré`) / tú(`no te acostumbres`) | 합쇼체 (metre=집사장 합쇼체·「후보생님」) | 이번 한 번은 그냥 보내 드리겠습니다만, 재미는 붙이지 마십시오! |
| 37:32 | DONCELLA/Helga | tú(`ganarte`) / — | 해요체 (개시가 해요체, 시녀 직군) | 다시는 술 안 마실 거예요, 딸꾹! 제 포켓몬들에게 못 할 짓이죠. |
| 39:36 | METRE/Mario | usted+tú 혼재(`¿Le gusta?`+`ayudarte`) / tú(`Te las apañas`) | 합쇼체 (metre 판정 우선, 원문 자체가 혼재) | 혼자서도 훌륭하게 잘 헤쳐나가시는군요. 정말 대단한 재능이십니다! |
| 41:26 | DUOMISTICO/Molly y Mila | tú(`Has sentido`,`Escucha`) / tú(`Nos has ganado`) | 반말 (개시의 예언조 하대) | 와! 더블 배틀에서 우릴 이겼구나! |
| 43:6 | BRUJITA/Carla | — / tú(`Has sido capaz`) | 반말+마녀 흉내 어른말 (brujita) | 인과율의 법칙을 새로 써 내려갔단 말이냐? 실로 놀랍구나! |
| 52:11 | BURGUES/Remi | tú(`enseñarte`) / — | 해요체 (burguesow) | 그야말로 격식 있는 배틀이었어요. |
| 52:9 | CAMPESINA/Pauline | — / — | 반말 (campesinaw) | 자, 이제 스트레스도 풀었으니 드디어 푹 낮잠을 잘 수 있겠어. |
| 53:8 | CAMPESINA/Vero | — / — | 반말 (campesinaw) | 지금 머릿속이 너무 어지러워! |
| 55:16 | CURANDERA/Maya | tú(`tú también puedes`) / tú(`tu espíritu`) | 반말+예언 단정 (curanderaow) | 승리할 때마다 네 영혼은 하늘을 향해 조금씩 더 드높아진다. |
| 55:13 | CAMPESINO/Daniel | tú(`Has cruzado`) / — | 반말 (campesinow) | 이제 내 마음속에 새로운 두려움이 생겼어. |
| 55:15 | BURGUESA/Diana | — / tú(`vetarte`) | 해요체 (burguesaow, 오만한 어휘로 살림) | 무례한 사람 같으니! 상류사회에서 매장해 버리겠어요! |
| 57:7 | BRUJITA/Sarah | tú(`alguien como tú`) / tú(`estás de visita`) | 반말+마녀 흉내 어른말 | 알겠다, 놀러 온 게로구나. 그렇지? |
| 69:60 | ILUSTRADO/Feric | tú(`Te has perdido`) / tú(`te has aprendido`) | 해요체 (ilustrado) | 교훈을 아주 제대로 얻으신 모양이네요! |
| 69:61 | ILUSTRADO/Marco | tú(`has gustado`) / 무주어(`no se puede`) | 해요체 (ilustrado) | 이보다 더 밑바닥으로 떨어질 수는 없을 것 같네요. |
| 69:62 | CANTANTE/Mía | tú(`Te gusta`) / — | 해요체 (cantanteow) | 드레스를 더럽힌 걸 아시면 섭정 님이 절 가만두지 않으실 거예요! |
| 70:11 | BRUJITA/Aida | tú(`eres tú`) / tú(`hagas`) | 반말+마녀 흉내 어른말 | 내 불쌍한 니로우를 해치지 말거라! |
| 78:42 | CURANDERA/Samira | tú(`tus Pokémon`) / tú(`a tu servicio`) | 반말 (curanderaow) | 내 의술은 언제든 준비돼 있다! |
| 81:40 | LADRONA/Telma | tú(`hacerte`,`vienes`) / — | 반말 (ladrona) | 봐줘! 난 그저 하찮은 좀도둑일 뿐이야! |
| 88:10 | AZOTHA/Emma | — / — | 반말 (azothaow) | 포켓몬도… 우리처럼 고통받는 걸까? |
| 89:3 | ALQUIMISTA/Viviana | — / — | 하게체 (alquimistaOW, 2026-08-04 판정) | 내 역할이 딱히 눈에 띄지는 않네만... |
| 91:14 | BURGUESA/Valentina | —(`Lanto tiene`=3인칭) / tú(`Tus Pokémon`) | 해요체 (burguesaow) | 당신 포켓몬들도... 정말 마음에 들어요! |
| 100:19 | JARDINERO/Romerales | tú(`Has entrado`,`sabías`) / — | 반말 (개시 유지, 직군 판정 없음·tú 전량) | 앗! 그 산울타리를 너무 많이 잘라버린 것 같은데. |
| 100:21 | JARDINERO/Pinares | tú(`Disfrutas`) / — | 반말 (같은 직군·같은 맵) | 내 가위질 솜씨는 아직 갈 길이 먼 것 같아. |
| 107:9 | DUOBURGUES/Emmanuel y Jaqueline | tú(`mira`) / tú(`que tú`) | 해요체 (burguesow/burguesaow) | 져도 상관없어요, 우린 여전히 당신보다 부자니까요! |
| 137:14 | REVOLUCIONARIA/Miquela | tú(`te unes`) / — | 반말+격문투 (revolucionaria) | 그냥 거절하기만 했어도 됐을 텐데. |
| 138:34 | CAZADOR/Camilo | — / tú(`tú puedas`) | 반말 (cazadorow) | 어쩌면 결국 네가 우리를 도와줄 수 있을지도 모르겠군. |
| 138:32 | CAZADOR/Pablo | tú(`unirte`,`te daré`) / — | 반말 (cazadorow) | 램프 불이 꺼져서 제대로 보이지 않았군. |
| 139:51 | GENOS1/Genos | tú(`defenderte`) / tú(`inyectarte`) | 반말 (개시의 하대 단정 유지, 이중 말투 인물 아님) | 흥미롭군! 정말 대단한 표본이야! 내 특제 시약을 너한테 주사할 수만 있다면 좋을 텐데! |
| 155:5 | CAZADOR/Evaristo | tú(`te gustaría`) / — | 하게체 (개시 「하겠나?」에 맞춤) | 트레이닝 잘 하게! |
| 155:4 | SANADORA/Lucrecia | 〃 | 〃 (155:5과 같은 행을 공유) | 〃 |
| 157:27 | REVOLUCIONARIA/Didri | tú(`únete`) / — | 반말+격문투 | 사람을 모으는 내 방식이 그리 설득력 있는 편은 아니지. |
| 159:11 | DUOMOSQUETERO/Archi y Marie | tú(`Quieres sentir`) / tú(`te lo has ganado`) | 반말+군대식 단정 (mosqueterow) | 미르시티에 들어가도 좋다. 그럴 자격을 얻었으니까. |
| 172:17 | REVOLUCIONARIO/Rodry | tú(`te incumbe`,`Vas a perder`) / — | 반말+격문투 | 난 이런 혁명 같은 건 처음이라서. |
| 191:27 | REVOLUCIONARIA/Foxua | — / — | 반말+격문투 | 이 이야기에서 내 역할은 이제 끝났다! |
| 191:29 | REVOLUCIONARIO/Luisvo | — / — | 반말+격문투 | 뭐라고? 정의를 생각하면 내가 이겼어야지! |
| 234:18 | RANGER/Alber | — / tú(`que tú`) | 해요체 (ranger) | 제가 졌을지는 몰라도, 여전히 당신보다 잘생겼어요. |
| 234:20 | RANGERA/Nixx | — / — | 합쇼체 (개시가 「~것입니다」) | 내일이 가져다줄 좋은 일들을 생각하면 패배의 아픔쯤은 아무것도 아닙니다. |
| 234:15 | RANGER/Chim | tú(`te ha parecido`) / — | 해요체 — **개시 쪽을 고쳤다**. 같은 맵의 레인저 둘(Alber·Nixx)이 존대이고 ranger 판정도 해요체라 개시가 어긋난 자리였다 | 완벽하게 기척을 숨긴 제 기술, 어떠셨나요? 여자들한테 얼마나 잘 통하는지 직접 보셔야 하는데 말이죠. |
| 235:2 | OBRERO/Olmos | — / — | 반말 (obrerow) | 팀워크는 언제나 이긴다고! 잘 조립하는 게 성공의 열쇠지. |
| 236:2 | OBRERO/Ludd | — / —(`sus`=몬스터볼) | 반말 (obrerow) | 트레이너와 포켓몬의 팀워크보다 더 정밀한 기계는 없지. |
| 242:2 | BURGUES/Trey | tú(`Quieres`,`darte`) / — | 해요체 (burguesow) | 내 우아한 포켓몬들이 지다니 정말 믿기지 않네요. |
| 243:26 | DUOBURGUES/Zarina y Otto | — / — | 해요체 (burguesow) | 저는 팔데아 사람들이 좋아요. 뭐라도 실천하거든요. |
| 245:16 | DUOMOSQUETERO/Icaro y Alice | — / — | 반말+군대식 단정 (mosqueterow) | 메가진화로 가는 길은 장애물로 가득하다. 하지만 우린 모두 극복할 것이다. |
| 245:15 | LADRONA/Posse | tú(`Sabes`,`eres capaz`) / — | 반말 (ladrona) | 진정한 보물은 여정에서 만난 친구들이지. |
| 251:1 | FERROFAZ/Ferrofaz | tú(`Puedes empezar`) / vosotros(`Lo habéis conseguido`) | 하게체 — **개시 쪽을 고쳤다**. 페로파스는 `voices.md`에 「온화한 하게체」로 판정돼 있고 패배 대사가 그 판정에 맞는다 | \PN, 시작해 보게. |
| 255:31 | LADRONA/Jona | tú(`tus Pokémon`) / tú(`darte`) | 반말 (ladrona) | 소중한 정보를 넘겨줄 준비가 돼 있다! |
| 256:20 | BURGUES/Estefan | tú(`Te costará`) / tú(`te ha molestado`) | 해요체 (burguesow) | 추위 따위는 전혀 개의치 않으시는 모양이네요. |
| 269:17 | BRUJITA/Vicky | tú(`Vas`,`Tendrás`) / tú(`haberte conocido`) | 반말+마녀 흉내 어른말 | 너를 만나 내 마음이 마법에 걸린 듯 사로잡혔구나! |
| 276:43 | LIDER8/Anturia | — / — | 반말 — **개시 쪽을 고쳤다**. 안투리아는 `voices.md`에 「마녀 말투 반말」 판정이 있고 패배 대사가 그 판정에 맞는다 | 이제 시작해 볼까? |
| 282:3 | OBREROS/Mariano y Luciano | tú(`darte una lección`) / — | 해요체 (mariow=손님에겐 해요체, Mamma mia 유지) | 맘마미아! 정말 대단한 힘이네요! |
| 282:4 | OBREROS/Mariano y Luciano | 〃 | 〃 (282:3과 같은 행을 공유) | 〃 |
| 284:5 | ILUSTRADO/Unai | — / tú(`Oponerte`) | 합쇼체 (개시가 「~겠습니다」) | 벌레타입의 위엄에 거스르는 것은 무의미합니다. |
| 292:29 | ELITEFRACTAL/Caruso | tú(`No podrás pasar`) / — | 반말 도발조 (eliteFractal) | 눈이 녹기 시작한 것 같군! |
| 298:21 | DRUIDA/Cmari | tú(`Vienes`,`Tendrás`) / tú(`tus secretos`) | 반말 어른말 (druida, 개시의 「그대」 유지) | 그대의 배틀 비결은 무엇인가? |
| 299:24 | BURGUES/Miguel | tú(`no serás tú`) / — | 해요체 (burguesow) | 프랑스의 우아함이란, 참으로 놀랍군요! |
| 299:25 | BURGUESA/Mar | — / tú(`asegúrate`) | 해요체 (burguesaow) | 행복의 기차는 한 번밖에 지나가지 않으니, 놓치지 말고 꼭 타세요! |
| 301:29 | MOSQUETERA/Sophie | — / — | 반말 (mosqueteraw) | 여기서 내 동굴 탐험도 끝인 것 같네. |
| 321:58 | ELITEFRACTAL/Irving | tú(`has caído`) / tú(`Te desenvuelves`,`unirte`) | 반말 도발조 (eliteFractal) | 얼음 위에서 꽤 잘 움직이는군. 우리 군에 들어올 생각은 없나? |
| 321:53 | ELITEFRACTAL/Marcelo | tú(`te atreves`,`Prepárate`) / — | 반말 도발조 | 등골이 오싹하군! 대단한 위력이다! |
| 359:11 | PAYASOMECANICO/Trilero | tú(`no te resistas`,`tu payaso`) / 3인칭 지문(`El cliente se resiste`) | 기계 합쇼체 (payasoAutomata, 2026-08-04 판정) | 손님이 포옹을 거부합니다. |
| 373:27 | MONJE/Axel | — / — | 합쇼체 (monjeYantra) | 때로는 무력을 쓰는 것이 불가피해 보일 때도 있습니다. |
| 373:30 | MONJES/Josu y Meer | — / tú(`ponerte de pie`) | 합쇼체 (monjeYantra) | 실패는 다시 일어서기 위한 기회일 뿐입니다! |
| 376:24 | MONJES/Vicent y Amber | — / 1인칭 복수(`no nos ponían a prueba`) | 합쇼체 (monjeYantra) | 전례 없는 메가배틀! 이렇게 시험에 들어 본 건 참 오랜만입니다. |
| 376:26 | MONJA/Nyra | — / — | 합쇼체 (monjaYantra) | 유대에 도달하려면 배틀에 좀 더 여유 있게 임해야 할지도 모르겠습니다. |
| 390:20 | DUOMOSQUETERO/Lovahi y Ros | tú(`subas`,`Ya sabes`) / 1인칭(`Caemos`) | 반말 (mosqueterow) | 급강하하고 있어! |
| 476:42 | ELITEAZOTH/Harvey | — / — | 반말 (개시의 열띤 반말 유지) | 배틀을 하면 할수록, 진실에 더 가까워지는 것 같아! |
| 477:19 | ELITEAZOTHA/Sash | tú(`¿Y tú?`,`Intentas`) / tú(`Eres`) | 하게체 (개시가 「~다네/~하나?」) | 자네는 참으로 영감을 주는 사람일세! |

## 보류

| 맵:이벤트 | 트레이너 | 보류 사유 |
|---|---|---|
| 112:4 | LANTO1/Lanto | 이중 말투가 정체성인 인물 아홉 중 하나. 사교장 해요체와 본색 반말이 갈리는 것이 연출이다(`voices.md` 란토 항목) |
| 418:19 | LIDER2R/Hisopo | 같은 이유 — 무대 위 합쇼 낭독과 무대 밖 격정 반말 |
| 418:19 | LIDER10R/Cendera | 같은 이유 — 공무 합쇼체와 사적 경멸조 반말 |
| 264:24 | LUNATICO/Danforth | `persona-table.jsonl`의 lunatico 항목이 「어투가 한 화자 안에서 흔들리는 것이 이 스프라이트의 연출이다. 어투 통일 게이트에서 걸리더라도 살려 둘 것」이라고 못박았다 |
| 292:26 | ELITEFRACTAL/Cristol | 패배 대사 「대장님, 기대에 부응하지 못했습니다!」의 수신자가 플레이어가 아니라 센데라 대장이다(원문 `¡Te he fallado, capitana!`). 상관에게 하는 합쇼체는 어긋남이 아니다 |
| 209:4 | ALTOMANDO4/Malva | 사천왕급 인물이고 `voices.md`의 파키라 항목(의전 합쇼체)이 이 배역과 같은 인물인지 확정할 수 없다. 게다가 어긋남이 패배 한 줄이 아니라 인접 대사 전체다 — 같은 맵 6899~6907행이 「누구니」(반말)·「~단다」·합쇼체를 오간다. 인물 단위 재판정이 먼저다 |
| 468:28 | URANO/Urano | 개시 대사가 비명 하나(`\sh¡IAAAAAAAH!`)라 맞출 어미가 없다 |

## 손댈 것 없음 — 선행 sweep이 이미 정합으로 만든 자리

표는 2026-08-06 요리사·사프라 반말 전환 전에 뜬 것이라, 아래 여덟은 표가 적은
「개시 존대」가 지금 파일에 없다. 개시가 이미 반말이고 패배도 반말이라 어긋남이 없다.

| 맵:이벤트 | 트레이너 | 현재 개시 | 현재 패배 |
|---|---|---|---|
| 85:15 | LIDER4/Zafra | 지-질 준비해!\n...\n제발! | 아아아! 역시 긴장해서 망칠 줄 알았어! … |
| 115:3 | CHEF/Gordon | 그 손으로 음식을 만지진 않겠지? … | 네 손은 깨끗하구나! |
| 115:4 | CHEF/Ferran | 바게트 빵 좋아해? … | 패배의 맛은 참으로 씁쓸하구나. |
| 115:5 | CHEF/Berasategui | 내 요리는 … 한번 맛볼래? | 훌륭한 요리사는 건설적인 비판을 기꺼이 받아들인다. |
| 115:6 | CHEF/Carmy | … 날 이기면 알려줄게. | 당연히 매콤하게 두들겨 맞은 샐러드지! |
| 115:7 | CHEF/Grimod | … 내 요리로 감동을 주고 싶어! | 너의 배틀 방식은... 간이 좀 세긴 하지만! … |
| 137:17 | CHEF/Sergio | … 자란다고들 하지. 포켓몬도 마찬가지일까? | 이럴 수가! 이렇게 어린 사람에게 지다니! |
| 269:16 | CHEF/Shawn | Bonjour! 너도 … 버섯을 따러 왔어? | 오, 라, 라! 오, 라, 라! |

## 자체 검사

`translate/ko/00-maps.jsonl` 대상, 커밋 직전 실행.

```
check1 parsed lines: 14278 / 14278
check2 lines old/new: 14278 14278 EQ
check3 k-changed rows: 0 | key-set changed: 0 | v-changed rows: 67
check3b edited idx count: 67 == v-changed: True
check4: 26 honorific-target, 41 plain-target, mismatches=0
```

check4는 고친 67행마다 의도한 격이 실제로 들어갔는지 본 것이다. 존대로 모은 26행에는
존대 종결(`습니다`·`세요`·`네요`·`군요`·`죠` 등)이 반드시 있어야 하고, 반말·하게체로
내린 41행에는 하나도 없어야 한다 — 양방향 모두 어긋남 0건.
