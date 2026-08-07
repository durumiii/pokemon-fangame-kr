# 웹 수정 스튜디오 (z-kr-studio) — 작업 가이드

포켓몬 Z 한글패치 유저용 브라우저 편집기. 라이브:
https://durumiii.github.io/z-kr-studio/ (Chrome/Edge 전용, 무설정 원칙 —
로그인·설치·설정 없음). 전체 스펙은 repo 루트
`docs/superpowers/specs/2026-08-03-web-fix-studio-design.md`, 작업 이력은
같은 자리 plans 문서.

## 파일 구조

| 파일 | 역할 |
|---|---|
| index.html | 마크업 + CSS 전부 인라인(fixgui.py 다크 테마 이식) |
| app.js | 상태·화면·파일IO·빌드·공유·제보 전부 (~1,000줄) |
| mine.js | [내 수정] 화면 — 대기 중인 수정·메모를 다시 고치고 지운다 (~75줄) |
| hist.js | [이력] 화면 — 동작 묶음으로 세우고 묶음째 되돌린다 (~80줄) |
| event.js | 이벤트 모아 보기 — 카드의 이벤트 칩·자리 목록·이벤트 화면 (~60줄) |
| core.py | pyodide에서 도는 파이썬 — dat 파싱·값 교체·왕복 검증 |
| rubywrite.py, vendor/rubymarshal/ | Ruby Marshal 직렬화(수정 금지 — repo 정본의 사본) |
| speakers.json | 화자 조인표 + 이벤트 자리 축약본(생성물 — `translate/make_speakers.py`로 재생성) |
| tests/selfcheck.js | node 자체점검(DOM·FS·pyodide 목업 위 로직 검증) |
| tests/test_core.py | pytest — 실물 korean.dat 대상(devbox에만 존재, 없으면 skip) |
| publish.sh | 공개 repo(durumiii/z-kr-studio) rsync 배포 + Pages 빌드 명시 발주 |

## 실행·검증·배포

- 로컬: `python3 -m http.server 8788` (이 디렉터리에서) → Windows 브라우저
  localhost:8788. file:// 는 안 됨(showDirectoryPicker).
- 기계 검증(수정 후 필수): `for f in app.js mine.js hist.js event.js; do node --check $f;
  done && node tests/selfcheck.js` → `SELFCHECK_OK`. selfcheck는 **렌더된 HTML
  문자열도 단언**하므로 마크업·클래스를 바꾸면 케이스를 같이 고칠 것.
- 배포: `bash publish.sh` (gh 인증 durumiii). tests·publish.sh는 배포 제외.

## 화면·상태 구조 (UI 수정 시 알아야 할 것)

- 화면은 SPA 없이 `#out` innerHTML 통째 교체 하나로 돈다. 화면 종류:
  홈(renderHome)·검색 결과(card/more)·이력(showHist)·내 수정(showMine)·
  바꾸기(replUI)·복원(restoreMenu)·찾아보기(browse)·이벤트(openEvent/evJump).
  상단 `#meta`가 상태 줄.
- 일괄 바꾸기는 번역 칸에서 찾지만 **원문 조건**(`#rsrc`)을 걸 수 있다 — 스페인어
  원문에 그 말이 없는 행은 빼고, 뺀 행을 목록으로 보여준다(개수만 알리면 조건이
  너무 좁아 놓친 자리를 확인할 길이 없다). 찾을 문구를 비우면 바꿀 것이 없으므로
  **원문 검색**으로 갈라져(srcSearch) 그 행들을 편집 카드로 연다.
- 되돌리기는 [이력] 화면에 산다 — 수정 이벤트에 `op`(동작 표)를 달아 묶고, 그 표가
  없는 옛 이력은 같은 갈래가 잇달아 온 5초 창으로 묶는다. 동작을 만드는 쪽이
  `opBegin('bulk')`/`opEnd()`로 감싼다. 되돌릴 때 **그 뒤에 다시 고쳐진 행은
  건너뛴다**(남의 고침을 지우게 된다). 되돌리기 자체도 한 동작으로 이력에 쌓인다.
- 이벤트 자리는 speakers.json의 `rows[원문][2]` = `[[이벤트, 페이지, 명령순번,
  이벤트이름색인], ...]`. 한 대사가 여러 자리에 걸리면(맵 하나에서만 2,606개)
  칩이 「이름 외 N곳」이 되고 자리 목록을 먼저 보여준다.
- 상태는 전역 `S` — rows(전체 행)·edits(대기 수정 Map)·applied(반영됨 Map)·
  base(순정 .bak 해시 = localStorage 키 기준)·meta/sha. 메모는
  memoIndex()(localStorage memos:<base>). 이력은 hist:<base> append-only.
- 사용자 문자열은 **반드시 esc() 경유**로만 innerHTML에 넣는다(전 화면 이
  규율로 리뷰 통과). 인라인 onclick에는 rid(숫자:콜론 조합)나 인덱스만.
- 제보 중복 방지: 보낸 건은 `sent:<base>`에 rid→서명(제안+메모, NUL 구분)으로
  남고 일괄 제보가 서명이 같은 건을 뺀다. 내용을 고치면 서명이 달라져 다시
  나간다. 이 장치 이전 제보자용 이주 수단이 홈의 [이미 보낸 것으로 표시].
- 버튼 잠금 규율: 빌드↔복원은 상호 잠금, 일괄 제보는 batchInFlight 가드,
  복원 후엔 재로드 성공까지 빌드·내보내기 잠금. 잠금 로직은 건드리지 말 것.
- 제약: 프레임워크·빌드 도구 금지(정적 파일 그대로), 이모지 금지(인라인
  SVG, ICON 객체), UI 문구 한국어, 파일당 800줄 상한(넘으면 분리).

## UI 손질 대기 목록 (리뷰에서 유예된 시각 항목)

- "반영됨" 칩이 절 칩과 같은 .chip 스타일 — 시각 구분 필요
- 바꾸기 화면 체크박스에 공통 input 배경 규칙이 걸림(appearance 확인)
- 가져오기 충돌 화면·[이력]·[내 수정]에서 이전 화면 복귀 동선 없음(재검색만)
- 비활성 primary 버튼 호버가 카드색으로 변함(의도된 선택 — 어색하면
  `button.primary:disabled:hover{background:var(--acc)}`)
- 고아 메모(패치 판 바뀐 rid)의 칩이 "절undefined"로 렌더될 수 있음
- 가져오기 안내가 건너뜀 0건일 때도 "0건 건너뜀" 표기
- 전반적 레이아웃·비중·타이포는 미손질(기능 우선으로 만든 상태)

## 조심할 것

- korean.dat 쓰기 경로(빌드·복원)와 백업(.bak 1회 보존/.prev 매 빌드) 로직,
  core.py의 왕복 검증은 데이터 안전 장치 — UI 작업에서 건드리지 않는다.
- 구글폼 entry ID(app.js 상단 REPORT_FORM)는 실폼과 배선돼 있다. 문항을
  바꾸면 시트 도달을 실측으로 재확인해야 한다(no-cors라 코드로 확인 불가).
- Pages는 푸시로 빌드가 안 돌 때가 있다 — publish.sh가 빌드를 명시 발주하니
  배포는 반드시 스크립트로.
