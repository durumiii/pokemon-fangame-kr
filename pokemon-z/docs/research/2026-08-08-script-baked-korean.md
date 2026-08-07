# 게임 스크립트에 한국어로 박혀 있는 문구 — 전수 (2026-08-08)

제보 「테이블에 없는 스크립트 수정」의 재료다. **번역표(`translate/ko/`)로는 못 고치는
한국어 문장**이 게임의 `Scripts.rxdata` 안에 직접 박혀 있다. 옛 한글패치가 `_INTL(...)`을
거치지 않고 소스에 한국어를 써 넣은 자리들이고, 우리 코어도 그 위에 서 있다.

Z-1(번역표에 키가 없어 **스페인어로 남는** 문구 102종)과는 다른 집합이다. 그쪽은 키가
없어 원문이 나오고, 이쪽은 이미 한국어인데 **정본이 아닌 곳에 있어 고치려면 코어를
다시 구워야 한다**.

## 어떻게 셌나

`/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata`를 `vendor/datread.py`로 열어
MOD 절을 뺀 270개 절에서 「주석이 아닌 줄의 따옴표 안에 한글이 있는 것」을 뽑았다.
재현: `uv run` 한 줄짜리 스크립트로 절마다 `zlib.decompress` 후 정규식 검색.

조사 판정용 내부 문자열(`Josa Select`의 「으로」·「로」)은 화면에 뜨지 않으므로 뺐다.
`PScreen_Summary:342`의 성격 24종은 한 줄에 배열로 들어 있어 한 행으로 묶었다.

## 눈에 띄는 것

- **옵션 화면**(`PScreen_Options`) 설명문 아홉 줄이 전부 여기 있다. 그중
  「배틀 방식을 정한다. **셋 모드**는 난이도가 올라간다.」의 「셋」은 옵션 값
  `Fijo`의 번역(절23 5652행 「셋」)을 가리킨다 — 값은 번역표에 있고 설명문은 없어,
  두 자리가 갈라져 있다. 본가 표기는 「승부방식 — 바꾸기 / 내보내기」다.
- **말투가 섞여 있다.** 대부분 평서·반말인데 `Export to Showdown` 두 줄만
  「덮어쓸까요?」·「~있습니다」로 존대다.
- 미니게임·부화기·제작·인포그래픽처럼 팬게임이 더한 화면은 통째로 이쪽에 있다.

## 전수 (70행)

| 절 | 줄 | 화면에 뜨는 말 |
|---|--:|---|
| `Settings` | 352 | 한국어 |
| `PokeBattle_MoveEffects` | 11 | 하지만 빗나갔다! |
| `PokeBattle_MoveEffects` | 25 | 하지만 빗나갔다! |
| `PokeBattle_Battle` | 2602 | 폭우가 그쳤다! |
| `PokeBattle_Battle` | 2613 | 햇살이 원래대로 돌아왔다! |
| `PokeBattle_Battle` | 2624 | 기묘한 난기류가 잦아들었다! |
| `PokeBattle_Scene` | 2368 | 몬스터볼이 없다. |
| `PokeBattle_Scene` | 2371 | 훔치는 건 도둑이나 하는 짓이다. |
| `PItem_ItemEffects` | 726 | #{pokemon.name}의 능력이 올랐다! |
| `PItem_ItemEffects` | 747 | #{pokemon.name}의 능력이 올랐다! |
| `PScreen_Summary` | 342 | 성격 이름 24종(「노력하는」…「변덕스러운」) — 한 줄에 배열로 |
| `PScreen_Options` | 741 | 게임 음악의 음량을 조절한다 |
| `PScreen_Options` | 743 | 효과음의 음량을 조절한다. |
| `PScreen_Options` | 745 | 대화가 표시되는 속도를 조절한다. |
| `PScreen_Options` | 747 | 포켓몬 애니메이션에 문제가 있으면 이 설정을 끈다. |
| `PScreen_Options` | 749 | 배틀에서 기술 애니메이션을 표시할지 정한다. |
| `PScreen_Options` | 751 | 배틀 방식을 정한다. 셋 모드는 난이도가 올라간다. |
| `PScreen_Options` | 753 | ‘누르기’로 두면 Z키로 계속 달릴 수 있다. |
| `PScreen_Options` | 755 | 게임이 너무 빠르면 수직동기화를 꺼라. 재시작이 필요하다. |
| `PScreen_Options` | 757 | 속도를 바꾸고 몇 초가 지나면 배속 아이콘을 숨긴다. |
| `PScreen_Options` | 759 | 배틀에서 준 데미지를 표시할지 정한다. |
| `PScreen_Storage` | 388 | 거기에는 놓을 수 없다. |
| `PScreen_PurifyChamber` | 498 | 모든 박스가 가득 찼다. |
| `PScreen_PurifyChamber` | 553 | 포켓몬을 들고 있다! |
| `PScreen_PurifyChamber` | 555 | 설정 편집을 계속할까? |
| `PScreen_PurifyChamber` | 611 | 위치를 서로 바꿀까? |
| `PScreen_PurifyChamber` | 633 | 홀로그램 보기를 계속할까? |
| `PBattle_BugContest` | 382 | 안내방송: 삐———! |
| `PBattle_BugContest` | 383 | 시간 종료! |
| `PBattle_BugContest` | 435 | 안내방송: 벌레잡이대회가 끝났습니다! |
| `PMinigame_VoltorbFlip` | 415 | 코인을 하나도 찾지 못했다! 정말 나갈까? |
| `Editor` | 2498 | 이 트레이너 타입을 삭제할까? |
| `Editor` | 2696 | 이 트레이너 배틀을 삭제할까? |
| `Incubadora` | 152 | 이 부화기에는 알이 없다. 하나 넣을까? |
| `Incubadora` | 171 | 고른 포켓몬은 알이 아니다 |
| `Incubadora` | 178 | 이 알을 꺼낼까? |
| `Incubadora` | 199 | 이 포켓몬을 파티에 넣을까? |
| `Incubadora` | 262 | 알을 부화기에 넣을까? |
| `Incubadora` | 284 | 부화기에 빈자리가 없다 |
| `Menu Mejorado` | 1166 | 포켓몬 |
| `Menu Mejorado` | 1317 | 도감 |
| `Menu Mejorado` | 1342 | 포켓몬 |
| `Menu Mejorado` | 1358 | 가방 |
| `Menu Mejorado` | 1372 | 제작 |
| `Menu Mejorado` | 1380 | 업적 |
| `Menu Mejorado` | 1387 | 저장 |
| `Menu Mejorado` | 1399 | 설정 |
| `Menu Mejorado` | 1516 | 배지: #{$Trainer.numbadges} |
| `Menu Mejorado` | 1521 | F1: 조작키 변경 |
| `Menu Mejorado` | 1540 | 최대 레벨: #{caplevel} |
| `FotoRemington` | 7 | F1을 누르면 조작키를 바꿀 수 있다. |
| `Diploma Nuz1` | 7 | 눌록을 완주했음을 증명하는 상장. |
| `Diploma Nuz2` | 7 | 하드 눌록을 완주했음을 증명하는 상장. |
| `DiplomaPokedex` | 5 | 부적이 강렬하게 빛나기 시작한다! |
| `DiplomaPokedex` | 8 | 부적을 들어 올렸지만 아무 일도 일어나지 않았다. |
| `Crafteo` | 780 | 레시피 목록 |
| `Crafteo` | 781 | 위/아래: 레시피 선택 |
| `Crafteo` | 782 | C: 레시피 열기 |
| `Monotype` | 72 | 새 스타팅 포켓몬을 골라라. |
| `Monotype` | 74 | 새 스타팅 포켓몬을 골라라. |
| `Monotype` | 80 | 지금부터 #{type_name}타입 <b>모노타입 도전</b>이 시작된다! |
| `Guia Personajes` | 429 | 인포그래픽 목록 |
| `Guia Personajes` | 430 | 위/아래: 선택 |
| `Guia Personajes` | 431 | C: 열기 |
| `Vsync` | 28 | 게임을 다시 시작할까? |
| `Vsync` | 29 | 나가기 전에 저장할까? |
| `Export to Showdown` | 107 | 게임 폴더에 이미 showdown.txt가 있습니다. 덮어쓸까요? |
| `Export to Showdown` | 158 | 게임 폴더에 showdown.txt를 만들었습니다. 이 파일로 Pokémon Showdown에서 팀을 구성할 수 있습니다. |
| `Sacar Equipo` | 10 | #{pokemon.name}(으)로 정할까? |
| `Sacar Equipo` | 16 | 포켓몬을 골라야 한다! |