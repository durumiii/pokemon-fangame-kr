# 신형 루비 호환 정적 감사 — 배포 코어 전수 (2026-08-09)

[Z-31](../../tickets/Z-31.md)(굵은 한글 튕김)을 계기로, 같은 부류의 지뢰를 밟기 전에
쓸어내려고 만든 감사. 도구는 `share/qa-ruby-compat.py`(신설), 대상은 v5.2.1 배포
zip(`share/dist/…_2-dppt.zip`)의 `Data/Scripts.rxdata` 260개 섹션 전부.

## 방법 (실측)

두 겹 — ① 루비 3.4.5(-c)로 섹션별 문법 검사, ② 1.8 전용 API·관용구 패턴 grep.
첨자 비교는 받는 쪽 타입을 정적으로 모르므로 「의심」으로 찍고 눈으로 가려냈다.

## 결과

**문법 불통 2 섹션** — 정식 1.9+ 루비는 로드하다 SyntaxError 즉사:
- `AudioUtilities` — `when 0:` 콜론 구문(1.9에서 제거). 재작성은 `when 0 then`.
- `PScreen_Load` — rescue 밖 `retry`(1.9부터 컴파일 불가). 루프 재구성 필요.

**즉사형 API 부재** — 정식 1.9+/3.2+에서 그 줄 실행 시 NameError·NoMethodError:
- `Array#nitems` 7곳, 전부 `PScreen_Storage` — 파티 수 세기·박스 목록. **포획 성공
  후 저장 경로와 PC 박스 화면이 여기를 지난다.**
- `Thread.critical` 12곳 — `Audio`·`BitmapCache`.
- `File.exists?` 8곳 — `Main`·`Scene_Intro`(기동 경로!)·`Compiler`·`Logros`.
- `Object#type` 클래스 비교 2곳 — `PBattle_OrgBattleRules`. `.type`이 그 클래스의
  속성일 수 있어 미확인.

**조용한 오판형** — 1.9 의미론에서 `문자열[i] == 정수`가 예외 없이 거짓:
- BOM 벗기기 `line[0]==0xEF…` — `Intl_Messages` 1곳·`Compiler` 9곳(컴파일러는 PC
  디버그 전용이라 실해 없음).
- GIF 서명 검사 `filestring[0]==0x47` — `SpriteWindow` 2곳.
- `AudioUtilities`의 `rstr[0]==0xFB` 1곳.
- 부등호형(즉사 가능)은 걸러낸 결과 전부 무해였다 — `Acentos`는 통째로 `=begin`
  주석, `DrawText:173`의 `yuv`는 Float 배열, 나머지는 정수 배열(iv·ev 등).

**우리 모드** — `003_BoldHangul.rb`의 getbyte 분기 하나뿐, 오늘 수리(Z-31).

## 모바일 실행기의 정체 — 둘은 다른 앱이다

처음에 「1.8 계열이되 문자열 첨자만 1.9 의미론인 혼종」으로 뭉뚱그렸으나(같은 날
앞선 판독), 유지자 전언으로 **Runa는 루비 3.1+**라 한다. 갈라서 다시 적는다.

- **RPG Player** — 오류 문구가 실측이다: 가드(`respond_to?(:getbyte)`)가 든 배포
  코드에서 「comparison of String with 192 failed」가 났으니, `String#[]`가 문자열을
  돌려주면서 `getbyte`는 없는 실행기다. 정식 3.1+에서는 이 오류가 나올 수 없다
  (릴리스 자산과 로컬 dist가 sha256까지 일치함을 확인 — 옛 판이 나간 것도 아니다).
- **Runa** — App Store 페이지가 「Powered by mkxp-z」를 명시한다(웹 확인,
  [Runa: RPG Maker & VN Player](https://apps.apple.com/nz/app/runa-rpg-maker-vn-player/id6779939767)).
  mkxp-z의 기본 루비가 3.1이라 유지자 전언(3.1+)과 부합한다. 이 경우 `Array#nitems`
  같은 「즉사형 API 부재」가 Runa에서 **살아 있는 지뢰**가 되고, 몬스터볼 제보(Z-31)와
  정확히 맞물린다 — 볼 사용 허가 검사(`PItem_ItemEffects`의 CanUseInBattle 핸들러)가
  `party.length>=6 && $PokemonStorage.full?`이고, `full?`(PScreen_Storage)이
  `nitems`를 부른다. **파티가 꽉 찼을 때만** 걸리므로 초반 무증상도 설명된다.
  남는 모순 둘 — ① 정식 3.1이면 getbyte가 있어서 난이도 선택 튕김이 설명 안 되는데,
  제보자의 003 수정이 Runa 쪽까지 고친 정황이 있다(전언 — 어느 앱에서 확인했는지
  불명). ② 문법 불통 2 섹션·`Thread.critical`을 부팅이 넘긴다. Runa 포트가 섹션
  오류를 삼키는지, 루비 판이 정확히 무엇인지는 미확인.

어느 쪽이든 Z-31의 `unpack` 수리와 Z-32의 호환 심은 두 실행기 모두에 유효하다.

## 남긴 것

선제 제거 방안과 우선순위 판정은 [Z-31](../../tickets/Z-31.md)
(구 Z-32 — 2026-08-09에 Z-31로 합쳤다).
