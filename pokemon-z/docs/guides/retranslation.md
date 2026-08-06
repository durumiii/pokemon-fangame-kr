# 주연 대사 재번역 — `translate/batch_pages.py`

단위는 **이벤트 페이지**(장면 하나). `plan [--pilot]` · `run [--pilot] [--fresh]` ·
`samples <이름>`(본보기 확인) · `report`. 배치 모델은 gemini-3.6-flash +
reasoning_effort=minimal. **작은 표본으로 파라미터를 판정하지 마라.**

## 사정권과 갈래

- **같은 (맵,원문)은 한 번만 번역한다** — 정본에 한 줄뿐이라 여러 자리에서 물으면 답이
  갈리고 마지막 것만 남는다. 남길 자리는 가장 큰 페이지(문맥이 많은 쪽).
- **갈래는 승인 줄(`docs/research/approved-lines.jsonl`)로 가른다** — 있으면 교정판
  (A: 현행을 함께 줌), 없으면 새 번역(B: 스페인어만 줌).
- 세 층을 구분한다: **보호**(`protected.jsonl`)는 사정권에서 아예 뺀다 · **승인 줄**은
  사정권에 남되 자동 채택 금지, 말투 본보기의 원천 · 그 밖은 자유.
- 유지자 판정 반영 커밋에는 `Edit-Source: human` 꼬리표. 고른 줄은 승인 줄에 합친다
  (`{"map","es","ko","who","src"}`).

## 마크업은 전부 기계 몫

서식 태그(`<b>`·`<i>`·줄 안 `\c[n]`)와 줄머리 화자 표기는 떼고 민글만 보낸 뒤 원문 쪽
표시 순서대로 되입힌다(`unmark`/`remark`/`split_head`). 되입히는 열쇠는 그 줄 자신의
현행 번역이고, 못 찾으면 원문 그대로 남은 삽입구도 찾아본다. **모델에게 태그를 시키지
마라** — 뜻이 없는 자리라 빠뜨리거나 없던 곳에 지어 붙인다. 모델이 화자 표기를 흉내
내면 그 화자의 이름일 때만 기계가 뗀다(`strip_fake_head`).

## 프롬프트 정본 규약

말투는 `translate/voice-prompts.jsonl`, 용어는 `translate/term-pairs.jsonl`, 본문은
`translate/prompt-pages.md`. **md 대장(voices.md·glossary.md)에서 표를 파싱해 프롬프트에
넣지 않는다** — 대장은 근거가 붙는 사람용이다. 새 판정은 jsonl과 대장 두 곳에.

1. **역사·행 수·판정 날짜를 넣지 마라** — 받는 쪽은 맥락이 없다.
2. **말투는 형용사보다 본보기가 정확하다** — 승인본에서 하대·존대를 섞어 뽑는다
   (`approved_samples`). 한쪽 격만 보이면 산출이 그쪽으로 쏠린다. 본보기는
   `"본보기": true/false`로 박거나 뺀다 — **뽑는 줄이 결과의 전부다.**
3. **이야기의 전후를 조건으로 쓰지 마라** — `[맵>=147] …` 꼴로 적고 장면의 맵 번호로
   미리 풀어 해당 절만 보낸다(`resolve_conditions`).
4. **금지 예시를 쓰지 마라 — 원하는 대체 표현을 예시로 준다.** 금지문에 든 문구는
   산출에 그대로 샌다.
5. 용어집은 그 장면에 나오는 항목만 발췌한다(`glossary_for`). 지명도 고유명이다 —
   표에 없으면 새로 음차된다. 장면의 고유명은 현행 번역의 `<b>` 짝에서도 캔다.

## 산출 선별 — 사람이 볼 행만 추린다

전량 실행에서 행마다 사람이 판정할 수는 없다. **`uv run translate/screen.py <out-dir>`**가
기계로 잡히는 이상 신호(중복어 · 의성어 변경 · 용어 이탈 · 금지 호칭 · 경칭 추가 ·
존칭 「~님」 변화 · 라틴 문자 추가/소실 · 길이 급감 · 기계 반려)를 걸어
`<out-dir>/screen.jsonl`로 추린다(2차 파일럿 실측: 133행 중 12행, 기계로 잡히는
문제 행의 대부분을 포함). **밋밋한 재작성 같은 취향 층은 여기 안 걸린다** — 그건
승인 줄 보호·실기·제보 몫이다. 자동 채택 전에 선별분만 사람이 본다.
비문·사실 왜곡 같은 의미 층 선별은 정규식으로 안 된다 — 모델 선별 층을 얹으려면
충분히 강한 모델과 effort가 필요하고 아직 미검증이다(같은 정답지로 재면 된다).

## 근거 문서

- 선행 연구 대조: [`../research/2026-08-06-translation-prompting-research.md`](../research/2026-08-06-translation-prompting-research.md)
- 판별자(LLM-as-judge) 실측·재시도 설계: [`../research/2026-08-06-discriminator-pilot.md`](../research/2026-08-06-discriminator-pilot.md)
- 파일럿 판정 이력·방법론: [`../design/z-translation-quality.md`](../design/z-translation-quality.md)
