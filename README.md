# pokemon-fangame-kr

포켓몬 팬게임 한국어 패치를 만들고 배포하는 곳이에요. 게임 하나가 폴더 하나예요.

## Pokémon Z Fangame — [`pokemon-z/`](pokemon-z/)

프랑스산 팬게임 Pokémon Z(스페인어판)의 한글패치. 기존 한글패치를 기반으로
전면 재번역(LLM 배치 + 사람 검수)과 조사 자동 선택·UI 한글화 모드를 얹었어요.

- 배포판은 [Releases](../../releases)에서 받아요 — 게임 폴더에 덮어쓰면 끝.
- 번역 정본은 [`pokemon-z/translate/ko/`](pokemon-z/translate/ko/)의 절별 JSONL이고,
  `korean.dat`는 `build.py`로 굽는 빌드 산출물이에요. 오역 제보·수정 PR은 이 파일들로.
- 번역 방식·용어 결정의 기록은 [`pokemon-z/docs/`](pokemon-z/docs/)에 있어요.

## 저작권

게임 본문 텍스트의 권리는 원작 팬게임 제작진에게, 포켓몬 관련 명칭의 권리는
Nintendo/Creatures/GAME FREAK에 있어요. 이 저장소는 비영리 팬 번역이에요.
