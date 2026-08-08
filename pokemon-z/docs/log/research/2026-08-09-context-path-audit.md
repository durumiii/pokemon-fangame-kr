# 작업 갈래별 진입 경로 감사 (2026-08-09)

**무엇을 조사했나** — 2026-08-02~09에 이 저장소에서 실제로 수행된 작업을 갈래로 나누고,
갈래마다 「지금 다시 한다면 어떤 파일을 읽고 들어가야 하는가」와 「지금의 네 층 구조가
거기까지 데려가는가」를 채점했다.

**무엇을 봤나** — 저장소 실물(`git log` 453커밋 · `AGENTS.md` · 지침 여덟 · 대장 셋 ·
`ROADMAP` · 티켓 열둘 · `translate/`·`tools/`·`share/`·`runa/` 스크립트 전수)과, 세션
축약본 아홉(`8f425161` 22M/36,277행 · `451f33c1` 16M/22,797행 · `252a26fa` 15M/16,336행 ·
`0a8da050` 3.5M · `df44e667` 3.2M · `2c053dae` 1.8M · `92367749` 1.4M · `aeb5878b` 6.7M ·
`44bc9b06` 0.7M). 축약은 `~/.claude/scripts/transcript-digest.sh`로 떴다.

**무엇을 못 봤나** — 서브에이전트가 부모에게 보낸 보고는 축약본에 남지 않는다. 그래서
축약본은 「무엇을 하려 했나·왜 그렇게 정했나」의 출처로만 썼고, 「실제로 이행됐나」는
전부 `git log`와 파일 실물로 다시 확인했다. 08-02 이전(다른 저장소에서 돌던 조사)과
`webapp/` 하위 세션은 사정권 밖이다.

**확정도 요약** — 아래 「지침에 뚫린 구멍」의 여섯 항목은 전부 **실측**이다(명령과 출력을
각 항목에 적었고, HEAD `fe63593` 시점에서 다시 확인했다). 갈래별 「그때 무엇에 걸렸나」는
커밋 메시지와 지침 본문에 남은 사고 기록이 근거라 **실측**이되, 그 사고가 세션에서
어떤 순서로 벌어졌는지는 축약본 기반이라 **전언**으로 적었다.

---

## 갈래 1 — 유저 제보를 정본에 넣기

**그때 무엇을 만졌나.** 제보 시트 CLI `tools/sheet.py`, 보관분
`docs/log/reports/설문지 응답 시트*.jsonl`, 그리고 정본 `translate/ko/00-maps.jsonl`이
주된 자리다. 08-07~08-08 나흘에 173건 · 137건 · 114건 · 47건이 들어갔고(커밋
`3e7658d`·`56833ad`·`63e3aeb`, `git log --oneline --all | grep 제보`), 웹 스튜디오로 고친
자리는 `translate/harvest.py`로 회수했다(`85cac72`, 39자리).

**그때 무엇에 걸렸나.** 두 가지가 반복됐다. 하나는 자리 표기의 해석이 절마다 달라
제안이 엉뚱한 자리에 붙는 것이고(맵 대사는 `맵:블록안순번`, 절23은 0-based 줄, 나머지
목록 절은 `i` 필드), 다른 하나는 dat를 직접 고친 것을 `export.py`로 회수하려다 정본이
옛 값으로 통째 되돌아간 것이다(282행, `docs/guides/text-pipeline.md:55-56` 실측 기록).
둘 다 지금은 지침에 박혀 있다.

**지금 다시 한다면 읽을 순서.** `AGENTS.md`로 시작해 제보가 지침 `reports`의 몫임을
확인하고 — `docs/guides/reports.md`에서 시트 명령과 자리 해석 절차를 읽고 — 제안이
말투를 건드리면 `docs/guides/events-and-speech.md`를, 표기를 건드리면
`docs/guides/names-terms.md`를 먼저 연다 — 회수와 빌드는 `docs/guides/text-pipeline.md`.

**지금 구조가 거기까지 데려가나.** 데려간다. 게이트의 ⚠ 한 줄(`AGENTS.md:26`)이
「제보를 그대로 옮겨 넣는 작업도 예외가 아니다」라고 못 박아 말투 지침을 강제하고,
`reports.md`의 「다루지 않는 것」이 말투·표기 지침을 이름으로 가리킨다. 이 갈래는
구멍이 없다.

## 갈래 2 — 말투·격 판정

**그때 무엇을 만졌나.** 정본 `translate/ko/00-maps.jsonl`, 말투 대장
`docs/ledger/voices.md`, 기계용 정본 `translate/voice-prompts.jsonl` ·
`translate/persona-table.jsonl` · `translate/sprite-groups.json`, 격 측정 도구
`translate/register.py`(`axis()`).

**그때 무엇에 걸렸나.** 이 저장소에서 가장 크게 되돌린 자리다. 커밋 `39a4873`
(`git show 39a4873`)이 그 경위를 본문에 적어 뒀다 — 교환 NPC 133줄을 반말로 밀었다가
물렸고, 까닭은 둘이었다. 짧은 NPC 대사의 말투 기준이 **스프라이트 페르소나**라는 것을
모르고 시작했고, 원문의 `tú`를 반말 근거로 읽었다. 커밋 본문의 표현을 그대로 옮기면
「`speakers-register.md`의 「어투의 최종 근거는 원문의 격」은 이름표가 붙은 인물을 다루는
절인데 그것을 잡담 NPC까지 덮는 규칙으로 읽었다」. 같은 종류의 오판이 앞서도 있었다 —
미라 어미 수선 15곳 되돌림(`98a4263`), 멜리아 해요체 다섯 줄 되돌림(`3c00ad7`).

**지금 다시 한다면 읽을 순서.** `AGENTS.md`의 ⚠ 줄이 정본 수정 전에 말투 지침을
읽으라고 막는다 — `docs/guides/events-and-speech.md`를 처음부터 끝까지(이벤트 두 부류를
가르는 첫 절이 나머지 규칙의 뿌리다) — 해당 인물이 이미 정본에 있으면
`docs/ledger/voices.md` — 격을 재려면 `translate/register.py`의 `axis()`이고 오판하는
꼴 넷은 `events-and-speech.md:82` — 뒤집으려는 판정이면 `docs/ledger/quality.md`.

**지금 구조가 거기까지 데려가나.** 데려간다. 사고 뒤에 세운 `events-and-speech.md`가
이름표 인물과 잡담 NPC를 절로 갈라 놓았고, `tú` 함정(122~125행)·두 축이 충돌해 보이는
까닭(154~158행)·이중 말투 인물 아홉의 검사 제외(150~152행)까지 본문에 있다. 이 갈래는
구조가 사고를 흡수한 모범 사례다.

## 갈래 3 — 고유명·용어 표기와 전수 치환

**그때 무엇을 만졌나.** 표기 원장 `translate/canon/names.jsonl`, 치환·검사 도구
`tools/names.py`, 프롬프트용 용어 정본 `translate/term-pairs.jsonl`, 판정 근거
`docs/ledger/glossary.md`. 굵직한 작업은 프랑스어 호칭 음차 통일 151행(`08-04`),
메달→배지 치환과 그 잔재 21곳(`08-03`), 리본 46자리 정식명(`08-07`), 지명 열 자리
정정(`8cd92ec`).

**그때 무엇에 걸렸나.** 「어색해 보이는 표기가 실은 공식 번역명」이라는 함정에 두 번
걸렸다. `Gruta Helada`를 「얼음 동굴」로 고쳤다가 공식명 「프로스트케이브」를 지웠고
(`8cd92ec`가 되돌림), `Sapin` 음차를 「샤핀」으로 바꿨다가 19행을 물렸다(`b8fc5f0`).
번역 칸만 보고 치환해 무관한 낱말까지 갈아엎은 사고도 있었다(「무사히」→「총사히」류).

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/names-terms.md`(첫 절이
「코퍼스 조회부터」라 함정을 앞에서 막는다) — 표기를 뒤집는 것이면
`docs/ledger/glossary.md`의 전거 서열 — 치환은 `tools/names.py rename`.

**지금 구조가 거기까지 데려가나.** 데려간다. `names-terms.md`가 44줄로 짧지만 함정
넷(코퍼스 우선 · 이름만 같은 별개 대상 · 원문 칸으로 치환 · 자동 매칭 금지)을 전부
담고 있고 도구 이름이 본문에 있다.

## 갈래 4 — 본가 자구 대조

**그때 무엇을 만졌나.** 문장 코퍼스 `translate/canon/messages.jsonl.gz`(163,106쌍),
`translate/verify.py`의 `check_canon()`·`check_ribbons()`, 그리고 절별 정본. 전수
측정은 `docs/log/research/2026-08-07-corpus-coverage.md`에 있고, 코퍼스에 걸리는 5,887행
가운데 **1,909행이 본가와 자구가 다르다**는 것이 지금 열려 있는 최대 티켓 Z-2다.
반영한 자리는 전투 문구 32행(`docs/ledger/quality.md`의 「전투 문구를 본가 자구로」 절),
튀어오르기 설명(`4db1c31`), 옵션 화면 배틀방식(`cf870bc`), 교환 NPC 정형 문구의
「귀여워해 줘」·「선두」(`bf093e8`).

**그때 무엇에 걸렸나.** 축약본에서 이 갈래의 되돌림은 못 찾았다(**한계** — 축약본 전수를
다 읽지는 못했다). 다만 실측으로 드러나는 것이 하나 있다. 코퍼스 대조가 자동으로 걸려
있는 범위는 이름 절 다섯과 리본뿐이고 나머지는 조회 전용인데
(`docs/log/research/2026-08-07-corpus-coverage.md`), 그 사실이 지침층에 올라와 있지 않다.

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/text-pipeline.md`의 값 판정
절에서 「(A) 본가에 있다 → 판정하지 않고 조회한다」를 확인하고 — **그다음이 끊긴다.**
지금은 `docs/ROADMAP.md`의 Z-2 근거 링크를 타고
`docs/log/research/2026-08-07-corpus-coverage.md`로 들어가야 절별 수치와 대조 방법
(원문 완전 일치 · 줄바꿈 공백 정규화 · 영어 칸 병용)을 만난다.

**지금 구조가 거기까지 데려가나.** **못 데려간다.** 「자구」라는 말이 게이트와 지침 여덟
어디에도 없다(`grep -c 자구 docs/guides/*.md AGENTS.md` → 전부 0). `names-terms.md`는 제
범위를 「고유명·용어의 표기」로 못 박아 문장 자구를 빼 두었고, `text-pipeline.md`의 (A)
항은 `canon.jsonl`(이름표)과 `verify` 전수 대조만 가리켜 문장 코퍼스 쪽은 언급이 없다.
로드맵의 Z-2를 집은 사람만 우연히 닿는다.

## 갈래 5 — LLM 배치 재번역과 검수

**그때 무엇을 만졌나.** `translate/batch_pages.py`·`batch_trainers.py`, 선별
`translate/screen.py`·`screen_llm.py`, 검수 화면 `translate/review_gui.py`, 반영
`translate/apply_verdicts.py`, 판정 원장 `translate/batch/verdicts-*.jsonl`. 08-06 하루에
156커밋이 났고 그 대부분이 「판정 끝난 이벤트 반영 — N이벤트 M행」이다
(`git log --date=short --pretty='%ad %s' --since=2026-08-06 --until=2026-08-07`).

**그때 무엇에 걸렸나.** 도구 자체의 결함 셋이 작업 중에 드러나 그 자리에서 고쳤다.
반영 도구가 주연 산출(`p…`)만 훑고 트레이너 산출(`t…`)을 지나쳐 판정이 조용히 사라진
것(`git log --oneline --all | grep 'p 접두'`), 완료 체크가 이벤트 단위로 잘못 걸려
12이벤트를 되살려야 했던 것, 진도를 판정 수로 세다가 「화면에서 빠진 행」으로 고쳐 센 것.

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/events-and-speech.md`(전제로
걸려 있다) — `docs/guides/retranslation.md` 전문 — 말투 본보기의 정본은
`docs/ledger/voices.md`와 `translate/voice-prompts.jsonl`.

**지금 구조가 거기까지 데려가나.** 대체로 데려간다. `retranslation.md` 103줄에 사정권 ·
프롬프트 규약 다섯 · 선별 두 층 · 반영 규칙 · `p…`/`t…` 함정 · 성적 실측까지 다 있고
전제로 `events-and-speech.md`를 건다. 다만 **보호 목록이 어디서 오는지가 비어 있다** —
아래 구멍 4.

## 갈래 6 — 화자 귀속 도구

**그때 무엇을 만졌나.** `translate/speaker.py`(`scan`·`lines`·`selftest`), 산출
`translate/data/speaker-attr.jsonl.gz`, 익명 화자 판정본
`translate/data/2026-08-06-anon-speakers.jsonl`, 웹용 축약본을 만드는
`translate/make_speakers.py`.

**그때 무엇에 걸렸나.** 이 저장소에서 가장 크게 헛돈 자리다. 옛 조인표
(`map-speaker-join.jsonl.gz`)에는 명령 순서와 분기 깊이가 없어 이름표 상속을 계산할 수
없는데, 그것을 모르고 스프라이트로 화자를 짐작하는 우회로를 썼다 — 이름표 없는 4,265행
가운데 **4분의 3에서 화자가 틀렸다**(`docs/guides/events-and-speech.md:62`, 2026-08-06
실측). 정본과 잇는 열쇠에 줄바꿈이 박혀 있어 그대로 맞추면 스무 줄쯤이 조용히 빠지는
함정도 여기서 나왔다.

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/events-and-speech.md`의
「화자 판정」 절(옛 조인표 금지와 키 정규화가 여기 있다) — 데이터 파일의 자리는
`docs/guides/text-pipeline.md:46`.

**지금 구조가 거기까지 데려가나.** 데려간다. 우회로 금지가 ⚠ 항목으로 서 있고
근거 수치가 붙어 있다.

## 갈래 7 — dat 빌드·인코딩 딱지

**그때 무엇을 만졌나.** `translate/build.py`, 판독을 한 자리로 모은 `vendor/datread.py`,
검증 `translate/verify.py`, 회수 `translate/harvest.py`, 조사 굽기 `share/bake_josa.py`.

**그때 무엇에 걸렸나.** UTF-8 딱지가 양쪽으로 문제를 냈다. 딱지 없는 마샬 문자열이
루비 1.9+ 실행기에서 크래시를 내 딱지를 붙였더니(`08-06`), 이번엔 딱지 붙은 dat를 옛
파이썬 도구가 못 읽어 `build`·`probe`·`verify`가 멎었다(Z-17, `bd3161b`로 판독을
`vendor/datread.py` 한 자리로 모아 해소). 해시 절 키가 게임의 정규화 모양과 어긋나면
예외도 로그도 없이 스페인어가 그대로 나오는 함정도 이 갈래다.

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/text-pipeline.md`(「dat 포맷의
함정들」과 「인코딩 딱지」 두 절) — 조사표가 화면에 보이면 같은 문서의 마지막 절.

**지금 구조가 거기까지 데려가나.** 함정은 데려간다. **환경 전제는 못 데려간다** —
아래 구멍 2.

## 갈래 8 — 웹 수정 스튜디오

**그때 무엇을 만졌나.** `webapp/`의 `app.js`(40커밋) · `index.html` · `mine.js` ·
`hist.js` · `event.js` · `core.py`, 검증 `webapp/tests/`(36커밋), 배포
`webapp/publish.sh`, 화자 축약본 `webapp/speakers.json`.

**그때 무엇에 걸렸나.** GitHub Pages가 통째로 404였고, 원인은 Pages를 켜기 전에 빌드를
발주한 순서였다(`publish.sh` 주석에 실측 기록이 남아 있다). Jekyll이 밑줄 파일을
빼먹어 `.nojekyll`을 넣은 것, 맵 태그 검색이 부분 일치라 `맵:1`이 137까지 걸리던 것도
같은 갈래다.

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/reports.md`의 「웹 수정
스튜디오」 절 — **그다음 `webapp/AGENTS.md`**(파일 구조표와 화면별 규약이 거기 있다) —
스펙은 저장소 루트 `docs/superpowers/specs/`.

**지금 구조가 거기까지 데려가나.** **못 데려간다.** `webapp/AGENTS.md`는 사실상 둘째
게이트인데 이 저장소의 어떤 문서도 그것을 가리키지 않는다 — 아래 구멍 3.

## 갈래 9 — 모드 조립·글꼴·릴리스

**그때 무엇을 만졌나.** 조립기 넷(`runa/make-patch-mod.py`·`make-galmuri-master.py`·
`make-hangul-variant.py`·`make-font-mods.py`), 묶음 `share/make_package.py`, 주입
`inject.py`, 안내문 `share/읽어주세요.txt`.

**그때 무엇에 걸렸나.** 손으로 만든 유일본이 하드링크로 원판과 이어져 있어 복제본을
고치면 원판까지 함께 바뀌었고, 그렇게 「한글패치 코어」의 코어에 주입 섹션 13개가 구워져
있었다(`packaging.md:56`). 글꼴에서 한자를 다 빼면 CJK 기준선이 무너져 한글이 크기마다
다른 높이로 갈리는 것도 실측으로 알아냈다. 릴리스 쪽에서는 v5.2 노트에 커밋 86개·정본
1,384행이 한 줄도 안 실린 사고가 있었다(`release.md:11`).

**지금 다시 한다면 읽을 순서.** `AGENTS.md` — `docs/guides/packaging.md`(전제가
text-pipeline의 층 개념이므로 층을 모르면 그쪽 첫 절 먼저) — 낼 차례면
`docs/guides/release.md`, 그리고 게이트의 「릴리스는 유지자에게 물어보고 낸다」.

**지금 구조가 거기까지 데려가나.** 절차는 데려간다. 다만 근거 기록으로 가는 링크 둘이
파일이 아니라 폴더를 가리켜 실질적으로 끊겨 있다 — 아래 구멍 5.

---

## 지침에 뚫린 구멍

우선순위 순. 각 줄은 「어느 문서의 어느 절에 무슨 한 줄이 없어서 어떤 사고가 날 수
있는가」 꼴로 적었다. 여섯 전부 HEAD `fe63593`에서 다시 확인한 **실측**이다.

**1. `docs/guides/text-pipeline.md`의 「정본과 빌드」 절에 「`build.py`는 모드 보관소와
설치된 게임 두 곳의 `korean.dat`에 곧바로 쓴다」는 한 줄이 없다.**
`translate/build.py:27-28`이 `STORE`(모드 보관소의 한글패치 코어)와 `GAME`
(`/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat`)을 상수로 잡고 193~194행에서 **둘 다에
쓴다.** 미리보기도 플래그도 없다. 지침은 「`build.py`가 dat로 만든다(왕복 검증 내장)」
까지만 적어 두어, 빌드가 저장소 안 산출물을 만드는 일로 읽힌다. 유지자가 설치된 게임의
dat에 손수정을 남겨 둔 상태에서 누가 빌드를 한 번 돌리면 그 수정이 회수 전에 사라진다.
재현: `grep -n "STORE\|GAME" translate/build.py`.

**2. 게이트 `AGENTS.md`의 「언제나 지키는 것」에 「도구 열넷이 설치된 게임 폴더를 직접
읽고 쓴다」는 전제가 없다.**
`grep -ln "mnt/d/Game/" translate/*.py tools/*.py share/*.py`가 열넷을 뱉는다
(`build`·`probe`·`verify`·`harvest`·`export`·`speaker`·`mapscan`·`fill`·`apply_*` 넷·
`status_icon`·`patch_intl`). 경로 자체는 이 기계에서만 참이라 에이전트 메모리
(`local-context`)에 있는 것이 맞지만, **게임이 그 자리에 깔려 있어야 도구가 돈다**는
사실은 저장소를 clone한 쪽에도 필요하다. 지금은 `probe.py`가 아무것도 못 찾을 때
원인이 「그 문구가 없다」인지 「게임이 없다」인지 갈리지 않는다.

**3. `docs/guides/reports.md`의 「웹 수정 스튜디오」 절이 `webapp/AGENTS.md`를 가리키지
않는다.**
`grep -rn "webapp/AGENTS" AGENTS.md docs/`가 빈다. 그런데 `webapp/AGENTS.md`에는 파일
여섯의 역할표와 화면별 규약이 있고, `rubywrite.py`·`vendor/rubymarshal/`이 **수정 금지
(저장소 정본의 사본)**라는 것도 거기에만 적혀 있다. 「스튜디오를 고쳐 달라」는 요청을
받은 사람이 `reports.md`만 읽고 들어가면 그 금지를 모른 채 사본을 고친다.

**4. `docs/guides/retranslation.md`의 「사정권과 갈래」 절에 「보호 목록은
`translate/provenance.py build`가 만든다」는 한 줄이 없다.**
그 절은 `translate/data/protected.jsonl`을 「사정권에서 아예 뺀다」고만 적고
(`text-pipeline.md:47`도 데이터 파일로만 열거한다), 그것을 만드는 도구는 어느 지침에도
없다(`grep -rn provenance AGENTS.md docs/guides/` → 없음). 정작 `provenance.py`의
독스트링은 **「재번역이 덮어쓰면 안 되는 자리를 정하는 데 쓴다」**고 밝히고, 게이트가
요구하는 `Edit-Source:` 꼬리표를 읽어 들이는 유일한 소비자다. 꼬리표 규칙은 문서 넷에
있는데 그 꼬리표를 무엇에 쓰는지는 어디에도 없어, 다음 배치가 낡은 보호 목록으로 돌면
사람이 판정한 자리를 모델이 덮어쓴다.

**5. `docs/guides/packaging.md`의 링크 둘이 파일이 아니라 폴더를 가리킨다.**
75행 「[글꼴 조사 기록](../log/research/)」과 95행 「[출처 조사](../log/research/)」다.
가리키려던 파일은 `2026-08-08-font-three-variants.md`와
`2026-08-08-patch-asset-provenance.md`로 보이는데, 지금은 57개짜리 폴더를 열어 이름으로
짐작해야 한다. 95행 쪽이 특히 위험하다 — 바로 앞 문장이 「패치 자산 182개 중 151개는
재생성이 불가능하다, 지우기 전에 이것을 보라」이기 때문이다. 넓게 보면 조사 기록 57개
가운데 **29개가 게이트·지침·대장·로드맵·티켓 어디에서도 가리켜지지 않는 고아**다.
세는 법: `docs/log/research/*.md`의 파일 이름을 `AGENTS.md`·`docs/guides`·`docs/ledger`·
`docs/ROADMAP.md`·`docs/tickets`·`docs/CHANGELOG.md`에서 문자열로 찾아 하나도 안 걸리는
것을 셌다. 기록층 문서끼리 서로 거는 링크는 세지 않았다 — 여기서 묻는 것은 「일하다
게이트에서 출발해 닿는가」이기 때문이다.

**6. `docs/ROADMAP.md`의 Z-21·Z-22는 근거 링크도 티켓 파일도 없다.**
근거 칸이 각각 「유지자 제보」·「유지자 판단 2026-08-08」 여섯 글자뿐이고
`docs/tickets/Z-21.md`·`Z-22.md`가 없다. 로드맵 제 규칙(「조사할 것이 없는 잔챙이는
티켓 파일 자체가 근거다」)을 스스로 어긴 자리다. Z-22는 「`fixgui.py`를 로컬 스튜디오로」
라는 중간 크기 일감이라, 무엇을 옮기고 무엇을 남길지가 아무 데도 없다.
재현: `ls docs/tickets/ | grep -E 'Z-(21|22)'`.
