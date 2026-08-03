# modkit Phase B 구현 계획 — GUI·exe·배포

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** modkit에 pywebview GUI를 얹고 윈도우 단일 exe로 조립해, 일반 유저가 더블클릭으로 진단→격리→얹기/빼기를 하는 배포물을 만든다.

**Architecture:** `app.py`의 `Api` 클래스(코어 호출 전담, 헤드리스 테스트 가능)를 pywebview JS bridge로 노출하고, 단일 `modkit/web/index.html`(fixgui 다크 테마 재활용)이 화면 3걸음을 담는다. exe는 윈도우 호스트(uv 0.11 + Python 3.13 + WebView2 150 — 2026-08-03 실측)에서 PyInstaller로 조립.

**Tech Stack:** pywebview(윈도우 EdgeChromium 백엔드), PyInstaller, 기존 modkit 코어(Phase A, HEAD 8213b0a).

## Global Constraints

- modkit repo: `/home/durumii/workspace/claude-native/sketches/modkit`. 커밋은 Conventional Commits, 만진 파일만 add.
- Phase A 코어(modstore·manifest·declare·cli)는 수정 금지가 기본 — GUI는 소비자다. 코어 결함을 발견하면 고치지 말고 보고(픽스 라운드에서 결정).
- WSL에서는 pywebview 창을 못 띄운다 — GUI 로직은 `Api` 클래스로 분리해 WSL pytest로 검증하고, 창 실행 실측은 윈도우 호스트에서 PowerShell 절대경로(`/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`)로 한다. WSL 파일은 윈도우에서 `\\wsl.localhost\Ubuntu\home\durumii\...`로 접근.
- 파괴 동사 금지·백업 규율 등 Phase A 안전 규약 그대로.
- 유저 대면 문구는 한국어 해요체, 기술 식별자는 원문.

---

### Task 12: GUI 백엔드 — Api 클래스 (헤드리스)

**Files:**
- Create: `app.py` (repo 루트 — GUI 진입점 + Api)
- Test: `tests/test_api.py`
- Modify: `pyproject.toml` — `[project.optional-dependencies] gui = ["pywebview"]`

**Interfaces:**
- Consumes: `modkit.manifest.capture/load/diagnose/quarantine`, `modkit.modstore.shelf/installed/apply/remove`, `modkit.declare.Blocked`.
- Produces: `Api` 클래스 — 모든 메서드는 JSON 직렬화 가능한 dict를 반환하고 예외를 밖으로 던지지 않는다(`{"ok": False, "error": 사유}`):
  - `Api(store_dir, state_path)` — 보관소 폴더와 상태 파일(최근 게임 폴더 목록) 경로 주입.
  - `pick_folder() -> {"ok", "path"}` — pywebview FOLDER_DIALOG 호출부는 창 없는 환경에서 `{"ok": False, "error": "no-window"}` 폴백(테스트 가능하게 window 주입은 `set_window(w)`).
  - `recent() -> {"ok", "paths": [...]}` / `remember(path)` — 상태 파일 JSON 왕복.
  - `game_status(path) -> {"ok", "title", "installed": [...], "has_manifest": bool}` — installed는 NoBundle이면 [].
  - `diagnose(path) -> {"ok", "intact": n, "known": [[경로,모드]...], "foreign": [...], "missing": [...], "backups": n}` — 게임 폴더 안 `manifest.json`(패치 동봉 규약 이름) 요구, 없으면 `{"ok": False, "error": "매니페스트가 없어요..."}`.
  - `quarantine_foreign(path) -> {"ok", "moved": n, "box": 경로}` — 직전 diagnose의 foreign을 다시 계산해 격리.
  - `mods(path) -> {"ok", "installed": [...], "available": [{"name","description","installed": bool}...]}` — shelf를 게임 제목으로 거른다.
  - `apply_mod(path, name, force=False)` / `remove_mod(path, name)` — 성공 시 `{"ok": True, "did", "warnings": [...]}`, Blocked면 `{"ok": False, "blocked": [...사유]}`.
  - `import_zip(zip_path) -> {"ok", "name"}` — mod.json 든 zip을 보관소에 해제(zip 루트 또는 1단계 하위에서 mod.json 탐색, 게임 하위폴더로 배치, 경로 탈출 zip 항목 거부).
- 행동 로그: 상태 변경 메서드는 게임 폴더의 `modkit-log.jsonl`에 한 줄 append(시각·행동·대상).

- [ ] **Step 1: 실패하는 테스트 작성** — Api를 tmp 게임·보관소로 생성해 위 계약을 검증. 최소 케이스: recent 왕복 / game_status(주입형 픽스처 재사용) / diagnose 매니페스트 없음 에러·있음 판정 / quarantine_foreign 후 재진단 깨끗 / apply·remove 왕복과 Blocked의 `{"ok": False}` 변환 / import_zip 정상·경로 탈출 거부 / 로그 append. 픽스처는 tests/test_inject.py 헬퍼 재사용.
- [ ] **Step 2: 실패 확인** (`uv run pytest tests/test_api.py -v`)
- [ ] **Step 3: app.py 구현** — Api는 순수 파이썬(웹뷰 임포트는 `main()` 안에서 지연). `main()`: 인자 있으면 `modkit.cli.main`으로 위임, 없으면 pywebview 창 생성(`webview.create_window("modkit", "modkit/web/index.html", js_api=api)` + `webview.start()`).
- [ ] **Step 4: 통과 확인** (전체 스위트 24+신규)
- [ ] **Step 5: Commit** — `feat: GUI 백엔드 Api — 진단·격리·모드 서랍·zip 반입(헤드리스)`

### Task 13: HTML UI + 윈도우 창 실측

**Files:**
- Create: `modkit/web/index.html` (단일 파일, 인라인 CSS/JS — fixgui 팔레트 재활용: `pokemon-z/translate/fixgui.py` 58~70행의 :root 변수)
- Modify: `app.py` (창 옵션·아이콘·타이틀 다듬기)

**Interfaces:**
- Consumes: Task 12 Api 전 메서드(`window.pywebview.api.*` — 전부 Promise).
- Produces: 화면 3걸음 — ① 폴더 화면(최근 목록 + [폴더 선택]) ② 진단 화면(신호등 요약, foreign 목록, [격리 후 계속]이 기본 버튼·[그냥 계속]·[돌아가기]) ③ 모드 서랍(설치/미설치 목록, 행마다 [얹기]/[빼기], warnings 토스트, zip 드래그앤드롭→`import_zip`). 매니페스트 없는 게임은 ②를 건너뛰고 안내 배너만.

- [ ] **Step 1: index.html 작성** — 한 파일, 프레임워크 없음. 드래그앤드롭은 File 객체 경로를 pywebview가 못 주므로 `webview.windows[0].create_file_dialog` 폴백 버튼 병행(드롭 존은 안내+버튼).
- [ ] **Step 2: WSL 정적 검증** — Api 메서드명·인자 대조(grep), HTML lint 수준 확인. JS의 모든 api 호출이 Task 12 계약에 존재하는지 목록 대조를 보고서에.
- [ ] **Step 3: 윈도우 창 실측** — PowerShell로: `uv run --with pywebview python \\wsl.localhost\Ubuntu\...\app.py`를 백그라운드 기동, 10초 뒤 프로세스 생존 확인 후 종료(창이 뜨고 즉사하지 않는지). 로그·스크린샷은 가능한 수단으로, 안 되면 생존 확인만으로 기록.
- [ ] **Step 4: Commit** — `feat: GUI 화면 3걸음 — 폴더·진단 신호등·모드 서랍`

### Task 14: exe 조립 (build.py)

**Files:**
- Create: `build.py` (WSL에서 실행하면 PowerShell을 통해 윈도우 쪽 빌드를 오케스트레이션)
- Create: `docs/build.md` (수동 재현 절차)

**Interfaces:**
- Produces: `dist/modkit.exe` (onefile). 콘솔 정책: `--windowed` + 시작 시 인자가 있으면 ctypes `AttachConsole(-1)`로 부모 콘솔에 붙어 CLI 출력(안 되면 CLI는 출력 파일 안내). GUI 유저에겐 콘솔 창이 안 뜬다.

- [ ] **Step 1: build.py 작성** — 절차: ① 소스를 윈도우 임시 폴더로 복사(UNC 경로 빌드 회피, `C:\Users\durumii\AppData\Local\Temp\modkit-build\`) ② `uv run --python 3.13 --with pyinstaller --with pywebview pyinstaller --onefile --windowed --name modkit --add-data "modkit/web;modkit/web" app.py` ③ 산출 exe를 WSL 쪽 `dist/`로 회수, 크기·해시 출력 ④ 임시 폴더 정리.
- [ ] **Step 2: 빌드 실측** — 실행해 exe 산출(크기 기록). 실패 시 오류를 그대로 보고(고치되 PyInstaller 옵션 범위 안에서).
- [ ] **Step 3: exe 스모크** — PowerShell로 `modkit.exe shelf --store <빈 폴더>`(AttachConsole 경로), GUI 기동 10초 생존 확인. 결과를 docs/build.md에 기록.
- [ ] **Step 4: Commit** — `feat: 윈도우 onefile exe 조립 — build.py`

### Task 15: 배포 준비

**Files:**
- Create: `README.md` (modkit repo — 유저용 빠른 시작·제작자용 카드 규약 요약·SPEC 링크)
- Modify: `pokemon-fangame-kr/pokemon-z/share/make_package.py` — 패키지에 `manifest.json` 동봉 단계
- Create: `pokemon-fangame-kr/pokemon-z/share/make_manifest.py` 또는 make_package 내 함수 — **v5 적용 완료 상태**의 게임 폴더에서 capture(기준은 클린 원본이 아니라 "패치가 완성된 상태" — 유저 진단 목적이 "v5가 제대로 깔렸고 잔재가 없나"이므로)

**Interfaces:**
- Consumes: modkit.manifest.capture (fanlib 심 경유 또는 MODKIT 경로 임포트).

- [ ] **Step 1: README 작성** (한국어; 영어 요약 절 하나).
- [ ] **Step 2: make_package에 매니페스트 단계** — full/debug/clean 각 variant 조립 직후 스테이징 폴더 자체를 capture해 `manifest.json`으로 동봉(variant마다 제 상태가 기준). 소요 시간은 스테이징(ext4)이라 drvfs보다 빠를 것 — 실측 기록.
- [ ] **Step 3: v5 자산 재조립·검증** — 3종 zip 재생성, zip 안 manifest.json으로 `modkit diagnose` 자기 검증(전부 intact). **릴리스 업로드는 하지 않는다** — 사용자 확인 후.
- [ ] **Step 4: GitHub 공개 준비만** — repo 공개(gh repo create)와 갤러리 안내문은 사용자 결정 게이트로 남기고, 초안 텍스트만 docs/에 둔다.
- [ ] **Step 5: Commit** (modkit repo와 pokemon-fangame-kr repo 각각)
