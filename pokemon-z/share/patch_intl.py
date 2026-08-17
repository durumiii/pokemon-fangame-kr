# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scripts.rxdata 보간 리터럴 수술 — _INTL("...#{x}...") → _INTL("...{1}...",x).

루비 보간이 _INTL 리터럴 안에 있으면 런타임 문자열이 매번 달라져 번역표 키와
영원히 안 맞는다(제보 목록의 「루비 보간 리터럴 12곳」). 이 도구는 원문 소스를
정확 일치로 치환해 정상 템플릿 경로에 합류시킨다. 대응 번역은 정본
translate/ko/23-script-texts.jsonl에 있다(동결 목록 data/frozen-keys.jsonl의
「보간 수술」 src 행들이 그 자리를 가리킨다).

12곳 중 수술 대상은 6곳 — 주머니 번호 보간 5곳은 런타임 키(bagPocket1~8)가
이미 dat에 번역돼 있어 손댈 필요가 없고, 1곳(166 타일퍼즐)은 그래픽 경로다.

멱등: 새 문자열이 이미 있으면 건너뛴다. 옛/새 어느 쪽도 없으면 에러로 멈춘다
(게임 판 갱신으로 원문이 바뀐 신호).

usage: uv run patch_intl.py [대상 Scripts.rxdata ...]
  무인자면 보관소 기반판 + 게임 설치본 둘 다.
"""
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)
from fanlib import rubywrite  # noqa: E402

DEFAULT_TARGETS = [
    Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/Scripts.rxdata"),
    Path("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata"),
]

# (섹션명 실마리, 옛 소스, 새 소스) — 옛 소스는 추출본과 글자 단위 일치해야 한다.
EDITS = [
    ("PokeBattle_Battler",
     '_INTL("¡#{pbThis} alteró las dimensiones!")',
     '_INTL("¡{1} alteró las dimensiones!",pbThis)'),
    ("PokeBattle_Battle",
     '_INTL("¡Solo puedes capturar Pokémon de tipo #{allowed_type}!")',
     '_INTL("¡Solo puedes capturar Pokémon de tipo {1}!",allowed_type)'),
    ("Following",
     '_INTL("#{$Trainer.party[0].name} está debilitado.\\nApenas puede tenerse en pie...")',
     '_INTL("{1} está debilitado.\\nApenas puede tenerse en pie...",$Trainer.party[0].name)'),
    ("Following",
     '_INTL("Sin duda, tienes el mejor #{$Trainer.party[0].name} del mundo.")',
     '_INTL("Sin duda, tienes el mejor {1} del mundo.",$Trainer.party[0].name)'),
    ("Cambia Habilidades",
     '_INTL("¿Qué habilidad quieres para #{pokemon.name}?")',
     '_INTL("¿Qué habilidad quieres para {1}?",pokemon.name)'),
]

# 이벤트 선택지(command_102) — 선택지 문자열이 번역 조회 없이 pbShowCommands로
# 직행해 Sí/No가 스페인어로 노출되는 기능 버그(제보 목록 「제보 6건」의 첫 건).
# Messages 절이 Interpreter/Game_Interpreter 양쪽에 같은 본문을 정의하므로
# 한 EDIT이 2곳을 치환한다. 조회는 게임의 정규 사슬(현재 맵 해시 → 맵0 공통
# 이벤트 폴백)을 그대로 탄다. 루비 1.8 문법 유의.
EDITS += [
    ("Messages",
     "command=Kernel.pbShowCommands(nil,@list[@index].parameters[0],@list[@index].parameters[1])",
     "command=Kernel.pbShowCommands(nil,@list[@index].parameters[0].collect{|c| "
     "MessageTypes.getFromMapHash($game_map ? $game_map.map_id : 0,c)},"
     "@list[@index].parameters[1])"),
]

# 앙코르 성공 문구가 저주 문구다(원작 소스의 문자열 오배치 — 2026-08-05 제보·조사).
# 0BC(Otra Vez/Encore)가 Encore 상태 값 셋을 세팅한 바로 다음 줄에서 저주 문구를 띄운다.
# 진짜 저주 자리는 PokeBattle_Battle의 턴 종료 처리에 따로 있고 그쪽은 정상이다.
# 두 자리가 같은 리터럴을 쓰므로 번역표로는 원리상 분리할 수 없다 — 소스에서 가른다.
# 새 문자열은 본가 스페인어판 자구(공식 코퍼스 실측: "¡… ha sufrido los efectos de
# Otra Vez!" → 「… 앙코르를 받았다!」), 짝 번역은 23-script-texts.jsonl.
# 옛 문자열이 저주 쪽과 안 겹치는 근거: 인자가 다르다(여기는 opponent.pbThis, 저주는 i.pbThis).
EDITS += [
    ("PokeBattle_MoveEffects",
     '_INTL("¡{1} es víctima de una Maldición!",opponent.pbThis)',
     '_INTL("¡{1} ha sufrido los efectos de Otra Vez!",opponent.pbThis)'),
]

# Constants.rxdata 로드 실패 표면화(진단 전용, 동작 불변) — JoiPlay에서 이 로드가
# 조용히 삼켜져 뒤(246 RandomObjects)에서 NameError로 터지는 사슬(제보 목록의 JoiPlay
# 건). 실패 시 진짜 원인을 화면에 띄운다. 문구는 ASCII — JoiPlay는 한글 폰트가
# 깨지는 환경이라서다. 기능 수정은 원인 확정 전 금지(2026-08-04 사용자 결정).
EDITS += [
    ("PSystem_System",
     '  begin\r\n'
     '    consts=pbSafeLoad("Data/Constants.rxdata")\r\n'
     '    consts=[] if !consts\r\n'
     '  rescue\r\n'
     '    consts=[]\r\n'
     '  end',
     '  begin\r\n'
     '    consts=pbSafeLoad("Data/Constants.rxdata")\r\n'
     '    consts=[] if !consts\r\n'
     '  rescue\r\n'
     '    p "KR-PATCH DIAG: Constants.rxdata load failed - #{$!.class}: #{$!.message}"\r\n'
     '    consts=[]\r\n'
     '  end\r\n'
     '  p "KR-PATCH DIAG: Constants.rxdata empty - game constants missing (please report this screen)" if consts.length==0'),
]

# 요약 화면 성격 한 줄 — 명사(얌전)를 활용형(얌전한)으로. 성격명 자체는 성격
# 변경 목록 등에서 명사로 계속 쓰이므로 이 화면의 변수에만 25종 표를 얹는다.
# 짝인 템플릿 번역은 절23 「{1} 성격이다.」 (translate/ko 정본). 루비 1.8 문법.
_NATURE_ADJ = ("노력하는,외로움을 타는,용감한,고집스러운,개구쟁이,대담한,온순한,"
               "무사태평한,장난꾸러기,촐랑거리는,겁이 많은,성급한,성실한,명랑한,"
               "천진난만한,조심스러운,의젓한,냉정한,수줍음이 많은,덜렁거리는,"
               "차분한,얌전한,건방진,신중한,변덕스러운").split(",")
EDITS += [
    ("PScreen_Summary",
     "naturename=PBNatures.getName(pokemon.nature)",
     "naturename=([" + ",".join(f'"{a}"' for a in _NATURE_ADJ) + "]"
     "[pokemon.nature] || PBNatures.getName(pokemon.nature))"),
]

# 트레이너 메모 — 장소 줄의 개행을 지워 다음 만남 문구와 한 줄로 병합한다:
# 「1번도로」+「에서 Lv. 5일 때 발견됨.」. 만난 곳·부화한 곳이 같은 리터럴이라
# EDIT 하나가 2곳을 치환한다. 만남 문구(절23 번역)는 「에서 …」로 시작하고
# sprintf가 회색 접두를 이미 붙이므로 색 경계도 그대로 선다.
EDITS += [
    ("PScreen_Summary",
     'memo+=sprintf("<c3=F83820,E09890>%s\\n",mapname)',
     'memo+=sprintf("<c3=F83820,E09890>%s",mapname)'),
]

# 트레이너가 붙인 포켓몬 별명 — 번역표가 닿지 않는 자리(Z-63). 별명은 trainers.dat에
# 들어 있고 pbLoadTrainer가 그대로 pokemon.name에 넣는다(바로 위 트레이너 이름은
# pbGetMessageFromHash를 통과하는데 별명에는 그 포장이 없다). 게임 전체에 별명은
# 간수 피노의 대포무노 하나뿐이라(trainers.dat 476 트레이너 전수 셈) 표 대신 조건 하나로
# 간다 — 늘면 그때 표로 바꾼다. 번역어는 대사 정본과 같은 「폴리」(유지자 판정 2026-08-16).
# 루비 1.8 문법.
EDITS += [
    ("PTrainer_NPCTrainers",
     'pokemon.name=poke[TPNAME] if poke[TPNAME] && poke[TPNAME]!=""',
     'pokemon.name=(poke[TPNAME]=="Paulie" ? "폴리" : poke[TPNAME]) '
     'if poke[TPNAME] && poke[TPNAME]!=""'),
]

# 보스 포켓몬 이름 둘 — 별명과 같은 병이다(Z-63). 코드가 pokemon.name에 리터럴을
# 곧바로 대입하므로 _INTL 포장이 없고, 그래서 어느 절에도 담기지 않는다(messages.dat에
# ARTIFICIO 0건). 둘 다 MISSINGNO에 폼만 갈아 끼운 보스다.
#   ARTIFICIO(맵 286 프레스코 풍차, 폼 1) → 「수호장치」 — 대사가 이 상대를 「수호 포켓몬」
#     이라 부른다(맵 283·286에 5줄). 유지자 판정 2026-08-17(의역).
#   FLOR(맵 474 최종병기, 폼 2) → 「꽃」 — 원문이 보통명사를 이름으로 세운 결을 그대로.
#     본가 공식 「영원의 꽃」은 안 쓴다: 그 말은 AZ의 플라엣테를 가리키는데 같은 장면에
#     플라엣테가 따로 등장해 섞인다(유지자 판정 2026-08-17).
# FLOR는 한 마리에 이름이 두 번 대입된다 — 훅(EncounterModifiers)이 먼저 넣고
# pbBossFight 본문(Boss)이 같은 값으로 덮으므로 **두 자리를 함께 고쳐야 한다.**
# 이름칸은 잘림 처리가 없고 다섯 글자까지 레벨 표시와 안 겹친다(실측).
EDITS += [
    ("PField_EncounterModifiers", 'pokemon.name="ARTIFICIO"', 'pokemon.name="수호장치"'),
    ("PField_EncounterModifiers", 'pokemon.name="FLOR"', 'pokemon.name="꽃"'),
    ("Boss", 'genwildpoke.name="FLOR"', 'genwildpoke.name="꽃"'),
]

# 부적(Amuleto) 18종 — pbAmuleto(116_PItem_ItemEffects)가 번역된 아이템 이름을
# 스페인어 원문과 문자열 비교해 인카운터 스위치(280~297)를 켠다. 이름이
# 한글화되면 영원히 거짓이 되는 기능 버그라, 이름 비교를 상수 비교로 수술한다.
_AMULETOS = [
    ("Amuleto Bicho", "AMULETOBICHO"), ("Amuleto Siniestro", "AMULETOSINIESTRO"),
    ("Amuleto Dragón", "AMULETODRAGON"), ("Amuleto Eléctrico", "AMULETOELECTRICO"),
    ("Amuleto Hada", "AMULETOHADA"), ("Amuleto Lucha", "AMULETOLUCHA"),
    ("Amuleto Fuego", "AMULETOFUEGO"), ("Amuleto Volador", "AMULETOVOLADOR"),
    ("Amuleto Fantasma", "AMULETOFANTASMA"), ("Amuleto Planta", "AMULETOPLANTA"),
    ("Amuleto Tierra", "AMULETOTIERRA"), ("Amuleto Hielo", "AMULETOHIELO"),
    ("Amuleto Normal", "AMULETONORMAL"), ("Amuleto Veneno", "AMULETOVENENO"),
    ("Amuleto Psíquico", "AMULETOPSIQUICO"), ("Amuleto Roca", "AMULETOROCA"),
    ("Amuleto Acero", "AMULETOACERO"), ("Amuleto Agua", "AMULETOAGUA"),
]
EDITS += [
    ("PItem_ItemEffects",
     f'PBItems.getName(item) == "{name}"',
     f'isConst?(item,PBItems,:{const})')
    for name, const in _AMULETOS
]

# 좌표 조회 1단(Z-73) — 맵 대사·선택지를 (맵, 이벤트, 명령 인덱스) + 원문으로 먼저 찾고,
# 없으면 지금까지의 사슬(현재 맵 → 맵0 → 원문)로 그대로 떨어진다. 좌표 항목이 있는 줄만
# 새 경로를 타므로 기존 동작은 안 바뀌고, 맵0 우회(Z-61)와도 안 부딪힌다.
#
# 열쇠 꼴 "krloc:<맵>:<이벤트>:<명령>|<정규화한 원문>" 은 translate/build.py와 한 글자도
# 어긋나면 안 된다 — 그래서 조립을 MessageTypes.krLoc 한 자리에 모으고 부르는 쪽은
# 한 줄씩만 얹는다. 원문에 stringToKey를 미리 걸어 두므로 getFromMapHash 안에서 한 번
# 더 걸려도 결과가 같다(정규화가 멱등이고 접두에는 공백이 없다).
#
# ⚠ 맵 번호는 이벤트 소속 맵 @map_id를 쓴다($game_map.map_id가 아니다 — 전이 뒤 대사에서
# 둘이 갈린다). 폴백 경로는 지금 값 그대로 둔다.
# 도는 인터프리터는 Interpreter 하나뿐이라(Game_Interpreter는 죽은 코드) 수술 자리도
# 그쪽뿐이다. 옛 소스가 두 클래스에 복제돼 있으므로 앵커에 Interpreter 쪽에만 있는
# 줄(firstText·주석·pbMessage의 nil 인자)을 물려 한쪽만 갈린다. 루비 1.8 문법.
# ⚠ 얹기만 하는 수술은 **옛 소스가 새 소스 안에 그대로 남는다** — 멱등 판정이
# 「새 것이 있고 옛 것이 없으면 건너뛴다」라서, 그러면 돌릴 때마다 또 얹힌다
# (2026-08-17에 실제로 두 번 얹혔다). 그래서 앵커에 **뒤따르는 줄까지** 물려
# 옛 소스가 새 소스의 부분 문자열이 되지 않게 한다.
EDITS += [
    ("Intl_Messages",
     '  def self.getFromMapHash(type,key)\r\n'
     '    @@messages.getFromMapHash(type,key)\r\n'
     '  end\r\n'
     'end\r\n',
     '  def self.getFromMapHash(type,key)\r\n'
     '    @@messages.getFromMapHash(type,key)\r\n'
     '  end\r\n'
     '\r\n'
     '  # 좌표 조회(Z-73) — 못 찾으면 nil을 주고 부르는 쪽이 옛 조회로 떨어진다.\r\n'
     '  def self.krLoc(mapid,eventid,index,str)\r\n'
     '    key="krloc:#{mapid}:#{eventid}:#{index}|"+Messages.stringToKey(str)\r\n'
     '    hit=@@messages.getFromMapHash(mapid,key)\r\n'
     '    return hit==key ? nil : hit\r\n'
     '  end\r\n'
     'end\r\n'),

    # 대사 조회 좌표의 명령 인덱스는 **101이 선 자리**다 — 아래 루프가 @index를 401
    # 마지막 줄까지 밀어 놓으므로 루프 전에 잡아 둔다.
    ("Messages",
     '    firstText=nil\r\n'
     '    if @list[@index].parameters.length==1\r\n',
     '    firstText=nil\r\n'
     '    krIndex=@index\r\n'
     '    if @list[@index].parameters.length==1\r\n'),

    ("Messages",
     '    message=_MAPINTL($game_map.map_id,message)\r\n'
     '    if commands\r\n'
     '      cmdlist=[]\r\n'
     '      for cmd in commands[0]\r\n'
     '        cmdlist.push(_MAPINTL($game_map.map_id,cmd))\r\n'
     '      end\r\n',
     '    krHit=MessageTypes.krLoc(@map_id,@event_id,krIndex,message)\r\n'
     '    message=krHit ? krHit : _MAPINTL($game_map.map_id,message)\r\n'
     '    if commands\r\n'
     '      cmdlist=[]\r\n'
     '      for cmd in commands[0]\r\n'
     '        krHit=MessageTypes.krLoc(@map_id,@event_id,@index,cmd)\r\n'
     '        cmdlist.push(krHit ? krHit : _MAPINTL($game_map.map_id,cmd))\r\n'
     '      end\r\n'),

    # 홀로 선 선택지(command_102). 앞의 pbMessage(...,nil)이 Interpreter 쪽 표식이다.
    ("Messages",
     '      Kernel.pbMessage(message+messageend,nil)\r\n'
     '    end\r\n'
     '    @message_waiting=false\r\n'
     '    return true\r\n'
     '  end\r\n'
     '\r\n'
     '  def command_102\r\n'
     '    @message_waiting=true\r\n'
     '    command=Kernel.pbShowCommands(nil,@list[@index].parameters[0].collect{|c| '
     'MessageTypes.getFromMapHash($game_map ? $game_map.map_id : 0,c)},'
     '@list[@index].parameters[1])\r\n',
     '      Kernel.pbMessage(message+messageend,nil)\r\n'
     '    end\r\n'
     '    @message_waiting=false\r\n'
     '    return true\r\n'
     '  end\r\n'
     '\r\n'
     '  def command_102\r\n'
     '    @message_waiting=true\r\n'
     '    command=Kernel.pbShowCommands(nil,@list[@index].parameters[0].collect{|c| '
     'MessageTypes.krLoc(@map_id,@event_id,@index,c) || '
     'MessageTypes.getFromMapHash($game_map ? $game_map.map_id : 0,c)},'
     '@list[@index].parameters[1])\r\n'),
]


def patch_file(path: Path) -> None:
    secs = load(open(path, "rb"))
    done = skipped = 0
    for hint, old, new in EDITS:
        hit = False
        for sec in secs:
            name = bytes(sec[1]).decode("utf-8", "replace")
            if hint not in name or name.startswith("MOD:"):
                continue
            src = zlib.decompress(bytes(sec[2])).decode("utf-8")
            if new in src and old not in src:
                skipped += 1
                hit = True
                break
            if old in src:
                n = src.count(old)
                sec[2] = zlib.compress(src.replace(old, new).encode("utf-8"))
                print(f"  {name}: {n}곳 치환")
                done += n
                hit = True
                break
        if not hit:
            sys.exit(f"중단: {path} 의 '{hint}' 절에서 옛/새 소스 모두 못 찾음 — 원문이 바뀌었는지 확인")
    if done:
        bak = path.with_suffix(".rxdata.pre-intl.bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())
        with open(path, "wb") as fd:
            rubywrite.dump(fd, secs)
    print(f"{path}: 치환 {done}곳, 기적용 건너뜀 {skipped}건")


if __name__ == "__main__":
    targets = [Path(a) for a in sys.argv[1:]] or DEFAULT_TARGETS
    for t in targets:
        patch_file(t)
