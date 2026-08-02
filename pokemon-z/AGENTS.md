# pokemon-z — 작업 규율

> poke-essentials(sketches)의 mod/AGENTS.md 「둘째 게임」 두 절을 2026-08-02 이사와 함께 옮겨 왔다.
> 판독·조회와 Wishing Star 갈래는 여전히 그쪽 repo 몫이다.

## 둘째 게임 — Pokemon Z (구형 엔진, 주입형)

**Pokemon Z(Essentials v16 · 루비 1.8.7 · mkxp-z 구판)는 플러그인 묶음이 없다.** 코드
모드는 `inject.py`가 `Scripts.rxdata` 배열에 `MOD:<모드명>/<파일명>` 섹션으로
덧붙인다(`Main` 직전, 나중 정의가 이긴다). 기반은 게임 폴더가 아니라 **모드 보관소의
한글패치판**이라 몇 번을 돌려도 결과가 같다. 보관소는 게임별 하위 폴더 체제다 —
`/mnt/d/GameVault/mods/Pokemon Z Fangame/<모드>/`(폴더명은 é 없는 쪽이 정본 —
2026-08-02 fangame-library가 근원 정리). 주입 모드는 일곱: Battle Speed Z(M-23 — 배틀 애니메이션 기본 2배속) · Better Movements Z ·
Frame Profiler(v3 — 단계별·이동/정지 분리 측정, 재진입 가드) · Josa Select ·
UI Text KR · GC Tamer · Controller UX Z(M-22 — 커서 숨김·이름 입력 패드 확인·
등록 아이템 패드 X·Xbox 글리프. 기본 패드 매핑은 F1 실측: JS 번호가 XInput 원시
순서라 패드 A·B·X·Y·LB·RB·RS클릭 → 가상 C·B·X·A·Y·Z·L. 화면 단축키 표기는
UI Text KR이 컨트롤러 기준으로 적는다).

**성능 조사(2026-08-02)가 걷기 멈칫의 정체를 갈랐다.** 지속 프레임 저하는 존재하지
않고(멈칫 프레임을 빼면 전 구간 60fps 복원 — v1 로그 3시간 전수 재검산), 체감의
실체는 멈칫 밀도다. 갈래 셋: ① 맵 경계 전환마다 ~0.58초(스프라이트셋 생성+전환 —
미해결), ② 12초 주기 ~85ms — 크기가 83~90ms에 몰리고 그 순간 돌던 단계에 얹히는
**루비 GC 지문**(이 루비엔 GC.count가 없어 개입 실험이 곧 판정), ③ 비탈 숲(map28·46)의
상주 이벤트. GC Tamer가 ②의 실험이자 처방이다 — 평소 GC.disable, 맵 전환·장면
전환에 몰아 돌리고 90초 안전판. **루비 1.8은 GC.disable 중 GC.start가 무시된다** —
enable→start→disable로 감싸야 한다. 실기 판정 대기 중.

지켜야 할 것들:

- **같은 모드를 두 번 주입하면 alias가 두 겹으로 걸려 무한 재귀다**(2026-08-01 실사고 —
  수확 폴더명의 é 표기가 어긋나 중복 폴더가 생겼고 무인자 열거가 양쪽을 다 셌다).
  inject.py가 이름으로 합치고 주입 후 `MOD:` 섹션 중복을 확인하지만, 주입 출력에
  같은 파일이 두 번 보이면 그 자리에서 멈춰라.
- **모드 .rb는 루비 1.8.7 문법으로.** 해시 로켓, `alias`. 신형 문법(`key:`, `&.`,
  `%i[]`)은 파싱조차 안 된다. 이 환경에 루비가 없어 구문 검사는 게임 부팅이 대신한다.
- **`Game_Player#update`를 통째로 다시 정의하지 마라.** Walk_Run(22)·Following(187)이
  alias 사슬로 잡고 있어 통째 재정의는 동행을 부순다. 사슬 끝에 alias로 얹는다 —
  본보기: `Better Movements Z/001_Movement.rb`(속도는 `update_move` 직전 표 바꿔치기,
  회전 문턱은 `@lastdirframe`을 과거로 밀기).
- **이동 속도는 `@move_speed`에 직접 박힌다**(setter를 안 지나간다). 걷기 3.8 ·
  달리기/서핑/얼음 4.8 · 자전거 5.2, 프레임마다 `2**눈금` 픽셀.
- **`mod.json`의 `expects`**(섹션 제목 → 원문 md5)를 적어 두면 게임 판이 올라 원문이
  바뀌었을 때 주입기가 멈춘다. 훅이 조용히 어긋나는 것보다 낫다.
- Wishing Star용 모드는 **옮기는 게 아니라 같은 의도를 v16에 재구현**하는 일이다 —
  21.1의 `@move_time`·`System.uptime`·`Battle::Scene` 세대 구조가 v16엔 없다.
  엔진 해부는 [`docs/research/2026-08-01-pokemon-z-fangame.md`](docs/research/2026-08-01-pokemon-z-fangame.md).

## 둘째 게임 — 번역 품질 갈래 (2026-08-01~02)

**걸음 1~4 + 걸음 5의 준비물·파일럿까지 끝났고, 초벌 배치가 2026-08-02에 발사됐다.**
플랜·현황 정본은 [`docs/design/z-translation-quality.md`](docs/design/z-translation-quality.md),
실행 상세는 [`z-batch-run-proposal.md`](docs/design/z-batch-run-proposal.md)(승인 문서 —
범위·모델 설정·비용 실측·인터페이스가 전부 근거와 함께 있다), 전체 그림은
[`z-retranslation-methodology.md`](docs/design/z-retranslation-methodology.md).
검수 재료는 `docs/research/2026-08-01-z-*` 넷과 `2026-08-02-z-*` 넷(말뭉치 전수·
적용 구조·파일럿 비교·파일럿 판정).

**걸음 5의 도구 일습은 `translate/`에 있다** — `voices.md`(말투표 42인, 별칭
병합 `speaker-aliases.json`) · `glossary.md`(고정 용어표 — 포켓프랑·입법관·선장·
그림자 포켓몬·후보생은 2026-08-02 사용자 판정) · `prompt.md`(배치 프롬프트 정본) ·
`validate.py`(7종 게이트 — 파일럿 산출로 보정됨) · `batch.py`(러너: plan/run/status/
redo/apply, 청크 원장 `batch/`). **모델은 gemini-3.6-flash + reasoning_effort=minimal** —
씽킹이 존재 강제이나 양은 조절되고, 실측 A/B에서 품질 동급·비용 3.2배였다. 한 줄짜리
탐침은 effort가 안 듣는 것처럼 보였다 — **작은 표본으로 파라미터를 판정하지 마라.**

**번역 정본은 `translate/ko/`다 — korean.dat는 빌드 산출물.** 절별 JSONL
(한 줄 = 한 문장, 원문 병기)이고 `build.py`로 굽는다(왕복 검증 내장). **dat를 직접
문지르면 직후 `export.py`로 재동기화하라.** apply_* 스크립트들은 정본 도입 이전의
이력이자 재적용 도구다.

**dat로 못 고치는 문자열이 있다** — 플러그인 스크립트에 하드코딩된 화면 문자열
(일시정지 단축키·출현 안내판·배지명). 그런 자리는 `mods/UI Text KR`의 교체표에
한 줄 더한다(그리기 진입점 훅). 조사 자동 선택은 `Josa Select` 모드가 맡는다 —
번역문은 `\j[받침형,무받침형]`을 쓴다.

밟아 둔 사실들:
- `korean.dat`은 Essentials 다국어 포맷(절 24개 = MessageTypes 상수). 대사 쌍은
  OrderedHash의 중첩 Marshal — `fanlib.rubywrite`로 왕복 검증됐다. **갱신할 때마다
  왕복 검증을 다시 하라.**
- **해시 절의 키는 게임의 stringToKey 정규화 모양이어야 한다** — 게임이 조회 때마다
  CRLF·연속 공백을 공백 하나로 뭉개므로, dat 키가 그 모양이 아니면 영원히 안 맞고
  **조용히 스페인어가 나온다**(예외도 로그도 없다). 이 병으로 도달 불가 키 73개를
  2026-08-02에 수선했다 — 원저자가 번역해 두고 몇 년째 안 나오던 배틀 문구 44개 포함.
  `build.py`가 추가 키를 자동 정규화한다. 전모는 적용 구조 조사 문서 §4.
- **스크립트 리터럴에 루비 보간(`#{...}`)이 든 12곳은 번역 불가다** — 런타임 문자열과
  키가 같아질 수 없다. 고치려면 스크립트 수정 모드가 필요하다(미착수).
- **용어 통일은 원문 쪽에서 세라** — 화폐가 포켓코인·쿼트·쿼터 세 갈래, 연금술이
  알케미와 52:57로 갈라져 있었다. 원문 반복어를 캐서 한국어 분포를 재면 바로 나온다
  (2026-08-02 전수: 29,678행에서 판정 5건·스윕 235행).
- **용어 대조의 기준 DB는 세대를 의심하라** — PokéAPI 한국어는 2020년 대개명 이전,
  WS 로케일에도 구명이 남아 있다. 최종 판정은 Bulbapedia `ko=` 칸. 그리고 스페인어
  가짜 친구에 당한 실사례: Cinta Focus=Focus **Band**, Banda Focus=Focus **Sash**
  (기합의띠 맞바꿈 사고 — 사용자 실기 제보로 발견).
- **접두 수식은 후치형 템플릿이다** — `{1} rival`·`{1} salvaje`·`{1} aliado`가
  절23에 따로 서 있고, 여기가 미번역이면 「슬리프 rival」이 나온다.
- 조사 병기는 **괄호 방향이 두 가지다** — `(은)는`과 `이(가)`. 한쪽만 훑으면 남는다.
- **이름을 문자열 자동 매칭으로 치환하지 마라** — 빈도 2·3위 Melia·Olivier가 공식
  캐릭터 스페인어명과 철자만 같은 우연 일치였다. 치환은 확정 명단으로만.
- **창작 지명처럼 보여도 스페인어 정식명 대조부터** — 도시 22곳 중 13곳이 본가
  칼로스 도시의 스페인어 정식명 그 자체였다(Luminalia=미르시티, Yantra=사라시티 …).
  음차로 새 이름을 지은 게 오판이었고 옛 패치의 본가명이 정답이었다(2026-08-02,
  PokeAPI location_names 실측). 대응표는 translate/glossary.md 지명 절.
- 절13(트레이너 클래스)과 절14(이름)가 화면에서 이어져 한 문장을 이루는 자리가 넷 있다
  (Rey de los + Acertijos 등) — 두 칸을 함께 번역해야 한다.
- 조사(助詞) 자동 선택(`\j[은,는]`)은 Z에 없다 — 플러그인을 번역 모드에 포함하기로
  결정(사용자). 표기는 「데미지」, 문구는 현행 세대, 음차는 한국어 어감 우선.
