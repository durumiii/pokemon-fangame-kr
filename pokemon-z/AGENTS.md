# pokemon-z — 작업 규율

스페인어 팬게임 Pokemon Z의 한글패치. **번역 정본은 `translate/ko/`**(절별 JSONL,
(맵, 원문)마다 한 줄)이고 `korean.dat`는 빌드 산출물이다.

**작업 범위** — 번역이 제대로 되기 위한 수정까지가 이 프로젝트의 일이다. 엔진·원작
버그는 진단을 표면화하는 데까지만 하고, 기능 수정은 원인 확정 뒤 유지자 판정으로 한다.

## 손대기 전에 읽는다

**시작 보고에 무엇을 읽었는지 적는다.** 안 읽고 시작한 것이 거기서 드러난다.
아래 표는 자주 가는 길일 뿐이다 — 개념이 낯설면 그 개념을 다루는 가이드부터 연다.
각 가이드 머리의 개요(범위 · 여는 때 · 다루지 않는 것 · 전제)가 열지 말지를 알려 준다.

| 가이드 | 다루는 것 |
|---|---|
| [events-and-speech](docs/guides/events-and-speech.md) | 이벤트·텍스트의 종류, 화자 판정, 말투 배정 |
| [text-pipeline](docs/guides/text-pipeline.md) | 텍스트가 어디 살고 어떻게 고치고 빌드하나 |
| [names-terms](docs/guides/names-terms.md) | 고유명·용어 표기, 전수 치환 |
| [retranslation](docs/guides/retranslation.md) | LLM 배치 재번역, 프롬프트 규약 |
| [reports](docs/guides/reports.md) | 유저 제보 시트, 웹 스튜디오 |
| [packaging](docs/guides/packaging.md) | 모드 조립·주입, 글꼴 모드 |
| [release](docs/guides/release.md) | 릴리스 노트, 자산 진열 |

⚠ **`translate/ko/*.jsonl`(번역 정본)은 events-and-speech를 읽기 전에 고치지 않는다.**
제보를 그대로 옮겨 넣는 작업도 예외가 아니다 — 제보가 건드리는 것이 말투일 때
그 판이 어디서 갈리는지 모르면 반영이 곧 사고다(2026-08-08, 133줄 되돌림).

## 문서 네 층

| 층 | 무엇 | 생명주기 |
|---|---|---|
| 게이트 | 이 문서 | 구조가 바뀔 때만 |
| 지침 | `docs/guides/` | 현행만. 낡으면 고쳐 쓴다. 이력·경위 금지 |
| 대장 | `docs/ledger/` — [glossary](docs/ledger/glossary.md)(표기) · [voices](docs/ledger/voices.md)(말투) · [quality](docs/ledger/quality.md)(그 밖의 판정) | **왜 그렇게 정했나**만. 뒤집히면 옛 판정을 남기고 새 항목. 새 항목은 위로 쌓는다 |
| 기록 | `docs/log/` (research · reports · attic) | 날짜 박제. 고치지 않는다 — 틀렸으면 새 파일에서 바로잡고 링크 |

열린 일감은 [docs/ROADMAP.md](docs/ROADMAP.md)(티켓 — 한 줄 + 근거 링크, 세부는
`docs/tickets/Z-번호.md`), 낸 것과 낼 것은 [docs/CHANGELOG.md](docs/CHANGELOG.md).
지침을 고칠 때 이력이 지워지는 것을 망설이지 마라 — 이력은 기록층에 있다.

**대장은 일하다 여는 곳이 아니다.** 지금 지켜야 할 규칙은 지침에, 지금 할 일은
로드맵에 있다. 대장은 이미 정한 것을 **뒤집으려 할 때** 근거를 보러 가는 곳이다.
규칙을 찾다가 대장을 열고 있다면 대개 지침이 빈 것이니, 찾은 것을 지침으로 올려라.

**지침 문서의 개요 규약** — 머리에 네 줄: **범위**(무엇을 다루나) · **여는 때**(어떤
상황에서 필요한가) · **다루지 않는 것**(그리고 그건 어디 있나) · **전제**(먼저 알아야
할 개념). 새 지침을 만들면 이 개요와 위 표의 한 줄이 곧 게이트다 — 중앙 목록을
따로 관리하지 않는다.

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
- **유지자가 판정할 자리는 재료를 갖춰 내놓는다** — 원문 · 앞뒤 대사(페이지 전문) ·
  현행 번역 · 제안 · 판단 근거. 근거가 확정돼 보여도 유지자 승인 전에 정본에 넣지
  않고, 승인받은 계획의 전제가 뒤집히면 다시 확인받는다.
- **릴리스는 유지자에게 물어보고 낸다.**
- **문서에 맵 번호를 쓸 때는 이름을 함께 적는다**(`uv run translate/mapname.py 150`,
  일괄 `--tag <문서.md>`).
