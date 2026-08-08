# 텍스트 층·정본·빌드

**범위** — 게임 텍스트가 어디 살고, 어떻게 고치고, 어떻게 빌드·검증하는가.
**여는 때** — 텍스트 문제를 조사할 때(첫 수는 `probe.py`) · 정본을 고쳐 빌드할 때 ·
dat 포맷 문제를 만났을 때.
**다루지 않는 것** — 말투·화자([events-and-speech.md](events-and-speech.md)) ·
표기([names-terms.md](names-terms.md)) · 제보 처리([reports.md](reports.md)).
**전제** — 없음. 층 개념은 이 문서 첫 절이 깐다.

## 개념도 — 층 × 값 판정

텍스트 문제는 「닿는 경로(층)」 × 「값 판정」 2차원으로 떨어진다.
**조사 첫 수는 `uv run translate/probe.py "문구"`** — dat 조회·jsonl·스크립트 소스·canon을
한 번에 훑고 층을 알려준다.

| 층 | 정본 | 도구 |
|---|---|---|
| ① 번역표 (_INTL→korean.dat) | translate/ko/*.jsonl | build.py |
| ② 키 어긋남 (①의 병리) | 〃 + *.add.jsonl | 루비 오라클, export.py |
| ③ 하드코딩 화면 문자열 | mods/UI Text KR 치환표 | modstore 재주입 |
| ④ 런타임 가변 문자열(보간) | share/patch_intl.py EDITS | 소스 수술(멱등) |
| ⑤ 로직-문자열 결합(기능 버그) | 〃 | 〃 (예: 부적 18종) |
| ⑥ 그림에 그려 넣은 글자 (PNG 베이크) | Graphics/Pictures (.orig 짝 = 한글화본) | PIL 재렌더. 텍스트 층 전수 미스면 이 층 의심. 상태이상 아이콘 띠는 `tools/status_icon.py` |

값 판정은 셋뿐: **(A) 본가에 있다 → 판정하지 않고 조회한다**(`translate/canon/canon.jsonl`,
PKHeX 산 — verify가 전수 대조. 이름만 같은 별개 대상은 canon/exceptions.jsonl, 구세대
스페인어명은 canon/aliases.jsonl). **(B) 창작 요소 → glossary.md 판정.**
**(C) 문체·어투 → voices.md.** 전거 서열은 glossary.md 머리.

## 정본과 빌드

**번역 정본은 `translate/ko/`다 — korean.dat는 빌드 산출물.** 절별 JSONL(한 줄 = 한 문장,
원문 병기)이고 `build.py`가 dat로 만든다(왕복 검증 내장). 정본은 원문 하나에 한 줄이 아니라
**(맵, 원문)마다 한 줄**이다.

- **정본을 고치는 도구만 쓴다** — dat를 직접 문지르는 수정은 빌드 한 번에 지워진다.
  부득이 dat를 직접 고쳤으면(웹 스튜디오 등) **`harvest.py`로 회수한다**:
  `uv run translate/harvest.py` → 미리보기, `--write` → 반영. 기준선(그 dat를 만든 배포본)·
  dat·정본 셋을 견주어 **dat에서만 고친 자리**를 가져오고, 정본이 그 뒤 따로 움직인 자리는
  충돌로 알린다. ⚠ **`export.py`로 하지 마라** — 통째 덮기라 정본이 옛 값으로 돌아간다
  (2026-08-08 실측 282행). export는 절 구조를 처음 만들거나 `*.add.jsonl`을 접어 넣는 자리다.
- **`*.add.jsonl`로 새 키를 얹었으면 빌드 뒤 `export.py`로 base jsonl에 접어 넣어라** —
  안 그러면 verify의 절23 미러 대조가 어긋난다.
- 수정 후 `uv run translate/verify.py`, 재배포 전 `--strict`.

## dat 포맷의 함정들

- `korean.dat`은 Essentials 다국어 포맷(절 24개 = MessageTypes 상수). 대사 쌍은
  OrderedHash의 중첩 Marshal — 갱신할 때마다 왕복 검증을 다시 하라(build.py 내장).
- **해시 절의 키는 게임의 stringToKey 정규화 모양이어야 한다** — 루비 `^`/`$`는 줄
  앵커라 `\r\n`은 공백이 아니라 `\n`으로 접히고, 키가 그 모양이 아니면 **조용히
  스페인어가 나온다**(예외도 로그도 없다). 정의는 `build.py string_to_key`(포터블 루비
  오라클로 전량 검증) — 의심되면 probe.py가 이 정규화로 조회해 준다.
- 스크립트 리터럴의 루비 보간(`#{...}`)은 번역표가 원천 불가 — `share/patch_intl.py`
  소스 수술(멱등)에 EDITS로 얹는다. 이름 「동등 비교」가 로직에 박힌 자리도 같은 도구 몫.
- 조사 자동 선택(`\j[받침형,무받침형]`)은 모드가 아니라 **한글패치 코어의 본문 섹션**이다.
  소스 정본 `share/josa.rb`, 코어 반영 `share/bake_josa.py`(수술판·pre-intl.bak 양쪽, 멱등).
  조사 병기는 괄호 방향이 두 가지다 — `(은)는`과 `이(가)`. 한쪽만 훑으면 남는다.
- **접두 수식은 후치형 템플릿이다** — `{1} rival`·`{1} salvaje`·`{1} aliado`가 절23에
  따로 서 있고, 여기가 미번역이면 「슬리프 rival」이 나온다.
- 절13(트레이너 클래스)과 절14(이름)가 화면에서 이어져 한 문장을 이루는 자리가 넷 있다 —
  두 칸을 함께 번역해야 한다.

## 인코딩 딱지 (루비 1.9+ 실행기)

딱지 없는 마샬 문자열은 루비 1.9+ 실행기(runa)에서 `Encoding::CompatibilityError`
크래시·조회 전량 실패를 낳는다(데스크톱 1.8.7은 무영향). `build.py`가 저장 때 딱지를
맞춘다. 반대로 **딱지 붙은 dat는 옛 파이썬 도구를 멈춘다** — 판독은 `vendor/datread.py`
한 자리로 모았고 거기서 딱지를 뗀다. dat에 손으로 넣은 수정의 회수는 `harvest.py`로
한다(`export.py`는 통째 덮기라 정본을 되돌린다).
