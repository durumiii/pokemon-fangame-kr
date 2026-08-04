# 핸드오프: 한글패치 통합 모드의 슬림화 (2026-08-04, modkit 세션에서)

modkit 실기 세션에서 결정된 방향을 넘긴다. **한글패치 통합 모드(mod.json 카드,
정본 D:\GameVault\mods\Pokemon Z Fangame\한글패치 통합)를 "빠지면 안 돌아가는
최소한"으로 줄이는 작업** — 사용자 지시 원문: "한글패치 모드(조사 등 빠지면 안
돌아가는 최소한만 남기고), UI Text KR (한글패치 대신 스크립트를 건드려야 하는
부분들)".

## 현재 실측 상태 (2026-08-04 밤, modkit 세션)

- 카드: 에셋형 182개 — Audio 17(울음소리), Data 7, Fonts 6, Graphics 151, mkxp.json 1.
- **코어(Data/Scripts.rxdata)는 순정 V2.18 대비 30개 섹션 수정 + 'Josa Select'
  섹션 1개 추가.** MOD:UI Text KR 조립 흔적은 없다(8/3 갱신판에서 이미 씻김 —
  moddiff 실측, added는 Josa Select뿐).
- mkxp.json은 fontSub(전 폰트→Galmuri11 치환)를 실어서 한글 표시에 기능적 필수.
  단 설정 파일 통짜 배포는 위험(같은 날 Wishing Star에서 설정 파일 잔재로 즉사
  크래시 사례 — integerScalingActive+창모드+클릭 = 0으로 나누기).
- 재현: essentials-modkit에서
  `uv run python -c "from modkit import moddiff; ..."` 로 순정 사본
  (C:\Users\durumii\Downloads\Modkit-Test\Pokemon Z V2.18\Data\Scripts.rxdata)과
  카드의 Scripts.rxdata를 diff.

## 작업 내용

> **작업 1 완료 (2026-08-04, 이 프로젝트 세션)** — 분류 정본은
> [`docs/design/z-kr-core-section-triage.md`](design/z-kr-core-section-triage.md).
> 요약: 기능 필수 8자리(33줄)+조사 109줄은 코어에 남고, 22섹션 68줄은 UI Text KR로
> 이관 가능하다(이관 시 수정 섹션 30 → 11). 성격 25종 1줄은 훅이 안 닿아 번역표로
> 올리는 편이 낫다. 아래 1번의 섹션 목록은 그 문서가 대신한다.

1. ~~**30개 수정 섹션의 분류**~~ — 각 섹션이 (a) 조사 시스템 등 기능 필수(빠지면
   게임이 안 돌거나 한글이 깨짐), (b) 단순 문구 조립(하드코딩 문자열 번역)인지
   가른다. 30개 목록(실측): Cambia Habilidades, Crafteo, Diploma Nuz1/2,
   DiplomaPokedex, Editor, Export to Showdown, Following, FotoRemington,
   Guia Personajes, Incubadora, Menu Mejorado, Messages, Monotype,
   PBattle_BugContest, PItem_ItemEffects, PMinigame_VoltorbFlip,
   PScreen_Options, PScreen_PurifyChamber, PScreen_Storage, … (전체는 moddiff로
   재현 — changed 30 + added 1).
2. (b)로 분류된 문구 조립분은 **UI Text KR 모드(주입형)로 이관** — 코어를 덮지
   않고 진입점 교체표로 처리하는 방식. UI Text KR 카드에는 이미
   `requires: ["한글패치 통합"]`이 선언될 예정(조사 의존, 사용자 확정).
3. 한글패치 통합은 (a) 최소분 + 데이터(dat)·그래픽·오디오·폰트만 남긴다.
4. mkxp.json은 fontSub만 필요하므로: 통짜 유지 시 카드 description에 근거 명시
   (modkit 세션이 mod.json.draft에 이미 써 둠), 또는 장기적으로 설정 병합 방식
   검토.
5. 재배포 시 make_package 경로로 manifest 동봉(기존 규율대로).

## 참고

- modkit 쪽 카드 스키마가 통일됐다: name/game/version/summary/description/
  engine/install/created_at·updated_at/requires/conflicts/order/scripts/assets/
  touches/expects/baseline_taken. 재배포물 mod.json도 이 순서를 따를 것.
- 카드 폴더의 mod.json.draft(모범 스키마 초안)가 원본 옆에 있다 — 사용자가
  직접 최종 손질 예정.
- 이 문서의 실측 근거는 essentials-modkit 세션(2026-08-04)의 것. 의문이 생기면
  moddiff로 30초 안에 재현 가능하다.
