# 잡담 채점판 — 유지자 검토 시트 (2026-08-09)

표본 100 중 심판 3인 이견·경계 지대와, 통과분 무작위 10건의 검산용 목록.
각 건에 O(잡담으로 취급 가능)/X(제외)/? 만 표시해 주면 된다.

### [검토] id=4 — 맵314 Batalla de Kalos Este · ev30 p0 · 그림 sanadoraow · 1줄
라벨: {"a": "기타", "b": "시스템지문", "c": "기타"}
- a: 1회 회복 제공 + 예/아니요 — 시설 기능 대사
- b: 회복 기능 대사 + 예/아니요 확인 선택지
- c: 치료 서비스 기능 대사+선택지
  - Puedo curar a tus Pokémon una sola vez, pero después tendrás que marcharte.
    → 당신 포켓몬을 딱 한 번 치료해 드릴 수는 있지만, 그 뒤엔 떠나셔야 해요.
  - [선택지] ¡Hazlo!
    → 해봐!
  - [선택지] Mejor no
    → 그만두기

### [검토] id=5 — 맵312 Transición · ev5 p0 · 그림 burguesow · 1줄
라벨: {"a": "잡담", "b": "스토리", "c": "스토리"}
- a: 시민 NPC가 정세 소문을 혼잣말로 한 줄, 장면 연결 없음
- b: 크리산토 대장·미라 입법관 고유명과 정변 정세를 전제로 한 해설
- c: 반란 지도자와 입법관 사이 미해결 사건을 언급(장면 전제 필요)
  - El Capitán <b>Crisanto</b> se ha alzado contra el gobierno y reclama estas tierras. ¿Pero 
    → <b>크리산토</b> 대장이 정부에 반기를 들고 이 땅을 요구하고 있어요. 하지만 어째서일까요? 그와 <b>미라</b> 입법관 사이에 무슨 일이 있었던 건지 몰라

### [검토] id=13 — 맵360 Pueblo Sanguino · ev34 p1 · 그림 nina · 1줄
라벨: {"a": "모름", "b": "기타", "c": "기타"}
- a: 교환 이벤트 사후 페이지의 한 줄 — 잡담체지만 교환 기능의 일부일 수 있음
- b: Trader 이벤트 page1 — 교환 성사 후 대사라 접촉 잡담이 아님
- c: 교환 이벤트 뒤 감사 인사(거래 기능 맥락)
  - Morpeko me parece mucho más chulo que Pachirisu. ¡Gracias por cambiármelo!
    → 모르페코가 파치리스보다 훨씬 멋진 것 같아. 바꿔줘서 고마워!

### [검토] id=17 — 맵120 Cámara Druídica · ev9 p0 · 그림 druidaow2 · 1줄
라벨: {"a": "시스템지문", "b": "시스템지문", "c": "시스템지문"}
- a: 시신을 서술하는 조사 지문, 화자 없음
- b: 조사 대상 묘사 내레이션(시신 상태 서술)
- c: 드루이드 시신을 묘사하는 서술문
  - El cuerpo inerte de una druida. No se ha visto afectado por la descomposición.
    → 미동 없는 드루이드의 시신. 전혀 부패하지 않았다.

### [검토] id=18 — 맵102 Pueblo Petroglifo · ev30 p0 · 그림 hombre1 · 1줄
라벨: {"a": "잡담", "b": "잡담", "c": "스토리"}
- a: 시민 NPC의 시국 불평 한 줄
- b: 왕정 비판 한마디 — 세계관 배경이지 장면 진행 아님
- c: 왕의 판결·농민 봉기라는 미표시 사건에 대한 반응(전제 필요)
  - ¿Este es el concepto de justicia del rey? ¡Qué decepción! Los campesinos solo estaban recl
    → 이게 왕이 말하는 정의란 말인가? 참 실망스럽군! 농민들은 그저 더 공정한 조건을 요구했을 뿐인데.

### [검토] id=25 — 맵106 Fort Leviatán · ev43 p0 · 그림 revolucionaria · 1줄
라벨: {"a": "잡담", "b": "잡담", "c": "스토리"}
- a: 혁명군 NPC의 승리 선언 한 줄, 단독 화자
- b: 혁명군 구호 — 정세 반영이나 화자 하나에 지시 없음
- c: 반란군의 요새 점령·다음 목표 선언(진행 중 플롯)
  - Hoy hemos ganado esta fortaleza para el pueblo, pero el día de mañana nos haremos con el c
    → 오늘 우리는 민중을 위해 이 요새를 차지했다. 내일은 <b>미르 궁전</b>을 손에 넣을 것이다.

### [검토] id=42 — 맵362 Expansiones de Luminalia - Centro · ev11 p0 · 그림 revolucionaria · 2줄
라벨: {"a": "잡담", "b": "잡담", "c": "스토리"}
- a: 혁명군 NPC의 타워 건설 소문 전달
- b: 타워 건설 배경 소문, 지시 없음
- c: 혁명정부의 세계 박람회 계획 등 정치 서사 전제
  - Según me he enterado, la construcción de la <b>Torre Prisma</b> se debe a que <b>Kalos</b>
    → 내가 들은 바에 의하면, <b>프리즘타워</b>를 건설하는 건 몇 년 뒤 <b>칼로스</b>에서 아주 중요한 세계 박람회가 열리기 때문이다.
  - El gobierno revolucionario pretende sacar músculo de la prosperidad de nuestra región ante
    → 혁명 정부는 전 포켓몬 세계에 우리 지방의 번영을 과시할 셈이다.

### [검토] id=55 — 맵80 Ciudad Novarte · ev43 p0 · 그림 mosqueteraw · 2줄
라벨: {"a": "잡담", "b": "기타", "c": "스토리"}
- a: 경비 NPC가 요새 폐쇄를 알리고 다음 장소를 일러 주는 한 자리 대사
- b: 요새 폐쇄 통보와 아카데미로 가라는 진행 지시
- c: 섭정 사망이라는 정치적 사건과 퀘스트 지시(전제 필요)
  - El bastión está cerrado. ¿No te has enterado, Aspirante? El regente de la ciudad falleció 
    → 요새는 폐쇄되었다! 소식 못 들었나, 후보생? 도시의 섭정께서 지난주에 세상을 떠나셨다.
  - ¿Por qué no te pasas por la <b>Academia Novarte</b> para que te orienten sobre cómo contin
    → <b>백단 아카데미</b>에 들러서 앞으로 어떻게 해야 할지 안내를 받아 봐라.

### [검토] id=61 — 맵22 Cuartel Mosquetero · ev3 p7 · 그림 mosqueterow · 2줄
라벨: {"a": "기타", "b": "기타", "c": "스토리"}
- a: 현상범 체포 보상 수여 — 퀘스트 진행 대사
- b: 현상수배 완료 보상 지급 — 퀘스트 결말 페이지(page7)
- c: 이전에 잡은 범죄자들을 전제로 한 현상금 퀘스트 보상·다음 목표 지시
  - Oye, que sepas que te has convertido en toda una leyenda en este cuartel.
    → 어이, 네가 이 주둔지의 전설이 되었다는 건 알고 있겠지.
  - Por haber apresado al último y peligrosísimo criminal, te haré entrega de este tesoro que 
    → 가장 위험한 마지막 범죄자를 체포했으니, 우리 최고의 영웅에게 수여하는 이 보물을 주겠다.

### [검토] id=65 — 맵261 Hostal Batik · ev9 p0 · 그림 lunatico · 4줄
라벨: {"a": "모름", "b": "스토리", "c": "스토리"}
- a: 냄새 맡고 '쓸모없어'라는 수상한 4연속 대사 — 복선 컷신인지 기괴 잡담인지 불명
- b: 플레이어의 정체를 냄새로 감지하고 「우리」 조직을 암시 — 접촉 잡담 아님
- c: '우리'라는 미표시 집단과 플레이어 정체에 대한 암시(전제 필요)
  - Snif, snif...
    → 흐윽, 흐윽...
  - Tu... tu olor...
    → 너... 네 냄새...
  - No tienes olor de persona corriente.
    → 너, 평범한 사람 냄새가 안 나는데.
  - No, no. Tú no nos sirves...
    → 아니야, 아니야. 당신은 우리에게 쓸모가 없어...

### [검토] id=75 — 맵345 Balneario Oculto · ev11 p0 · 그림 kimono · 4줄
라벨: {"a": "기타", "b": "시스템지문", "c": "기타"}
- a: 온천 회복 시설 기능 대사
- b: 온천 회복 서비스 확인창
- c: 온천 치료 기능 대사+선택지
  - Te doy la bienvenida al Balneario Oculto. ¿Quieres curar a tu equipo?
    → 비밀 온천에 오신 것을 환영해요. 팀을 치료하시겠습니까?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - Esto llevará un rato.
    → 잠시만 기다려 주세요.
  - Misión cumplida, ¡vuelve cuando lo necesites!
    → 맡겨 두신 포켓몬이 모두 건강해졌습니다! 또 이용해 주세요!
  - Estamos a tu servicio.
    → 언제든 정성껏 모시겠습니다.

### [검토] id=82 — 맵22 Cuartel Mosquetero · ev3 p1 · 그림 mosqueterow · 4줄
라벨: {"a": "기타", "b": "기타", "c": "스토리"}
- a: 현상범 보상 지급 + 다음 목표 지시 — 퀘스트 진행
- b: 현상수배 보상 지급과 다음 표적 지시 — 퀘스트 진행
- c: 이전에 물리친 마녀를 전제로 한 현상금 퀘스트 보상·다음 목표 지시
  - ¡Bien hecho! Esa bruja nos estaba dando más de un dolor de cabeza.
    → 잘했다! 그 마녀 때문에 아주 골치가 아팠거든.
  - Como prometí, aquí tienes tu recompensa.
    → 약속대로 여기 보상을 지급하겠다.
  - El siguiente malhechor del que tenemos constancia es un Cazador que fue visto por última v
    → 다음으로 파악된 악당은 <b>음침한 동굴</b>에서 마지막으로 목격된 사냥꾼이다.
  - Dicha cueva se encuentra en la <b>Ruta 6</b>. ¡Piensa en ello si pasas por ahí, pero proce
    → 해당 동굴은 <b>6번도로</b>에 있다. 근처를 지나게 되면 염두에 두어라. 단, 조심해서 행동해라!

### [검토] id=85 — 맵114 Centro Pokémon · ev4 p0 · 그림 enfermera2 · 4줄
라벨: {"a": "기타", "b": "시스템지문", "c": "기타"}
- a: 포켓몬센터 접수 회복 기능
- b: 포켓몬센터 회복 확인창
- c: 포켓몬센터 치료 기능 대사+선택지(간호사=사람)
  - ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Qui
    → <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - Esto llevará un rato.
    → 잠시만 기다려 주세요.
  - Misión cumplida, ¡vuelve cuando lo necesites!
    → 맡겨 두신 포켓몬이 모두 건강해졌습니다! 또 이용해 주세요!
  - Estamos a tu servicio.
    → 언제든 정성껏 모시겠습니다.

### [검토] id=91 — 맵164 Centro Pokémon · ev4 p0 · 그림 enfermera2 · 4줄
라벨: {"a": "기타", "b": "시스템지문", "c": "기타"}
- a: 포켓몬센터 회복 기능
- b: 포켓몬센터 회복 확인창
- c: 포켓몬센터 치료 기능 대사+선택지
  - ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Qui
    → <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - Esto llevará un rato.
    → 잠시만 기다려 주세요.
  - Misión cumplida, ¡vuelve cuando lo necesites!
    → 맡겨 두신 포켓몬이 모두 건강해졌습니다! 또 이용해 주세요!
  - Estamos a tu servicio.
    → 언제든 정성껏 모시겠습니다.

### [검토] id=92 — 맵142 Centro Pokémon · ev4 p0 · 그림 enfermera2 · 4줄
라벨: {"a": "기타", "b": "시스템지문", "c": "기타"}
- a: 포켓몬센터 회복 기능
- b: 포켓몬센터 회복 확인창
- c: 포켓몬센터 치료 기능 대사+선택지
  - ¡<i>Bonjour</i>! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Qui
    → <i>Bonjour</i>! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - Esto llevará un rato.
    → 잠시만 기다려 주세요.
  - Misión cumplida, ¡vuelve cuando lo necesites!
    → 맡겨 두신 포켓몬이 모두 건강해졌습니다! 또 이용해 주세요!
  - Estamos a tu servicio.
    → 언제든 정성껏 모시겠습니다.

### [검토] id=94 — 맵233 Ciudad Romantis · ev48 p1 · 그림 ilustrado · 4줄
라벨: {"a": "잡담", "b": "기타", "c": "스토리"}
- a: 퇴치 후 감사 인사와 소문 전달, 한 자리에서 종료
- b: 유령 퇴치 보답으로 다음 목표를 알려주는 퀘스트 연결
- c: 플레이어가 이전에 유령을 쫓아냈다는 미표시 사건을 전제
  - ¿Has espantado al Pokémon fantasmal? ¡Te debo una!
    → 고스트 포켓몬을 쫓아내 주셨군요! 정말 감사합니다!
  - Lamentablemente, no tengo mucho con lo que recompensarte. Pero te contaré un rumor.
    → 아쉽게도 보답으로 드릴 건 별로 없어요. 대신 소문 하나를 들려드릴게요.
  - He oído que hay otro fantasma cerca de la <b>Fábrica de Pokéball</b>, donde los setos.
    → <b>몬스터볼 공장</b> 근처 울타리 쪽에 또 다른 유령이 나타난다는 말을 들었습니다.
  - ¡Te lo digo por si te gusta dedicarte a esto de cazar fantasmas!
    → 혹시 유령을 퇴치하는 일에 관심이 있다면 가보세요!

### [검토] id=98 — 맵357 Centro Pokémon · ev4 p1 · 그림 enfermera2 · 5줄
라벨: {"a": "기타", "b": "시스템지문", "c": "기타"}
- a: 졸던 접수원의 포켓몬센터 회복 기능
- b: 졸다 깬 연출만 얹힌 포켓몬센터 회복 확인창
- c: 포켓몬센터 치료 기능 대사+선택지
  - Zzzz...
    → Zzzz...
  - ... ¡Uy! Te doy la bienvenida al Centro Pokémon, hacemos milagros sanitarios. ¿Quieres cur
    → ... 어머나! 포켓몬센터에 오신 것을 환영해요. 저희는 건강의 기적을 만들어낸답니다. 포켓몬들을 치료하시겠습니까?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - Esto llevará un rato.
    → 잠시만 기다려 주세요.
  - Misión cumplida, ¡vuelve cuando lo necesites!
    → 맡겨 두신 포켓몬이 모두 건강해졌습니다! 또 이용해 주세요!
  - Estamos a tu servicio.
    → 언제든 정성껏 모시겠습니다.

## 통과분 무작위 10건 (검산용 — 셋 다 잡담∪기타 합의)

### [통과검산] id=60 — 맵182 Catedral Señorial · ev8 p0 · 그림 anciana · 2줄
라벨: {"a": "잡담", "b": "잡담", "c": "잡담"}
- a: 노파 NPC의 추모 이야기
- b: 추모 이야기, 단일 화자
- c: 남편과 파트너 포켓몬 추모담
  - Vengo todos los días para recordar a mi marido y a mi compañero Pokémon.
    → 매일 이곳에 와서 남편과 내 파트너 포켓몬을 추모한단다.
  - Les sobreviví a ambos. Aprovecharé el tiempo que me queda para hacer todo el bien que me s
    → 둘보다 오래 살아남았구나. 그들과 다시 만나기 전까지, 남은 시간 동안 할 수 있는 한 선행을 베풀어야겠지.

### [통과검산] id=33 — 맵399 Centro Pokémon · ev6 p0 · 그림 monjaYantra · 2줄
라벨: {"a": "잡담", "b": "잡담", "c": "잡담"}
- a: 수도승 NPC가 센터 사정 설명, 두 줄로 종료
- b: 센터 개설 경위 설명, 단일 화자 flavor
- c: 포켓몬센터 개설 배경 설명, 완결
  - Este Centro Pokémon fue abierto hace poco. Se trata de una excepción única que hemos hecho
    → 이 포켓몬센터는 얼마 전 문을 열었습니다. <b>사라시티</b>에서 외부의 영향을 받아 예외적으로 딱 한 번 허용한 사례지요.
  - Pero como comprenderás, era muy difícil curarle la columna vertebral a Pikachu a base de u
    → 하지만 아시다시피, 연고와 약초만으로는 피카츄의 척추를 치료하기가 너무 어려웠으니까요.

### [통과검산] id=72 — 맵395 Café Galanes · ev5 p0 · 그림 curanderaow · 5줄
라벨: {"a": "기타", "b": "기타", "c": "기타"}
- a: 인게임 교환 기능 분기
- b: 포켓몬 교환 기능 이벤트
- c: 포켓몬 교환 기능 대사+선택지
  - Estoy buscando un Heliolisk, ¿lo cambiarías por 
mi Quaxly?
    → 일레도리자드를 찾고 있다만... 내 꾸왁스랑 바꾸지 않겠나?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - ¡Cúidalo muy bien! 
    → 귀여워해 줘!
  - ¡Vaya! Veo que no tienes uno.
    → 이런! 아직 안 갖고 있군.
  - Si te haces con ese Pokémon, ponlo en el primer 
lugar de tu equipo para que pueda verlo.
    → 그 포켓몬을 손에 넣거든 볼 수 있게 선두에 세워서 보여 줘.
  - Bueno, otra vez será.
    → 그렇다면 다음 기회에.

### [통과검산] id=10 — 맵284 Ruta 16 · ev22 p0 · 그림 ilustrado · 1줄
라벨: {"a": "잡담", "b": "기타", "c": "기타"}
- a: NPC가 지금은 나중에 오라고 한 줄, 단독 화자
- b: 「나중에 다시 와 달라」 — 콘텐츠 차단 안내
- c: 시공간 균열로 진입 불가라는 진행 게이트 안내
  - ¿Podrías volver más adelante? Ha aparecido una fisura espaciotemporal que está causando gr
    → 나중에 다시 와 주시겠어요? 이 지역에 시공간 균열이 나타나 큰 재앙을 일으키고 있거든요.

### [통과검산] id=16 — 맵102 Pueblo Petroglifo · ev15 p1 · 그림 burguesow · 1줄
라벨: {"a": "잡담", "b": "잡담", "c": "잡담"}
- a: 시민 NPC의 바다 감상 두 문장
- b: 바다 생물 감상, 단일 화자 flavor
- c: 심해 생물에 대한 트리비아 발언
  - Apenas sabemos una centésima parte de toda la vida que alberga el mar. ¿Cuántas especies d
    → 우리는 바다가 품은 생명의 백분의 일도 알지 못합니다. 저 깊은 곳에 얼마나 많은 포켓몬이 남아 있을까요?

### [통과검산] id=21 — 맵59 Ciudad Óleo · ev20 p2 · 그림 cantanteow · 1줄
라벨: {"a": "잡담", "b": "잡담", "c": "잡담"}
- a: 가수 NPC의 오디션 이야기
- b: 오디션 포부 — 고유명은 극작가일 뿐 진행 무관
- c: 오디션 계획 발언, 완결
  - Voy a audicionar para el papel protagonista de la próxima ópera de <b>Hisopo</b>. ¡Este po
    → <b>히소포</b>의 다음 오페라 주연 오디션을 보러 갈 거예요. 오늘이 새로운 삶의 첫날이 될지도 몰라요!

### [통과검산] id=67 — 맵302 Café Pedrín · ev5 p0 · 그림 lenador · 5줄
라벨: {"a": "기타", "b": "기타", "c": "기타"}
- a: 인게임 교환 기능 분기
- b: 포켓몬 교환 기능 이벤트
- c: 포켓몬 교환 기능 대사+선택지
  - Estoy buscando un Heatmor, ¿lo cambiarías por mi Scorbunny?
    → 앤티골을 하나 찾고 있는데, 제 스코버니랑 안 바꾸실래요?
  - [선택지] Sí
    → 예
  - [선택지] No
    → 아니요
  - ¡Cúidalo muy bien! 
    → 귀여워해 주세요!
  - ¡Vaya! Veo que no tienes uno.
    → 이런! 갖고 계시지 않네요.
  - Si te haces con un Heatmor, ponlo en el primer lugar de tu equipo para que pueda verlo.
    → 앤티골을 손에 넣으시면 볼 수 있게 선두에 세워서 보여 주세요.
  - Bueno, otra vez será.
    → 그렇다면 다음 기회에.

### [통과검산] id=11 — 맵338 Campamento de Crisanto · ev19 p1 · 그림 carabineraow · 1줄
라벨: {"a": "잡담", "b": "잡담", "c": "기타"}
- a: 병사 NPC의 조언 한 줄
- b: 전투 준비 조언이지만 지시가 아닌 일반 팁, 단일 NPC
- c: 회복 아이템을 직접 챙기라는 공략 조언
  - No tenemos muchos suministros de curación durante la batalla, ¡así que deberías considerar
    → 전투 중에는 회복 물자가 많지 않으니, 직접 챙겨 오시는 게 좋을 거예요!

### [통과검산] id=81 — 맵137 Ruta 12 · ev12 p0 · 그림 prodigio · 4줄
라벨: {"a": "기타", "b": "기타", "c": "기타"}
- a: 종족값 기준 교환 서비스 NPC
- b: Le Prodige 종족값 교환 서비스
- c: 능력치 기반 포켓몬 교환 기능 대사+선택지
  - ¡Hola, soy <b>Le Prodige</b>!
    → 안녕하세요, 제가 바로 <b>르 프로디주</b>예요!
  - Puedo cambiarte a uno de tus Pokémon por otro de valor similar según la suma total de sus 
    → 능력치 합계에 맞춰, 당신의 포켓몬 중 하나를 비슷한 가치의 다른 포켓몬으로 교환해 드립니다.
  - ¿Qué te parece?
    → 어떻게 생각하세요?
  - [선택지] Acepto
    → 그렇게 하죠
  - [선택지] No me interesa
    → 관심 없어요
  - ¿No? Pues te pierdes Pokémon maravillosos...
    → 안 하시나요? 그럼 멋진 포켓몬을 놓치게 될 텐데요...

### [통과검산] id=49 — 맵178 Café Concordia · ev10 p0 · 그림 anciano · 2줄
라벨: {"a": "잡담", "b": "잡담", "c": "잡담"}
- a: 노인 NPC의 회상 두 줄
- b: 노인의 추억 한 토막
- c: 아내와의 추억담, 완결
  - Mi mujer y yo nos conocimos en esta cafetería, hace muchas décadas.
    → 아내와 나는 수십 년 전 바로 이 카페에서 만났다네.
  - Ella ya no está conmigo, pero seguiré desayunando aquí para honrar su memoria.
    → 그 사람은 이제 세상에 없지만, 추억을 기리려고 계속 여기서 아침을 먹고 있다네.
