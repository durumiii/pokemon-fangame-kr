# 2026-08-18 — harvest 실전 회수 실측 (Z-53 ④)

날짜 박제 — 고치지 않는다. stage0 전환 뒤 처음으로 회수 쓰기를 실물로 돌렸다.

## 무엇을 했나

설치본 dat를 백업(sha256 기록)한 뒤, 웹 스튜디오와 같은 코드 경로(`webapp/core.py`의
load/build)로 맵41 대사 한 줄에 시험 수정을 심고 왕복을 돌렸다.

1. `harvest.py` 미리보기 — 심은 한 줄만 정확히 잡힘(회수 1 · 충돌 0).
2. `--write` — stage0 창구(`put_lines`)를 지나 `stage0/messages.jsonl`에 앉고 emit이
   자동으로 돌아 `ko/00-maps.jsonl`까지 따라옴. gate 검사 6 초록.
3. 되돌리기 — `fix.py`로 원래 값 복원, `build.py` 재빌드(왕복 검증 통과).
4. 잔재 0 — git 깨끗, 설치본·보관소 dat가 백업과 sha256까지 동일.

**판정: 회수 경로는 미리보기·좌표·창구·emit·gate까지 설계대로 돈다.** 실측 1회.

## 수확 — uv 의존 선언 결함

`harvest.py --write`가 이 기계에서 항상 죽고 있었다 — PEP723 헤더가
`["rubymarshal"]`뿐인데 stage0 전환으로 `put_lines`→`edit`→`diff`→`yaml` 사슬이
붙어 `ModuleNotFoundError: yaml`. 미리보기는 그 사슬을 안 타서 지금까지 안 드러났다.
전수 점검에서 같은 누락이 넷 더 나왔다(fill · batch · judge · unified) — 다섯 파일에
pyyaml을 추가하고 harvest `--write`(0건)·unified check로 확인했다. ①-꼬리의
「값 수정 창구 pyyaml 헤더 점검」이 이것으로 닫힌다.

## 한계

표본이 맵 대사 한 줄이다. 목록 절·절23 갈래 줄의 회수, 충돌·빈값 갈래, 여러 줄 동시
회수는 실전을 안 겪었다(`--selftest`가 논리만 덮는다). 웹 스튜디오의 앞단(딱지 처리·
`.prev` 백업)은 이번 경로 밖 — 다음 실제 유저 회수가 그쪽의 시험이다.
