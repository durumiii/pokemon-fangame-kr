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

## 남은 것

실기 확인 — 다리를 한 번 건넌 뒤 그 아래 물길을 파도타기로 지나가 보는 것.
조사 기록이 재현 자리로 짚은 맵에서 눈으로 봐야 닫힌다.
