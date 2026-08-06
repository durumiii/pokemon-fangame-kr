# 유저 제보와 웹 스튜디오

## 제보 시트 — `tools/sheet.py`

`archive`(보관 + 행 삭제, 겹침 거르기) · `upload`(jsonl → 시트 탭) · `rows` · `set`.
SA `z-sheet@golden-tide-361608.iam.gserviceaccount.com` impersonation(키 없음).

- 시트를 비울 땐 **내용 지우기가 아니라 행 삭제**여야 폼이 다음 응답을 2행부터 쓴다.
- patch 칸 표시는 화면 버튼 이름 그대로 — 「모아서」=모아서 제보, 「일괄바꾸기」=일괄
  바꾸기. ⚠ 옛 제보의 「일괄」은 모아서 제보를 뜻한다.
- 제출 시각은 플레이 시각이 아니다.
- 유지자 본인의 제보자 해시: `u:911f0bab` · `u:8e2a930c`(기기·브라우저마다 늘어난다).

## 웹 수정 스튜디오 — `webapp/`

https://durumiii.github.io/z-kr-studio/ — 브라우저에서 korean.dat를 검색·수정·빌드하는
정적 앱. pyodide로 core.py(build.py 값-교체 이식)를 돌리고, 제보는 구글폼 no-cors
(entry 배선은 app.js 상단, 패치 식별은 `__kr_patch__` 표식+해시 폴백, 제보자는 익명
난수 `u:해시`). 유저 고침 파일(jsonl)은 가져오기로 정본 병합 가능.

- 재배포는 `webapp/publish.sh` — **Pages 켜기를 빌드 발주보다 먼저**(통째 404 이력).
- 화자 조인표 축약본은 `translate/make_speakers.py`가 speakers.json으로 생성 —
  조인표 갱신 시 재생성 후 재배포.
- 검증은 `webapp/tests/`(pytest 실물 dat + node selfcheck). 스펙: `docs/superpowers/`(repo 루트).
