# Z-47 잡담 라운드 — 전량 배치·선별·선판독 경위 (2026-08-13)

전량 배치 2,221행(1,144페이지, pack 15 + flex, $0.905, 반려 0)의 신판 694행을
세 바퀴로 갈랐다. 행별 판정은 [z47-triage-verdicts.jsonl](../../../translate/batch/z47-triage-verdicts.jsonl)
(694행 — apply 568 · reject 115 · human 11, src 칸이 판정 바퀴).

## 선별·선판독 구성

1. 기계 선별(screen.py) 24 · 원문 대조 LLM(screen_llm) 42 · 격 전환 검사 127 →
   걸린 행 합집합 175. LLM 선별은 flex 지연으로 1차 중단·재실행($4.97, 부분 저장
   없던 옛 설계로 절반치 소실 — screen_llm에 부분 저장·재개·병렬 4워커를 이때 넣음).
   ⚠ 유지 행 1,527행까지 태운 것은 낭비였다 — 같은 급 모델의 유지 행 재검은 정보
   가치가 없다(유지자 지적). 유지 행 지적 61건은 신뢰 낮음 표시로
   [kept-row-flags-z47.jsonl](../../../translate/batch/kept-row-flags-z47.jsonl)에 격리.
2. 무신호 519행: opus 선판독 2기 → pass 438 · suspect 81.
3. 걸린 175행 + 의심 81행: opus 재판정 3기(정본 — glossary·voices·persona-table·canon
   — 을 열어 apply/reject/human) → 최종 apply 568 · reject 115 · human 11.

검수 스튜디오 최종판은 reject+human 126행만 실었다(translate/batch/z47-final-review/,
사유는 screen-verdicts.jsonl — 「반려 추천/판정 필요: 사유」).

## 라운드에서 잡힌 구조 결함과 수선 (전부 이날 커밋)

- **용어 SoT 위반**: batch_pages TITLES 하드코딩이 8/9 「올리비에=박사」 판정을 놓쳐
  회귀 2건 + bastión 규칙 부재 1건. TITLES 해체·term-pairs 이관(aa7cfa1), 전수
  감사는 [Z-53](../../tickets/Z-53.md).
- **프롬프트 결함**: 버킷 코드(B1~B7) 무정의 전량 노출 831회 → 자연어화, 빈 화자
  「(화자 미상)」 명명, 대소문자 중복 접기 가드(5275415).
- 배치 요청 묶음(--pack)·flex 티어로 비용 88% 절감 실측(fbe1796).

## 남는 한계 (반영 때 참고)

- 총사 퀴즈 9행의 합쇼 전환 apply는 「보고체 합쇼체」가 청자 무관이라는 해석에 기댐.
- 한국어 감각 의존 reject 2건(133:26:0:6 밈 연상 · 9:18:0:1), 정본 조문 아님.
- 같은 원문·같은 맵 짝 4건은 반영 때 승자 지정 필요, apply 후 낱말 손질 셋과 이웃
  행 격 정리 1건 — 행별 why에 적혀 있음.
- 비용 합계 ~$6.5 (배치 0.9 + 선별 5.5 + 서브들). 선별 낭비분 ~$3 포함.
