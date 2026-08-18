# 다리 밑 파도타기 통행 수술 — Bridge Fix 모드 (2026-08-19)

파도타기로 다리 아래 물길을 지나가지 못하던 원작 엔진 결함을 스크립트 모드 하나로
고쳤다. 원인 판독은 [조사 기록](research/2026-08-19-surf-under-bridge.md)에 있다 —
`$PokemonGlobal.bridge`가 맵 이동·세이브 로드에서 리셋되지 않고 켜진 채 남아,
`Game_Map#playerPassable?`의 레이어 순회가 다리 타일에서 판정을 끝내 버린다.

## 무엇을 어떻게

새 모드 `mods/Bridge Fix/`(스크립트 `000_BridgeSurf.rb` 하나). 순정 `Game_Map#playerPassable?`
전문을 그대로 떠 와 다리 타일 건너뛰기 조건 한 줄만 바꿨다. 나머지 줄은 원본 그대로다.

    - next if $PokemonGlobal && $PokemonGlobal.bridge==0 &&
    -    tile_id && PBTerrain.isBridge?(@terrain_tags[tile_id])
    + next if $PokemonGlobal && tile_id &&
    +    PBTerrain.isBridge?(@terrain_tags[tile_id]) &&
    +    ($PokemonGlobal.bridge==0 || $PokemonGlobal.surfing)

다리 위에서는 파도타기를 할 수 없으므로 surfing 중에 다리 타일을 언제나 건너뛰어도
다른 상황의 통행은 달라지지 않는다. 원본의 `$PokemonGlobal &&` nil 가드는 승인된 한 줄에는
없었지만 그대로 남겼다 — 빼면 `$PokemonGlobal`이 nil일 때 원본에 없던 예외가 난다.

`share/make_package.py`의 합본(runa) 주입 목록 `RUNA_INJECT`에 넣었다. `expects`의
`Game_Map` 지문이 순정과 한글패치 코어 양쪽에서 같아서 `FORCE_INJECT`는 필요 없다.

## 검증 (실측)

- 루비 1.8.7 구문 — 게임 실행기 시험대(`D:\ztest`)로 `000_BridgeSurf.rb`를 eval.
  `RUBY_VERSION = "1.8.7"` · `OK (구문 통과, 실행도 통과)`.
- `modkit lint` 오류 0 · 권장 0. `modkit apply` → 「Bridge Fix: 설치됨」.
- `uv run translate/verify.py` → `scripts: 절 278, MOD 21` (직전 277·MOD 20),
  `결과: FAIL 0 · WARN 0`.
- 설치본 `Scripts.rxdata`에 절 `MOD:Bridge Fix/000_BridgeSurf.rb`(2003바이트) 실림 확인.

## 맵 수술 — 19번도로(맵 299) 다리 밑 물길 열네 칸

통행 판정만 고쳐서는 지나가지지 않는다. 파도타기는 마주 보는 칸의 지형이 물이 아니면
`pbEndSurf`(103_PField_HiddenMoves.rb:524)가 뭍으로 내려버리는데, 19번도로의 다리 데크
밑 두 줄에는 물 타일이 아예 없다. 그래서 맵 데이터도 함께 고쳤다.

다리를 쓰는 맵 여섯을 전수 조사했다. 「다리 타일이 얹혔는데 그 밑에 물이 없는 칸」을 모으고,
구멍을 건너뛰며 축 방향 양끝을 봐서 강이 데크에서 끊긴 자리만 골랐다.

| 맵 | 구멍 칸 | 양끝이 물 | 판정 |
|---|---|---|---|
| 55 · 5번도로 | 44 | 0 | 물길 없음 — 대상 아님 |
| 76 · 7번도로 북쪽 | 44 | 0 | 물길 없음 — 대상 아님 |
| 140 · 옛 고목내마을 | 5 | 0 | 한쪽만 물(x19의 y24~27·y32). 다리가 못 위에 세로로 서 있고 못에 닿는 칸(y28~31)은 이미 물이 깔려 있다 — 나머지는 진입로. 대상 아님 |
| 287 · 18번도로 | 120 | 0 | 물길 없음 — 대상 아님 |
| **299 · 19번도로** | 54 | **14** | **수술 대상** |
| 391 · 미르 신시가지 - 서쪽 | 19 | 0 | 물길 없음 — 대상 아님 |

19번도로의 강은 x40~46 폭으로 세로로 흐르고 다리가 가로로 지난다. 데크는 y23~y26 네 줄인데
물 레이어(L1)는 y24·y25 두 줄에서만 0이었다. 그 열네 칸에 같은 열의 위아래가 쓰는 값을
그대로 깔았다 — x40은 592, x41~45는 593, x46은 594. y19부터 y31까지 그 열이 줄곧 쓰는
값이라 이음새가 새로 생기지 않는다. L0(바닥)과 L2(데크)는 건드리지 않았다.

299의 나머지 마흔 칸은 강 바깥의 다리 진입로다(x37~39·x47~53의 y23·y26). 한쪽에만 물이
닿으니 대상이 아니다.

### 어떻게 고쳤나

`Map299.rxdata`의 원본 바이트를 그대로 두고 `@data` 테이블의 해당 스물여덟 바이트만
덮어썼다. rubymarshal로 다시 쓰지 않았으므로 이벤트·속성·직렬화 꼴이 원본 그대로다.

### 검증 (실측)

- 파일 크기 48,853바이트로 동일, 다른 바이트 28개(14칸 × 2바이트). 원본 CRC32 454427164,
  수술본 2415055712.
- 원본과 수술본을 각각 읽어 전 필드 2,606개를 대조 — 다른 필드 없음. `@data`에서 바뀐 칸은
  정확히 열넷이고 전부 L1이며 0에서 물 타일로만 갔다. 이벤트 28개 완전 동일.
- 통행 시뮬레이션(`passable?` + `playerPassable?` + `pbEndSurf` 재현)으로 강 북쪽
  (43,22)에서 남쪽 (43,28)까지 폭 탐색: 원본은 네 조건 전부 막힘, 수술본은
  `bridge==0`에서 통과하며 다리 밑 열네 칸에 모두 닿는다.

### 남은 구멍 — `terrain_tag`는 아직 다리를 건너뛰지 않는다

같은 시뮬레이션에서 `$PokemonGlobal.bridge > 0`이면 수술본도 여전히 막힌다.
`Game_Map#terrain_tag`(016_Game_Map.rb:380)의 다리 건너뛰기가 `bridge==0`일 때만 걸려서,
표시가 켜진 채면 데크의 지형 15가 그대로 나오고 `pbEndSurf`가 하선시킨다. 표시는 맵을
옮겨도 꺼지지 않으므로 다리를 한 번이라도 건넌 판에서는 이쪽이 남는다.

`playerPassable?`에 넣은 것과 같은 꼴의 한 줄이면 닫힌다:

    - next if tile_id && PBTerrain.isBridge?(@terrain_tags[tile_id]) &&
    -         $PokemonGlobal && $PokemonGlobal.bridge==0 && !countBridge
    + next if tile_id && PBTerrain.isBridge?(@terrain_tags[tile_id]) && !countBridge &&
    +         $PokemonGlobal && ($PokemonGlobal.bridge==0 || $PokemonGlobal.surfing)

모드 스크립트를 다른 갈래에서 손대고 있어 이번 커밋에는 넣지 않았다 — 유지자 판정 대기.

## 남은 것

실기 확인 — 19번도로(맵 299)의 다리 아래 물길을 파도타기로 지나가 보는 것. 위의
`terrain_tag` 구멍 때문에, 다리를 건너지 않고 물에 들어간 판에서 먼저 봐야 한다.
