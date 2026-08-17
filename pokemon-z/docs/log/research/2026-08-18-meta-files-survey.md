# 판정 메타 여섯 파일 전수 조사 — 스키마·생산자·소비자 (Z-53 흡수 재료)

2026-08-18, 서브에이전트 조사 + 메인 실측 보완. 흡수 실행은 같은 날 커밋
(`a6f614b`)이고, 이 문서는 그 판단이 딛은 관측의 박제다.

## 요약표

| 파일 | 행 | 열쇠 | 생산자 | 소비자 | 재생성 |
|---|---|---|---|---|---|
| protected.jsonl | 1,768 | (map,event,page) | `provenance.py build`(전체 재작성) **+** `apply_verdicts.py lock_pages`(append) | `batch_pages.protected_pages/excluded_pages` — 사정권 제외 | 혼합(아래 결함 후보) |
| approved-lines.jsonl | 999 | (map, fold(es)) | 미발견 — 사람/스튜디오 추정 | `batch_pages.approved_set/approved_samples` — 자동 채택 금지·말투 본보기 | 사람 원본 |
| approved-events.jsonl | 448 | (map,event) | `apply_verdicts.record_applied`(append) | `batch_pages.approved_events` · `review_page.applied_events` — 재전송 금지 | 기계 append |
| frozen-keys.jsonl | 54 | es 전역 | 미발견 — 사람 추정 | `batch.frozen_keys` — 절23 재번역 금지 | 사람 원본 |
| register-ok.jsonl | 11 | (map[,event][,page][,cmd]) 부분 | 사람 등재(register 보고서 보고) | `register.py` 오탐 억제 · `stage0/materials.py` 표시 | 사람 원본 |
| z4-excluded.jsonl | 98 | (map,event,page) | 사람 3치 전수 판독(2026-08-13, Z-4) | `batch_pages.excluded_pages` — 재번역 대상 아님 | 사람 원본, 재생성 불가 |

## 메인 실측 (조인율·중복)

- approved-lines: (map, norm(es)) 조인으로 **999/999** stage0 자리 매치. `fold`와
  stage0 `norm`은 같은 정의다(공백 접기+strip).
- approved-events: 448/448 이벤트가 stage0에 실재.
- frozen-keys: 54/54가 절23 자리에 정확 매치.
- z4-excluded 98페이지 → stage0 자리 548개: 층 N 542 · **PS 5 · PC 1**. 어긋난
  6자리는 전부 Z-4 판독 사유가 붙어 있었고(AZ 회상 내레이션 자막 5 · 맵261 숙박
  지문 1) overrides로 층 N 실행했다.
- `본보기` 칸은 999행 중 **21행에만 명시**(True 2 · False 19). 서브 보고의 「전
  999행 명시」는 오류였다 — 없음(자동 선별)과 False(명시 제외)는 의미가 다르다.
- approved-events 448행 중 18행은 `src` 없이 `note`만 있다(npc 파일럿 3차).

## 흡수 판정 (2026-08-18)

- **흡수함**: 승인 줄 → 값 항목 `state=reviewed`·`by=human/<src>`·`sample`(명시만).
  승인 이벤트 → 자리별 항목(공유 값이 승인 안 된 자리로 새지 않게, 줄 승인 우선).
  동결 → 절23 값 `by=human/frozen-keys`.
- **지금 안 함(사유 있는 유예)**:
  - protected — 페이지 단위 **파생 캐시**다(원천은 커밋 이력·제보 시트). 행 단위
    진실 없이 페이지 전체를 reviewed로 찍으면 과잉 주장. 주도권 이전 때 fixlog·커밋
    이력에서 **행 단위 by**를 직접 찍는 것이 맞다(Z-54의 provenance 칸 설계와 합류).
  - register-ok — 격 검사기 allowlist. 소비자(register.py)가 stage0를 읽게 될 때
    자리 칸으로 옮긴다. 지금은 materials.py가 원본을 잘 읽는다.
  - z4-excluded — 층 정보는 542자리가 이미 N이라 중복, 정보량은 어긋난 6자리뿐
    (실행 완료). 파일 자체는 배치 사정권 필터의 원천으로 잔류.

## 결함 후보 (Z-54 재료)

`protected.jsonl`은 `provenance.py build`가 **전체 재작성**하는데
`apply_verdicts.lock_pages`가 **append**도 한다 — build를 다시 돌리면 lock_pages가
붙인 행이 커밋 이력·제보 시트에 안 잡히는 한 사라질 수 있다(미검증, 코드 구조
관측만). 같은 이벤트가 approved-events에도 등재돼 사정권 제외는 이중으로 가려져
있어 실해가 드러나지 않았을 수 있다.

## 한계

- 「생산자 미발견」은 `.py` grep 무결과에 기댄 부정 증거다 — 스튜디오(웹 UI) 코드는
  안 읽었고, approved-lines는 스튜디오가 생산자일 가능성이 높다(retranslation.md
  「고른 줄은 승인 줄에 합친다」).
- z4-excluded는 두 지침 문서 어디에도 언급이 없다 — 규율이 batch_pages.py docstring에만
  산다(지침 승격 후보).
