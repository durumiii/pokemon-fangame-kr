# pokemon-z — 작업 규율

스페인어 팬게임 Pokemon Z의 한글패치. **번역 정본은 `translate/ko/`**(절별 JSONL,
(맵, 원문)마다 한 줄)이고 `korean.dat`는 빌드 산출물이다.

## 어디를 읽을 것인가 (필요한 것만 연다)

| 하려는 일 | 가이드 |
|---|---|
| 텍스트 문제 조사·수정, 빌드, dat 포맷 | [docs/guides/text-pipeline.md](docs/guides/text-pipeline.md) |
| 화자 귀속, 존대·반말(격) 판정 | [docs/guides/speakers-register.md](docs/guides/speakers-register.md) |
| 주연 대사 재번역 배치, 프롬프트 규약 | [docs/guides/retranslation.md](docs/guides/retranslation.md) |
| 고유명·용어 표기, 전수 치환 | [docs/guides/names-terms.md](docs/guides/names-terms.md) |
| 유저 제보 시트, 웹 스튜디오 | [docs/guides/reports.md](docs/guides/reports.md) |
| 모드 주입(UI Text KR 등) | [docs/guides/mods.md](docs/guides/mods.md) |

**열린 일감의 정본은 [docs/ROADMAP.md](docs/ROADMAP.md)**(티켓), 낸 것과 낼 것은
[docs/CHANGELOG.md](docs/CHANGELOG.md)에 쌓는다. 판정 근거·사고 경위의 원장은
[docs/design/z-translation-quality.md](docs/design/z-translation-quality.md),
조사·실측 기록은 `docs/research/`.

## 언제나 지키는 것

- **조사 첫 수는 `uv run translate/probe.py "문구"`**, 수정 후 `uv run translate/verify.py`,
  재배포 전 `--strict`.
- **정본을 고치는 도구만 쓴다** — dat를 직접 문지르는 수정은 빌드 한 번에 지워진다.
  웹 스튜디오로 dat를 고쳤으면 `uv run translate/harvest.py`(미리보기) → `--write`로
  정본에 회수하고 `build.py`로 다시 내려보낸다. ⚠ 회수를 `export.py`로 하지 마라 —
  통째 덮기라 정본이 옛 값으로 돌아간다.
- **유지자 판정을 반영하는 커밋에는 꼬리표를 단다** — 마지막 줄에 `Edit-Source: human` ·
  `batch` · `bulk-term`. 문장 통째 재작성은 사람과 모델이 텍스트로 구분되지 않으므로
  그때 기록하지 않으면 복원할 수 없다.
- **릴리스는 유지자에게 물어보고 낸다.**
- **문서에 맵 번호를 쓸 때는 이름을 함께 적는다**(`uv run translate/mapname.py 150`,
  일괄 `--tag <문서.md>`).

## 문서 층위 — 깨끗한 문서와 대장을 가른다

**현행 지침만 담는 문서**(이력·경위 금지): 이 문서 · `docs/guides/*` ·
`translate/prompt-pages.md` · `translate/voice-prompts.jsonl` · `translate/term-pairs.jsonl`.
판정 근거·사고 경위·진행 서사는 `docs/research/`와 원장에 적는다.
`translate/voices.md`·`translate/glossary.md`는 근거가 붙는 **판정 대장**이다 —
새 판정은 기계 정본(jsonl)과 대장 두 곳에 함께 적는다.
