# 모드 조립·주입

**범위** — 코드 모드 주입, 한글패치 모드·글꼴 모드의 조립, 게임에 얹고 빼는 규율.
**여는 때** — `mods/`·`runa/`·`share/`를 건드릴 때 · 모드 설치가 이상하다는 제보를
받았을 때 · 새 모드를 만들 때.
**다루지 않는 것** — 릴리스에 올리는 절차와 자산 진열([release.md](release.md)) ·
번역 텍스트 수정([text-pipeline.md](text-pipeline.md)).
**전제** — 텍스트 층 개념(text-pipeline의 층 × 값 판정) — 어느 층의 문제인지에 따라
korean.dat로 고칠지 모드로 고칠지 갈린다.

Pokemon Z는 Essentials v16 · 루비 1.8.7 · mkxp-z 구판. 플러그인 묶음이 없어 코드 모드는
`Scripts.rxdata`에 `MOD:<모드명>/<파일명>` 섹션으로 덧붙는다(`Main` 직전, 나중 정의가
이긴다).

**설치·제거는 essentials-modkit으로 한다**(`~/workspace/claude-native/sketches/essentials-modkit`).
모드 하나만 얹고 내리므로 다른 모드를 건드리지 않고, 기준선 대조·백업·겹침 안내가 붙는다.
저장소의 모드 폴더를 그대로 보관소로 넘긴다:

    cd ~/workspace/claude-native/sketches/essentials-modkit
    uv run python -c "from modkit.cli import main; main(['apply','<모드명>','/mnt/d/Game/Pokemon Z/V2.18','--store','<모드 폴더의 부모>'])"

`lint`(카드·스크립트 검사) · `remove` · `shelf`도 같은 자리에서 부르고, 새 모드의 뼈대는
`modkit new`가 만든다. 판이 어긋나 멈추면(BaseChanged) 경고를 읽고 `--force`로 강행한다.

⚠ **새 모드는 보관소에 복사해야 사용자의 모드 서랍에 보인다.** `--store`를 저장소 쪽으로
돌려도 게임에는 잘 얹히지만, 라이브러리는 보관소만 본다. 저장소에서 짓고 보관소
(`/mnt/d/GameVault/mods/Pokemon Z Fangame/<모드>/`)로 복사한 다음 그 보관소를 `--store`로 얹는다.

**repo에 남는 모드는 넷이다.** `UI Text KR`(스크립트에 박힌 화면 문자열은 korean.dat로
못 고쳐서 그리기 진입점에서 갈아 끼운다 — 텍스트 층 ③) · `Type Matchup Z`(기술 선택창
상성 색칠) · `Debug Toggle Z`(W키로 `$DEBUG` 토글, 디버그 중 전투 후 전원 회복) ·
`Native Tilemap`(맵 렌더러를 엔진 내장으로 — Joiplay 렌더 깨짐 우회, Z-35).
셋은 커뮤니티 배포판에서 떼어 오거나 착안한 것이라 출처가 이 저장소의 조사에 걸려 있다
([커뮤니티 수정판 조사](../log/research/2026-08-09-community-mods-triage.md) ①·②).
새 주입형 모드의 소스는 이 저장소 `mods/`에 둔다(유지자 판정 2026-08-09).
편의·성능 모드 여섯은 poke-essentials `mod/z/` 몫이다. ⚠ **양쪽 저장소의 `inject.py`는
쓰지 마라** — 기반에서 전부를 다시 짓는 도구라 나열에서 빠진 모드가 결과에서 사라지고,
무인자 전체 재구축은 Controller UX의 `expects`(순정 기준 md5)가 패치판 기반과 어긋나
멈춘다(Z-35에서 실측). 설치는 위의 modkit `apply`가 기준선 대조로 넘어간다.
**한 자리만 얽혀 있다** — 일시정지 단축키 표기를
UI Text KR이 키보드 기준으로 적고 저쪽 `004_PadLabels`가 덮는다. 그 줄을 건드리면 저쪽도 본다.
보관소에는 양쪽 모드가 함께 서 있으므로 주입기를 무인자로 돌리면 전부 세운다.

## 지켜야 할 것

- **같은 모드를 두 번 주입하면 alias가 두 겹으로 걸려 무한 재귀다.** inject.py가 이름으로
  합치고 중복을 확인하지만, 주입 출력에 같은 파일이 두 번 보이면 그 자리에서 멈춰라.
- **모드 .rb는 1.8.7과 3.x의 공통 부분집합으로.** PC는 1.8.7이라 신형 문법(`key:`, `&.`,
  `%i[]`)은 파싱조차 안 되고 **인자 목록의 트레일링 콤마도 SyntaxError다.** 모바일은
  루비 3.1+(mkxp-z)라 반대로 1.8 전용 구문(`when 0:` 콜론, rescue 밖 `retry`)이 즉사하고,
  바이트를 `s[i]`로 읽는 관용구는 String이 나와 어긋난다 — 바이트는 `unpack`으로
  (아래 「신형 루비 실행기 호환」).
- **주입 섹션은 모드명 정렬 순으로 실린다** — 다른 모드의 상수·모듈은 로드 시점에 없을 수
  있다. 참조는 씬 진입 훅으로 미뤄라(로드 시점 `defined?` 분기는 조용히 무동작이 된다).
- **`mod.json`의 `expects`**(섹션 제목 → 원문 md5)는 **순정 기준으로 뜬다.** 섹션 전체를
  보는 값이라 한글패치가 같은 섹션의 다른 문구를 바꾸면 어긋나는데, modkit이 그때
  기준선(`baseline/`)으로 훅 거는 메서드를 다시 대조해 그쪽이 그대로면 경고 한 줄로
  지나간다(2026-08-07). 그래서 순정에서도 패치 위에서도 같은 카드로 선다.
  카드에 넣을 순정 지문은 **게임 폴더의 `Scripts.rxdata.orig`**(modkit이 처음 덮을 때
  남긴 백업)에서 뜬다 — 보관소의 한글패치 코어에서 뜨면 패치 지문이 박힌다.
  ⚠ **기준선 폴더가 비어 있으면 그 재대조가 못 서서 `apply`가 `BaseChanged`로 멈춘다** —
  그때는 경고 내용을 확인하고 `force`로 강행한다(2026-08-09 Type Matchup Z 설치 실측).
  `inject.py`에는 이 우회가 아예 없어 무조건 멈추므로, 설치는 modkit으로 한다.
- 엔진 해부: [`../research/2026-08-01-pokemon-z-fangame.md`](../log/research/2026-08-01-pokemon-z-fangame.md).
- ⚠ 한글패치 코어(에셋)를 적용하면 게임 코어가 갈려 주입분이 지워진다 — 복구는 inject.py 재실행.

## 한글패치 모드 자체는 손으로 만들지 않는다

배포용 모드는 보관소에 놓인 폴더가 아니라 **재료에서 짓는 산출물**이다. 조립기 넷:

    uv run runa/make-patch-mod.py      # 한글패치 코어 (번역표·코어·자산)
    uv run runa/make-galmuri-master.py # 갈무리 마스터 — 통짜 원본을 우리 글자 수만큼 줄인다
    uv run runa/make-hangul-variant.py # BW 마스터 — DPPt의 한글만 갈아 끼운다
    uv run runa/make-font-mods.py      # 글꼴 모드 셋(DPPT·Galmuri·BW Font)

재료는 번역표 정본(`translate/ko/`)과 「한글패치 코어」 모드다. 같은 재료로 몇 번을
돌려도 바이트까지 같다 — 글꼴에 저장 시각이 새로 매겨지지 않게 `recalcTimestamp=False`를
쓴다(안 그러면 설치 판정이 「원본이 달라졌다」로 읽는다).

배포 zip은 `share/make_package.py --variant runa --font <갈래> --zip`이 만든다.

- **게임에는 modkit으로 얹는다.** 손으로 복사하면 덮은 자리에 원본 백업(`.orig`)이 안
  남아, 호환 검사가 우리가 넣은 폰트를 게임의 원본으로 읽고 「판이 달라졌어요」라고
  경고한다. 루나판이 실제로 그 상태였다.
- **모드 폴더끼리 하드링크로 이어질 수 있다.** 복제로 만든 판에 파일을 `cp`로 밀어
  넣으면 원판 모드의 같은 파일까지 함께 바뀐다 — 그렇게 「한글패치 코어」의 코어에
  주입 섹션 13개가 구워져 있었다. 조립기는 늘 옆에 쓰고 이름을 바꿔 갈아 낀다.
- **주입형 모드는 한글패치 코어에 굽지 않는다.** 각자 제 모드로 설치되는 것이 맞고,
  구워 두면 설치한 적 없는 모드가 딸려 들어간다. **다만 합본 배포물은 예외다** —
  거기서는 굽되 `MOD:` 표를 떼어 제 살로 만든다(`share/make_package.py`의 `_settle_injections`).

## 신형 루비 실행기 호환

모바일 유저는 mkxp-z 계열(루비 3.1+) 실행기로 하므로 **코어는 1.8.7과 3.x 양쪽에서
살아야 한다.** 호환 층은 둘이고, 근거 목록은
[2026-08-09 호환 감사](../log/research/2026-08-09-ruby-compat-sweep.md)다.

- **심 섹션 「Z-32 Ruby Compat」** — 코어 맨 앞. 없는 API만 채운다(`nitems`·
  `Thread.critical`·`File.exists?`·`Fixnum`·`getbyte` 등). 소스 정본은
  `share/ruby-compat.rb`, 코어 반영은 `share/patch_ruby_compat.py`(멱등 — 심을 고치고
  다시 돌리면 갈아 끼운다. 보관소 기반판·게임 설치본 양쪽이 기본 대상).
- **문법 수술** — 1.8 전용 구문은 심으로 못 덮는다(파싱 단계에서 죽는다). 같은 도구가
  `when N:` 콜론과 rescue 밖 `retry`를 공통 문법으로 바꿔 둔다.

코어를 새로 굽거나 스크립트를 수술했으면 `share/qa-ruby-compat.py <코어> --ruby
<신형 루비>`로 문법 불통 0을 확인한다. 첨자 비교류는 「의심」으로만 나오니 눈으로
가려낸다.

## 글꼴 모드 셋

`DPPT Font` · `Galmuri Font` · `BW Font`. 셋은 같은 능력 `hangul-font`를 주고 서로를
`conflicts`로 밀어낸다 — 한 게임에 하나만 선다. 한글패치가 `requires: ["hangul-font"]`로
그중 아무거나를 가리킨다.

- **글꼴은 패밀리명으로 잡힌다.** 조이플레이 계열 엔진은 `mkxp.json`의 `fontSub`(글꼴
  대체표)를 안 읽으므로, 폰트 파일 내부 패밀리명을 게임이 요청하는 이름으로 개명해
  넣는 것이 정본이다. 그림자·굵게의 반(半)픽셀은 알파로 만든다 — `solidFonts`를 켜면
  알파가 죽어 무효가 된다.
- **글꼴 세 벌의 관계** — 갈무리는 통짜 원본을 우리 글자만큼 줄인 것, DPPt·BW는 한글
  음절만 다른 형제다. 갈래별 실측과 반증된 가설은
  [글꼴 조사 기록](../log/research/2026-08-08-font-three-variants.md)을 본다.

⚠ **글꼴을 줄일 때 한자를 다 빼면 안 된다.** FreeType의 자동 힌팅은 한자 몇 자의
윤곽선을 재서 CJK 기준선을 잡는데, 그것이 없으면 같은 높이여야 할 한글이 크기마다 다른
높이로 갈린다(게임이 쓰는 24·25·26·28·29·31·32에서 실측). 한자가 아예 없는 글꼴은
`runa/add-blue-zone.py`가 **한글과 같은 높이의 속 빈 네모**를 그 자리에 심어 기준선을
만들어 준다 — 심은 뒤 일곱 크기를 재서 갈리면 저장하지 않는다.

## 이 폴더들의 함정

- **루나판(딱지판)은 fanlib에 별도 버전·별도 모드로 등록한다.** 하드링크 복사본을
  제자리에서 편집하면 원본 모드까지 함께 바뀐다(위 「하드링크」 항목과 같은 뿌리).
  fanlib 명령은 Windows 쪽에서 돌린다 — 목록 파일이 홈 기준이라 WSL에서 돌리면
  낡은 사본에 쓴다.
- **`Game.ini`의 제목 정본은 「Pokemon Z」다.** 「Pokemon Z Fangame」은 손으로 넣은
  값이다(행위자 미확인). 세이브 폴더 이름만 이 제목에 걸리고, 모드 설치는 안 걸린다
  (canon이 별칭 처리). 제목을 되돌릴 일이 있으면 세이브 폴더 연속성부터 본다 —
  세이브는 `Saved Games\Pokemon Z\`에 산다.
- ⚠ **패치 자산 182개 중 151개는 원본 배포물을 못 찾아 재생성이 불가능하다** — 지금
  모드 폴더가 유일본이다. 자산을 지우거나 다시 만들려 하기 전에
  [출처 조사](../log/research/2026-08-08-patch-asset-provenance.md)를 본다. `mod.json`의 설명 문구는 실제 자산 목록과
  어긋나는 자리가 있다.

## modkit과의 접점

`share/make_package.py`가 MODKIT_HOME(기본 `~/workspace/claude-native/sketches/essentials-modkit`)
에서 modkit을 임포트해 변형마다 `manifest.json`을 동봉한다. 기준 지문은
`share/make_manifest_full.py`가 뜨고, Z 고유 제외 목록(Constants·MapChecker·LastSave 등)은
이 스크립트 몫이다(코어 기본값은 2게임 이상 실측만). 모드 배포는 그쪽 repo
(`durumiii/essentials-modkit`, mods-z-v2)가 정본이다.
