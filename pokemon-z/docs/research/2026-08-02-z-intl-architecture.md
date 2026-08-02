# Pokémon Z Fangame — 번역 텍스트가 화면까지 가는 경로 (2026-08-02)

**목적**: LLM 전량 재번역 배치 설계를 위한 기초 자료. 「우리가 `korean.dat`의 값을
바꾸면 그 글자가 어느 코드를 지나 화면에 뜨는가」를 코드 근거로 적는다.

**판독 대상**: `/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/Scripts.rxdata`
(255절, Essentials v16 계열 + Ruby 1.8.7). 아래 인용의 「절이름:줄」은 그 rxdata를 풀어
`{순번}_{제목}.rb`로 떨군 파일 기준이다. 재현:

```
uv run --with rubymarshal python3 -c "
import zlib,io;from rubymarshal.reader import load
d=load(io.BytesIO(open('/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/Scripts.rxdata','rb').read()))
print(zlib.decompress(bytes(d[41][2])).decode('utf-8'))"   # 41 = Intl_Messages
```

**확정도 표기**: 코드 인용이 붙은 것은 스크립트 정독으로 확인한 것(실측). 게임을 실행해
확인한 것은 하나도 없다 — 아래 「4-6 도달 불가 키」의 결론은 **정적 판독 기반 추론**이고
그렇게 표시했다.

---

## 1. 언어 파일 적재 경로

### 1-1. 언어 목록과 기본값

`000_Settings.rb:350`

```ruby
LANGUAGES = [
  ["Español","messages.dat"],
  ["한국어","korean.dat"]
]
```

한글패치가 여기에 둘째 줄을 넣었다. 이게 두 줄 이상이라는 사실이 적재 분기 전체의 조건이다
(`LANGUAGES.length>=2`가 세 군데에서 문지기 노릇을 한다).

기본 선택은 한국어다 — `143_PScreen_Options.rb:454`가 `@language = 1`로 초기화한다.
다만 게터가 따로 있어서 `143:389`

```ruby
def language
  return (!@language) ? 0 : @language
end
```

**`@language`가 nil이면 0(스페인어)으로 떨어진다.** 이 ivar이 없는 옛 세이브를 물려받으면
한국어 설정이 조용히 풀린다.

### 1-2. 언제 읽나

세 곳에서 `pbLoadMessages`를 부른다. 셋 다 파일명을 `LANGUAGES[언어번호][1]`에서 가져온다.

부팅 경로 — `170_PSystem_System.rb:115`

```ruby
if LANGUAGES.length>=2
  if !havedata
    pokemonSystem.language=pbChooseLanguage
  end
  pbLoadMessages("Data/"+LANGUAGES[pokemonSystem.language][1])
end
```

이 코드는 `pbSetUpSystem`(`170:47`) 안에 있고, 그 함수는 같은 절 맨 아래 `170:188`에서
최상위 호출된다. 곧 **게임이 뜨자마자 스크립트 적재 시점에 한 번 돈다.** 바로 위에서
`Data/Constants.rxdata`를 eval하므로(`170:105-112`) `PBSpecies.getName` 같은 조회 함수는
언어 파일보다 먼저 정의되지만, 그 함수들은 호출 시점에 조회하므로 순서 문제가 없다(§2-3).

세이브 화면의 언어 바꾸기 — `141_PScreen_Load.rb:884`

```ruby
elsif cmdLanguage>=0 && command==cmdLanguage
  @scene.pbEndScene
  $PokemonSystem.language=pbChooseLanguage
  pbLoadMessages("Data/"+LANGUAGES[$PokemonSystem.language][1])
  ...
  $scene=pbCallTitle
```

메뉴 항목은 `141:519`에서 `_INTL("Idioma")`로 붙는다. **인게임 설정(`143_PScreen_Options`)에는
언어 항목이 없다** — 바꾸려면 타이틀/불러오기 화면으로 나와야 한다.

컴파일 경로 — `177_Compiler.rb:4150`. `$DEBUG`일 때만 도는 `pbCompileAllData` 끝자락이고,
그 직전 `4148-4149`가 `pbSetTextMessages` → `MessageTypes.saveMessages`다. 곧 **디버그로
게임을 켜면 `messages.dat`가 스크립트·맵에서 다시 구워진 뒤에 `korean.dat`가 그 위에
얹힌다.** `korean.dat`를 덮어쓰지는 않는다.

### 1-3. 적재된 뒤의 모양

`pbLoadMessages`는 `MessageTypes.loadMessageFile` → `Messages#loadMessageFile`
(`041_Intl_Messages.rb:525`)이고, 하는 일은 `Marshal.load` 한 번과 배열 여부 검사뿐이다.

```ruby
def loadMessageFile(filename)
  begin
    Kernel.pbRgssOpen(filename,"rb"){|f| @messages=Marshal.load(f) }
    if !@messages.is_a?(Array)
      @messages=nil
      raise "Corrupted data"
    end
    return @messages
  rescue
    @messages=nil
    return nil
  end
end
```

**실패가 조용하다.** 파일이 깨졌거나 Marshal이 못 읽으면 `@messages=nil`이 되고 예외가
바깥으로 안 나간다. 그 뒤 모든 조회가 원문(스페인어)을 그대로 돌려준다 — 곧 **`korean.dat`를
잘못 구우면 「오류」가 아니라 「게임 전체가 스페인어」로 나타난다.**

저장소는 클래스 변수 둘이다 — `041:614`

```ruby
@@messages         = Messages.new                        # korean.dat 가 여기 들어온다
@@messagesFallback = Messages.new("Data/messages.dat",true)   # 지연 적재
```

---

## 2. 절 번호 ↔ 용도 대응표

정의는 `041_Intl_Messages.rb:589-613`. 0번은 주석으로만 예약돼 있다(`# Value 0 is used for
common event and map event text`).

| 절 | 상수 | 용도 | dat 모양 | 현재 줄 수 | 조회 함수 |
|---|---|---|---|---|---|
| 0 | (예약) | 맵 이벤트·공통 이벤트 대사와 선택지 | 맵별 OrderedHash 배열 (508맵) | 13,262 | `getFromMapHash` |
| 1 | `Species` | 종 이름 | 목록 | 1,019 | `get` |
| 2 | `Kinds` | 분류("씨앗포켓몬") | 목록 | 1,019 | `get` |
| 3 | `Entries` | 도감 설명 | 목록 | 1,019 | `get` |
| 4 | `FormNames` | 폼 이름(줄바꿈 구분 한 덩이) | 목록 | 1,017 (971이 빈 값) | `get` |
| 5 | `Moves` | 기술 이름 | 목록 | 733 | `get` |
| 6 | `MoveDescriptions` | 기술 설명 | 목록 | 733 | `get` |
| 7 | `Items` | 도구 이름 | 목록 | 949 | `get` |
| 8 | `ItemPlurals` | 도구 복수형 | 목록 | 949 | `get` |
| 9 | `ItemDescriptions` | 도구 설명 | 목록 | 949 | `get` |
| 10 | `Abilities` | 특성 이름 | 목록 | 257 | `get` |
| 11 | `AbilityDescs` | 특성 설명 | 목록 | 257 | `get` |
| 12 | `Types` | 타입 이름 | 목록 | 19 | `get` |
| 13 | `TrainerTypes` | 트레이너 클래스 | 목록 | 196 | `get` |
| 14 | `TrainerNames` | 트레이너 이름 | OrderedHash | 362 | `getFromHash` |
| 15 | `BeginSpeech` | 전투 시작 대사 | OrderedHash | **0** | `getFromHash` |
| 16 | `EndSpeechWin` | 패배 대사 | OrderedHash | **0** | `getFromHash` |
| 17 | `EndSpeechLose` | 승리 대사 | OrderedHash | **0** | `getFromHash` |
| 18 | `RegionNames` | 지방 이름 | 목록 | 1 | `get` |
| 19 | `PlaceNames` | 지명 | OrderedHash | 90 | `getFromHash` |
| 20 | `PlaceDescriptions` | 지명 설명 | OrderedHash | 22 | `getFromHash` |
| 21 | `MapNames` | 맵 이름 | 목록 | 508 | `get` |
| 22 | `PhoneMessages` | 전화 대사 | OrderedHash | 19 | `getFromHash` |
| 23 | `ScriptTexts` | `_INTL`/`_ISPRINTF` 문구 | OrderedHash | 6,827 (+우리 추가분 45) | `getFromHash` |

줄 수는 `mod/z/translate/ko/*.jsonl`을 센 값이다(`wc -l`, 절0은 맵 헤더 508줄 제외).

**15~17이 비어 있는 것은 누락이 아니다.** 컴파일러가 트레이너 대사를 맵 이벤트 스크립트로
구워 넣기 때문이다 — `177_Compiler.rb:3917`

```ruby
sprintf("pbTrainerBattle(%s,_I(\"%s\"),%s,%d,%s,%d)", safetrcombo,safequote2(espeech), ...)
```

`_I(...)`는 **맵 해시(절0)** 조회다(§2-1). 그래서 트레이너 대사는 15~17이 아니라 그 트레이너가
서 있는 맵의 절0 항목으로 들어간다. `155_PBattle_OrgBattle.rb:760`처럼 15번을 실제로 읽는
자리가 남아 있지만, 절이 비어 있으므로 그 경로는 원문을 그대로 돌려준다.

---

## 3. 조회 경로별 구조

### 3-1. 맵 이벤트 대사 (절0)

훅은 인터프리터의 `command_101`이다 — RMXP용이 `052_Messages.rb:565`, RMVX용이 `052:445`.
둘 다 마지막에 같은 두 줄을 놓는다(`052:500`, `052:634`).

```ruby
message=_MAPINTL($game_map.map_id,message)
@message_waiting=true
if commands
  cmdlist=[]
  for cmd in commands[0]
    cmdlist.push(_MAPINTL($game_map.map_id,cmd))
  end
```

**키는 원문 전체 덩어리이지 위치가 아니다.** 인터프리터가 이벤트 명령 101(첫 줄)과 401(이어지는
줄)을 하나로 이어 붙여 만든 문자열을 그대로 키로 쓴다 — `052:576-595`가 줄마다
`text+=" " if text[text.length-1,1]!=" "`로 끝에 공백 하나를 붙이며 잇는다. 선택지(명령 102)는
**한 항목씩 따로** 조회한다.

조회는 `041:751`

```ruby
def _MAPINTL(mapid,*arg)
  string=MessageTypes.getFromMapHash(mapid,arg[0])
  string=string.clone
  for i in 1...arg.length
    string.gsub!(/\{#{i}\}/,"#{arg[i]}")
  end
  return string
end
```

`getFromMapHash`(`041:572`)에 **폴백이 하나 있다.**

```ruby
id=Messages.stringToKey(key)
if @messages[0][type] && @messages[0][type][id]
  return @messages[0][type][id]
elsif @messages[0][0] && @messages[0][0][id]
  return @messages[0][0][id]
end
return key
```

그 맵 절에 없으면 **맵 0번 절**(공통 이벤트 텍스트가 모이는 곳)을 한 번 더 본다. 거기도
없으면 **키 자신** — 곧 스페인어 원문을 돌려준다. 예외도 로그도 없다.

키가 어떻게 만들어졌는지는 `041:22`의 `pbSetTextMessages`가 답한다. 맵 파일을 열어 같은
규칙으로 101/401을 잇고(`041:134-145`), 102의 선택지를 따로 밀어 넣고, 355/655(스크립트
명령) 안의 `_I("...")` 리터럴을 뽑는다(`041:146-149`, `pbAddScriptTexts`는 `041:1`).
그리고 `setMapMessagesAsHash`(`041:496`) → `createHash`(`041:472`)가

```ruby
key=Messages.stringToKey(array[i])
arr[key]=array[i]
```

로 **키를 정규화해서** 담는다. 이 정규화가 §4의 함정 대부분의 뿌리다.

### 3-2. `_INTL` / `_ISPRINTF` (절23)

`041:716`

```ruby
def _INTL(*arg)
  begin
    string=MessageTypes.getFromHash(MessageTypes::ScriptTexts,arg[0])
  rescue
    string=arg[0]
  end
  string=string.clone
  for i in 1...arg.length
    string.gsub!(/\{#{i}\}/,"#{arg[i]}")
  end
  return string
end
```

`_ISPRINTF`(`041:732`)는 조회는 같고 치환만 `{1:d}` 꼴을 `sprintf("%"+지시자, 값)`으로 푼다.

**실패 시 동작은 「원문 그대로」다.** `getFromHash`(`041:563`)

```ruby
def getFromHash(type,key)
  delayedLoad
  return key if !@messages
  return key if !@messages[type]
  id=Messages.stringToKey(key)
  return key if !@messages[type][id]
  return @messages[type][id]
end
```

세 갈래 전부 `key`(스페인어 리터럴)를 돌려준다. **폴백도 없고 경고도 없다** — 배열 절과 다른
점이다(§3-3). 그리고 **값이 빈 문자열이면 빈 문자열이 그대로 나간다** — 루비에서 `""`는
참이라 `!@messages[type][id]`가 거짓이기 때문이다. 곧 해시 절에서 값을 비우면 스페인어가
아니라 **아무것도 안 뜬다.**

호출 규모: `_INTL(` 5,031곳, `_ISPRINTF(` 103곳(255절 전수 grep).

### 3-3. 이름류 목록 절 (1~13·18·21)

조인 축은 **데이터 파일의 정수 id**다. 컴파일러가 상수 모듈에 조회 함수를 구워 넣는다 —
`177_Compiler.rb:1873`

```ruby
code+="def PBSpecies.getName(id)\r\nreturn pbGetMessage(MessageTypes::Species,id)\r\nend\r\n"
```

같은 꼴이 `PBTypes.getName`(`177:1257`), `PBAbilities`(`1405`), `PBMoves`(`1544`),
`PBItems.getName`/`getNamePlural`(`1641-1642`), `PBTrainers`(`2158`)에 있다. 맵 이름은
`015_Game_Map.rb:496`이 `pbGetMessage(MessageTypes::MapNames,self.map_id)`로 직접 읽는다.

목록 절만 **폴백이 있다** — `041:669`

```ruby
def self.get(type,id)
  ret=@@messages.get(type,id)
  if ret==""
    ret=@@messagesFallback.get(type,id)
  end
  return ret
end
```

`korean.dat`에서 빈 값이면 `messages.dat`의 스페인어로 내려간다. 절4(폼 이름)가 1,017칸 중
971칸이 비어 있는데 그게 정상 동작인 이유다 — 폼이 없는 종은 원래 빈 칸이다.

폼 이름은 한 칸에 여러 폼이 줄바꿈으로 들어간 한 덩이다(`171_PSystem_Utilities NUEVO.rb:1917`이
`formnames`를 통째로 받아 쓴다). **줄 수를 바꾸면 폼 번호가 어긋난다.**

---

## 4. 표시 계층과 함정

### 4-1. 조회된 문자열이 지나는 길

맵 대사 기준으로 순서가 이렇다.

1. `Interpreter#command_101` (`052:565`) — 101/401을 이어 붙여 원문 덩어리를 만든다.
2. `_MAPINTL` (`041:751`) — **여기서 번역이 일어난다.** 이 시점의 문자열은 아직 제어 코드가
   날것이다(`\v[12]`, `\PN`, `\c[1]` 그대로).
3. `Kernel.pbMessage` (`052:996`) → `Kernel.pbMessageDisplay` (`052:1285`) — 여기서 치환이
   쏟아진다. `\\`를 `\5`로 피신시키고(`052:1300`), `\PN`을 주인공 이름으로(`1314`),
   `\v[n]`을 변수 값으로 반복 치환하고(`1341-1344`), `\c[n]`을 색 태그로(`1338`) 바꾼다.
   그다음 `\w[..]`·`\ff[..]`·`\.`·`\|` 같은 흐름 제어를 뜯어내 별도 목록으로 뺀다
   (`052:1352-1362`).
4. `msgwindow.text=text` (`052:1437`) → `Window_AdvancedTextPokemon#text=`
   (`050_SpriteWindow.rb:3530`) → `setText` (`050:3551`).
5. `setText` 안에서 `getFormattedText`(`051_DrawText.rb:482`)가 색·정렬 태그를 해석해 글자
   단위로 쪼갠다.

**번역이 2단계, 제어 코드 해석이 3단계다.** 그래서 절0·절23의 키에는 `\v[..]`·`\PN`·`{1}`이
날것으로 남아 있고, 값에서도 그대로 유지해야 한다.

### 4-2. 우리 모드 둘이 끼어드는 자리

둘 다 **4단계**, 곧 창의 `setText` 직전이다.

`mod/z/mods/Josa Select/001_Josa.rb:86`

```ruby
class Window_AdvancedTextPokemon
  alias josaz_setText setText
  def setText(value)
    josaz_setText(JosaZ.resolve(value))
  end
end
```

`Window_UnformattedTextPokemon#text=`(`:93`)와, 창을 안 거치고 비트맵에 바로 그리는
`drawTextEx`/`drawFormattedTextEx`(`:101`, `:106` — 원본은 `051_DrawText.rb:1059`, `:1075`)도
같이 감싼다.

`mod/z/mods/UI Text KR/001_UiText.rb:37`이 같은 두 진입점을 감싸고, 더해서
`pbDrawTextPositions`(원본 `050_SpriteWindow.rb:1167`)를 감싼다.

**이 자리를 고른 것이 맞다.** `\PN`·`\v[..]` 치환이 이미 끝난 뒤라 조사 판정기가 실제로
화면에 뜰 이름을 보고 은/는을 고를 수 있다. 3단계 앞에 끼우면 `\PN`이라는 글자를 보고
판정하게 된다.

**새 제어 코드를 넣으려면 두 자리 중 하나다.** 흐름 제어(대기·효과음처럼 텍스트 밖에서
작동하는 것)라면 `052:1352`의 큰 정규식에 글자를 추가해야 한다. 순수 문자열 변환이라면
`\j`처럼 4단계에서 잡는 편이 안전하다 — 3단계 정규식이 모르는 코드는 건드리지 않고
통과시키기 때문이다(`\j`가 지금 그렇게 살아 있다).

**대신 결합이 하나 생겼다.** `korean.dat` 값 1,104곳에 `\j[..]`가 들어 있다(절23이 1,072,
절22가 15, 우리 추가분이 17). **Josa Select 모드가 안 깔린 채로 이 dat만 들어가면 그 글자가
화면에 그대로 뜬다.** 재번역 배치가 `\j`를 더 쓰면 이 결합이 더 굵어진다.

### 4-3. 함정 — 키 정규화 (`stringToKey`)

가장 큰 함정이다. `041:367`

```ruby
def self.stringToKey(str)
  if str[/[\r\n\t\1]|^\s+|\s+$|\s{2,}/]
     key=str.clone
     key.gsub!(/^\s+/,"")
     key.gsub!(/\s+$/,"")
     key.gsub!(/\s{2,}/," ")
     return key
  end
  return str
end
```

루비의 `\s`는 `[ \t\r\n\f]`다. 그래서 **`\r\n`은 공백 두 개라 한 칸으로 뭉개지고, 홑 `\n`은
그대로 남는다.** 앞뒤 공백과 연속 공백도 사라진다.

이 함수는 **조회할 때마다** 걸린다(`getFromHash:567`, `getFromMapHash:577`). 따라서
**`korean.dat`의 키가 이 함수를 통과한 모양이 아니면 그 항목은 영원히 안 맞는다.**

### 4-4. 함정 — 개행 표기 불일치의 정확한 정체

스크립트 리터럴 `"a\r\nb"`는 게임 안에서 진짜 CR LF 두 글자가 되고(추출기도 같은 변환을
한다 — `041:13-14`가 `\\r`→`\r`, `\\n`→`\n`), 조회 순간 `stringToKey`가 그것을 `"a b"`로
뭉갠다. 반면 `"a\nb"`는 공백 하나뿐이라 `"a\nb"` 그대로 조회된다.

**곧 두 표기를 구별해야 한다 — `\r\n`은 사라지고 `\n`은 남는다.** 절23 키 6,827개 중 홑 `\n`을
품은 것이 357개인데 이것들은 정상이고, `\r\n`을 품은 47개는 §4-6의 문제 항목이다.

### 4-5. 함정 — 원문 안의 보간과 동적 조립

추출기는 **소스 코드의 리터럴을 정규식으로 긁는다**(`041:11`).

```ruby
script.scan(/(?:_INTL|_ISPRINTF)\s*\(\s*\"((?:[^\\\"]*\\\"?)*[^\"]*)\"/)
```

그래서 리터럴 안에 `#{...}`가 있으면 **키에 `#{...}`라는 글자가 그대로 들어간다.** 런타임에는
이미 값으로 풀린 문자열로 조회하므로 절대 안 맞는다. 실례 12곳:

- `084_PokeBattle_Battle.rb:87` — `_INTL("¡Solo puedes capturar Pokémon de tipo #{allowed_type}!")`
- `080_PokeBattle_Battler.rb:1242` — `_INTL("¡#{pbThis} alteró las dimensiones!")`
- `098_PField_Field.rb:2156` — `_INTL("{1} puso \\c[1]{2}\\c[0]\r\nen el bolsillo <icon=bagPocket#{pocket}>...")`
- `187_Following.rb:66` — `_INTL("#{$Trainer.party[0].name} está debilitado...")`
- `223_Dropeo.rb:30`, `244_Cambia Habilidades.rb:24`, `107_PField_BerryPlants.rb:499`·`565`,
  `166_PMinigame_TilePuzzles.rb:155` 등.

`166`번은 심지어 그림 경로를 `_INTL`로 감싼 것이라 번역 대상도 아니다.

**이 12곳은 번역 불가다.** 값이 무엇이든 조회가 안 되므로 스페인어가 뜬다. 고치려면 스크립트
쪽을 `_INTL("... {1} ...", 변수)`로 바꾸는 모드가 필요하다.

### 4-6. 함정 — 지금 실제로 도달 불가인 키 73개

`ko/*.jsonl`의 모든 해시 키에 `stringToKey`를 파이썬으로 흉내 내어 원본과 비교했다.

```
23-script-texts.jsonl:      도달 불가 54 / 6,827
23-script-texts.add.jsonl:  도달 불가 19 / 45     ← 우리가 넣은 것
00-maps.jsonl:              0 / 13,262
```

재현(`mod/z/translate/ko/`에서):

```python
import json,re,glob
def s2k(s):
    if re.search(r"[\r\n\t\x01]|^\s+|\s+$|\s{2,}", s):
        k=re.sub(r"^\s+","",s); k=re.sub(r"\s+$","",k); return re.sub(r"\s{2,}"," ",k)
    return s
for p in sorted(glob.glob("*.jsonl")):
    rows=[json.loads(l) for l in open(p,encoding='utf-8')]
    bad=[r for r in rows if "k" in r and s2k(r["k"])!=r["k"]]
    if bad: print(p, len(bad))
```

54개 중 정규화형 쌍둥이가 따로 있는 것이 10개(그쪽으로 조회가 성공하니 무해한 중복),
**나머지 44개는 한국어 값이 붙어 있는데 닿을 길이 없다.** 눈에 띄는 것들:

| 키 | 쓰이는 곳 |
|---|---|
| `¡{1} envió\r\na {2}!` | `084_PokeBattle_Battle.rb:1751`·`2826`·`2829`·`2869` — 상대 포켓몬 내보내기 |
| `{1} ha olvidado cómo\r\nusar {2}.\x01` | `123_Pokemon_MultipleForms.rb:475`·`543` — 기술 잊기 |
| `PS Máx.<r>{1}\r\nAtaque<r>{2}\r\n…` | 능력치 표 |

**확정도: 정적 판독 기반 추론이다.** 게임을 돌려 「이 문장이 스페인어로 뜬다」를 확인하지
않았다. 다만 방증이 있다 — 6,827개 중 6,773개가 정규화형이고, 어긋난 54개 중 10개는 정규화형
쌍둥이가 나중에 덧붙은 모양이다(누군가 안 나와서 다시 넣은 흔적으로 **추정**).

**우리 `.add.jsonl` 19개는 우리가 만든 것이다.** 스크립트 리터럴을 그대로 키로 썼기 때문이다.
`build.py`에 정규화 검사를 넣는 것이 이 조사에서 나온 가장 값싼 수확이다.

### 4-7. 함정 — 조회 뒤 `gsub`

번역된 값 위에서 다시 문자열을 자르고 바꾸는 자리가 있다. 전화 대사가 그렇다 —
`138_PScreen_Phone.rb:467`

```ruby
messages=call.split("\\m")
...
messages[i].gsub!(/\\TP/,trainerspecies)
```

`\m`이 대사를 여러 화면으로 자르는 구분자이고 `\TP`·`\TE`·`\TM`이 각각 상대 포켓몬 종·
트레이너·장소로 치환된다. **번역이 이 표식을 빠뜨리면 정보가 통째로 사라진다.** 실제로 절22
19줄 중 9줄에서 표식 구성이 원문과 다르다(대부분은 우리가 `\j`를 붙인 것이지만, `\TE`가
빠진 줄도 섞여 있다 — 재번역 때 다시 봐야 한다).

### 4-8. 함정 — 번역 표를 아예 안 지나는 하드코딩

`_INTL`을 안 거친 리터럴은 `korean.dat`로 못 고친다. 확인된 자리:

- `206_Menu Mejorado.rb:1466` — `["[A] Curar",120,20,2,BaseColor,ShadowColor, true]`
  (`pbDrawTextPositions`에 바로 넘기는 배열)
- `189_Fancy Badges.rb:18` — `"Medalla Guardia"` 등 배지 이름 목록
- `204_CartelesPokemon.rb` — 야생 출현 안내판 문구

이 셋이 `UI Text KR` 모드가 만들어진 이유다(`mod/z/mods/UI Text KR/001_UiText.rb:7-26`의 표).
**전량 재번역 배치는 이 자리를 못 건드린다** — 새로 발견되는 하드코딩은 dat가 아니라 그 모드의
`TABLE`에 넣어야 한다.

그리고 `bitmap.draw_text`를 직접 부르는 자리가 여럿 있다(`060_Scene_Credits.rb` 10곳,
`050_SpriteWindow.rb` 14곳, `143_PScreen_Options.rb` 3곳 등). **이 경로는 Josa Select도
UI Text KR도 안 감싼다** — 두 모드는 `drawTextEx`·`drawFormattedTextEx`·`pbDrawTextPositions`
셋만 잡는다. 그런 자리의 `\j`는 안 풀린다.

### 4-9. 함정 — 게임 업데이트로 원문이 바뀌면

절0 맵 대사의 키가 **원문 덩어리 전체**이므로, 제작자가 대사에서 쉼표 하나를 고치면 키가
달라지고 `getFromMapHash`가 못 찾아 그 대사만 스페인어로 돌아간다. 조용하다 — 로그도 예외도
없고, 맵 0번 폴백에 우연히 같은 문장이 있으면 **엉뚱한 맥락의 번역**이 대신 나올 수도 있다.

절23도 같은 성질이지만 스크립트 리터럴이라 덜 흔들린다. 이름 목록 절(1~13·21)은 **키가
정수 인덱스**라 원문이 바뀌어도 안 깨지고, 대신 **항목이 추가·삭제되면 그 뒤가 통째로
밀린다.**

`build.py`가 이 사태를 막는다 — 키를 dat와 한 줄씩 대조해 어긋나면 그 자리에서 멈춘다
(`build.py:59`, `:82`, `:91`). 원문이 바뀐 뒤에는 `export.py`로 재동기화부터 해야 한다.

---

## 5. 재조립 경로 — `build.py`가 내는 dat가 왜 호환되나

형식 면의 근거는 셋이다.

**최상위가 배열이다.** `loadMessageFile`(`041:530`)이 `@messages.is_a?(Array)`만 검사하고,
`build.py`는 읽은 목록의 원소만 바꿔 다시 덤프한다(`build.py:113` `rubywrite.dumps(d)`).

**OrderedHash의 직렬화 규약을 정확히 지킨다.** 그 클래스는 `_dump`/`_load`를 손수 정의한다 —
`041:329`

```ruby
def self._load(string)
  ret=self.new
  keysvalues=Marshal.load(string)
  keys=keysvalues[0]; values=keysvalues[1]
  for i in 0...keys.length
    ret[keys[i]]=values[i]
  end
  return ret
end
```

곧 Marshal 안에 **`[keys, values]`를 다시 Marshal한 바이트열**이 들어 있는 모양이고,
`build.py`가 손대는 `_private_data`가 정확히 그 바이트열이다(`build.py:32` `inner_of`,
`:74` `rubywrite.dumps([keys, values])`). 새 항목을 뒤에 덧붙여도 `_load`가 `[]=`로 하나씩
넣으므로 순서가 보존된다(`041:318`의 `[]=`가 `@keys`에 push한다).

**값은 그냥 바이트열이다.** Ruby 1.8은 문자열에 인코딩 꼬리표가 없으므로 UTF-8 바이트를
그대로 실어도 된다. `<<n>>` 같은 이스케이프는 **텍스트 파일(`intl.txt`) 경로 전용**이다 —
`normalizeValue`/`denormalizeValue`(`041:378`, `:392`)는 `pbGetText`·`extract`에서만 불리고
Marshal 경로에는 안 낀다. **재번역 값에 `<<n>>`을 쓰면 그 글자가 그대로 화면에 뜬다.**

### 5-1. 전량 재번역이 깨뜨릴 수 있는 자리와, 어디서 막을 것인가

`build.py`가 지금 검사하는 것은 **골격**뿐이다 — 절 수, 줄 수, 키 일치, 왕복 무결성. 값 안쪽은
안 본다. 재번역 배치를 태우기 전에 아래를 값 검사로 세워야 한다.

1. **자리표 보존**: 값의 `{1}`·`{2}`… 집합이 키와 같아야 한다. `_INTL`은 없으면 조용히 인자를
   버린다(`041:723`의 `gsub!`가 안 걸릴 뿐이다). **지금은 20,600여 줄에서 불일치 0건** —
   이 상태를 유지하는 것이 검사의 목적이다.
2. **`_ISPRINTF` 지시자 보존**: `{1:02d}` 꼴은 콜론 뒤 글자까지 정확해야 `sprintf`가 돈다
   (`041:740`). `026_Sprite_Timer.rb:38`, `135_PScreen_Bag.rb:73` 등 103곳이 걸린다.
3. **`\x01` 보존**: 메시지 끝 대기 표식이다. 절23 키 119개에 있고 현재 불일치 0건. 빠지면
   대사가 다음 대사와 붙어 버린다.
4. **제어 코드 보존**: `\c[n]`·`\v[n]`·`\PN`·`\n`·`\m`·`\TP`·`\TE`·`\TM`·`<icon=...>`·`<r>`.
   `\j[..]`만 우리가 **더하는** 것이라 예외로 둔다. 지금 `\j`를 뺀 실질 불일치가 절23 13건 ·
   절0 25건 · 절22 9건이다(대부분 `\n` 위치 이동, 절22는 표식 누락 의심).
5. **키 정규화 검사(새로 필요)**: `stringToKey(key) == key`가 아닌 키는 절대 안 맞는다.
   지금 73건이 걸린다(§4-6). `build.py`가 `assert`로 막아야 할 자리다.
6. **`<<n>>` 금지 검사**: Marshal 경로에는 안 풀리는 표기다.
7. **`\j` 사용 시 Josa Select 동반 검사**: dat와 모드가 따로 배포되면 화면에 `\j[은,는]`이
   그대로 뜬다.

값 검사를 넣을 자리는 `build.py`의 절별 순회 안쪽 — 지금 `assert row["k"] == keys[j]…`를
하는 바로 그 줄 옆이다(`build.py:64`, `:91`). 골격 검사와 같은 곳에서 멈추게 두는 편이,
게임을 켜서 스페인어가 나오는 걸 보고 되짚는 것보다 싸다.

---

## 6. 못 찾은 것 · 확인 안 한 것

- **게임 실행 검증이 하나도 없다.** §4-6의 「도달 불가 44건」은 코드 판독에서 나온 예측이다.
  검증하려면 전투를 한 번 걸어 「상대가 포켓몬을 내보내는 문장」이 스페인어인지 보면 된다 —
  30초짜리 확인인데 못 했다.
- **`Data/messages.dat`(스페인어 원본)의 절 구성**을 직접 안 열어 봤다. `export.py`가 목록 절
  참조용으로만 읽고 있어 `es` 칸으로 간접 확인한 정도다.
- **`Window_UnformattedTextPokemon`을 실제로 쓰는 화면 목록**을 안 셌다. Josa 모드가 감싸고
  있으니 경로는 열려 있지만, `draw_text` 직결 경로와의 비율은 모른다.
- **`\j`가 안 풀리는 화면이 실제로 있는지** 확인 안 했다(§4-8의 `draw_text` 14+10+3곳 중
  한국어가 지나는 곳이 어디인지).
- **`204_CartelesPokemon.rb` 원문**을 열어 하드코딩 문구 전수를 세지 않았다. `UI Text KR`의
  표에 든 세 줄이 전부인지 미확인.
- **절2(Kinds)·절3(Entries)의 줄 수 1,019가 종 수와 맞는지** 대조 안 했다.
